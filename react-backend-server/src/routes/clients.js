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
        const { pharmacyId, pharmacyCode, facilityId, status, page = 1, limit = 20 } = req.query;
        const offset = (page - 1) * limit;

        const where = { is_active: true };
        
        // If pharmacyId or pharmacyCode provided, filter by pharmacy
        if (pharmacyId) {
            where.pharmacy_id = pharmacyId;
        } else if (pharmacyCode) {
            // Find pharmacy by code first
            const pharmacy = await sequelize.models.Pharmacy.findOne({ 
                where: { pharmacy_code: pharmacyCode } 
            });
            if (pharmacy) {
                where.pharmacy_id = pharmacy.id;
            } else {
                return res.json({
                    message: 'No pharmacy found with the provided code',
                    clients: [],
                    total: 0,
                    page: 1,
                    pages: 0
                });
            }
        }
        
        if (facilityId) where.facility_id = facilityId;
        if (status) where.status = status;

        const result = await sequelize.models.Client.findAndCountAll({
            where,
            limit: parseInt(limit),
            offset: parseInt(offset),
            order: [['createdAt', 'DESC']],
            include: [
                {
                    model: sequelize.models.Pharmacy,
                    attributes: ['pharmacy_code', 'pharmacy_name'],
                    required: false
                },
                {
                    model: sequelize.models.Facility,
                    attributes: ['facility_code', 'facility_name'],
                    required: false
                }
            ]
        });

        // Map to frontend format with all required fields
        const clients = result.rows.map(client => ({
            id: client.id,
            name: client.full_name,
            age: client.date_of_birth ? Math.floor((new Date() - client.date_of_birth) / (365.25 * 24 * 60 * 60 * 1000)) : null,
            gender: client.gender,
            phone: client.phone_number,
            email: client.email,
            address: client.address,
            pepfarId: client.pepfar_id,
            pharmacyId: client.pharmacy_id,
            pharmacyCode: client.Pharmacy?.pharmacy_code,
            facilityId: client.facility_id,
            facilityCode: client.Facility?.facility_code
        }));

        res.json({
            message: 'Clients retrieved successfully',
            clients: clients,
            total: result.count,
            page: parseInt(page),
            pages: Math.ceil(result.count / limit)
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

        const client = await sequelize.models.Client.findByPk(clientId, {
            include: [
                {
                    model: sequelize.models.Pharmacy,
                    attributes: ['pharmacy_code', 'pharmacy_name'],
                    required: false
                },
                {
                    model: sequelize.models.Facility,
                    attributes: ['facility_code', 'facility_name'],
                    required: false
                }
            ]
        });

        if (!client) {
            return res.status(404).json({ message: 'Client not found' });
        }

        // Format response to match frontend expectations
        const formattedClient = {
            id: client.id,
            name: client.full_name,
            age: client.date_of_birth ? Math.floor((new Date() - client.date_of_birth) / (365.25 * 24 * 60 * 60 * 1000)) : null,
            gender: client.gender,
            phone: client.phone_number,
            email: client.email,
            address: client.address,
            pepfarId: client.pepfar_id,
            pharmacyId: client.pharmacy_id,
            pharmacyCode: client.Pharmacy?.pharmacy_code,
            facilityId: client.facility_id,
            facilityCode: client.Facility?.facility_code
        };

        res.json({
            message: 'Client retrieved successfully',
            client: formattedClient
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
        const { name, pepfar_id, facility_id, pharmacy_id, age, gender, phone, email, address } = req.body;

        if (!name || !pepfar_id || !facility_id || !pharmacy_id) {
            return res.status(400).json({ message: 'Client name, PEPFAR ID, Facility ID, and Pharmacy ID are required' });
        }

        // Get or create the pharmacy record
        let pharmacyRecord = await sequelize.models.Pharmacy.findOne({ 
            where: { pharmacy_code: pharmacy_id } 
        });
        
        if (!pharmacyRecord) {
            pharmacyRecord = await sequelize.models.Pharmacy.create({
                pharmacy_code: pharmacy_id,
                pharmacy_name: `Pharmacy ${pharmacy_id}`,
                api_key: `api_key_${Date.now()}`,
                is_active: true
            });
        }

        // Get or create the facility record
        let facility = await sequelize.models.Facility.findOne({ 
            where: { facility_code: facility_id } 
        });
        
        if (!facility) {
            facility = await sequelize.models.Facility.create({
                facility_code: facility_id,
                facility_name: `Facility ${facility_id}`,
                is_active: true
            });
        }

        // Create client with all required fields
        const clientData = {
            pepfar_id: pepfar_id,
            full_name: name,
            gender: gender || null,
            phone_number: phone || null,
            email: email || null,
            address: address || null,
            facility_id: facility.id,
            pharmacy_id: pharmacyRecord.id
        };

        // Convert age to date_of_birth if provided
        if (age) {
            const dob = new Date();
            dob.setFullYear(dob.getFullYear() - parseInt(age));
            clientData.date_of_birth = dob;
        }

        const client = await sequelize.models.Client.create(clientData);
        logger.info(`Client created: ${pepfar_id}`);

        res.status(201).json({
            message: 'Client created successfully',
            clients: [client]
        });
    } catch (error) {
        logger.error('Create client error:', error);
        res.status(500).json({ message: 'Error creating client: ' + error.message });
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
        const { name, pepfar_id, facility_id, pharmacy_id, age, gender, phone, email, address } = req.body;

        const client = await sequelize.models.Client.findByPk(clientId, {
            include: [
                { model: sequelize.models.Pharmacy, attributes: ['pharmacy_code'] },
                { model: sequelize.models.Facility, attributes: ['facility_code'] }
            ]
        });

        if (!client) {
            return res.status(404).json({ message: 'Client not found' });
        }

        // Authorization check: only admin, facility managers of the facility, and pharmacy staff of the pharmacy can edit
        if (req.user.role !== 'admin') {
            if (req.user.role === 'facility_manager' && client.Facility?.facility_code !== req.user.facilityId) {
                return res.status(403).json({ message: 'You can only edit clients in your facility' });
            }
            if (req.user.role === 'pharmacy_staff' && client.Pharmacy?.pharmacy_code !== req.user.pharmacyId) {
                return res.status(403).json({ message: 'You can only edit clients in your pharmacy' });
            }
        }

        const updateData = {};

        if (name) updateData.full_name = name;
        if (pepfar_id) updateData.pepfar_id = pepfar_id;
        if (gender) updateData.gender = gender;
        if (phone) updateData.phone_number = phone;
        if (email) updateData.email = email;
        if (address) updateData.address = address;

        // Handle facility_id and pharmacy_id
        if (facility_id) {
            const facility = await sequelize.models.Facility.findOne({ 
                where: { facility_code: facility_id } 
            });
            if (facility) {
                updateData.facility_id = facility.id;
            } else {
                const newFacility = await sequelize.models.Facility.create({
                    facility_code: facility_id,
                    facility_name: `Facility ${facility_id}`,
                    is_active: true
                });
                updateData.facility_id = newFacility.id;
            }
        }

        if (pharmacy_id) {
            const pharmacy = await sequelize.models.Pharmacy.findOne({ 
                where: { pharmacy_code: pharmacy_id } 
            });
            if (pharmacy) {
                updateData.pharmacy_id = pharmacy.id;
            } else {
                const newPharmacy = await sequelize.models.Pharmacy.create({
                    pharmacy_code: pharmacy_id,
                    pharmacy_name: `Pharmacy ${pharmacy_id}`,
                    api_key: `api_key_${Date.now()}`,
                    is_active: true
                });
                updateData.pharmacy_id = newPharmacy.id;
            }
        }

        if (age) {
            const dob = new Date();
            dob.setFullYear(dob.getFullYear() - parseInt(age));
            updateData.date_of_birth = dob;
        }

        await client.update(updateData);

        logger.info(`Client updated: ${clientId}`);

        // Return formatted response
        const updatedClient = await sequelize.models.Client.findByPk(clientId, {
            include: [
                { model: sequelize.models.Pharmacy, attributes: ['pharmacy_code', 'pharmacy_name'] },
                { model: sequelize.models.Facility, attributes: ['facility_code', 'facility_name'] }
            ]
        });

        res.json({
            message: 'Client updated successfully',
            client: {
                id: updatedClient.id,
                name: updatedClient.full_name,
                age: updatedClient.date_of_birth ? Math.floor((new Date() - updatedClient.date_of_birth) / (365.25 * 24 * 60 * 60 * 1000)) : null,
                gender: updatedClient.gender,
                phone: updatedClient.phone_number,
                email: updatedClient.email,
                address: updatedClient.address,
                pepfarId: updatedClient.pepfar_id,
                pharmacyId: updatedClient.pharmacy_id,
                pharmacyCode: updatedClient.Pharmacy?.pharmacy_code,
                facilityId: updatedClient.facility_id,
                facilityCode: updatedClient.Facility?.facility_code
            }
        });
    } catch (error) {
        logger.error('Update client error:', error);
        res.status(500).json({ message: 'Error updating client: ' + error.message });
    }
});

// Delete client
router.delete('/:clientId', authenticate, async (req, res) => {
    try {
        const { clientId } = req.params;

        const client = await sequelize.models.Client.findByPk(clientId, {
            include: [
                { model: sequelize.models.Pharmacy, attributes: ['pharmacy_code'] },
                { model: sequelize.models.Facility, attributes: ['facility_code'] }
            ]
        });

        if (!client) {
            return res.status(404).json({ message: 'Client not found' });
        }

        // Authorization check: only admin, facility managers of the facility, and pharmacy staff of the pharmacy can delete
        if (req.user.role !== 'admin') {
            if (req.user.role === 'facility_manager' && client.Facility?.facility_code !== req.user.facilityId) {
                return res.status(403).json({ message: 'You can only delete clients in your facility' });
            }
            if (req.user.role === 'pharmacy_staff' && client.Pharmacy?.pharmacy_code !== req.user.pharmacyId) {
                return res.status(403).json({ message: 'You can only delete clients in your pharmacy' });
            }
            if (!['admin', 'facility_manager', 'pharmacy_staff'].includes(req.user.role)) {
                return res.status(403).json({ message: 'You do not have permission to delete clients' });
            }
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
