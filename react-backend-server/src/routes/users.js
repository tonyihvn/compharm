/**
 * Users Routes - Manage system users
 */

import express from 'express';
import { sequelize } from '../models/index.js';
import { authenticate, authorizeAdmin } from '../middleware/auth.js';
import logger from '../config/logger.js';
import bcryptjs from 'bcryptjs';

const router = express.Router();

// Get all users (admin only)
router.get('/', authenticate, authorizeAdmin, async (req, res) => {
    try {
        const users = await sequelize.models.User.findAll({
            attributes: { exclude: ['password_hash'] },
            order: [['createdAt', 'DESC']]
        });

        res.json({
            message: 'Users retrieved successfully',
            users: users.map(u => ({
                id: u.id,
                username: u.username,
                email: u.email,
                full_name: u.full_name,
                role: u.role,
                pharmacy_id: u.pharmacy_id,
                facility_id: u.facility_id,
                is_active: u.is_active,
                last_login: u.last_login,
                createdAt: u.createdAt,
                updatedAt: u.updatedAt
            })),
            total: users.length
        });
    } catch (error) {
        logger.error('Failed to fetch users:', error);
        res.status(500).json({ error: 'Internal server error' });
    }
});

// Get single user
router.get('/:userId', authenticate, async (req, res) => {
    try {
        const user = await sequelize.models.User.findByPk(req.params.userId, {
            attributes: { exclude: ['password_hash'] }
        });

        if (!user) {
            return res.status(404).json({ error: 'User not found' });
        }

        // Authorization: can only view own profile or admin can view any
        if (req.user.id !== user.id && req.user.role !== 'admin') {
            return res.status(403).json({ error: 'Unauthorized' });
        }

        res.json({
            message: 'User retrieved successfully',
            user: {
                id: user.id,
                username: user.username,
                email: user.email,
                full_name: user.full_name,
                role: user.role,
                pharmacy_id: user.pharmacy_id,
                facility_id: user.facility_id,
                is_active: user.is_active,
                last_login: user.last_login,
                createdAt: user.createdAt,
                updatedAt: user.updatedAt
            }
        });
    } catch (error) {
        logger.error('Failed to fetch user:', error);
        res.status(500).json({ error: 'Internal server error' });
    }
});

// Create new user (admin only)
router.post('/', authenticate, authorizeAdmin, async (req, res) => {
    try {
        const { email, username, password, fullName, role, pharmacyId, facilityId } = req.body;

        // Validate required fields
        if (!email || !password || !fullName) {
            return res.status(400).json({ error: 'Missing required fields' });
        }

        // Check if user already exists
        const existingUser = await sequelize.models.User.findOne({
            where: { email }
        });

        if (existingUser) {
            return res.status(409).json({ error: 'User with this email already exists' });
        }

        // Hash password
        const saltRounds = 10;
        const hashedPassword = await bcryptjs.hash(password, saltRounds);

        // Create user
        const user = await sequelize.models.User.create({
            username: username || email.split('@')[0],
            email,
            password_hash: hashedPassword,
            full_name: fullName,
            role: role || 'pharmacy_staff',
            pharmacy_id: pharmacyId || null,
            facility_id: facilityId || null,
            is_active: true
        });

        res.status(201).json({
            message: 'User created successfully',
            user: {
                id: user.id,
                username: user.username,
                email: user.email,
                full_name: user.full_name,
                role: user.role,
                pharmacy_id: user.pharmacy_id,
                facility_id: user.facility_id,
                is_active: user.is_active
            }
        });
    } catch (error) {
        logger.error('Failed to create user:', error);
        res.status(500).json({ error: 'Internal server error' });
    }
});

// Update user (admin only, or user updating themselves)
router.put('/:userId', authenticate, async (req, res) => {
    try {
        const user = await sequelize.models.User.findByPk(req.params.userId);

        if (!user) {
            return res.status(404).json({ error: 'User not found' });
        }

        // Authorization
        if (req.user.id !== user.id && req.user.role !== 'admin') {
            return res.status(403).json({ error: 'Unauthorized' });
        }

        // Update allowed fields
        const updates = {};
        if (req.body.full_name) updates.full_name = req.body.full_name;
        if (req.body.email && req.user.role === 'admin') updates.email = req.body.email;
        if (req.body.role && req.user.role === 'admin') updates.role = req.body.role;
        if (req.body.pharmacy_id && req.user.role === 'admin') updates.pharmacy_id = req.body.pharmacy_id;
        if (req.body.facility_id && req.user.role === 'admin') updates.facility_id = req.body.facility_id;
        if (req.body.is_active !== undefined && req.user.role === 'admin') updates.is_active = req.body.is_active;

        await user.update(updates);

        res.json({
            message: 'User updated successfully',
            user: {
                id: user.id,
                username: user.username,
                email: user.email,
                full_name: user.full_name,
                role: user.role,
                pharmacy_id: user.pharmacy_id,
                facility_id: user.facility_id,
                is_active: user.is_active
            }
        });
    } catch (error) {
        logger.error('Failed to update user:', error);
        res.status(500).json({ error: 'Internal server error' });
    }
});

// Delete user (admin only)
router.delete('/:userId', authenticate, authorizeAdmin, async (req, res) => {
    try {
        const user = await sequelize.models.User.findByPk(req.params.userId);

        if (!user) {
            return res.status(404).json({ error: 'User not found' });
        }

        // Prevent deleting yourself
        if (req.user.id === user.id) {
            return res.status(400).json({ error: 'Cannot delete your own account' });
        }

        await user.destroy();

        res.json({
            message: 'User deleted successfully'
        });
    } catch (error) {
        logger.error('Failed to delete user:', error);
        res.status(500).json({ error: 'Internal server error' });
    }
});

export default router;
