/**
 * Logger configuration using Winston
 */

import winston from 'winston';
import path from 'path';
import { fileURLToPath } from 'url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));

const logger = winston.createLogger({
    level: process.env.LOG_LEVEL || 'info',
    format: winston.format.combine(
        winston.format.timestamp(),
        winston.format.errors({ stack: true }),
        winston.format.json()
    ),
    defaultMeta: { service: 'pharmacy-sync-server' },
    transports: [
        new winston.transports.File({ filename: path.join(__dirname, '../../logs/error.log'), level: 'error' }),
        new winston.transports.File({ filename: path.join(__dirname, '../../logs/combined.log') }),
        new winston.transports.Console({
            format: winston.format.combine(
                winston.format.colorize(),
                winston.format.printf(({ level, message, timestamp, ...meta }) => {
                    return `${timestamp} [${level}]: ${message} ${Object.keys(meta).length ? JSON.stringify(meta) : ''}`;
                })
            )
        })
    ]
});

export default logger;
