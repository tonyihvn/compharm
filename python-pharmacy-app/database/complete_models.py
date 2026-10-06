"""Complete database models for pharmacy application."""

from datetime import datetime
from sqlalchemy import (
    Column, String, Integer, Text, DateTime, Boolean, 
    Float, ForeignKey, LargeBinary, Enum, JSON, Index
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
import enum
import uuid

Base = declarative_base()


class User(Base):
    """User model for authentication."""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    user_id = Column(String(36), default=lambda: str(uuid.uuid4()), unique=True)
    username = Column(String(100), unique=True, nullable=False, index=True)
    email = Column(String(100), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    full_name = Column(String(255))
    role = Column(String(50), nullable=False)  # admin, pharmacy_staff, facility_staff
    facility_id = Column(String(100))
    pharmacy_id = Column(String(100))
    is_active = Column(Boolean, default=True)
    last_login = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    form_submissions = relationship("FormSubmission", back_populates="user")
    sync_logs = relationship("SyncLog", back_populates="user")

    __table_args__ = (Index('idx_user_pharmacy_id', 'pharmacy_id'),
                      Index('idx_user_facility_id', 'facility_id'),)

    def __repr__(self):
        return f"<User {self.username} ({self.role})>"


class PharmacyForm(Base):
    """Uploaded pharmacy forms from admin."""
    __tablename__ = "pharmacy_forms"

    id = Column(Integer, primary_key=True)
    form_id = Column(String(36), default=lambda: str(uuid.uuid4()), unique=True)
    form_name = Column(String(255), nullable=False)
    form_uuid = Column(String(36), unique=True)
    description = Column(Text)
    form_data = Column(JSON, nullable=False)  # Stores the complete form schema
    version = Column(Integer, default=1)
    is_active = Column(Boolean, default=True)
    created_by = Column(Integer, ForeignKey('users.id'))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    form_submissions = relationship("FormSubmission", back_populates="form")

    def __repr__(self):
        return f"<PharmacyForm {self.form_name}>"


class Client(Base):
    """Client/Patient model."""
    __tablename__ = "clients"

    id = Column(Integer, primary_key=True)
    client_id = Column(String(36), default=lambda: str(uuid.uuid4()), unique=True)
    pepfar_id = Column(String(100), unique=True, nullable=False, index=True)
    full_name = Column(String(255), nullable=False)
    date_of_birth = Column(DateTime)
    gender = Column(String(10))  # M, F
    phone_number = Column(String(20))
    email = Column(String(100))
    address = Column(Text)
    
    # Facility and Pharmacy mapping
    facility_id = Column(String(100), nullable=False, index=True)
    pharmacy_id = Column(String(100), nullable=False, index=True)
    
    # Clinical data (read-only, synced from central server)
    weight = Column(Float)  # kg
    height = Column(Float)  # cm
    bmi = Column(Float)
    last_visit_date = Column(DateTime)
    hiv_status = Column(String(50))  # Positive, Negative, Unknown
    art_status = Column(String(50))  # On ART, Not on ART
    current_cd4 = Column(Integer)
    current_viral_load = Column(Integer)
    
    # Metadata
    synced_at = Column(DateTime)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    form_submissions = relationship("FormSubmission", back_populates="client")
    client_data_snapshots = relationship("ClientDataSnapshot", back_populates="client")

    __table_args__ = (Index('idx_client_pepfar_id', 'pepfar_id'),
                      Index('idx_client_pharmacy_id', 'pharmacy_id'),
                      Index('idx_client_facility_id', 'facility_id'),)

    def __repr__(self):
        return f"<Client {self.pepfar_id} - {self.full_name}>"


class ClientDataSnapshot(Base):
    """Snapshot of client data from central server for audit/history."""
    __tablename__ = "client_data_snapshots"

    id = Column(Integer, primary_key=True)
    snapshot_id = Column(String(36), default=lambda: str(uuid.uuid4()), unique=True)
    client_id = Column(Integer, ForeignKey('clients.id'), nullable=False)
    snapshot_data = Column(JSON, nullable=False)  # Stores complete client data
    synced_from = Column(String(100))  # Source system (central_server, openmrs)
    sync_hash = Column(String(64))  # SHA256 hash for change detection
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    client = relationship("Client", back_populates="client_data_snapshots")

    __table_args__ = (Index('idx_snapshot_client_id', 'client_id'),)

    def __repr__(self):
        return f"<Snapshot {self.snapshot_id}>"


class FormSubmission(Base):
    """Form submission/encounter data."""
    __tablename__ = "form_submissions"

    id = Column(Integer, primary_key=True)
    submission_id = Column(String(36), default=lambda: str(uuid.uuid4()), unique=True)
    form_id = Column(Integer, ForeignKey('pharmacy_forms.id'), nullable=False)
    client_id = Column(Integer, ForeignKey('clients.id'), nullable=False)
    submitted_by = Column(Integer, ForeignKey('users.id'), nullable=False)
    
    # Form data
    form_data = Column(JSON, nullable=False)  # Stores the submitted form data
    validation_errors = Column(JSON)  # Stores validation errors if any
    
    # Status
    status = Column(String(50), default='draft')  # draft, submitted, synced, error
    sync_status = Column(String(50), default='pending')  # pending, synced, failed
    sync_error_message = Column(Text)
    
    # Timestamps
    submitted_at = Column(DateTime, default=datetime.utcnow)
    synced_at = Column(DateTime)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    form = relationship("PharmacyForm", back_populates="form_submissions")
    client = relationship("Client", back_populates="form_submissions")
    user = relationship("User", back_populates="form_submissions")

    __table_args__ = (Index('idx_submission_client_id', 'client_id'),
                      Index('idx_submission_form_id', 'form_id'),
                      Index('idx_submission_status', 'status'),)

    def __repr__(self):
        return f"<FormSubmission {self.submission_id}>"


class DrugInventory(Base):
    """Drug inventory tracking."""
    __tablename__ = "drug_inventory"

    id = Column(Integer, primary_key=True)
    drug_id = Column(String(36), default=lambda: str(uuid.uuid4()), unique=True)
    drug_name = Column(String(255), nullable=False)
    drug_code = Column(String(100), nullable=False)
    generic_name = Column(String(255))
    quantity = Column(Integer, nullable=False)
    unit = Column(String(50))  # tablets, ml, vials, etc.
    batch_number = Column(String(100))
    expiry_date = Column(DateTime)
    manufacturer = Column(String(255))
    cost_per_unit = Column(Float)
    reorder_level = Column(Integer)
    is_active = Column(Boolean, default=True)
    last_updated = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<Drug {self.drug_name}>"


class SyncLog(Base):
    """Sync operation logs."""
    __tablename__ = "sync_logs"

    id = Column(Integer, primary_key=True)
    sync_id = Column(String(36), default=lambda: str(uuid.uuid4()), unique=True)
    sync_type = Column(String(50))  # pull_clients, push_forms, full_sync
    user_id = Column(Integer, ForeignKey('users.id'))
    status = Column(String(50))  # started, completed, failed
    records_synced = Column(Integer, default=0)
    error_message = Column(Text)
    sync_duration_seconds = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="sync_logs")

    __table_args__ = (Index('idx_sync_status', 'status'),
                      Index('idx_sync_created_at', 'created_at'),)

    def __repr__(self):
        return f"<SyncLog {self.sync_id}>"


class AuditLog(Base):
    """Audit trail for all operations."""
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True)
    audit_id = Column(String(36), default=lambda: str(uuid.uuid4()), unique=True)
    action = Column(String(255), nullable=False)
    entity_type = Column(String(100))
    entity_id = Column(String(100))
    user_id = Column(Integer, ForeignKey('users.id'))
    old_values = Column(JSON)
    new_values = Column(JSON)
    ip_address = Column(String(50))
    user_agent = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)

    __table_args__ = (Index('idx_audit_action', 'action'),
                      Index('idx_audit_entity_type', 'entity_type'),
                      Index('idx_audit_created_at', 'created_at'),)

    def __repr__(self):
        return f"<AuditLog {self.audit_id}>"
