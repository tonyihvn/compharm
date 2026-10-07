"""
System Settings Dialog for Python Pharmacy App
Allows users to configure backend server credentials
"""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, 
    QPushButton, QGroupBox, QMessageBox, QWidget, QSpinBox
)
from PyQt6.QtCore import Qt
from config.settings import settings
import json
import os
from pathlib import Path


class SystemSettingsDialog(QDialog):
    """Dialog for managing system settings and backend credentials"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("System Settings")
        self.setGeometry(100, 100, 500, 600)
        self.init_ui()
        self.load_settings()
    
    def init_ui(self):
        """Initialize the UI"""
        layout = QVBoxLayout()
        
        # Backend Server Settings
        server_group = QGroupBox("Backend Server Configuration")
        server_layout = QVBoxLayout()
        
        # Server URL
        url_layout = QHBoxLayout()
        url_layout.addWidget(QLabel("Server URL:"))
        self.server_url_input = QLineEdit()
        self.server_url_input.setPlaceholderText("http://localhost:3001")
        url_layout.addWidget(self.server_url_input)
        server_layout.addLayout(url_layout)
        
        # Username
        username_layout = QHBoxLayout()
        username_layout.addWidget(QLabel("Backend Email/Username:"))
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Use super@compharm.org or superadmin")
        username_layout.addWidget(self.username_input)
        server_layout.addLayout(username_layout)
        
        # Password
        password_layout = QHBoxLayout()
        password_layout.addWidget(QLabel("Password:"))
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_input.setPlaceholderText("Enter backend password")
        password_layout.addWidget(self.password_input)
        server_layout.addLayout(password_layout)
        
        # Test Connection Button
        test_btn = QPushButton("Test Connection")
        test_btn.clicked.connect(self.test_connection)
        server_layout.addWidget(test_btn)
        
        server_group.setLayout(server_layout)
        layout.addWidget(server_group)
        
        # Pharmacy Settings
        pharmacy_group = QGroupBox("Pharmacy Configuration")
        pharmacy_layout = QVBoxLayout()
        
        # Pharmacy ID
        pharmacy_id_layout = QHBoxLayout()
        pharmacy_id_layout.addWidget(QLabel("Pharmacy ID:"))
        self.pharmacy_id_input = QLineEdit()
        self.pharmacy_id_input.setPlaceholderText("e.g., PHARM-IKOYI-001")
        pharmacy_id_layout.addWidget(self.pharmacy_id_input)
        pharmacy_layout.addLayout(pharmacy_id_layout)
        
        # Pharmacy Name
        pharmacy_name_layout = QHBoxLayout()
        pharmacy_name_layout.addWidget(QLabel("Pharmacy Name:"))
        self.pharmacy_name_input = QLineEdit()
        self.pharmacy_name_input.setPlaceholderText("e.g., Ikoyi Pharmacy")
        pharmacy_name_layout.addWidget(self.pharmacy_name_input)
        pharmacy_layout.addLayout(pharmacy_name_layout)
        
        pharmacy_group.setLayout(pharmacy_layout)
        layout.addWidget(pharmacy_group)
        
        # Sync Settings
        sync_group = QGroupBox("Synchronization Settings")
        sync_layout = QVBoxLayout()
        
        # Auto Sync
        auto_sync_layout = QHBoxLayout()
        auto_sync_layout.addWidget(QLabel("Auto Sync Interval (minutes):"))
        self.sync_interval_spin = QSpinBox()
        self.sync_interval_spin.setMinimum(1)
        self.sync_interval_spin.setMaximum(1440)
        self.sync_interval_spin.setValue(settings.SYNC_INTERVAL)
        auto_sync_layout.addWidget(self.sync_interval_spin)
        sync_layout.addLayout(auto_sync_layout)
        
        # Batch Size
        batch_layout = QHBoxLayout()
        batch_layout.addWidget(QLabel("Sync Batch Size:"))
        self.batch_size_spin = QSpinBox()
        self.batch_size_spin.setMinimum(10)
        self.batch_size_spin.setMaximum(1000)
        self.batch_size_spin.setValue(settings.SYNC_BATCH_SIZE)
        batch_layout.addWidget(self.batch_size_spin)
        sync_layout.addLayout(batch_layout)
        
        sync_group.setLayout(sync_layout)
        layout.addWidget(sync_group)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        save_btn = QPushButton("Save Settings")
        save_btn.setStyleSheet("background-color: #27ae60; color: white; padding: 8px; border-radius: 4px;")
        save_btn.clicked.connect(self.save_settings)
        button_layout.addWidget(save_btn)
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.setStyleSheet("background-color: #95a5a6; color: white; padding: 8px; border-radius: 4px;")
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)
        
        reset_btn = QPushButton("Reset to Defaults")
        reset_btn.setStyleSheet("background-color: #e74c3c; color: white; padding: 8px; border-radius: 4px;")
        reset_btn.clicked.connect(self.reset_to_defaults)
        button_layout.addWidget(reset_btn)
        
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
    
    def load_settings(self):
        """Load current settings into the form"""
        self.server_url_input.setText(settings.CENTRAL_SERVER_URL)
        self.username_input.setText(settings.BACKEND_USERNAME)
        self.password_input.setText(settings.BACKEND_PASSWORD)
        self.pharmacy_id_input.setText(settings.PHARMACY_ID)
        self.pharmacy_name_input.setText(settings.PHARMACY_NAME)
        self.sync_interval_spin.setValue(settings.SYNC_INTERVAL)
        self.batch_size_spin.setValue(settings.SYNC_BATCH_SIZE)
    
    def save_settings(self):
        """Save settings to configuration"""
        try:
            # Update settings object
            settings.CENTRAL_SERVER_URL = self.server_url_input.text()
            settings.BACKEND_USERNAME = self.username_input.text()
            settings.BACKEND_PASSWORD = self.password_input.text()
            settings.PHARMACY_ID = self.pharmacy_id_input.text()
            settings.PHARMACY_NAME = self.pharmacy_name_input.text()
            settings.SYNC_INTERVAL = self.sync_interval_spin.value()
            settings.SYNC_BATCH_SIZE = self.batch_size_spin.value()
            
            # Save to env file
            self.save_to_env_file()
            
            QMessageBox.information(
                self,
                "Success",
                "Settings saved successfully!\n\nChanges will take effect after restart."
            )
            self.accept()
        except Exception as e:
            QMessageBox.critical(
                self,
                "Error",
                f"Error saving settings: {str(e)}"
            )
    
    def save_to_env_file(self):
        """Save settings to .env file"""
        env_file = Path.cwd() / ".env"
        
        env_content = f"""# Application Settings
CENTRAL_SERVER_URL={settings.CENTRAL_SERVER_URL}
BACKEND_USERNAME={settings.BACKEND_USERNAME}
BACKEND_PASSWORD={settings.BACKEND_PASSWORD}
PHARMACY_ID={settings.PHARMACY_ID}
PHARMACY_NAME={settings.PHARMACY_NAME}
SYNC_INTERVAL={settings.SYNC_INTERVAL}
SYNC_BATCH_SIZE={settings.SYNC_BATCH_SIZE}
AUTO_SYNC_ENABLED=True
THEME=light
DEBUG=False
"""
        
        with open(env_file, 'w') as f:
            f.write(env_content)
    
    def reset_to_defaults(self):
        """Reset settings to default values"""
        reply = QMessageBox.warning(
            self,
            "Confirm Reset",
            "Are you sure you want to reset all settings to defaults?\nThis cannot be undone.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            self.server_url_input.setText("http://localhost:3001")
            self.username_input.setText("")
            self.password_input.setText("")
            self.pharmacy_id_input.setText("local-pharmacy")
            self.pharmacy_name_input.setText("Local Pharmacy")
            self.sync_interval_spin.setValue(5)
            self.batch_size_spin.setValue(100)
    
    def test_connection(self):
        """Test connection to backend server"""
        import requests
        
        server_url = self.server_url_input.text().strip()
        username = self.username_input.text().strip()
        password = self.password_input.text().strip()
        
        if not all([server_url, username, password]):
            QMessageBox.warning(
                self,
                "Missing Fields",
                "Please fill in all backend connection fields."
            )
            return
        
        try:
            # Test login
            response = requests.post(
                f"{server_url}/api/auth/login",
                json={"username": username, "password": password},
                timeout=5
            )
            
            if response.status_code == 200:
                data = response.json()
                QMessageBox.information(
                    self,
                    "Connection Success",
                    f"Successfully connected to backend server!\n\n"
                    f"User: {data.get('user', {}).get('email', 'Unknown')}\n"
                    f"Role: {data.get('user', {}).get('role', 'Unknown')}"
                )
            else:
                error_msg = response.json().get('message', 'Unknown error')
                QMessageBox.critical(
                    self,
                    "Authentication Failed",
                    f"Failed to authenticate with backend server.\n\n{error_msg}"
                )
        except requests.exceptions.ConnectionError:
            QMessageBox.critical(
                self,
                "Connection Error",
                f"Cannot connect to backend server at:\n{server_url}\n\n"
                f"Please check the server URL and ensure the server is running."
            )
        except requests.exceptions.Timeout:
            QMessageBox.critical(
                self,
                "Connection Timeout",
                f"Connection to backend server timed out.\n\n"
                f"Please check your network connection."
            )
        except Exception as e:
            QMessageBox.critical(
                self,
                "Error",
                f"Error testing connection: {str(e)}"
            )


if __name__ == "__main__":
    # Test the dialog
    from PyQt6.QtWidgets import QApplication
    import sys
    
    app = QApplication(sys.argv)
    dialog = SystemSettingsDialog()
    dialog.show()
    sys.exit(app.exec())
