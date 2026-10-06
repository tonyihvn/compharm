"""
Login Window - Initial authentication screen
"""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, 
    QPushButton, QCheckBox, QMessageBox, QComboBox
)
from PyQt6.QtCore import Qt, pyqtSignal, QTimer
from PyQt6.QtGui import QPixmap, QFont, QIcon
import requests
import json
from pathlib import Path
from utils.auth import authenticate_user, init_default_admin
import logging

logger = logging.getLogger(__name__)


class LoginWindow(QWidget):
    """Login window for user authentication"""
    
    login_successful = pyqtSignal(dict)  # user data dict
    
    def __init__(self, db_manager, settings):
        super().__init__()
        self.db_manager = db_manager
        self.settings = settings
        self.api_url = settings.CENTRAL_SERVER_URL
        self.credentials_file = Path.home() / ".pharmacy" / "credentials.json"
        self.init_ui()
        self.load_saved_credentials()
    
    def init_ui(self):
        """Initialize UI components"""
        self.setWindowTitle("Community Pharmacy App - Login")
        self.setGeometry(100, 100, 500, 400)
        
        main_layout = QVBoxLayout()
        main_layout.setSpacing(15)
        main_layout.setContentsMargins(30, 30, 30, 30)
        
        # Title
        title = QLabel("Community Pharmacy Manager")
        title_font = QFont()
        title_font.setPointSize(18)
        title_font.setBold(True)
        title.setFont(title_font)
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(title)
        
        # Subtitle
        subtitle = QLabel("Professional Pharmacy Management System")
        subtitle_font = QFont()
        subtitle_font.setPointSize(10)
        subtitle.setFont(subtitle_font)
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(subtitle)
        
        main_layout.addSpacing(20)
        
        # User type selection
        user_type_layout = QHBoxLayout()
        user_type_layout.addWidget(QLabel("Role:"))
        self.role_combo = QComboBox()
        self.role_combo.addItems(["pharmacy_staff", "admin", "facility_staff"])
        user_type_layout.addWidget(self.role_combo)
        main_layout.addLayout(user_type_layout)
        
        # Username
        username_layout = QHBoxLayout()
        username_layout.addWidget(QLabel("Username:"))
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Enter your username")
        username_layout.addWidget(self.username_input)
        main_layout.addLayout(username_layout)
        
        # Password
        password_layout = QHBoxLayout()
        password_layout.addWidget(QLabel("Password:"))
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Enter your password")
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        password_layout.addWidget(self.password_input)
        main_layout.addLayout(password_layout)
        
        # Remember me
        self.remember_me = QCheckBox("Remember me")
        main_layout.addWidget(self.remember_me)
        
        main_layout.addSpacing(10)
        
        # Login button
        login_btn = QPushButton("Login")
        login_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                padding: 10px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        login_btn.clicked.connect(self.login)
        main_layout.addWidget(login_btn)
        
        # Register link
        register_btn = QPushButton("Register Account")
        register_btn.setFlat(True)
        register_btn.setStyleSheet("color: blue; text-decoration: underline;")
        register_btn.clicked.connect(self.show_register)
        main_layout.addWidget(register_btn)
        
        main_layout.addStretch()
        
        self.setLayout(main_layout)
    
    def login(self):
        """Handle login action"""
        username = self.username_input.text().strip()
        password = self.password_input.text()
        role = self.role_combo.currentText()
        
        if not username or not password:
            QMessageBox.warning(self, "Input Error", "Please enter username and password")
            return
        
        # Try local authentication first
        session = self.db_manager.get_session()
        try:
            user_data = authenticate_user(session, username, password)
            
            if user_data:
                # Save credentials if remember me is checked
                if self.remember_me.isChecked():
                    self.save_credentials(username, password, role)
                
                # Emit login success with user data
                logger.info(f"User authenticated locally: {username}")
                self.login_successful.emit(user_data)
                return
            else:
                # Local authentication failed
                logger.info(f"Local authentication failed for user: {username}")
                QMessageBox.critical(self, "Login Failed", "Invalid username or password")
                return
                
        except Exception as e:
            logger.error(f"Local authentication error: {e}")
            QMessageBox.critical(self, "Error", f"Login error: {str(e)}")
        finally:
            session.close()
    
    def save_credentials(self, username, password, role):
        """Save credentials locally (encrypted in production)"""
        self.credentials_file.parent.mkdir(parents=True, exist_ok=True)
        credentials = {
            "username": username,
            "password": password,  # Should be encrypted in production
            "role": role
        }
        with open(self.credentials_file, "w") as f:
            json.dump(credentials, f)
    
    def load_saved_credentials(self):
        """Load previously saved credentials"""
        if self.credentials_file.exists():
            try:
                with open(self.credentials_file, "r") as f:
                    credentials = json.load(f)
                    self.username_input.setText(credentials.get("username", ""))
                    self.password_input.setText(credentials.get("password", ""))
                    role = credentials.get("role", "pharmacy_staff")
                    idx = self.role_combo.findText(role)
                    if idx >= 0:
                        self.role_combo.setCurrentIndex(idx)
                    self.remember_me.setChecked(True)
            except Exception as e:
                print(f"Error loading credentials: {e}")
    
    def show_register(self):
        """Show registration dialog"""
        QMessageBox.information(
            self,
            "Registration",
            "Please contact your administrator to register a new account."
        )
