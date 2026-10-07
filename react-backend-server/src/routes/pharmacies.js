/**
 * Pharmacies Routes - Manage pharmacy information
 */

import express from 'express';
import { sequelize } from '../models/index.js';
import { authenticate, authorizeAdmin } from '../middleware/auth.js';
import logger from '../config/logger.js';
import crypto from 'crypto';
import multer from 'multer';
import csv from 'csv-parser';
import { Readable } from 'stream';

const router = express.Router();
const upload = multer({ storage: multer.memoryStorage(), limits: { fileSize: 50 * 1024 * 1024 } });

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

// Bulk upload pharmacies
router.post('/bulk/upload', authenticate, authorizeAdmin, async (req, res) => {
    try {
        const payload = Array.isArray(req.body) ? req.body : req.body?.pharmacies;
        if (!Array.isArray(payload) || payload.length === 0) {
            return res.status(400).json({ message: 'Provide a non-empty pharmacies array' });
        }

        const results = [];
        let created = 0;
        let updated = 0;
        let failed = 0;

        for (const row of payload) {
            const pharmacyCode = row?.pharmacyCode || row?.pharmacy_code;
            const pharmacyName = row?.pharmacyName || row?.pharmacy_name;

            if (!pharmacyCode || !pharmacyName) {
                failed++;
                results.push({
                    pharmacyCode: pharmacyCode || null,
                    status: 'error',
                    message: 'pharmacyCode/pharmacy_code and pharmacyName/pharmacy_name are required'
                });
                continue;
            }

            try {
                const existing = await sequelize.models.Pharmacy.findOne({
                    where: { pharmacy_code: pharmacyCode }
                });

                const mapped = {
                    pharmacy_name: pharmacyName,
                    description: row?.description || null,
                    address: row?.address || null,
                    phone: row?.phone || null,
                    email: row?.email || null,
                    is_active: row?.is_active !== undefined ? Boolean(row.is_active) : true
                };

                if (existing) {
                    await existing.update(mapped);
                    updated++;
                    results.push({ pharmacyCode, status: 'updated', pharmacyId: existing.id });
                } else {
                    const createdPharmacy = await sequelize.models.Pharmacy.create({
                        pharmacy_code: pharmacyCode,
                        ...mapped,
                        api_key: crypto.randomBytes(32).toString('hex')
                    });
                    created++;
                    results.push({ pharmacyCode, status: 'created', pharmacyId: createdPharmacy.id });
                }
            } catch (error) {
                failed++;
                results.push({ pharmacyCode, status: 'error', message: error.message });
            }
        }

        logger.info(`Pharmacy bulk upload completed: created=${created}, updated=${updated}, failed=${failed}`);
        res.json({
            message: 'Pharmacy bulk upload completed',
            summary: { total: payload.length, created, updated, failed },
            results
        });
    } catch (error) {
        logger.error('Bulk upload pharmacies error:', error);
        res.status(500).json({ message: 'Error uploading pharmacies in bulk' });
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

// CSV file upload for bulk pharmacy import
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
        const pharmacyRows = [];

        stream
            .pipe(csv())
            .on('data', (row) => {
                pharmacyRows.push(row);
            })
            .on('end', async () => {
                try {
                    // Process all rows
                    for (const row of pharmacyRows) {
                        const pharmacyCode = row?.pharmacy_code || row?.pharmacyCode;
                        const pharmacyName = row?.pharmacy_name || row?.pharmacyName;

                        if (!pharmacyCode || !pharmacyName) {
                            failed++;
                            results.push({
                                pharmacyCode: pharmacyCode || null,
                                status: 'error',
                                message: 'pharmacy_code and pharmacy_name are required'
                            });
                            continue;
                        }

                        try {
                            const existing = await sequelize.models.Pharmacy.findOne({
                                where: { pharmacy_code: pharmacyCode }
                            });

                            const mapped = {
                                pharmacy_name: pharmacyName,
                                description: row?.description || null,
                                address: row?.address || null,
                                phone: row?.phone || null,
                                email: row?.email || null,
                                is_active: row?.is_active !== undefined ? Boolean(row.is_active === 'true' || row.is_active === '1' || row.is_active === true) : true
                            };

                            if (existing) {
                                await existing.update(mapped);
                                updated++;
                                results.push({ pharmacyCode, status: 'updated', pharmacyId: existing.id });
                            } else {
                                const createdPharmacy = await sequelize.models.Pharmacy.create({
                                    pharmacy_code: pharmacyCode,
                                    ...mapped,
                                    api_key: crypto.randomBytes(32).toString('hex')
                                });
                                created++;
                                results.push({ pharmacyCode, status: 'created', pharmacyId: createdPharmacy.id });
                            }
                        } catch (rowError) {
                            failed++;
                            results.push({
                                pharmacyCode,
                                status: 'error',
                                message: rowError.message
                            });
                        }
                    }

                    logger.info(`Pharmacy CSV upload completed: created=${created}, updated=${updated}, failed=${failed}`);

                    res.json({
                        message: 'Pharmacy CSV upload completed',
                        summary: {
                            created,
                            updated,
                            failed,
                            total: pharmacyRows.length
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
