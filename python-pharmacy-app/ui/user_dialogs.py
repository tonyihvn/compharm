"""User Management Dialog Classes for AdminPanel"""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, 
    QComboBox, QPushButton, QMessageBox, QCheckBox
)
from PyQt6.QtCore import Qt
import requests
import logging

logger = logging.getLogger(__name__)


class AddUserDialog(QDialog):
    """Dialog for adding a new user"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.api_url = parent.api_url
        self.get_auth_token = parent.get_auth_token
        self.init_ui()
    
    def init_ui(self):
        self.setWindowTitle("Add User")
        self.setGeometry(100, 100, 400, 300)
        
        layout = QVBoxLayout()
        
        # Username
        layout.addWidget(QLabel("Username:"))
        self.username_input = QLineEdit()
        layout.addWidget(self.username_input)
        
        # Email
        layout.addWidget(QLabel("Email:"))
        self.email_input = QLineEdit()
        layout.addWidget(self.email_input)
        
        # Full Name
        layout.addWidget(QLabel("Full Name:"))
        self.fullname_input = QLineEdit()
        layout.addWidget(self.fullname_input)
        
        # Password
        layout.addWidget(QLabel("Password:"))
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        layout.addWidget(self.password_input)
        
        # Role
        layout.addWidget(QLabel("Role:"))
        self.role_combo = QComboBox()
        self.role_combo.addItems(["pharmacy_staff", "facility_officer", "admin"])
        layout.addWidget(self.role_combo)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        save_btn = QPushButton("Save")
        save_btn.clicked.connect(self.save_user)
        button_layout.addWidget(save_btn)
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)
        
        layout.addLayout(button_layout)
        self.setLayout(layout)
    
    def save_user(self):
        """Save new user to backend"""
        username = self.username_input.text().strip()
        email = self.email_input.text().strip()
        fullname = self.fullname_input.text().strip()
        password = self.password_input.text()
        role = self.role_combo.currentText()
        
        if not username or not email or not password:
            QMessageBox.warning(self, "Validation Error", "Username, email, and password are required")
            return
        
        try:
            token = self.get_auth_token()
            if not token:
                QMessageBox.warning(self, "Error", "Authentication token not available")
                return
            
            headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
            
            payload = {
                "username": username,
                "email": email,
                "full_name": fullname,
                "password": password,
                "role": role
            }
            
            response = requests.post(
                f"{self.api_url}/api/users",
                json=payload,
                headers=headers,
                timeout=10
            )
            
            if response.status_code in [200, 201]:
                QMessageBox.information(self, "Success", "User created successfully")
                self.accept()
            else:
                error_msg = response.json().get("message", "Unknown error")
                QMessageBox.warning(self, "Error", f"Failed to create user: {error_msg}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Save error: {str(e)}")


class EditUserDialog(QDialog):
    """Dialog for editing a user"""
    
    def __init__(self, parent=None, user_id=None, api_url=None):
        super().__init__(parent)
        self.user_id = user_id
        self.api_url = api_url
        self.get_auth_token = parent.get_auth_token
        self.init_ui()
        self.load_user_data()
    
    def init_ui(self):
        self.setWindowTitle("Edit User")
        self.setGeometry(100, 100, 400, 250)
        
        layout = QVBoxLayout()
        
        # Email
        layout.addWidget(QLabel("Email:"))
        self.email_input = QLineEdit()
        layout.addWidget(self.email_input)
        
        # Full Name
        layout.addWidget(QLabel("Full Name:"))
        self.fullname_input = QLineEdit()
        layout.addWidget(self.fullname_input)
        
        # Role
        layout.addWidget(QLabel("Role:"))
        self.role_combo = QComboBox()
        self.role_combo.addItems(["pharmacy_staff", "facility_officer", "admin"])
        layout.addWidget(self.role_combo)
        
        # Active status
        self.active_check = QCheckBox("Active")
        layout.addWidget(self.active_check)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        save_btn = QPushButton("Save")
        save_btn.clicked.connect(self.save_user)
        button_layout.addWidget(save_btn)
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)
        
        layout.addLayout(button_layout)
        self.setLayout(layout)
    
    def load_user_data(self):
        """Load user data from backend"""
        try:
            token = self.get_auth_token()
            if not token:
                return
            
            headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
            response = requests.get(
                f"{self.api_url}/api/users/{self.user_id}",
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                user_data = response.json().get("data", {})
                self.email_input.setText(user_data.get("email", ""))
                self.fullname_input.setText(user_data.get("full_name", ""))
                self.role_combo.setCurrentText(user_data.get("role", "pharmacy_staff"))
                self.active_check.setChecked(user_data.get("is_active", True))
        except Exception as e:
            logger.error(f"Error loading user data: {str(e)}")
    
    def save_user(self):
        """Save user changes to backend"""
        try:
            token = self.get_auth_token()
            if not token:
                QMessageBox.warning(self, "Error", "Authentication token not available")
                return
            
            headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
            
            payload = {
                "email": self.email_input.text(),
                "full_name": self.fullname_input.text(),
                "role": self.role_combo.currentText(),
                "is_active": self.active_check.isChecked()
            }
            
            response = requests.put(
                f"{self.api_url}/api/users/{self.user_id}",
                json=payload,
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                QMessageBox.information(self, "Success", "User updated successfully")
                self.accept()
            else:
                error_msg = response.json().get("message", "Unknown error")
                QMessageBox.warning(self, "Error", f"Failed to update user: {error_msg}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Save error: {str(e)}")


class ResetPasswordDialog(QDialog):
    """Dialog for resetting user password"""
    
    def __init__(self, parent=None, user_id=None, api_url=None):
        super().__init__(parent)
        self.user_id = user_id
        self.api_url = api_url
        self.get_auth_token = parent.get_auth_token
        self.init_ui()
    
    def init_ui(self):
        self.setWindowTitle("Reset Password")
        self.setGeometry(100, 100, 350, 150)
        
        layout = QVBoxLayout()
        
        # New Password
        layout.addWidget(QLabel("New Password:"))
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        layout.addWidget(self.password_input)
        
        # Confirm Password
        layout.addWidget(QLabel("Confirm Password:"))
        self.confirm_input = QLineEdit()
        self.confirm_input.setEchoMode(QLineEdit.EchoMode.Password)
        layout.addWidget(self.confirm_input)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        reset_btn = QPushButton("Reset")
        reset_btn.clicked.connect(self.reset_password)
        button_layout.addWidget(reset_btn)
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)
        
        layout.addLayout(button_layout)
        self.setLayout(layout)
    
    def reset_password(self):
        """Reset user password"""
        password = self.password_input.text()
        confirm = self.confirm_input.text()
        
        if not password:
            QMessageBox.warning(self, "Validation Error", "Password is required")
            return
        
        if password != confirm:
            QMessageBox.warning(self, "Validation Error", "Passwords do not match")
            return
        
        try:
            token = self.get_auth_token()
            if not token:
                QMessageBox.warning(self, "Error", "Authentication token not available")
                return
            
            headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
            
            payload = {"password": password}
            
            response = requests.post(
                f"{self.api_url}/api/users/{self.user_id}/reset-password",
                json=payload,
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                self.accept()
            else:
                error_msg = response.json().get("message", "Unknown error")
                QMessageBox.warning(self, "Error", f"Failed to reset password: {error_msg}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Reset error: {str(e)}")
