"""
SQLAlchemy ORM Models for Community Pharmacy App
Comprehensive database schema with full relationships
"""

from datetime import datetime
from sqlalchemy import (
    Column, String, Integer, Text, DateTime, Boolean, 
    Float, ForeignKey, JSON, Index, Numeric
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()


class User(Base):
    """User authentication and authorization model"""
    __tablename__ = "users"
    __table_args__ = (
        Index('idx_username', 'username'),
        Index('idx_email', 'email'),
    )

    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(100), unique=True, nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=False)
    phone = Column(String(20))
    
    # Role and permissions
    role = Column(String(50), nullable=False)  # admin, pharmacy_staff, facility_officer
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)
    
    # Facility/Pharmacy mapping
    facility_id = Column(String(100))
    pharmacy_id = Column(String(100), ForeignKey('pharmacies.code'))
    
    # Audit fields
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    last_login = Column(DateTime)
    
    # Relationships
    form_submissions = relationship("FormSubmission", back_populates="filled_by_user")
    uploaded_forms = relationship("Form", back_populates="uploaded_by_user")
    sync_logs = relationship("SyncLog", back_populates="user")

    def __repr__(self):
        return f"<User {self.username} - {self.role}>"


class Pharmacy(Base):
    """Pharmacy information and settings"""
    __tablename__ = "pharmacies"

    id = Column(Integer, primary_key=True, autoincrement=True)
    code = Column(String(50), unique=True, nullable=False, index=True)
    name = Column(String(255), nullable=False)
    location = Column(String(255))
    district = Column(String(100))
    region = Column(String(100))
    
    # Contact information
    phone = Column(String(20))
    email = Column(String(100))
    
    # API credentials for central server
    api_key = Column(String(255), unique=True, nullable=False)
    is_active = Column(Boolean, default=True)
    
    # Audit fields
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    users = relationship("User", foreign_keys=[User.pharmacy_id])
    clients = relationship("Client", back_populates="pharmacy")

    def __repr__(self):
        return f"<Pharmacy {self.code} - {self.name}>"


class Facility(Base):
    """Facility/Health center information"""
    __tablename__ = "facilities"

    id = Column(Integer, primary_key=True, autoincrement=True)
    code = Column(String(50), unique=True, nullable=False, index=True)
    name = Column(String(255), nullable=False)
    location = Column(String(255))
    district = Column(String(100))
    region = Column(String(100))
    
    # Contact information
    phone = Column(String(20))
    email = Column(String(100))
    
    # API endpoint
    api_url = Column(String(500))
    is_active = Column(Boolean, default=True)
    
    # Audit fields
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    clients = relationship("Client", back_populates="facility")

    def __repr__(self):
        return f"<Facility {self.code} - {self.name}>"


class Client(Base):
    """Patient/Client model - downloaded from facilities"""
    __tablename__ = "clients"
    __table_args__ = (
        Index('idx_pepfar_id', 'pepfar_id'),
        Index('idx_pharmacy_id', 'pharmacy_id'),
        Index('idx_facility_id', 'facility_id'),
    )

    id = Column(Integer, primary_key=True, autoincrement=True)
    
    # Client identification
    pepfar_id = Column(String(100), unique=True, nullable=False, index=True)
    full_name = Column(String(255), nullable=False)
    date_of_birth = Column(DateTime)
    gender = Column(String(10))  # M, F, O
    
    # Contact information
    phone_number = Column(String(20))
    email = Column(String(100))
    national_id = Column(String(50))
    
    # Assignment information
    facility_id = Column(String(100), ForeignKey('facilities.code'), nullable=False)
    pharmacy_id = Column(String(100), ForeignKey('pharmacies.code'), nullable=False)
    
    # Clinical data (stored as JSON for flexibility)
    additional_data = Column(JSON, default={})
    
    # Status tracking
    status = Column(String(20), default='active')  # active, inactive, archived
    
    # Sync tracking
    server_client_id = Column(String(100))  # ID from central server
    last_updated_from_server = Column(DateTime)
    created_locally_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_locally_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    facility = relationship("Facility", back_populates="clients")
    pharmacy = relationship("Pharmacy", back_populates="clients")
    form_submissions = relationship("FormSubmission", back_populates="client", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Client {self.pepfar_id} - {self.full_name}>"


class Form(Base):
    """Form definitions uploaded from admin"""
    __tablename__ = "forms"
    __table_args__ = (
        Index('idx_form_uuid', 'uuid'),
    )

    id = Column(Integer, primary_key=True, autoincrement=True)
    
    # Form identification
    name = Column(String(255), nullable=False)
    uuid = Column(String(100), unique=True, nullable=False, index=True)
    version = Column(String(50), default='1.0')
    
    # Form definition (OpenMRS JSON schema)
    definition = Column(JSON, nullable=False)
    description = Column(Text)
    
    # Metadata
    is_published = Column(Boolean, default=False)
    is_retired = Column(Boolean, default=False)
    
    # Upload information
    uploaded_by_user_id = Column(Integer, ForeignKey('users.id'))
    uploaded_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Audit fields
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    uploaded_by_user = relationship("User", back_populates="uploaded_forms")
    form_submissions = relationship("FormSubmission", back_populates="form", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Form {self.name} v{self.version}>"


class FormSubmission(Base):
    """Completed form submissions"""
    __tablename__ = "form_submissions"
    __table_args__ = (
        Index('idx_client_id', 'client_id'),
        Index('idx_form_id', 'form_id'),
    )

    id = Column(Integer, primary_key=True, autoincrement=True)
    
    # References
    form_id = Column(Integer, ForeignKey('forms.id'), nullable=False)
    client_id = Column(Integer, ForeignKey('clients.id'), nullable=False)
    filled_by_user_id = Column(Integer, ForeignKey('users.id'))
    
    # Form data
    data = Column(JSON, nullable=False)
    
    # Metadata
    filled_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    status = Column(String(20), default='draft')  # draft, submitted, synced, rejected
    
    # Sync information
    is_synced_to_server = Column(Boolean, default=False)
    synced_at = Column(DateTime)
    server_submission_id = Column(String(100))  # ID from central server
    
    # Audit fields
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    form = relationship("Form", back_populates="form_submissions")
    client = relationship("Client", back_populates="form_submissions")
    filled_by_user = relationship("User", back_populates="form_submissions")

"""
SQLAlchemy ORM Models for Community Pharmacy App
Comprehensive database schema with full relationships
"""

from datetime import datetime
from sqlalchemy import (
    Column, String, Integer, Text, DateTime, Boolean, 
    Float, ForeignKey, JSON, Index, Numeric
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()


class User(Base):
    """User authentication and authorization model"""
    __tablename__ = "users"
    __table_args__ = (
        Index('idx_username', 'username'),
        Index('idx_email', 'email'),
    )

    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(100), unique=True, nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=False)
    phone = Column(String(20))
    
    # Role and permissions
    role = Column(String(50), nullable=False)  # admin, pharmacy_staff, facility_officer
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)
    
    # Facility/Pharmacy mapping
    facility_id = Column(String(100))
    pharmacy_id = Column(String(100), ForeignKey('pharmacies.code'))
    
    # Audit fields
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    last_login = Column(DateTime)
    
    # Relationships
    form_submissions = relationship("FormSubmission", back_populates="filled_by_user")
    uploaded_forms = relationship("Form", back_populates="uploaded_by_user")
    sync_logs = relationship("SyncLog", back_populates="user")

    def __repr__(self):
        return f"<User {self.username} - {self.role}>"


class Pharmacy(Base):
    """Pharmacy information and settings"""
    __tablename__ = "pharmacies"

    id = Column(Integer, primary_key=True, autoincrement=True)
    code = Column(String(50), unique=True, nullable=False, index=True)
    name = Column(String(255), nullable=False)
    location = Column(String(255))
    district = Column(String(100))
    region = Column(String(100))
    
    # Contact information
    phone = Column(String(20))
    email = Column(String(100))
    
    # API credentials for central server
    api_key = Column(String(255), unique=True, nullable=False)
    is_active = Column(Boolean, default=True)
    
    # Audit fields
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    users = relationship("User", foreign_keys=[User.pharmacy_id])
    clients = relationship("Client", back_populates="pharmacy")

    def __repr__(self):
        return f"<Pharmacy {self.code} - {self.name}>"


class Facility(Base):
    """Facility/Health center information"""
    __tablename__ = "facilities"

    id = Column(Integer, primary_key=True, autoincrement=True)
    code = Column(String(50), unique=True, nullable=False, index=True)
    name = Column(String(255), nullable=False)
    location = Column(String(255))
    district = Column(String(100))
    region = Column(String(100))
    
    # Contact information
    phone = Column(String(20))
    email = Column(String(100))
    
    # API endpoint
    api_url = Column(String(500))
    is_active = Column(Boolean, default=True)
    
    # Audit fields
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    clients = relationship("Client", back_populates="facility")

    def __repr__(self):
        return f"<Facility {self.code} - {self.name}>"


class Client(Base):
    """Patient/Client model - downloaded from facilities"""
    __tablename__ = "clients"
    __table_args__ = (
        Index('idx_pepfar_id', 'pepfar_id'),
        Index('idx_pharmacy_id', 'pharmacy_id'),
        Index('idx_facility_id', 'facility_id'),
    )

    id = Column(Integer, primary_key=True, autoincrement=True)
    
    # Client identification
    pepfar_id = Column(String(100), unique=True, nullable=False, index=True)
    full_name = Column(String(255), nullable=False)
    date_of_birth = Column(DateTime)
    gender = Column(String(10))  # M, F, O
    
    # Contact information
    phone_number = Column(String(20))
    email = Column(String(100))
    national_id = Column(String(50))
    
    # Assignment information
    facility_id = Column(String(100), ForeignKey('facilities.code'), nullable=False)
    pharmacy_id = Column(String(100), ForeignKey('pharmacies.code'), nullable=False)
    
    # Clinical data (stored as JSON for flexibility)
    additional_data = Column(JSON, default={})
    
    # Status tracking
    status = Column(String(20), default='active')  # active, inactive, archived
    
    # Sync tracking
    server_client_id = Column(String(100))  # ID from central server
    last_updated_from_server = Column(DateTime)
    created_locally_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_locally_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    facility = relationship("Facility", back_populates="clients")
    pharmacy = relationship("Pharmacy", back_populates="clients")
    form_submissions = relationship("FormSubmission", back_populates="client", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Client {self.pepfar_id} - {self.full_name}>"


class Form(Base):
    """Form definitions uploaded from admin"""
    __tablename__ = "forms"
    __table_args__ = (
        Index('idx_form_uuid', 'uuid'),
    )

    id = Column(Integer, primary_key=True, autoincrement=True)
    
    # Form identification
    name = Column(String(255), nullable=False)
    uuid = Column(String(100), unique=True, nullable=False, index=True)
    version = Column(String(50), default='1.0')
    
    # Form definition (OpenMRS JSON schema)
    definition = Column(JSON, nullable=False)
    description = Column(Text)
    
    # Metadata
    is_published = Column(Boolean, default=False)
    is_retired = Column(Boolean, default=False)
    
    # Upload information
    uploaded_by_user_id = Column(Integer, ForeignKey('users.id'))
    uploaded_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Audit fields
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    uploaded_by_user = relationship("User", back_populates="uploaded_forms")
    form_submissions = relationship("FormSubmission", back_populates="form", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Form {self.name} v{self.version}>"


class FormSubmission(Base):
    """Completed form submissions"""
    __tablename__ = "form_submissions"
    __table_args__ = (
        Index('idx_client_id', 'client_id'),
        Index('idx_form_id', 'form_id'),
    )

    id = Column(Integer, primary_key=True, autoincrement=True)
    
    # References
    form_id = Column(Integer, ForeignKey('forms.id'), nullable=False)
    client_id = Column(Integer, ForeignKey('clients.id'), nullable=False)
    filled_by_user_id = Column(Integer, ForeignKey('users.id'))
    
    # Form data
    data = Column(JSON, nullable=False)
    
    # Metadata
    filled_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    status = Column(String(20), default='draft')  # draft, submitted, synced, rejected
    
    # Sync information
    is_synced_to_server = Column(Boolean, default=False)
    synced_at = Column(DateTime)
    server_submission_id = Column(String(100))  # ID from central server
    
    # Audit fields
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    form = relationship("Form", back_populates="form_submissions")
    client = relationship("Client", back_populates="form_submissions")
    filled_by_user = relationship("User", back_populates="form_submissions")

    def __repr__(self):
        return f"<FormSubmission form={self.form_id} client={self.client_id} status={self.status}>"


class SyncLog(Base):
    """Sync operation log"""
    __tablename__ = "sync_logs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    
    # Sync type
    sync_type = Column(String(50), nullable=False)  # download_clients, upload_submissions, download_forms
    
    # Status
    status = Column(String(20), nullable=False)  # pending, in_progress, success, failed
    
    # Details
    total_items = Column(Integer, default=0)
    processed_items = Column(Integer, default=0)
    error_message = Column(Text)
    
    # Timing
    started_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    completed_at = Column(DateTime)
    
    # Relationships
    user = relationship("User", back_populates="sync_logs")

    def __repr__(self):
        return f"<SyncLog {self.sync_type} - {self.status}>"


class AppSettings(Base):
    """Application settings storage"""
    __tablename__ = "app_settings"

    id = Column(Integer, primary_key=True, autoincrement=True)
    key = Column(String(100), unique=True, nullable=False, index=True)
    value = Column(Text)
    description = Column(String(255))
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    def __repr__(self):
        return f"<AppSettings {self.key}>"

    id = Column(Integer, primary_key=True)
    key = Column(String(100), unique=True, nullable=False)
    value = Column(Text)
    description = Column(String(255))
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<AppSettings {self.key}>"
