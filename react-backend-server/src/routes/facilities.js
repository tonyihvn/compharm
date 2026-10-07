/**
 * Facilities Routes - Manage health facility information
 */

import express from 'express';
import { sequelize } from '../models/index.js';
import { authenticate, authorizeAdmin } from '../middleware/auth.js';
import logger from '../config/logger.js';
import multer from 'multer';
import csv from 'csv-parser';
import { Readable } from 'stream';

const router = express.Router();
const upload = multer({ storage: multer.memoryStorage(), limits: { fileSize: 50 * 1024 * 1024 } });

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
        const { facilityCode, facilityName, address, phone, email, district, description, systemType, system_type } = req.body;

        if (!facilityCode || !facilityName) {
            return res.status(400).json({ message: 'Missing required fields' });
        }

        const facility = await sequelize.models.Facility.create({
            facility_code: facilityCode,
            facility_name: facilityName,
            description,
            system_type: systemType || system_type || 'openmrs',
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

// Bulk upload facilities
router.post('/bulk/upload', authenticate, authorizeAdmin, async (req, res) => {
    try {
        const payload = Array.isArray(req.body) ? req.body : req.body?.facilities;
        if (!Array.isArray(payload) || payload.length === 0) {
            return res.status(400).json({ message: 'Provide a non-empty facilities array' });
        }

        const results = [];
        let created = 0;
        let updated = 0;
        let failed = 0;

        for (const row of payload) {
            const facilityCode = row?.facilityCode || row?.facility_code;
            const facilityName = row?.facilityName || row?.facility_name;

            if (!facilityCode || !facilityName) {
                failed++;
                results.push({
                    facilityCode: facilityCode || null,
                    status: 'error',
                    message: 'facilityCode/facility_code and facilityName/facility_name are required'
                });
                continue;
            }

            try {
                const existing = await sequelize.models.Facility.findOne({
                    where: { facility_code: facilityCode }
                });

                const mapped = {
                    facility_name: facilityName,
                    description: row?.description || null,
                    system_type: row?.systemType || row?.system_type || 'openmrs',
                    address: row?.address || null,
                    phone: row?.phone || null,
                    email: row?.email || null,
                    district: row?.district || null,
                    is_active: row?.is_active !== undefined ? Boolean(row.is_active) : true
                };

                if (existing) {
                    await existing.update(mapped);
                    updated++;
                    results.push({ facilityCode, status: 'updated', facilityId: existing.id });
                } else {
                    const createdFacility = await sequelize.models.Facility.create({
                        facility_code: facilityCode,
                        ...mapped
                    });
                    created++;
                    results.push({ facilityCode, status: 'created', facilityId: createdFacility.id });
                }
            } catch (error) {
                failed++;
                results.push({ facilityCode, status: 'error', message: error.message });
            }
        }

        logger.info(`Facility bulk upload completed: created=${created}, updated=${updated}, failed=${failed}`);
        res.json({
            message: 'Facility bulk upload completed',
            summary: { total: payload.length, created, updated, failed },
            results
        });
    } catch (error) {
        logger.error('Bulk upload facilities error:', error);
        res.status(500).json({ message: 'Error uploading facilities in bulk' });
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

// CSV file upload for bulk facility import
router.post('/csv/upload', authenticate, authorizeAdmin, upload.single('file'), async (req, res) => {
    try {
        if (!req.file) {
            return res.status(400).json({ message: 'No file provided' });
        }

        const fileBuffer = req.file.buffer;
        const results = [];
        let created = 0;
        let updated = 0;
        let failed = 0;

        // Parse CSV from buffer
        const stream = Readable.from([fileBuffer]);
        const facilityRows = [];

        stream
            .pipe(csv())
            .on('data', (row) => {
                facilityRows.push(row);
            })
            .on('end', async () => {
                try {
                    // Process all rows
                    for (const row of facilityRows) {
                        const facilityCode = row?.facility_code || row?.facilityCode;
                        const facilityName = row?.facility_name || row?.facilityName;

                        if (!facilityCode || !facilityName) {
                            failed++;
                            results.push({
                                facilityCode: facilityCode || null,
                                status: 'error',
                                message: 'facility_code and facility_name are required'
                            });
                            continue;
                        }

                        try {
                            const existing = await sequelize.models.Facility.findOne({
                                where: { facility_code: facilityCode }
                            });

                            const mapped = {
                                facility_name: facilityName,
                                description: row?.description || null,
                                address: row?.address || null,
                                phone: row?.phone || null,
                                email: row?.email || null,
                                facility_type: row?.facility_type || 'clinic',
                                is_active: row?.is_active !== undefined ? Boolean(row.is_active === 'true' || row.is_active === '1' || row.is_active === true) : true
                            };

                            if (existing) {
                                await existing.update(mapped);
                                updated++;
                                results.push({ facilityCode, status: 'updated', facilityId: existing.id });
                            } else {
                                const createdFacility = await sequelize.models.Facility.create({
                                    facility_code: facilityCode,
                                    ...mapped
                                });
                                created++;
                                results.push({ facilityCode, status: 'created', facilityId: createdFacility.id });
                            }
                        } catch (rowError) {
                            failed++;
                            results.push({
                                facilityCode,
                                status: 'error',
                                message: rowError.message
                            });
                        }
                    }

                    logger.info(`Facility CSV upload completed: created=${created}, updated=${updated}, failed=${failed}`);

                    res.json({
                        message: 'Facility CSV upload completed',
                        summary: {
                            created,
                            updated,
                            failed,
                            total: facilityRows.length
                        },
                        results
                    });
                } catch (error) {
                    logger.error('CSV processing error:', error);
                    res.status(500).json({ message: 'Error processing CSV file' });
                }
            })
            .on('error', (error) => {
                logger.error('CSV parse error:', error);
                res.status(400).json({ message: 'Invalid CSV format' });
            });
    } catch (error) {
        logger.error('CSV upload error:', error);
        res.status(500).json({ message: 'Error uploading CSV file' });
    }
});

export default router;
