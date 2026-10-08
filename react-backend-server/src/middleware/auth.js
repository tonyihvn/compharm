/**
 * Authentication Middleware
 */

import jwt from 'jsonwebtoken';
import logger from '../config/logger.js';

export const normalizeRole = (role) =>
    String(role ?? '').trim().toLowerCase().replace(/[\s_-]+/g, '_');

export const isAdminRole = (role) => {
    const normalizedRole = normalizeRole(role);
    return ['admin', 'super_admin', 'superadmin', 'administrator', 'system_admin'].includes(normalizedRole);
};

export const hasRole = (user, allowedRoles) => {
    if (!user) {
        return false;
    }

    const normalizedUserRole = normalizeRole(user.role);
    const normalizedAllowedRoles = allowedRoles.map(normalizeRole);

    if (normalizedAllowedRoles.includes(normalizedUserRole)) {
        return true;
    }

    return user.is_superuser === true && normalizedAllowedRoles.includes('admin');
};

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

        req.user = {
            ...decoded,
            role: normalizeRole(decoded.role)
        };
        next();
    } catch (error) {
        logger.error('Authentication error:', error);
        res.status(401).json({ message: 'Invalid token' });
    }
};

export const authorizeAdmin = (req, res, next) => {
    // Check if user is admin or superuser
    const isAdmin = isAdminRole(req.user?.role);
    const isSuperuser = req.user?.is_superuser === true || req.user?.is_superuser === 'true';
    
    if (!isAdmin && !isSuperuser) {
        logger.error(`Admin access denied for user ${req.user?.userId} with role ${req.user?.role} and is_superuser ${req.user?.is_superuser}`);
        return res.status(403).json({ message: 'Admin access required' });
    }
    next();
};

export const authorizeFacility = (req, res, next) => {
    if (!hasRole(req.user, ['facility_staff', 'admin'])) {
        return res.status(403).json({ message: 'Facility access required' });
    }
    next();
};

export const authorizePharmacy = (req, res, next) => {
    if (!hasRole(req.user, ['pharmacy_staff', 'admin'])) {
        return res.status(403).json({ message: 'Pharmacy access required' });
    }
    next();
};

export const authorizeFacilityOrAdmin = (req, res, next) => {
    if (!hasRole(req.user, ['facility_staff', 'admin'])) {
        return res.status(403).json({ message: 'Access denied' });
    }
    next();
};

export const authorizeOpenMRS = (req, res, next) => {
    if (normalizeRole(req.user?.role) !== 'openmrs_sync') {
        return res.status(403).json({ message: 'OpenMRS access required' });
    }
    next();
};
