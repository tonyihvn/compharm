/**
 * Sequelize models for the pharmacy sync system
 */

import { Sequelize, DataTypes, Model } from 'sequelize';
import dotenv from 'dotenv';
import path from 'path';
import { fileURLToPath } from 'url';

dotenv.config();

const __dirname = path.dirname(fileURLToPath(import.meta.url));

// Initialize Sequelize - use SQLite for development (independent operation)
// To use MySQL, set DB_TYPE=mysql in .env and ensure MySQL is running
const sequelize = process.env.DB_TYPE === 'mysql'
    ? new Sequelize({
        dialect: 'mysql',
        host: process.env.DB_HOST || 'localhost',
        port: process.env.DB_PORT || 3306,
        database: process.env.DB_NAME || 'pharmacy_sync',
        username: process.env.DB_USER || 'root',
        password: process.env.DB_PASSWORD || 'root',
        logging: process.env.NODE_ENV === 'development' ? console.log : false,
        define: {
            timestamps: true,
            underscored: true
        }
    })
    : new Sequelize({
        dialect: 'sqlite',
        storage: path.join(__dirname, '../../pharmacy_sync_backend.db'),
        logging: process.env.NODE_ENV === 'development' ? console.log : false,
        define: {
            timestamps: true,
            underscored: true
        }
    });

// User model
class User extends Model { }
User.init({
    id: {
        type: DataTypes.UUID,
        defaultValue: DataTypes.UUIDV4,
        primaryKey: true
    },
    username: {
        type: DataTypes.STRING(100),
        allowNull: false,
        unique: true
    },
    email: {
        type: DataTypes.STRING(100),
        allowNull: false,
        unique: true,
        validate: { isEmail: true }
    },
    password_hash: {
        type: DataTypes.STRING(255),
        allowNull: false
    },
    full_name: {
        type: DataTypes.STRING(255)
    },
    role: {
        type: DataTypes.STRING(50),
        allowNull: false,
        defaultValue: 'pharmacy_staff'
    },
    facility_id: DataTypes.STRING(100),
    pharmacy_id: DataTypes.STRING(100),
    is_active: {
        type: DataTypes.BOOLEAN,
        defaultValue: true
    },
    last_login: DataTypes.DATE
}, {
    sequelize,
    modelName: 'User',
    tableName: 'users',
    timestamps: true
});

// Pharmacy model
class Pharmacy extends Model { }
Pharmacy.init({
    id: {
        type: DataTypes.UUID,
        defaultValue: DataTypes.UUIDV4,
        primaryKey: true
    },
    pharmacy_code: {
        type: DataTypes.STRING(100),
        allowNull: false,
        unique: true
    },
    pharmacy_name: {
        type: DataTypes.STRING(255),
        allowNull: false
    },
    description: DataTypes.TEXT,
    address: DataTypes.TEXT,
    phone: DataTypes.STRING(20),
    email: DataTypes.STRING(100),
    api_key: {
        type: DataTypes.STRING(255),
        allowNull: false,
        unique: true
    },
    is_active: {
        type: DataTypes.BOOLEAN,
        defaultValue: true
    }
}, {
    sequelize,
    modelName: 'Pharmacy',
    tableName: 'pharmacies',
    timestamps: true
});

// Facility model
class Facility extends Model { }
Facility.init({
    id: {
        type: DataTypes.UUID,
        defaultValue: DataTypes.UUIDV4,
        primaryKey: true
    },
    facility_code: {
        type: DataTypes.STRING(100),
        allowNull: false,
        unique: true
    },
    facility_name: {
        type: DataTypes.STRING(255),
        allowNull: false
    },
    description: DataTypes.TEXT,
    system_type: {
        type: DataTypes.STRING(50),
        defaultValue: 'openmrs'
    },
    address: DataTypes.TEXT,
    phone: DataTypes.STRING(20),
    email: DataTypes.STRING(100),
    is_active: {
        type: DataTypes.BOOLEAN,
        defaultValue: true
    }
}, {
    sequelize,
    modelName: 'Facility',
    tableName: 'facilities',
    timestamps: true
});

// Client model
class Client extends Model { }
Client.init({
    id: {
        type: DataTypes.UUID,
        defaultValue: DataTypes.UUIDV4,
        primaryKey: true
    },
    pepfar_id: {
        type: DataTypes.STRING(100),
        allowNull: false,
        unique: true
    },
    full_name: {
        type: DataTypes.STRING(255),
        allowNull: false
    },
    date_of_birth: DataTypes.DATE,
    gender: DataTypes.STRING(10),
    phone_number: DataTypes.STRING(20),
    email: DataTypes.STRING(100),
    address: DataTypes.TEXT,
    facility_id: {
        type: DataTypes.UUID,
        allowNull: false,
        references: { model: 'facilities', key: 'id' }
    },
    pharmacy_id: {
        type: DataTypes.UUID,
        allowNull: false,
        references: { model: 'pharmacies', key: 'id' }
    },
    weight: DataTypes.FLOAT,
    height: DataTypes.FLOAT,
    bmi: DataTypes.FLOAT,
    last_visit_date: DataTypes.DATE,
    hiv_status: DataTypes.STRING(50),
    art_status: DataTypes.STRING(50),
    current_cd4: DataTypes.INTEGER,
    current_viral_load: DataTypes.INTEGER,
    is_active: {
        type: DataTypes.BOOLEAN,
        defaultValue: true
    }
}, {
    sequelize,
    modelName: 'Client',
    tableName: 'clients',
    timestamps: true,
    indexes: [
        { fields: ['pepfar_id'] },
        { fields: ['facility_id'] },
        { fields: ['pharmacy_id'] }
    ]
});

// PharmacyForm model
class PharmacyForm extends Model { }
PharmacyForm.init({
    id: {
        type: DataTypes.UUID,
        defaultValue: DataTypes.UUIDV4,
        primaryKey: true
    },
    form_name: {
        type: DataTypes.STRING(255),
        allowNull: false
    },
    form_uuid: {
        type: DataTypes.STRING(36),
        unique: true
    },
    description: DataTypes.TEXT,
    form_data: {
        type: DataTypes.JSON,
        allowNull: false
    },
    version: {
        type: DataTypes.INTEGER,
        defaultValue: 1
    },
    created_by: {
        type: DataTypes.UUID,
        references: { model: 'users', key: 'id' }
    },
    is_active: {
        type: DataTypes.BOOLEAN,
        defaultValue: true
    }
}, {
    sequelize,
    modelName: 'PharmacyForm',
    tableName: 'pharmacy_forms',
    timestamps: true
});

// FormSubmission model
class FormSubmission extends Model { }
FormSubmission.init({
    id: {
        type: DataTypes.UUID,
        defaultValue: DataTypes.UUIDV4,
        primaryKey: true
    },
    form_id: {
        type: DataTypes.UUID,
        allowNull: false,
        references: { model: 'pharmacy_forms', key: 'id' }
    },
    client_id: {
        type: DataTypes.UUID,
        allowNull: false,
        references: { model: 'clients', key: 'id' }
    },
    submitted_by: {
        type: DataTypes.UUID,
        allowNull: false,
        references: { model: 'users', key: 'id' }
    },
    form_data: {
        type: DataTypes.JSON,
        allowNull: false
    },
    validation_errors: DataTypes.JSON,
    status: {
        type: DataTypes.STRING(50),
        defaultValue: 'draft'
    },
    sync_status: {
        type: DataTypes.STRING(50),
        defaultValue: 'pending'
    },
    sync_error_message: DataTypes.TEXT,
    synced_at: DataTypes.DATE
}, {
    sequelize,
    modelName: 'FormSubmission',
    tableName: 'form_submissions',
    timestamps: true,
    indexes: [
        { fields: ['client_id'] },
        { fields: ['form_id'] },
        { fields: ['status'] }
    ]
});

// SyncLog model
class SyncLog extends Model { }
SyncLog.init({
    id: {
        type: DataTypes.UUID,
        defaultValue: DataTypes.UUIDV4,
        primaryKey: true
    },
    sync_type: {
        type: DataTypes.STRING(50),
        allowNull: false
    },
    source: DataTypes.STRING(100),
    user_id: {
        type: DataTypes.UUID,
        references: { model: 'users', key: 'id' }
    },
    status: {
        type: DataTypes.STRING(50),
        defaultValue: 'started'
    },
    records_synced: {
        type: DataTypes.INTEGER,
        defaultValue: 0
    },
    error_message: DataTypes.TEXT,
    sync_duration_seconds: DataTypes.FLOAT
}, {
    sequelize,
    modelName: 'SyncLog',
    tableName: 'sync_logs',
    timestamps: true,
    indexes: [
        { fields: ['status'] },
        { fields: ['created_at'] }
    ]
});

// AuditLog model
class AuditLog extends Model { }
AuditLog.init({
    id: {
        type: DataTypes.UUID,
        defaultValue: DataTypes.UUIDV4,
        primaryKey: true
    },
    action: {
        type: DataTypes.STRING(255),
        allowNull: false
    },
    entity_type: DataTypes.STRING(100),
    entity_id: DataTypes.STRING(100),
    user_id: {
        type: DataTypes.UUID,
        references: { model: 'users', key: 'id' }
    },
    old_values: DataTypes.JSON,
    new_values: DataTypes.JSON,
    ip_address: DataTypes.STRING(50),
    user_agent: DataTypes.TEXT
}, {
    sequelize,
    modelName: 'AuditLog',
    tableName: 'audit_logs',
    timestamps: true,
    indexes: [
        { fields: ['action'] },
        { fields: ['entity_type'] },
        { fields: ['created_at'] }
    ]
});

// Associations
User.hasMany(PharmacyForm, { foreignKey: 'created_by' });
User.hasMany(FormSubmission, { foreignKey: 'submitted_by' });
User.hasMany(SyncLog, { foreignKey: 'user_id' });

PharmacyForm.hasMany(FormSubmission, { foreignKey: 'form_id' });
Client.hasMany(FormSubmission, { foreignKey: 'client_id' });
FormSubmission.belongsTo(PharmacyForm, { foreignKey: 'form_id' });
FormSubmission.belongsTo(Client, { foreignKey: 'client_id' });
FormSubmission.belongsTo(User, { foreignKey: 'submitted_by' });

Facility.hasMany(Client, { foreignKey: 'facility_id' });
Pharmacy.hasMany(Client, { foreignKey: 'pharmacy_id' });
Client.belongsTo(Facility, { foreignKey: 'facility_id' });
Client.belongsTo(Pharmacy, { foreignKey: 'pharmacy_id' });

// Export sequelize and all models
export {
    sequelize,
    User,
    Pharmacy,
    Facility,
    Client,
    PharmacyForm,
    FormSubmission,
    SyncLog,
    AuditLog
};
