"""
Community Pharmacy Application
Main entry point for the PyQt6 desktop application
"""

import sys
import logging
from pathlib import Path

from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt

from config.settings import Settings
from ui.login_window import LoginWindow
from ui.main_window import MainWindow
from database.db_manager import DatabaseManager

logger = None


def setup_logging():
    """Configure logging after creating logs directory"""
    global logger
    
    # Create logs directory if not exists
    logs_dir = Path('logs')
    logs_dir.mkdir(exist_ok=True)
    
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(logs_dir / 'pharmacy_app.log'),
            logging.StreamHandler()
        ]
    )
    
    logger = logging.getLogger(__name__)
    return logger


def main():
    """Main application entry point"""
    try:
        # Setup logging
        global logger
        logger = setup_logging()
        
        # Initialize settings
        settings = Settings()
        logger.info(f"Application initialized with settings: {settings.APP_NAME}")
        
        # Initialize database
        db_manager = DatabaseManager(settings.DATABASE_URL)
        db_manager.init_db()
        logger.info("Database initialized successfully")
        
        # Initialize default admin user if no admin exists
        from utils.auth import init_default_admin
        session = db_manager.get_session()
        try:
            init_default_admin(session)
        finally:
            session.close()
        
        # Create Qt application
        app = QApplication(sys.argv)
        app.setStyle('Fusion')
        
        # Set application properties
        app.setApplicationName(settings.APP_NAME)
        app.setApplicationVersion(settings.APP_VERSION)
        
        # Show login window first
        login_window = LoginWindow(db_manager, settings)
        
        # Store references for signal handling
        main_window_ref = [None]
        
        def on_login_success(user_data):
            """Handle successful login"""
            logger.info(f"User logged in: {user_data.get('email', 'unknown')}")
            login_window.close()
            
            # Create main window with user data
            main_window = MainWindow(db_manager, settings)
            main_window.current_user = user_data
            
            # Set auth token on admin panel if available
            if 'token' in user_data:
                main_window.admin_panel.set_auth_token(user_data['token'])
            
            main_window.show()
            
            # Setup sync worker after login
            main_window.setup_sync_worker()
            
            # Don't auto-load clients - let user click the load button
            # main_window.show_client_list()
            
            main_window_ref[0] = main_window
        
        # Connect login signal
        login_window.login_successful.connect(on_login_success)
        login_window.show()
        
        logger.info("Login window displayed")
        sys.exit(app.exec())
        
    except Exception as e:
        logger.error(f"Application failed to start: {str(e)}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
