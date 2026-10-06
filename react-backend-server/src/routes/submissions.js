/**
 * Form Submissions Routes - Handle form submission data
 */

import express from 'express';
import { sequelize } from '../models/index.js';
import { authenticate } from '../middleware/auth.js';
import logger from '../config/logger.js';

const router = express.Router();

// Submit form
router.post('/submit', authenticate, async (req, res) => {
    try {
        const submissionData = req.body;
        const { userId, pharmacyId } = req.user;

        // Validate required fields
        if (!submissionData.formId || !submissionData.clientId) {
            return res.status(400).json({ message: 'Missing formId or clientId' });
        }

        // Create submission record
        const submission = await sequelize.models.FormSubmission.create({
            form_id: submissionData.formId,
            client_id: submissionData.clientId,
            pharmacy_id: pharmacyId,
            submitted_by: userId,
            submission_data: JSON.stringify(submissionData.fields || {}),
            status: 'submitted',
            submitted_at: new Date()
        });

        logger.info(`Form submitted: Form ${submissionData.formId} by Client ${submissionData.clientId}`);

        // Emit event for OpenMRS sync
        // This could be a webhook or message queue
        req.app.emit('form:submitted', {
            submissionId: submission.id,
            formId: submissionData.formId,
            clientId: submissionData.clientId,
            pharmacyId,
            timestamp: new Date()
        });

        res.status(201).json({
            message: 'Form submitted successfully',
            submissionId: submission.id,
            data: submission
        });
    } catch (error) {
        logger.error('Form submission error:', error);
        res.status(500).json({ message: 'Error submitting form' });
    }
});

// Save form as draft
router.post('/save-draft', authenticate, async (req, res) => {
    try {
        const draftData = req.body;
        const { userId, pharmacyId } = req.user;

        if (!draftData.formId || !draftData.clientId) {
            return res.status(400).json({ message: 'Missing formId or clientId' });
        }

        // Check if draft already exists
        let submission = await sequelize.models.FormSubmission.findOne({
            where: {
                form_id: draftData.formId,
                client_id: draftData.clientId,
                status: 'draft',
                pharmacy_id: pharmacyId
            }
        });

        if (submission) {
            // Update existing draft
            await submission.update({
                submission_data: JSON.stringify(draftData.fields || {}),
                updated_at: new Date()
            });
            logger.info(`Draft updated: Form ${draftData.formId} by Client ${draftData.clientId}`);
        } else {
            // Create new draft
            submission = await sequelize.models.FormSubmission.create({
                form_id: draftData.formId,
                client_id: draftData.clientId,
                pharmacy_id: pharmacyId,
                submitted_by: userId,
                submission_data: JSON.stringify(draftData.fields || {}),
                status: 'draft'
            });
            logger.info(`Draft created: Form ${draftData.formId} by Client ${draftData.clientId}`);
        }

        res.json({
            message: 'Form saved as draft',
            submissionId: submission.id,
            data: submission
        });
    } catch (error) {
        logger.error('Save draft error:', error);
        res.status(500).json({ message: 'Error saving draft' });
    }
});

// Get submission by ID
router.get('/:submissionId', authenticate, async (req, res) => {
    try {
        const { submissionId } = req.params;

        const submission = await sequelize.models.FormSubmission.findByPk(submissionId);

        if (!submission) {
            return res.status(404).json({ message: 'Submission not found' });
        }

        res.json({
            message: 'Submission retrieved successfully',
            data: {
                ...submission.toJSON(),
                submission_data: JSON.parse(submission.submission_data || '{}')
            }
        });
    } catch (error) {
        logger.error('Get submission error:', error);
        res.status(500).json({ message: 'Error retrieving submission' });
    }
});

// Get client submissions
router.get('/client/:clientId/submissions', authenticate, async (req, res) => {
    try {
        const { clientId } = req.params;
        const { page = 1, limit = 20, status } = req.query;
        const offset = (page - 1) * limit;

        const where = { client_id: clientId };
        if (status) where.status = status;

        const submissions = await sequelize.models.FormSubmission.findAndCountAll({
            where,
            limit: parseInt(limit),
            offset: parseInt(offset),
            order: [['createdAt', 'DESC']],
            include: [
                { model: sequelize.models.Form, attributes: ['form_name'] }
            ]
        });

        res.json({
            message: 'Client submissions retrieved',
            data: submissions.rows.map(s => ({
                ...s.toJSON(),
                submission_data: JSON.parse(s.submission_data || '{}')
            })),
            total: submissions.count,
            page: parseInt(page),
            pages: Math.ceil(submissions.count / limit)
        });
    } catch (error) {
        logger.error('Get client submissions error:', error);
        res.status(500).json({ message: 'Error retrieving submissions' });
    }
});

// Update submission status (e.g., approve, reject)
router.patch('/:submissionId/status', authenticate, async (req, res) => {
    try {
        const { submissionId } = req.params;
        const { status, notes } = req.body;

        const submission = await sequelize.models.FormSubmission.findByPk(submissionId);

        if (!submission) {
            return res.status(404).json({ message: 'Submission not found' });
        }

        const validStatuses = ['draft', 'submitted', 'approved', 'rejected', 'synced'];
        if (!validStatuses.includes(status)) {
            return res.status(400).json({ message: 'Invalid status' });
        }

        await submission.update({
            status,
            status_notes: notes,
            status_updated_at: new Date()
        });

        logger.info(`Submission status updated: ${submissionId} -> ${status}`);

        res.json({
            message: 'Submission status updated',
            data: submission
        });
    } catch (error) {
        logger.error('Update submission status error:', error);
        res.status(500).json({ message: 'Error updating submission' });
    }
});

// Get submissions for sync to OpenMRS
router.get('/sync/pending', authenticate, async (req, res) => {
    try {
        const submissions = await sequelize.models.FormSubmission.findAll({
            where: { status: 'submitted', synced_at: null },
            include: [
                { model: sequelize.models.Client, attributes: ['id', 'pepfarid', 'full_name'] },
                { model: sequelize.models.Form, attributes: ['id', 'form_code', 'form_name'] }
            ],
            order: [['submittedAt', 'ASC']],
            limit: 100
        });

        res.json({
            message: 'Pending submissions retrieved',
            data: submissions.map(s => ({
                ...s.toJSON(),
                submission_data: JSON.parse(s.submission_data || '{}')
            }))
        });
    } catch (error) {
        logger.error('Get pending submissions error:', error);
        res.status(500).json({ message: 'Error retrieving submissions' });
    }
});

// Mark submission as synced to OpenMRS
router.patch('/:submissionId/synced', authenticate, async (req, res) => {
    try {
        const { submissionId } = req.params;
        const { openMrsEncounterId } = req.body;

        const submission = await sequelize.models.FormSubmission.findByPk(submissionId);

        if (!submission) {
            return res.status(404).json({ message: 'Submission not found' });
        }

        await submission.update({
            status: 'synced',
            synced_at: new Date(),
            openmrs_encounter_id: openMrsEncounterId
        });

        logger.info(`Submission marked as synced: ${submissionId}`);

        res.json({
            message: 'Submission marked as synced',
            data: submission
        });
    } catch (error) {
        logger.error('Mark synced error:', error);
        res.status(500).json({ message: 'Error marking submission as synced' });
    }
});

// Delete submission
router.delete('/:submissionId', authenticate, async (req, res) => {
    try {
        const { submissionId } = req.params;

        const submission = await sequelize.models.FormSubmission.findByPk(submissionId);

        if (!submission) {
            return res.status(404).json({ message: 'Submission not found' });
        }

        await submission.destroy();

        logger.info(`Submission deleted: ${submissionId}`);

        res.json({ message: 'Submission deleted successfully' });
    } catch (error) {
        logger.error('Delete submission error:', error);
        res.status(500).json({ message: 'Error deleting submission' });
    }
});

export default router;
