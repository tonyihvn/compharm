/**
 * Client Field Configuration Routes
 * Allows admins to customize the client form fields
 */

import express from 'express';
import { sequelize } from '../models/index.js';
import { authenticate, authorizeAdmin } from '../middleware/auth.js';
import logger from '../config/logger.js';

const router = express.Router();

// Get all field definitions
router.get('/', authenticate, async (req, res) => {
    try {
        const fields = await sequelize.models.ClientField.findAll({
            order: [['order_index', 'ASC']]
        });

        res.json({
            message: 'Fields retrieved successfully',
            fields: fields
        });
    } catch (error) {
        logger.error('Get fields error:', error);
        res.status(500).json({ message: 'Error retrieving fields' });
    }
});

// Create new field
router.post('/', authenticate, authorizeAdmin, async (req, res) => {
    try {
        const { name, field_name, field_type, required, order_index } = req.body;

        if (!name || !field_name || !field_type) {
            return res.status(400).json({ message: 'Missing required fields' });
        }

        const field = await sequelize.models.ClientField.create({
            name,
            field_name,
            field_type,
            required: required || false,
            order_index: order_index || 999
        });

        logger.info(`Field created: ${name}`);

        res.status(201).json({
            message: 'Field created successfully',
            field: field
        });
    } catch (error) {
        logger.error('Create field error:', error);
        res.status(500).json({ message: 'Error creating field' });
    }
});

// Update field
router.put('/:fieldId', authenticate, authorizeAdmin, async (req, res) => {
    try {
        const { fieldId } = req.params;
        const { name, field_type, required, order_index } = req.body;

        const field = await sequelize.models.ClientField.findByPk(fieldId);

        if (!field) {
            return res.status(404).json({ message: 'Field not found' });
        }

        if (name) field.name = name;
        if (field_type) field.field_type = field_type;
        if (required !== undefined) field.required = required;
        if (order_index !== undefined) field.order_index = order_index;

        await field.save();

        logger.info(`Field updated: ${fieldId}`);

        res.json({
            message: 'Field updated successfully',
            field: field
        });
    } catch (error) {
        logger.error('Update field error:', error);
        res.status(500).json({ message: 'Error updating field' });
    }
});

// Delete field
router.delete('/:fieldId', authenticate, authorizeAdmin, async (req, res) => {
    try {
        const { fieldId } = req.params;

        const field = await sequelize.models.ClientField.findByPk(fieldId);

        if (!field) {
            return res.status(404).json({ message: 'Field not found' });
        }

        await field.destroy();

        logger.info(`Field deleted: ${fieldId}`);

        res.json({ message: 'Field deleted successfully' });
    } catch (error) {
        logger.error('Delete field error:', error);
        res.status(500).json({ message: 'Error deleting field' });
    }
});

// Reset to default fields
router.post('/reset/defaults', authenticate, authorizeAdmin, async (req, res) => {
    try {
        // Delete all current fields
        await sequelize.models.ClientField.destroy({ where: {} });

        // Create default fields
        const defaultFields = [
            { name: 'Full Name', field_name: 'full_name', field_type: 'text', required: true, order_index: 1 },
            { name: 'PEPFAR ID', field_name: 'pepfar_id', field_type: 'text', required: true, order_index: 2 },
            { name: 'Date of Birth', field_name: 'date_of_birth', field_type: 'date', required: false, order_index: 3 },
            { name: 'Gender', field_name: 'gender', field_type: 'select', required: false, order_index: 4 },
            { name: 'Phone Number', field_name: 'phone_number', field_type: 'tel', required: false, order_index: 5 },
            { name: 'Email', field_name: 'email', field_type: 'email', required: false, order_index: 6 },
            { name: 'Address', field_name: 'address', field_type: 'text', required: false, order_index: 7 }
        ];

        await sequelize.models.ClientField.bulkCreate(defaultFields);

        logger.info('Fields reset to defaults');

        res.json({
            message: 'Fields reset to defaults',
            fields: defaultFields
        });
    } catch (error) {
        logger.error('Reset fields error:', error);
        res.status(500).json({ message: 'Error resetting fields' });
    }
});

export default router;
