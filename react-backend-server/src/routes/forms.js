/**
 * Forms Routes - Manage JSON form definitions
 */

import express from 'express';
import { sequelize } from '../models/index.js';
import { authenticate, authorizeAdmin } from '../middleware/auth.js';
import logger from '../config/logger.js';
import { randomUUID } from 'crypto';

const router = express.Router();

function getFormName(formData) {
    return formData?.name || formData?.label || null;
}

function getFormSections(formData) {
    if (Array.isArray(formData?.sections)) {
        return formData.sections;
    }

    if (Array.isArray(formData?.pages)) {
        return formData.pages.flatMap((page) => Array.isArray(page?.sections) ? page.sections : []);
    }

    return [];
}

// Get all forms
router.get('/', authenticate, async (req, res) => {
    try {
        const { page = 1, limit = 20, active = true } = req.query;
        const offset = (page - 1) * limit;

        const where = {};
        if (active) where.is_active = true;

        const forms = await sequelize.models.PharmacyForm.findAndCountAll({
            where,
            limit: parseInt(limit),
            offset: parseInt(offset),
            order: [['createdAt', 'DESC']]
        });

        res.json({
            message: 'Forms retrieved successfully',
            data: forms.rows,
            total: forms.count,
            page: parseInt(page),
            pages: Math.ceil(forms.count / limit)
        });
    } catch (error) {
        logger.error('Get forms error:', error);
        res.status(500).json({ message: 'Error retrieving forms' });
    }
});

// Get form by ID
router.get('/:formId', authenticate, async (req, res) => {
    try {
        const { formId } = req.params;

        const form = await sequelize.models.PharmacyForm.findByPk(formId);

        if (!form) {
            return res.status(404).json({ message: 'Form not found' });
        }

        res.json({
            message: 'Form retrieved successfully',
            data: form
        });
    } catch (error) {
        logger.error('Get form error:', error);
        res.status(500).json({ message: 'Error retrieving form' });
    }
});

// Upload/Create new form
router.post('/upload', authenticate, authorizeAdmin, async (req, res) => {
    try {
        const formData = req.body;
        const { userId } = req.user;
        const formName = getFormName(formData);
        const sections = getFormSections(formData);

        // Validate form structure
        if (!formName || sections.length === 0) {
            return res.status(400).json({ message: 'Form must have a name and at least one section (directly or under pages)' });
        }

        // Create form
        const form = await sequelize.models.PharmacyForm.create({
            form_uuid: formData.uuid || formData.id || randomUUID(),
            form_name: formName,
            description: formData.description,
            form_data: formData,
            version: 1,
            created_by: userId,
            is_active: true
        });

        logger.info(`Form created: ${form.form_name}`);

        res.status(201).json({
            message: 'Form created successfully',
            data: form
        });
    } catch (error) {
        logger.error('Create form error:', error);
        res.status(500).json({ message: 'Error creating form' });
    }
});

// Update form
router.put('/:formId', authenticate, authorizeAdmin, async (req, res) => {
    try {
        const { formId } = req.params;
        const formData = req.body;

        const form = await sequelize.models.PharmacyForm.findByPk(formId);

        if (!form) {
            return res.status(404).json({ message: 'Form not found' });
        }

        // Increment version
        const newVersion = (form.version || 1) + 1;

        await form.update({
            form_name: getFormName(formData) || form.form_name,
            description: formData.description || form.description,
            form_data: formData,
            version: newVersion
        });

        logger.info(`Form updated: ${formId} - Version ${newVersion}`);

        res.json({
            message: 'Form updated successfully',
            data: form
        });
    } catch (error) {
        logger.error('Update form error:', error);
        res.status(500).json({ message: 'Error updating form' });
    }
});

// Deactivate form
router.patch('/:formId/deactivate', authenticate, authorizeAdmin, async (req, res) => {
    try {
        const { formId } = req.params;

        const form = await sequelize.models.PharmacyForm.findByPk(formId);

        if (!form) {
            return res.status(404).json({ message: 'Form not found' });
        }

        await form.update({ is_active: false });

        logger.info(`Form deactivated: ${formId}`);

        res.json({
            message: 'Form deactivated successfully',
            data: form
        });
    } catch (error) {
        logger.error('Deactivate form error:', error);
        res.status(500).json({ message: 'Error deactivating form' });
    }
});

// Delete form
router.delete('/:formId', authenticate, authorizeAdmin, async (req, res) => {
    try {
        const { formId } = req.params;

        const form = await sequelize.models.PharmacyForm.findByPk(formId);

        if (!form) {
            return res.status(404).json({ message: 'Form not found' });
        }

        await form.destroy();

        logger.info(`Form deleted: ${formId}`);

        res.json({ message: 'Form deleted successfully' });
    } catch (error) {
        logger.error('Delete form error:', error);
        res.status(500).json({ message: 'Error deleting form' });
    }
});

// Get form submissions
router.get('/:formId/submissions', authenticate, async (req, res) => {
    try {
        const { formId } = req.params;
        const { page = 1, limit = 20, status } = req.query;
        const offset = (page - 1) * limit;

        const where = { form_id: formId };
        if (status) where.status = status;

        const submissions = await sequelize.models.FormSubmission.findAndCountAll({
            where,
            limit: parseInt(limit),
            offset: parseInt(offset),
            order: [['createdAt', 'DESC']]
        });

        res.json({
            message: 'Submissions retrieved successfully',
            data: submissions.rows,
            total: submissions.count,
            page: parseInt(page),
            pages: Math.ceil(submissions.count / limit)
        });
    } catch (error) {
        logger.error('Get submissions error:', error);
        res.status(500).json({ message: 'Error retrieving submissions' });
    }
});

export default router;
