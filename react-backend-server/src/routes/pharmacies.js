/**
 * Pharmacies Routes - Manage pharmacy information
 */

import express from 'express';
import { sequelize } from '../models/index.js';
import { authenticate, authorizeAdmin } from '../middleware/auth.js';
import logger from '../config/logger.js';
import crypto from 'crypto';

const router = express.Router();

// Get all pharmacies
router.get('/', authenticate, async (req, res) => {
    try {
        const { page = 1, limit = 20, active = true } = req.query;
        const offset = (page - 1) * limit;

        const where = {};
        if (active) where.is_active = true;

        const pharmacies = await sequelize.models.Pharmacy.findAndCountAll({
            where,
            attributes: { exclude: ['api_key'] },
            limit: parseInt(limit),
            offset: parseInt(offset)
        });

        res.json({
            message: 'Pharmacies retrieved successfully',
            data: pharmacies.rows,
            total: pharmacies.count,
            page: parseInt(page),
            pages: Math.ceil(pharmacies.count / limit)
        });
    } catch (error) {
        logger.error('Get pharmacies error:', error);
        res.status(500).json({ message: 'Error retrieving pharmacies' });
    }
});

// Get pharmacy by ID
router.get('/:pharmacyId', authenticate, async (req, res) => {
    try {
        const { pharmacyId } = req.params;

        const pharmacy = await sequelize.models.Pharmacy.findByPk(pharmacyId, {
            attributes: { exclude: ['api_key'] }
        });

        if (!pharmacy) {
            return res.status(404).json({ message: 'Pharmacy not found' });
        }

        res.json({
            message: 'Pharmacy retrieved successfully',
            data: pharmacy
        });
    } catch (error) {
        logger.error('Get pharmacy error:', error);
        res.status(500).json({ message: 'Error retrieving pharmacy' });
    }
});

// Create pharmacy
router.post('/', authenticate, authorizeAdmin, async (req, res) => {
    try {
        const { pharmacyCode, pharmacyName, address, phone, email, description } = req.body;

        if (!pharmacyCode || !pharmacyName) {
            return res.status(400).json({ message: 'Missing required fields' });
        }

        // Generate API key
        const apiKey = crypto.randomBytes(32).toString('hex');

        const pharmacy = await sequelize.models.Pharmacy.create({
            pharmacy_code: pharmacyCode,
            pharmacy_name: pharmacyName,
            description,
            address,
            phone,
            email,
            api_key: apiKey,
            is_active: true
        });

        logger.info(`Pharmacy created: ${pharmacyName}`);

        res.status(201).json({
            message: 'Pharmacy created successfully',
            data: {
                ...pharmacy.toJSON(),
                api_key: apiKey  // Return API key only on creation
            }
        });
    } catch (error) {
        logger.error('Create pharmacy error:', error);

        if (error.name === 'SequelizeUniqueConstraintError') {
            return res.status(409).json({ message: 'Pharmacy code already exists' });
        }

        res.status(500).json({ message: 'Error creating pharmacy' });
    }
});

// Update pharmacy
router.put('/:pharmacyId', authenticate, authorizeAdmin, async (req, res) => {
    try {
        const { pharmacyId } = req.params;
        const updateData = req.body;

        // Don't allow API key to be updated this way
        delete updateData.api_key;

        const pharmacy = await sequelize.models.Pharmacy.findByPk(pharmacyId);

        if (!pharmacy) {
            return res.status(404).json({ message: 'Pharmacy not found' });
        }

        await pharmacy.update(updateData);

        logger.info(`Pharmacy updated: ${pharmacyId}`);

        res.json({
            message: 'Pharmacy updated successfully',
            data: pharmacy
        });
    } catch (error) {
        logger.error('Update pharmacy error:', error);
        res.status(500).json({ message: 'Error updating pharmacy' });
    }
});

// Deactivate pharmacy
router.patch('/:pharmacyId/deactivate', authenticate, authorizeAdmin, async (req, res) => {
    try {
        const { pharmacyId } = req.params;

        const pharmacy = await sequelize.models.Pharmacy.findByPk(pharmacyId);

        if (!pharmacy) {
            return res.status(404).json({ message: 'Pharmacy not found' });
        }

        await pharmacy.update({ is_active: false });

        logger.info(`Pharmacy deactivated: ${pharmacyId}`);

        res.json({
            message: 'Pharmacy deactivated successfully',
            data: pharmacy
        });
    } catch (error) {
        logger.error('Deactivate pharmacy error:', error);
        res.status(500).json({ message: 'Error deactivating pharmacy' });
    }
});

// Regenerate API key
router.post('/:pharmacyId/regenerate-api-key', authenticate, authorizeAdmin, async (req, res) => {
    try {
        const { pharmacyId } = req.params;

        const pharmacy = await sequelize.models.Pharmacy.findByPk(pharmacyId);

        if (!pharmacy) {
            return res.status(404).json({ message: 'Pharmacy not found' });
        }

        const newApiKey = crypto.randomBytes(32).toString('hex');
        await pharmacy.update({ api_key: newApiKey });

        logger.info(`API key regenerated for pharmacy: ${pharmacyId}`);

        res.json({
            message: 'API key regenerated successfully',
            api_key: newApiKey
        });
    } catch (error) {
        logger.error('Regenerate API key error:', error);
        res.status(500).json({ message: 'Error regenerating API key' });
    }
});

// Get pharmacy statistics
router.get('/:pharmacyId/stats', authenticate, async (req, res) => {
    try {
        const { pharmacyId } = req.params;

        const pharmacy = await sequelize.models.Pharmacy.findByPk(pharmacyId);

        if (!pharmacy) {
            return res.status(404).json({ message: 'Pharmacy not found' });
        }

        // Get statistics
        const clientsCount = await sequelize.models.Client.count({
            where: { pharmacy_id: pharmacyId }
        });

        const submissionsCount = await sequelize.models.FormSubmission.count({
            where: { pharmacy_id: pharmacyId }
        });

        const lastSync = await sequelize.models.SyncLog.findOne({
            where: { pharmacy_id: pharmacyId },
            order: [['createdAt', 'DESC']]
        });

        res.json({
            message: 'Pharmacy statistics retrieved',
            data: {
                pharmacyId,
                pharmacyName: pharmacy.pharmacy_name,
                clientsCount,
                submissionsCount,
                lastSync: lastSync ? lastSync.created_at : null
            }
        });
    } catch (error) {
        logger.error('Get pharmacy stats error:', error);
        res.status(500).json({ message: 'Error retrieving statistics' });
    }
});

export default router;
