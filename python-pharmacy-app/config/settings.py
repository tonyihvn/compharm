"""
Application Settings and Configuration
"""
import os
from pathlib import Path
from pydantic_settings import BaseSettings
from pydantic import ConfigDict

class Settings(BaseSettings):
    """Application settings from environment variables"""
    
    model_config = ConfigDict(
        env_file=".env",
        case_sensitive=False,
        extra="ignore"
    )
    
    # App Settings
    APP_NAME: str = "Community Pharmacy App"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    
    # Database
    DATABASE_URL: str = "sqlite:///pharmacy.db"
    DATABASE_PATH: str = str(Path.home() / ".pharmacy" / "pharmacy.db")
    
    # Pharmacy Settings
    PHARMACY_ID: str = "local-pharmacy"
    PHARMACY_NAME: str = "Local Pharmacy"
    
    # API Configuration
    CENTRAL_SERVER_URL: str = "http://localhost:3001"
    API_TIMEOUT: int = 30
    
    # Sync Configuration
    AUTO_SYNC_ENABLED: bool = True
    SYNC_INTERVAL: int = 5  # minutes
    SYNC_BATCH_SIZE: int = 100
    
    # Security
    JWT_ALGORITHM: str = "HS256"
    JWT_SECRET: str = "your-secret-key-change-this"
    PASSWORD_MIN_LENGTH: int = 8
    
    # UI Configuration
    THEME: str = "light"
    WINDOW_WIDTH: int = 1400
    WINDOW_HEIGHT: int = 900
    
    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FILE: str = str(Path.home() / ".pharmacy" / "app.log")
    
    # File Upload
    UPLOAD_FOLDER: str = str(Path.home() / ".pharmacy" / "uploads")
    MAX_UPLOAD_SIZE: int = 50 * 1024 * 1024  # 50MB
    ALLOWED_EXTENSIONS: set = {"json", "pdf", "txt"}
    
    # Features
    ENABLE_OFFLINE_MODE: bool = True
    ENABLE_FORM_SIGNATURES: bool = True
    ENABLE_BARCODE_SCANNING: bool = True
    
    # Super User Credentials
    SUPER_USER_EMAIL: str = "super@compharm.org"
    SUPER_USER_PASSWORD: str = "@@ComPharm22"
    SUPER_USER_NAME: str = "System Administrator"
    
    @property
    def db_path(self):
        """Get database path"""
        os.makedirs(os.path.dirname(self.DATABASE_PATH), exist_ok=True)
        return self.DATABASE_PATH
    
    @property
    def upload_path(self):
        """Get upload path"""
        os.makedirs(self.UPLOAD_FOLDER, exist_ok=True)
        return self.UPLOAD_FOLDER
    
    @property
    def log_path(self):
        """Get log path"""
        os.makedirs(os.path.dirname(self.LOG_FILE), exist_ok=True)
        return self.LOG_FILE


# Global settings instance
settings = Settings()

# Create upload folder if it doesn't exist
Path(settings.UPLOAD_FOLDER).mkdir(parents=True, exist_ok=True)
