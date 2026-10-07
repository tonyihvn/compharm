/**
 * Authentication Routes
 */

import express from 'express';
import jwt from 'jsonwebtoken';
import bcrypt from 'bcryptjs';
import { sequelize } from '../models/index.js';
import logger from '../config/logger.js';
import { normalizeRole } from '../middleware/auth.js';

const router = express.Router();

// Signup endpoint
router.post('/signup', async (req, res) => {
    try {
        const { username, email, password, full_name, role, facility_id, pharmacy_id } = req.body;

        // Validate input
        if (!username || !email || !password) {
            return res.status(400).json({ message: 'Missing required fields' });
        }

        // Hash password
        const hashedPassword = await bcrypt.hash(password, 10);

        // Create user
        const user = await sequelize.models.User.create({
            username,
            email,
            password_hash: hashedPassword,
            full_name,
            role: role || 'pharmacy_staff',
            facility_id,
            pharmacy_id
        });

        logger.info(`User created: ${username}`);

        res.status(201).json({
            message: 'User created successfully',
            userId: user.id
        });
    } catch (error) {
        logger.error('Signup error:', error);

        if (error.name === 'SequelizeUniqueConstraintError') {
            return res.status(409).json({ message: 'Username or email already exists' });
        }

        res.status(500).json({ message: 'Error creating user' });
    }
});

// Login endpoint
router.post('/login', async (req, res) => {
    try {
        const { username, email, password, role } = req.body;

        if (!password || !username && !email) {
            return res.status(400).json({ message: 'Missing credentials' });
        }

        // Find user by username or email
        const user = await sequelize.models.User.findOne({
            where: username ? { username } : { email }
        });

        if (!user) {
            return res.status(401).json({ message: 'Invalid credentials' });
        }

        // Verify password
        const passwordMatch = await bcrypt.compare(password, user.password_hash);
        if (!passwordMatch) {
            return res.status(401).json({ message: 'Invalid credentials' });
        }

        // Verify role if provided
        if (role && user.role !== role) {
            return res.status(403).json({ message: 'Invalid role' });
        }

        // Create JWT token
        const token = jwt.sign(
            {
                userId: user.id,
                username: user.username,
                email: user.email,
                role: user.role,
                pharmacyId: user.pharmacy_id,
                facilityId: user.facility_id
            },
            process.env.JWT_SECRET || 'your-secret-key',
            { expiresIn: '24h' }
        );

        // Update last login
        await user.update({ last_login: new Date() });

        logger.info(`User logged in: ${user.username}`);

        res.json({
            message: 'Login successful',
            token,
            user: {
                id: user.id,
                username: user.username,
                email: user.email,
                role: user.role,
                fullName: user.full_name,
                pharmacyId: user.pharmacy_id,
                facilityId: user.facility_id
            }
        });
    } catch (error) {
        logger.error('Login error:', error);
        res.status(500).json({ message: 'Login error' });
    }
});

// Verify token endpoint
router.post('/verify', (req, res) => {
    try {
        const token = req.headers.authorization?.replace('Bearer ', '');

        if (!token) {
            return res.status(401).json({ message: 'No token provided' });
        }

        const decoded = jwt.verify(token, process.env.JWT_SECRET || 'your-secret-key');

        res.json({
            message: 'Token valid',
            user: decoded
        });
    } catch (error) {
        logger.error('Token verification error:', error);
        res.status(401).json({ message: 'Invalid token' });
    }
});

// Refresh token endpoint
router.post('/refresh', (req, res) => {
    try {
        const token = req.headers.authorization?.replace('Bearer ', '');

        if (!token) {
            return res.status(401).json({ message: 'No token provided' });
        }

        const decoded = jwt.verify(token, process.env.JWT_SECRET || 'your-secret-key', {
            ignoreExpiration: true
        });

        const newToken = jwt.sign(
            {
                userId: decoded.userId,
                username: decoded.username,
                email: decoded.email,
                role: decoded.role,
                pharmacyId: decoded.pharmacyId,
                facilityId: decoded.facilityId
            },
            process.env.JWT_SECRET || 'your-secret-key',
            { expiresIn: '24h' }
        );

        res.json({
            message: 'Token refreshed',
            token: newToken
        });
    } catch (error) {
        logger.error('Token refresh error:', error);
        res.status(401).json({ message: 'Invalid token' });
    }
});

// Logout endpoint
router.post('/logout', (req, res) => {
    // In a stateless JWT system, logout is typically handled on the client side
    // However, you could implement token blacklisting here if needed
    res.json({ message: 'Logout successful' });
});

export default router;
