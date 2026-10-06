/**
 * Authentication Middleware
 */

import jwt from 'jsonwebtoken';
import logger from '../config/logger.js';

export const authenticate = (req, res, next) => {
    try {
        const token = req.headers.authorization?.replace('Bearer ', '');

        if (!token) {
            return res.status(401).json({ message: 'No token provided' });
        }

        const decoded = jwt.verify(
            token,
            process.env.JWT_SECRET || 'your-secret-key'
        );

        req.user = decoded;
        next();
    } catch (error) {
        logger.error('Authentication error:', error);
        res.status(401).json({ message: 'Invalid token' });
    }
};

export const authorizeAdmin = (req, res, next) => {
    if (req.user?.role !== 'admin') {
        return res.status(403).json({ message: 'Admin access required' });
    }
    next();
};

export const authorizeFacility = (req, res, next) => {
    if (!['facility_staff', 'admin'].includes(req.user?.role)) {
        return res.status(403).json({ message: 'Facility access required' });
    }
    next();
};

export const authorizePharmacy = (req, res, next) => {
    if (!['pharmacy_staff', 'admin'].includes(req.user?.role)) {
        return res.status(403).json({ message: 'Pharmacy access required' });
    }
    next();
};

export const authorizeFacilityOrAdmin = (req, res, next) => {
    if (!['facility_staff', 'admin'].includes(req.user?.role)) {
        return res.status(403).json({ message: 'Access denied' });
    }
    next();
};

export const authorizeOpenMRS = (req, res, next) => {
    if (req.user?.role !== 'openmrs_sync') {
        return res.status(403).json({ message: 'OpenMRS access required' });
    }
    next();
};
