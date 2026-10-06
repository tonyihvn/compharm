/**
 * Error handler middleware
 */

import logger from '../config/logger.js';

const errorHandler = (err, req, res, next) => {
    logger.error('Error:', {
        message: err.message,
        stack: err.stack,
        path: req.path,
        method: req.method,
        body: req.body
    });

    // Sequelize validation errors
    if (err.name === 'SequelizeValidationError') {
        return res.status(400).json({
            error: 'Validation Error',
            details: err.errors.map(e => ({ field: e.path, message: e.message }))
        });
    }

    // Sequelize unique constraint errors
    if (err.name === 'SequelizeUniqueConstraintError') {
        return res.status(409).json({
            error: 'Conflict',
            message: 'This record already exists'
        });
    }

    // Authentication errors
    if (err.name === 'UnauthorizedError' || err.message === 'Unauthorized') {
        return res.status(401).json({
            error: 'Unauthorized',
            message: 'Invalid or missing credentials'
        });
    }

    // Forbidden errors
    if (err.name === 'ForbiddenError' || err.message === 'Forbidden') {
        return res.status(403).json({
            error: 'Forbidden',
            message: 'You do not have permission to perform this action'
        });
    }

    // Default error response
    res.status(err.status || 500).json({
        error: err.name || 'Internal Server Error',
        message: err.message || 'An unexpected error occurred',
        ...(process.env.NODE_ENV === 'development' && { stack: err.stack })
    });
};

export default errorHandler;
