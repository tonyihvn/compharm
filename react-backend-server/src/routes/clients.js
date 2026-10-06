/**
 * Clients Routes - Manage client data synced from facilities
 */

import express from 'express';
import { sequelize } from '../models/index.js';
import { authenticate, authorizeFacilityOrAdmin } from '../middleware/auth.js';
import logger from '../config/logger.js';

const router = express.Router();

// Get all clients
router.get('/', authenticate, async (req, res) => {
    try {
        const { pharmacyId, facilityId, status, page = 1, limit = 20 } = req.query;
        const offset = (page - 1) * limit;

        const where = {};
        if (pharmacyId) where.pharmacy_id = pharmacyId;
        if (facilityId) where.facility_id = facilityId;
        if (status) where.status = status;

        const clients = await sequelize.models.Client.findAndCountAll({
            where,
            limit: parseInt(limit),
            offset: parseInt(offset),
            order: [['createdAt', 'DESC']]
        });

        res.json({
            message: 'Clients retrieved successfully',
            data: clients.rows,
            total: clients.count,
            page: parseInt(page),
            pages: Math.ceil(clients.count / limit)
        });
    } catch (error) {
        logger.error('Get clients error:', error);
        res.status(500).json({ message: 'Error retrieving clients' });
    }
});

// Get client by ID
router.get('/:clientId', authenticate, async (req, res) => {
    try {
        const { clientId } = req.params;

        const client = await sequelize.models.Client.findByPk(clientId);

        if (!client) {
            return res.status(404).json({ message: 'Client not found' });
        }

        res.json({
            message: 'Client retrieved successfully',
            data: client
        });
    } catch (error) {
        logger.error('Get client error:', error);
        res.status(500).json({ message: 'Error retrieving client' });
    }
});

// Get clients by PEPFARID
router.get('/search/pepfarid/:pepfarId', authenticate, async (req, res) => {
    try {
        const { pepfarId } = req.params;

        const client = await sequelize.models.Client.findOne({
            where: { pepfarid: pepfarId }
        });

        if (!client) {
            return res.status(404).json({ message: 'Client not found' });
        }

        res.json({
            message: 'Client retrieved successfully',
            data: client
        });
    } catch (error) {
        logger.error('Search client error:', error);
        res.status(500).json({ message: 'Error searching client' });
    }
});

// Create/Upload client
router.post('/', authenticate, async (req, res) => {
    try {
        const clientData = req.body;
        const { facilityId } = req.user;

        // Client data should come from facility
        clientData.facility_id = facilityId;

        // Check if client already exists by PEPFARID
        let client = await sequelize.models.Client.findOne({
            where: { pepfarid: clientData.pepfarId }
        });

        if (client) {
            // Update existing client
            await client.update(clientData);
            logger.info(`Client updated: ${clientData.pepfarId}`);
        } else {
            // Create new client
            client = await sequelize.models.Client.create(clientData);
            logger.info(`Client created: ${clientData.pepfarId}`);
        }

        res.status(201).json({
            message: 'Client created/updated successfully',
            data: client
        });
    } catch (error) {
        logger.error('Create client error:', error);
        res.status(500).json({ message: 'Error creating client' });
    }
});

// Bulk upload clients
router.post('/bulk/upload', authenticate, async (req, res) => {
    try {
        const { clients } = req.body;
        const { facilityId } = req.user;

        if (!Array.isArray(clients)) {
            return res.status(400).json({ message: 'Clients must be an array' });
        }

        const results = [];

        for (const clientData of clients) {
            try {
                clientData.facility_id = facilityId;

                let client = await sequelize.models.Client.findOne({
                    where: { pepfarid: clientData.pepfarId }
                });

                if (client) {
                    await client.update(clientData);
                } else {
                    client = await sequelize.models.Client.create(clientData);
                }

                results.push({
                    pepfarId: clientData.pepfarId,
                    status: 'success',
                    clientId: client.id
                });
            } catch (error) {
                results.push({
                    pepfarId: clientData.pepfarId,
                    status: 'error',
                    message: error.message
                });
            }
        }

        logger.info(`Bulk upload completed: ${results.filter(r => r.status === 'success').length} success`);

        res.json({
            message: 'Bulk upload completed',
            results
        });
    } catch (error) {
        logger.error('Bulk upload error:', error);
        res.status(500).json({ message: 'Error in bulk upload' });
    }
});

// Assign client to pharmacy
router.post('/:clientId/assign-pharmacy', authenticate, authorizeFacilityOrAdmin, async (req, res) => {
    try {
        const { clientId } = req.params;
        const { pharmacyId } = req.body;

        const client = await sequelize.models.Client.findByPk(clientId);

        if (!client) {
            return res.status(404).json({ message: 'Client not found' });
        }

        await client.update({
            pharmacy_id: pharmacyId,
            assigned_at: new Date()
        });

        logger.info(`Client assigned to pharmacy: ${clientId} -> ${pharmacyId}`);

        res.json({
            message: 'Client assigned to pharmacy successfully',
            data: client
        });
    } catch (error) {
        logger.error('Assign pharmacy error:', error);
        res.status(500).json({ message: 'Error assigning pharmacy' });
    }
});

// Update client
router.put('/:clientId', authenticate, async (req, res) => {
    try {
        const { clientId } = req.params;
        const clientData = req.body;

        const client = await sequelize.models.Client.findByPk(clientId);

        if (!client) {
            return res.status(404).json({ message: 'Client not found' });
        }

        await client.update(clientData);

        logger.info(`Client updated: ${clientId}`);

        res.json({
            message: 'Client updated successfully',
            data: client
        });
    } catch (error) {
        logger.error('Update client error:', error);
        res.status(500).json({ message: 'Error updating client' });
    }
});

// Delete client
router.delete('/:clientId', authenticate, authorizeFacilityOrAdmin, async (req, res) => {
    try {
        const { clientId } = req.params;

        const client = await sequelize.models.Client.findByPk(clientId);

        if (!client) {
            return res.status(404).json({ message: 'Client not found' });
        }

        await client.destroy();

        logger.info(`Client deleted: ${clientId}`);

        res.json({ message: 'Client deleted successfully' });
    } catch (error) {
        logger.error('Delete client error:', error);
        res.status(500).json({ message: 'Error deleting client' });
    }
});

// Get clients for pharmacy
router.get('/pharmacy/:pharmacyId/clients', authenticate, async (req, res) => {
    try {
        const { pharmacyId } = req.params;
        const { page = 1, limit = 50 } = req.query;
        const offset = (page - 1) * limit;

        const clients = await sequelize.models.Client.findAndCountAll({
            where: { pharmacy_id: pharmacyId },
            limit: parseInt(limit),
            offset: parseInt(offset),
            order: [['updatedAt', 'DESC']]
        });

        res.json({
            message: 'Pharmacy clients retrieved',
            data: clients.rows,
            total: clients.count,
            page: parseInt(page),
            pages: Math.ceil(clients.count / limit)
        });
    } catch (error) {
        logger.error('Get pharmacy clients error:', error);
        res.status(500).json({ message: 'Error retrieving clients' });
    }
});

export default router;
