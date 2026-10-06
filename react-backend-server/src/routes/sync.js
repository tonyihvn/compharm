/**
 * Sync Routes - Handle OpenMRS and Pharmacy sync operations
 */

import express from 'express';
import { sequelize } from '../models/index.js';
import { authenticate } from '../middleware/auth.js';
import logger from '../config/logger.js';

const router = express.Router();

// Get sync logs
router.get('/logs', authenticate, async (req, res) => {
    try {
        const { page = 1, limit = 50, type, status } = req.query;
        const offset = (page - 1) * limit;

        const where = {};
        if (type) where.sync_type = type;
        if (status) where.sync_status = status;

        const logs = await sequelize.models.SyncLog.findAndCountAll({
            where,
            limit: parseInt(limit),
            offset: parseInt(offset),
            order: [['createdAt', 'DESC']]
        });

        res.json({
            message: 'Sync logs retrieved',
            data: logs.rows,
            total: logs.count,
            page: parseInt(page),
            pages: Math.ceil(logs.count / limit)
        });
    } catch (error) {
        logger.error('Get sync logs error:', error);
        res.status(500).json({ message: 'Error retrieving sync logs' });
    }
});

// Get sync status
router.get('/status', authenticate, async (req, res) => {
    try {
        const lastSync = await sequelize.models.SyncLog.findOne({
            order: [['createdAt', 'DESC']]
        });

        const pendingSubmissions = await sequelize.models.FormSubmission.count({
            where: { status: 'submitted', synced_at: null }
        });

        res.json({
            message: 'Sync status retrieved',
            data: {
                lastSync: lastSync ? lastSync.created_at : null,
                lastSyncStatus: lastSync ? lastSync.sync_status : null,
                pendingSubmissions,
                systemHealthy: pendingSubmissions < 1000
            }
        });
    } catch (error) {
        logger.error('Get sync status error:', error);
        res.status(500).json({ message: 'Error retrieving sync status' });
    }
});

// Pharmacy sync endpoint - Pull clients
router.post('/pharmacy/pull-clients', authenticate, async (req, res) => {
    try {
        const { pharmacyId } = req.body;
        const { userId } = req.user;

        if (!pharmacyId) {
            return res.status(400).json({ message: 'Missing pharmacyId' });
        }

        // Get all clients assigned to this pharmacy
        const clients = await sequelize.models.Client.findAll({
            where: { pharmacy_id: pharmacyId },
            raw: true
        });

        // Log sync
        await sequelize.models.SyncLog.create({
            pharmacy_id: pharmacyId,
            sync_type: 'pharmacy_pull',
            sync_status: 'success',
            records_count: clients.length,
            sync_data: JSON.stringify({ clients_count: clients.length }),
            synced_by: userId
        });

        logger.info(`Pharmacy ${pharmacyId} pulled ${clients.length} clients`);

        res.json({
            message: 'Clients synced successfully',
            data: clients,
            count: clients.length,
            timestamp: new Date()
        });
    } catch (error) {
        logger.error('Pharmacy sync error:', error);

        // Log failed sync
        const { pharmacyId, userId } = req.body;
        if (pharmacyId) {
            await sequelize.models.SyncLog.create({
                pharmacy_id: pharmacyId,
                sync_type: 'pharmacy_pull',
                sync_status: 'failed',
                error_message: error.message,
                synced_by: userId
            }).catch(e => logger.error('Error logging sync failure:', e));
        }

        res.status(500).json({ message: 'Error syncing clients' });
    }
});

// Pharmacy sync endpoint - Push forms
router.post('/pharmacy/push-forms', authenticate, async (req, res) => {
    try {
        const { pharmacyId } = req.body;
        const { userId } = req.user;

        if (!pharmacyId) {
            return res.status(400).json({ message: 'Missing pharmacyId' });
        }

        // Get all active forms
        const forms = await sequelize.models.Form.findAll({
            where: { is_active: true },
            raw: true
        });

        // Log sync
        await sequelize.models.SyncLog.create({
            pharmacy_id: pharmacyId,
            sync_type: 'pharmacy_push_forms',
            sync_status: 'success',
            records_count: forms.length,
            sync_data: JSON.stringify({ forms_count: forms.length }),
            synced_by: userId
        });

        logger.info(`Pharmacy ${pharmacyId} pulled ${forms.length} forms`);

        res.json({
            message: 'Forms synced successfully',
            data: forms,
            count: forms.length,
            timestamp: new Date()
        });
    } catch (error) {
        logger.error('Forms sync error:', error);
        res.status(500).json({ message: 'Error syncing forms' });
    }
});

// OpenMRS sync endpoint - Pull form submissions
router.post('/openmrs/pull-submissions', authenticate, async (req, res) => {
    try {
        const { userId } = req.user;

        // Get submissions ready for OpenMRS
        const submissions = await sequelize.models.FormSubmission.findAll({
            where: { status: 'submitted', synced_at: null },
            include: [
                { model: sequelize.models.Client, attributes: ['id', 'pepfarid', 'full_name'] },
                { model: sequelize.models.Form, attributes: ['id', 'form_code'] }
            ],
            limit: 100,
            raw: false
        });

        // Log sync
        await sequelize.models.SyncLog.create({
            sync_type: 'openmrs_pull',
            sync_status: 'success',
            records_count: submissions.length,
            sync_data: JSON.stringify({ submissions_count: submissions.length }),
            synced_by: userId
        });

        logger.info(`OpenMRS pulled ${submissions.length} submissions`);

        res.json({
            message: 'Submissions ready for OpenMRS',
            data: submissions.map(s => ({
                submissionId: s.id,
                clientId: s.client_id,
                pepfarId: s.Client?.pepfarid,
                formCode: s.Form?.form_code,
                submissionData: JSON.parse(s.submission_data || '{}'),
                submittedAt: s.submitted_at
            })),
            count: submissions.length,
            timestamp: new Date()
        });
    } catch (error) {
        logger.error('OpenMRS sync error:', error);
        res.status(500).json({ message: 'Error retrieving submissions for OpenMRS' });
    }
});

// OpenMRS sync endpoint - Confirm sync
router.post('/openmrs/confirm-sync', authenticate, async (req, res) => {
    try {
        const { submissions } = req.body;
        const { userId } = req.user;

        if (!Array.isArray(submissions)) {
            return res.status(400).json({ message: 'Invalid submissions format' });
        }

        let syncedCount = 0;

        for (const submissionData of submissions) {
            try {
                const submission = await sequelize.models.FormSubmission.findByPk(
                    submissionData.submissionId
                );

                if (submission) {
                    await submission.update({
                        status: 'synced',
                        synced_at: new Date(),
                        openmrs_encounter_id: submissionData.encounterId
                    });
                    syncedCount++;
                }
            } catch (error) {
                logger.error(`Error syncing submission ${submissionData.submissionId}:`, error);
            }
        }

        // Log sync
        await sequelize.models.SyncLog.create({
            sync_type: 'openmrs_push',
            sync_status: 'success',
            records_count: syncedCount,
            sync_data: JSON.stringify({ synced_count: syncedCount }),
            synced_by: userId
        });

        logger.info(`OpenMRS confirmed sync for ${syncedCount} submissions`);

        res.json({
            message: 'Sync confirmation received',
            syncedCount,
            timestamp: new Date()
        });
    } catch (error) {
        logger.error('OpenMRS confirm sync error:', error);
        res.status(500).json({ message: 'Error confirming sync' });
    }
});

// Get sync history for a specific pharmacy
router.get('/pharmacy/:pharmacyId/history', authenticate, async (req, res) => {
    try {
        const { pharmacyId } = req.params;
        const { limit = 20 } = req.query;

        const history = await sequelize.models.SyncLog.findAll({
            where: { pharmacy_id: pharmacyId },
            order: [['createdAt', 'DESC']],
            limit: parseInt(limit)
        });

        res.json({
            message: 'Sync history retrieved',
            data: history
        });
    } catch (error) {
        logger.error('Get sync history error:', error);
        res.status(500).json({ message: 'Error retrieving sync history' });
    }
});

// Manual sync trigger endpoint
router.post('/trigger-sync', authenticate, async (req, res) => {
    try {
        const { pharmacyId, syncType } = req.body;
        const { userId } = req.user;

        logger.info(`Manual sync triggered: pharmacy ${pharmacyId}, type: ${syncType}`);

        // Emit event for sync worker
        req.app.emit('sync:triggered', {
            pharmacyId,
            syncType,
            userId,
            timestamp: new Date()
        });

        res.json({
            message: 'Sync triggered successfully',
            timestamp: new Date()
        });
    } catch (error) {
        logger.error('Trigger sync error:', error);
        res.status(500).json({ message: 'Error triggering sync' });
    }
});

export default router;
