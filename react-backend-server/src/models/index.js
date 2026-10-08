/**
 * Sequelize models for the pharmacy sync system
 */

import { DataTypes, Model } from 'sequelize';
import dotenv from 'dotenv';
import { sequelize } from '../config/database.js';

dotenv.config();

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
    is_superuser: {
        type: DataTypes.BOOLEAN,
        defaultValue: false
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

// ClientField model
class ClientField extends Model { }
ClientField.init({
    id: {
        type: DataTypes.UUID,
        defaultValue: DataTypes.UUIDV4,
        primaryKey: true
    },
    name: {
        type: DataTypes.STRING(255),
        allowNull: false
    },
    field_name: {
        type: DataTypes.STRING(255),
        allowNull: false,
        unique: true
    },
    field_type: {
        type: DataTypes.STRING(50),
        allowNull: false
    },
    required: {
        type: DataTypes.BOOLEAN,
        defaultValue: false
    },
    order_index: {
        type: DataTypes.INTEGER,
        defaultValue: 999
    }
}, {
    sequelize,
    modelName: 'ClientField',
    tableName: 'client_fields',
    timestamps: true,
    indexes: [
        { fields: ['field_name'] },
        { fields: ['order_index'] }
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
    underscored: false,
    indexes: [
        { fields: ['status'] },
        { fields: ['createdAt'] }
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
    underscored: false,
    indexes: [
        { fields: ['action'] },
        { fields: ['entity_type'] },
        { fields: ['createdAt'] }
    ]
});

// FormFieldPermission model for field-level access control
class FormFieldPermission extends Model { }
FormFieldPermission.init({
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
    field_name: {
        type: DataTypes.STRING(255),
        allowNull: false,
        comment: 'Name of the form field (e.g., "patient_id", "dosage")'
    },
    field_path: {
        type: DataTypes.STRING(500),
        comment: 'Full path to nested field if applicable (e.g., "sections[0].questions[1]")'
    },
    allow_read: {
        type: DataTypes.BOOLEAN,
        defaultValue: true,
        comment: 'Whether pharmacy app can read this field'
    },
    allow_edit: {
        type: DataTypes.BOOLEAN,
        defaultValue: false,
        comment: 'Whether pharmacy app can edit this field'
    },
    read_only_in_app: {
        type: DataTypes.BOOLEAN,
        defaultValue: false,
        comment: 'If true, field is visible but cannot be edited in app'
    },
    hidden_in_app: {
        type: DataTypes.BOOLEAN,
        defaultValue: false,
        comment: 'If true, field is not visible in pharmacy app'
    },
    role_restrictions: {
        type: DataTypes.JSON,
        comment: 'Array of roles that can access this field. Empty means all roles.'
    },
    description: DataTypes.TEXT,
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
    modelName: 'FormFieldPermission',
    tableName: 'form_field_permissions',
    timestamps: true,
    indexes: [
        { fields: ['form_id'] },
        { fields: ['form_id', 'field_name'] },
        { fields: ['is_active'] }
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

// FormFieldPermission associations
PharmacyForm.hasMany(FormFieldPermission, { foreignKey: 'form_id' });
FormFieldPermission.belongsTo(PharmacyForm, { foreignKey: 'form_id' });
FormFieldPermission.belongsTo(User, { foreignKey: 'created_by' });

// Export sequelize and all models
export {
    sequelize,
    User,
    Pharmacy,
    Facility,
    Client,
    ClientField,
    PharmacyForm,
    FormSubmission,
    SyncLog,
    AuditLog,
    FormFieldPermission
};
