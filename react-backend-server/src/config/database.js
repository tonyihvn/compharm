/**
 * Database configuration for Sequelize
 */

import { Sequelize } from 'sequelize';
import dotenv from 'dotenv';

dotenv.config();

const DB_TYPE = process.env.DB_TYPE || 'sqlite';

const sequelize = DB_TYPE === 'mysql'
    ? new Sequelize(
        process.env.DB_NAME || 'pharmacy_sync',
        process.env.DB_USER || 'root',
        process.env.DB_PASSWORD || 'root',
        {
            host: process.env.DB_HOST || 'localhost',
            port: process.env.DB_PORT || 3306,
            dialect: 'mysql',
            logging: process.env.NODE_ENV === 'development' ? console.log : false,
            pool: {
                max: 10,
                min: 2,
                acquire: 30000,
                idle: 10000
            },
            dialectOptions: {
                charset: 'utf8mb4',
                supportBigNumbers: true,
                bigNumberStrings: true
            },
            define: {
                timestamps: true,
                underscored: true,
                charset: 'utf8mb4'
            }
        }
    )
    : new Sequelize({
        dialect: 'sqlite',
        storage: process.env.DATABASE_URL || ':memory:',
        logging: process.env.NODE_ENV === 'development' ? console.log : false,
        pool: {
            max: 5,
            min: 0,
            acquire: 30000,
            idle: 10000
        },
        define: {
            timestamps: true,
            underscored: true
        }
    });

export { sequelize, DB_TYPE };
