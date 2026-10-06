/**
 * Facilities Routes - Manage health facility information
 */

import express from 'express';
import { sequelize } from '../models/index.js';
import { authenticate, authorizeAdmin } from '../middleware/auth.js';
import logger from '../config/logger.js';

const router = express.Router();

// Get all facilities
router.get('/', authenticate, async (req, res) => {
    try {
        const { page = 1, limit = 20, active = true } = req.query;
        const offset = (page - 1) * limit;

        const where = {};
        if (active) where.is_active = true;

        const facilities = await sequelize.models.Facility.findAndCountAll({
            where,
            limit: parseInt(limit),
            offset: parseInt(offset)
        });

        res.json({
            message: 'Facilities retrieved successfully',
            data: facilities.rows,
            total: facilities.count,
            page: parseInt(page),
            pages: Math.ceil(facilities.count / limit)
        });
    } catch (error) {
        logger.error('Get facilities error:', error);
        res.status(500).json({ message: 'Error retrieving facilities' });
    }
});

// Get facility by ID
router.get('/:facilityId', authenticate, async (req, res) => {
    try {
        const { facilityId } = req.params;

        const facility = await sequelize.models.Facility.findByPk(facilityId);

        if (!facility) {
            return res.status(404).json({ message: 'Facility not found' });
        }

        res.json({
            message: 'Facility retrieved successfully',
            data: facility
        });
    } catch (error) {
        logger.error('Get facility error:', error);
        res.status(500).json({ message: 'Error retrieving facility' });
    }
});

// Create facility
router.post('/', authenticate, authorizeAdmin, async (req, res) => {
    try {
        const { facilityCode, facilityName, address, phone, email, district, description } = req.body;

        if (!facilityCode || !facilityName) {
            return res.status(400).json({ message: 'Missing required fields' });
        }

        const facility = await sequelize.models.Facility.create({
            facility_code: facilityCode,
            facility_name: facilityName,
            description,
            address,
            phone,
            email,
            district,
            is_active: true
        });

        logger.info(`Facility created: ${facilityName}`);

        res.status(201).json({
            message: 'Facility created successfully',
            data: facility
        });
    } catch (error) {
        logger.error('Create facility error:', error);

        if (error.name === 'SequelizeUniqueConstraintError') {
            return res.status(409).json({ message: 'Facility code already exists' });
        }

        res.status(500).json({ message: 'Error creating facility' });
    }
});

// Update facility
router.put('/:facilityId', authenticate, authorizeAdmin, async (req, res) => {
    try {
        const { facilityId } = req.params;
        const updateData = req.body;

        const facility = await sequelize.models.Facility.findByPk(facilityId);

        if (!facility) {
            return res.status(404).json({ message: 'Facility not found' });
        }

        await facility.update(updateData);

        logger.info(`Facility updated: ${facilityId}`);

        res.json({
            message: 'Facility updated successfully',
            data: facility
        });
    } catch (error) {
        logger.error('Update facility error:', error);
        res.status(500).json({ message: 'Error updating facility' });
    }
});

// Assign clients to pharmacy
router.post('/:facilityId/assign-clients-to-pharmacy', authenticate, async (req, res) => {
    try {
        const { facilityId } = req.params;
        const { clientIds, pharmacyId } = req.body;

        if (!Array.isArray(clientIds) || !pharmacyId) {
            return res.status(400).json({ message: 'Missing clientIds array or pharmacyId' });
        }

        const facility = await sequelize.models.Facility.findByPk(facilityId);
        if (!facility) {
            return res.status(404).json({ message: 'Facility not found' });
        }

        // Update clients with pharmacy assignment
        const result = await sequelize.models.Client.update(
            { pharmacy_id: pharmacyId, assigned_at: new Date() },
            { where: { id: clientIds, facility_id: facilityId } }
        );

        logger.info(`Assigned ${result[0]} clients from facility ${facilityId} to pharmacy ${pharmacyId}`);

        res.json({
            message: 'Clients assigned to pharmacy successfully',
            assigned: result[0]
        });
    } catch (error) {
        logger.error('Assign clients error:', error);
        res.status(500).json({ message: 'Error assigning clients' });
    }
});

// Get facility clients
router.get('/:facilityId/clients', authenticate, async (req, res) => {
    try {
        const { facilityId } = req.params;
        const { page = 1, limit = 50 } = req.query;
        const offset = (page - 1) * limit;

        const clients = await sequelize.models.Client.findAndCountAll({
            where: { facility_id: facilityId },
            limit: parseInt(limit),
            offset: parseInt(offset),
            order: [['createdAt', 'DESC']]
        });

        res.json({
            message: 'Facility clients retrieved',
            data: clients.rows,
            total: clients.count,
            page: parseInt(page),
            pages: Math.ceil(clients.count / limit)
        });
    } catch (error) {
        logger.error('Get facility clients error:', error);
        res.status(500).json({ message: 'Error retrieving clients' });
    }
});

// Deactivate facility
router.patch('/:facilityId/deactivate', authenticate, authorizeAdmin, async (req, res) => {
    try {
        const { facilityId } = req.params;

        const facility = await sequelize.models.Facility.findByPk(facilityId);

        if (!facility) {
            return res.status(404).json({ message: 'Facility not found' });
        }

        await facility.update({ is_active: false });

        logger.info(`Facility deactivated: ${facilityId}`);

        res.json({
            message: 'Facility deactivated successfully',
            data: facility
        });
    } catch (error) {
        logger.error('Deactivate facility error:', error);
        res.status(500).json({ message: 'Error deactivating facility' });
    }
});

export default router;
