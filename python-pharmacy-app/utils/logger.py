"""
Centralized logging configuration
"""
import logging
import logging.handlers
import os
from config.settings import settings


def setup_logger(name: str = None, level=None) -> logging.Logger:
    """Configure and return logger"""
    
    logger = logging.getLogger(name or __name__)
    
    if logger.handlers:
        return logger
    
    # Create logs directory
    log_dir = os.path.dirname(settings.LOG_FILE)
    os.makedirs(log_dir, exist_ok=True)
    
    # Set log level
    log_level = getattr(logging, settings.LOG_LEVEL, logging.INFO)
    logger.setLevel(log_level)
    
    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # File handler with rotation
    file_handler = logging.handlers.RotatingFileHandler(
        settings.LOG_FILE,
        maxBytes=10 * 1024 * 1024,  # 10MB
        backupCount=5
    )
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    return logger


# Global logger instance
logger = setup_logger(__name__)
