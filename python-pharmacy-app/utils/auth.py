"""
Authentication utilities for local user management
"""
import hashlib
import secrets
from typing import Optional, Tuple
from sqlalchemy.orm import Session
from database.models import User
import logging

logger = logging.getLogger(__name__)


def hash_password(password: str) -> str:
    """Hash a password using PBKDF2-SHA256."""
    salt = secrets.token_hex(16)
    pwd_hash = hashlib.pbkdf2_hmac(
        'sha256',
        password.encode('utf-8'),
        salt.encode('utf-8'),
        100000
    )
    return f"{salt}${pwd_hash.hex()}"


def verify_password(password: str, password_hash: str) -> bool:
    """Verify a password against a hash."""
    try:
        salt, pwd_hash = password_hash.split('$')
        new_hash = hashlib.pbkdf2_hmac(
            'sha256',
            password.encode('utf-8'),
            salt.encode('utf-8'),
            100000
        )
        return new_hash.hex() == pwd_hash
    except Exception as e:
        logger.error(f"Password verification error: {e}")
        return False


def authenticate_user(
    session: Session, 
    username: str, 
    password: str
) -> Optional[dict]:
    """
    Authenticate user against local database.
    Supports login by username or email.
    Returns user data if authentication succeeds, None otherwise.
    """
    try:
        # Try to find user by username first, then by email
        user = session.query(User).filter_by(username=username).first()
        if not user:
            user = session.query(User).filter_by(email=username).first()
        
        if not user:
            return None
        
        if not user.is_active:
            return None
        
        if not verify_password(password, user.password_hash):
            return None
        
        # Update last login
        from datetime import datetime
        user.last_login = datetime.utcnow()
        session.commit()
        
        # Return user data
        return {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "full_name": user.full_name,
            "role": user.role,
            "facility_id": user.facility_id,
            "pharmacy_id": user.pharmacy_id,
            "is_active": user.is_active,
            "is_superuser": user.is_superuser
        }
    except Exception as e:
        logger.error(f"Authentication error: {e}")
        return None


def create_user(
    session: Session,
    username: str,
    email: str,
    password: str,
    full_name: str,
    role: str = "pharmacy_staff",
    facility_id: Optional[str] = None,
    pharmacy_id: Optional[str] = None,
    is_superuser: bool = False
) -> Optional[dict]:
    """
    Create a new user in the local database.
    Returns user data if creation succeeds, None otherwise.
    """
    try:
        # Check if user already exists
        existing_user = session.query(User).filter(
            (User.username == username) | (User.email == email)
        ).first()
        
        if existing_user:
            logger.warning(f"User already exists: {username}")
            return None
        
        # Hash password
        password_hash = hash_password(password)
        
        # Create user
        new_user = User(
            username=username,
            email=email,
            password_hash=password_hash,
            full_name=full_name,
            role=role,
            facility_id=facility_id,
            pharmacy_id=pharmacy_id,
            is_active=True,
            is_superuser=is_superuser
        )
        
        session.add(new_user)
        session.commit()
        
        logger.info(f"User created successfully: {username}")
        
        return {
            "id": new_user.id,
            "username": new_user.username,
            "email": new_user.email,
            "full_name": new_user.full_name,
            "role": new_user.role,
            "facility_id": new_user.facility_id,
            "pharmacy_id": new_user.pharmacy_id,
            "is_active": new_user.is_active,
            "is_superuser": new_user.is_superuser
        }
    except Exception as e:
        logger.error(f"Error creating user: {e}")
        session.rollback()
        return None


def init_default_admin(session: Session) -> bool:
    """
    Initialize default admin user if no admin exists.
    Uses settings from config.
    """
    try:
        from config.settings import settings
        
        # Check if any admin or superuser exists
        admin_exists = session.query(User).filter(
            (User.is_superuser == True) | (User.role == "admin")
        ).first()
        
        if admin_exists:
            logger.info("Admin user already exists")
            return True
        
        # Create default admin
        result = create_user(
            session,
            username="admin",
            email=settings.SUPER_USER_EMAIL,
            password=settings.SUPER_USER_PASSWORD,
            full_name=settings.SUPER_USER_NAME,
            role="admin",
            is_superuser=True
        )
        
        if result:
            logger.info("Default admin user created successfully")
            return True
        else:
            logger.warning("Failed to create default admin user")
            return False
            
    except Exception as e:
        logger.error(f"Error initializing default admin: {e}")
        return False
