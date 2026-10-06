/**
 * Main Express server for Pharmacy Sync System
 */

import express from 'express';
import cors from 'cors';
import helmet from 'helmet';
import rateLimit from 'express-rate-limit';
import 'express-async-errors';
import dotenv from 'dotenv';
import logger from './config/logger.js';
import { sequelize } from './models/index.js';
import errorHandler from './middleware/errorHandler.js';
import authRoutes from './routes/auth.js';
import clientRoutes from './routes/clients.js';
import formRoutes from './routes/forms.js';
import submissionRoutes from './routes/submissions.js';
import pharmacyRoutes from './routes/pharmacies.js';
import facilityRoutes from './routes/facilities.js';
import syncRoutes from './routes/sync.js';

dotenv.config();

const app = express();
const PORT = process.env.PORT || 3001;

// Security middleware
app.use(helmet());

// Rate limiting
const limiter = rateLimit({
    windowMs: 15 * 60 * 1000, // 15 minutes
    max: 100 // limit each IP to 100 requests per windowMs
});
app.use(limiter);

// CORS configuration
app.use(cors({
    origin: process.env.ALLOWED_ORIGINS?.split(',') || '*',
    credentials: true,
    methods: ['GET', 'POST', 'PUT', 'DELETE', 'PATCH'],
    allowedHeaders: ['Content-Type', 'Authorization', 'X-Pharmacy-ID', 'X-Facility-ID']
}));

// Body parser
app.use(express.json({ limit: '10mb' }));
app.use(express.urlencoded({ limit: '10mb', extended: true }));

// Request logging middleware
app.use((req, res, next) => {
    logger.info(`${req.method} ${req.path} - ${req.ip}`);
    next();
});

// Health check endpoint
app.get('/api/health', (req, res) => {
    res.json({
        status: 'healthy',
        timestamp: new Date().toISOString(),
        version: '1.0.0'
    });
});

// API Routes
app.use('/api/auth', authRoutes);
app.use('/api/clients', clientRoutes);
app.use('/api/forms', formRoutes);
app.use('/api/submissions', submissionRoutes);
app.use('/api/pharmacies', pharmacyRoutes);
app.use('/api/facilities', facilityRoutes);
app.use('/api/sync', syncRoutes);

// 404 handler
app.use((req, res) => {
    res.status(404).json({
        error: 'Not Found',
        path: req.path,
        method: req.method
    });
});

// Error handling middleware
app.use(errorHandler);

// Seed default users
async function seedDefaultUsers() {
    try {
        const { User } = await import('./models/index.js');

        // Check if super admin already exists
        const superAdminExists = await User.findOne({
            where: { email: 'super@compharm.org' }
        });

        if (!superAdminExists) {
            const bcrypt = await import('bcryptjs');
            const saltRounds = 10;
            const hashedPassword = await bcrypt.default.hash('@@ComPharm22', saltRounds);

            await User.create({
                username: 'superadmin',
                email: 'super@compharm.org',
                password_hash: hashedPassword,
                full_name: 'System Administrator',
                role: 'admin',
                is_active: true
            });

            logger.info('Default super admin user created: super@compharm.org');
        } else {
            logger.info('Super admin user already exists');
        }
    } catch (error) {
        logger.warn('Failed to seed default users:', error.message);
    }
}

// Database synchronization and server startup
async function startServer() {
    try {
        // Test database connection
        await sequelize.authenticate();
        logger.info('Database connection established');

        // Sync models with database
        await sequelize.sync({ alter: process.env.NODE_ENV === 'development' });
        logger.info('Database models synchronized');

        // Seed default super admin user
        await seedDefaultUsers();

        // Start server
        app.listen(PORT, () => {
            logger.info(`Server is running on port ${PORT}`);
            logger.info(`Environment: ${process.env.NODE_ENV || 'development'}`);
        });
    } catch (error) {
        logger.error('Failed to start server:', error);
        process.exit(1);
    }
}

// Handle uncaught exceptions
process.on('uncaughtException', (error) => {
    logger.error('Uncaught Exception:', error);
    process.exit(1);
});

// Handle unhandled promise rejections
process.on('unhandledRejection', (reason, promise) => {
    logger.error('Unhandled Rejection at:', promise, 'reason:', reason);
});

startServer();

export default app;
