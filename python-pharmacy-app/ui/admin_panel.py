"""
Admin Panel - Settings and configuration for administrators
"""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
    QFileDialog, QMessageBox, QTabWidget, QListWidget, QListWidgetItem,
    QLineEdit, QComboBox, QCheckBox, QSpinBox, QTextEdit
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont
import requests
import json
import logging
from pathlib import Path

logger = logging.getLogger(__name__)


class AdminPanel(QWidget):
    """Admin panel for system configuration and management"""
    
    close_requested = pyqtSignal()
    
    def __init__(self, api_url, current_user):
        super().__init__()
        self.api_url = api_url
        self.current_user = current_user
        self.init_ui()
    
    def init_ui(self):
        """Initialize UI components"""
        layout = QVBoxLayout()
        
        # Title
        title = QLabel("Admin Panel")
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        title.setFont(title_font)
        layout.addWidget(title)
        
        # Tabs
        tabs = QTabWidget()
        
        # Forms Management Tab
        forms_tab = self.create_forms_management_tab()
        tabs.addTab(forms_tab, "Forms Management")
        
        # Users Management Tab
        users_tab = self.create_users_management_tab()
        tabs.addTab(users_tab, "Users Management")
        
        # System Settings Tab
        settings_tab = self.create_system_settings_tab()
        tabs.addTab(settings_tab, "System Settings")
        
        # Sync Status Tab
        sync_tab = self.create_sync_status_tab()
        tabs.addTab(sync_tab, "Sync Status")
        
        layout.addWidget(tabs)
        
        # Close button
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.close_panel)
        layout.addWidget(close_btn)
        
        self.setLayout(layout)
        self.setGeometry(50, 50, 900, 700)
    
    def create_forms_management_tab(self):
        """Create forms management tab"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # Title
        title = QLabel("Manage JSON Forms")
        title_font = QFont()
        title_font.setBold(True)
        title.setFont(title_font)
        layout.addWidget(title)
        
        # Forms list
        forms_layout = QHBoxLayout()
        self.forms_list = QListWidget()
        forms_layout.addWidget(self.forms_list)
        
        # Buttons
        button_layout = QVBoxLayout()
        
        upload_btn = QPushButton("Upload Form")
        upload_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                padding: 8px;
                border-radius: 4px;
            }
        """)
        upload_btn.clicked.connect(self.upload_form)
        button_layout.addWidget(upload_btn)
        
        edit_btn = QPushButton("Edit")
        edit_btn.clicked.connect(self.edit_form)
        button_layout.addWidget(edit_btn)
        
        delete_btn = QPushButton("Delete")
        delete_btn.setStyleSheet("color: red;")
        delete_btn.clicked.connect(self.delete_form)
        button_layout.addWidget(delete_btn)
        
        preview_btn = QPushButton("Preview")
        preview_btn.clicked.connect(self.preview_form)
        button_layout.addWidget(preview_btn)
        
        button_layout.addStretch()
        
        forms_layout.addLayout(button_layout)
        layout.addLayout(forms_layout)
        
        # Load forms list
        self.load_forms_list()
        
        widget.setLayout(layout)
        return widget
    
    def create_users_management_tab(self):
        """Create users management tab"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # Title
        title = QLabel("Manage Users")
        title_font = QFont()
        title_font.setBold(True)
        title.setFont(title_font)
        layout.addWidget(title)
        
        # Users list
        users_layout = QHBoxLayout()
        self.users_list = QListWidget()
        users_layout.addWidget(self.users_list)
        
        # Buttons
        button_layout = QVBoxLayout()
        
        add_btn = QPushButton("Add User")
        add_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                padding: 8px;
            }
        """)
        add_btn.clicked.connect(self.add_user)
        button_layout.addWidget(add_btn)
        
        edit_btn = QPushButton("Edit")
        edit_btn.clicked.connect(self.edit_user)
        button_layout.addWidget(edit_btn)
        
        delete_btn = QPushButton("Delete")
        delete_btn.setStyleSheet("color: red;")
        delete_btn.clicked.connect(self.delete_user)
        button_layout.addWidget(delete_btn)
        
        reset_btn = QPushButton("Reset Password")
        reset_btn.clicked.connect(self.reset_user_password)
        button_layout.addWidget(reset_btn)
        
        button_layout.addStretch()
        
        users_layout.addLayout(button_layout)
        layout.addLayout(users_layout)
        
        # Load users list
        self.load_users_list()
        
        widget.setLayout(layout)
        return widget
    
    def create_system_settings_tab(self):
        """Create system settings tab"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # Server Configuration
        server_label = QLabel("Server Configuration")
        server_label_font = QFont()
        server_label_font.setBold(True)
        server_label.setFont(server_label_font)
        layout.addWidget(server_label)
        
        # Server URL
        server_url_layout = QHBoxLayout()
        server_url_layout.addWidget(QLabel("Server URL:"))
        self.server_url_input = QLineEdit()
        self.server_url_input.setText(self.api_url)
        server_url_layout.addWidget(self.server_url_input)
        layout.addLayout(server_url_layout)
        
        # Sync Configuration
        sync_label = QLabel("Sync Configuration")
        sync_label_font = QFont()
        sync_label_font.setBold(True)
        sync_label.setFont(sync_label_font)
        layout.addWidget(sync_label)
        
        # Auto-sync enabled
        auto_sync_layout = QHBoxLayout()
        self.auto_sync_check = QCheckBox("Enable Auto-sync")
        self.auto_sync_check.setChecked(True)
        auto_sync_layout.addWidget(self.auto_sync_check)
        layout.addLayout(auto_sync_layout)
        
        # Sync interval
        sync_interval_layout = QHBoxLayout()
        sync_interval_layout.addWidget(QLabel("Sync Interval (minutes):"))
        self.sync_interval_spin = QSpinBox()
        self.sync_interval_spin.setValue(5)
        self.sync_interval_spin.setMinimum(1)
        self.sync_interval_spin.setMaximum(120)
        sync_interval_layout.addWidget(self.sync_interval_spin)
        sync_interval_layout.addStretch()
        layout.addLayout(sync_interval_layout)
        
        # Data Encryption
        encryption_label = QLabel("Data Security")
        encryption_label_font = QFont()
        encryption_label_font.setBold(True)
        encryption_label.setFont(encryption_label_font)
        layout.addWidget(encryption_label)
        
        self.encryption_check = QCheckBox("Enable Data Encryption")
        self.encryption_check.setChecked(False)
        layout.addWidget(self.encryption_check)
        
        layout.addSpacing(20)
        
        # Save settings button
        save_btn = QPushButton("Save Settings")
        save_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                padding: 8px;
                border-radius: 4px;
            }
        """)
        save_btn.clicked.connect(self.save_settings)
        layout.addWidget(save_btn)
        
        layout.addStretch()
        
        widget.setLayout(layout)
        return widget
    
    def create_sync_status_tab(self):
        """Create sync status tab"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # Title
        title = QLabel("Sync Status & Logs")
        title_font = QFont()
        title_font.setBold(True)
        title.setFont(title_font)
        layout.addWidget(title)
        
        # Status info
        status_layout = QHBoxLayout()
        status_layout.addWidget(QLabel("Last Sync:"))
        self.last_sync_label = QLabel("Never")
        status_layout.addWidget(self.last_sync_label)
        status_layout.addStretch()
        layout.addLayout(status_layout)
        
        # Logs display
        logs_label = QLabel("Sync Logs:")
        layout.addWidget(logs_label)
        
        self.logs_display = QTextEdit()
        self.logs_display.setReadOnly(True)
        layout.addWidget(self.logs_display)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        sync_now_btn = QPushButton("Sync Now")
        sync_now_btn.setStyleSheet("""
            QPushButton {
                background-color: #2196F3;
                color: white;
                padding: 8px;
            }
        """)
        sync_now_btn.clicked.connect(self.sync_now)
        button_layout.addWidget(sync_now_btn)
        
        clear_logs_btn = QPushButton("Clear Logs")
        clear_logs_btn.clicked.connect(self.clear_logs)
        button_layout.addWidget(clear_logs_btn)
        
        button_layout.addStretch()
        
        layout.addLayout(button_layout)
        
        # Load sync logs
        self.load_sync_logs()
        
        widget.setLayout(layout)
        return widget
    
    def load_forms_list(self):
        """Load list of uploaded forms"""
        self.forms_list.clear()
        try:
            response = requests.get(f"{self.api_url}/forms/list", timeout=10)
            if response.status_code == 200:
                forms = response.json().get("data", [])
                for form in forms:
                    item = QListWidgetItem(form.get("name", "Unknown"))
                    item.setData(Qt.ItemDataRole.UserRole, form.get("id"))
                    self.forms_list.addItem(item)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load forms: {str(e)}")
    
    def load_users_list(self):
        """Load list of users"""
        self.users_list.clear()
        try:
            response = requests.get(f"{self.api_url}/users/list", timeout=10)
            if response.status_code == 200:
                users = response.json().get("data", [])
                for user in users:
                    item = QListWidgetItem(f"{user.get('username')} ({user.get('role')})")
                    item.setData(Qt.ItemDataRole.UserRole, user.get("id"))
                    self.users_list.addItem(item)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load users: {str(e)}")
    
    def upload_form(self):
        """Upload a new JSON form"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select JSON Form",
            "",
            "JSON Files (*.json)"
        )
        
        if file_path:
            try:
                with open(file_path, "r") as f:
                    form_data = json.load(f)
                
                response = requests.post(
                    f"{self.api_url}/forms/upload",
                    json=form_data,
                    timeout=10
                )
                
                if response.status_code == 200 or response.status_code == 201:
                    QMessageBox.information(self, "Success", "Form uploaded successfully")
                    self.load_forms_list()
                else:
                    QMessageBox.warning(self, "Error", "Failed to upload form")
            
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Upload error: {str(e)}")
    
    def edit_form(self):
        """Edit selected form"""
        QMessageBox.information(self, "Edit", "Form editing coming soon")
    
    def delete_form(self):
        """Delete selected form"""
        current_item = self.forms_list.currentItem()
        if not current_item:
            QMessageBox.warning(self, "Selection Error", "Please select a form")
            return
        
        reply = QMessageBox.question(
            self,
            "Confirm Delete",
            f"Delete form '{current_item.text()}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            form_id = current_item.data(Qt.ItemDataRole.UserRole)
            try:
                response = requests.delete(f"{self.api_url}/forms/{form_id}", timeout=10)
                if response.status_code == 200:
                    QMessageBox.information(self, "Success", "Form deleted")
                    self.load_forms_list()
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Delete error: {str(e)}")
    
    def preview_form(self):
        """Preview selected form"""
        current_item = self.forms_list.currentItem()
        if not current_item:
            QMessageBox.warning(self, "Selection Error", "Please select a form")
            return
        
        QMessageBox.information(self, "Preview", "Form preview coming soon")
    
    def add_user(self):
        """Add new user"""
        QMessageBox.information(self, "Add User", "User creation coming soon")
    
    def edit_user(self):
        """Edit selected user"""
        QMessageBox.information(self, "Edit User", "User editing coming soon")
    
    def delete_user(self):
        """Delete selected user"""
        QMessageBox.information(self, "Delete User", "User deletion coming soon")
    
    def reset_user_password(self):
        """Reset user password"""
        QMessageBox.information(self, "Reset Password", "Password reset coming soon")
    
    def save_settings(self):
        """Save system settings"""
        try:
            settings = {
                "serverUrl": self.server_url_input.text(),
                "autoSync": self.auto_sync_check.isChecked(),
                "syncInterval": self.sync_interval_spin.value(),
                "encryption": self.encryption_check.isChecked()
            }
            
            response = requests.post(
                f"{self.api_url}/settings/save",
                json=settings,
                timeout=10
            )
            
            if response.status_code == 200:
                QMessageBox.information(self, "Success", "Settings saved successfully")
            else:
                QMessageBox.warning(self, "Error", "Failed to save settings")
        
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Save error: {str(e)}")
    
    def load_sync_logs(self):
        """Load sync logs"""
        try:
            response = requests.get(f"{self.api_url}/sync/logs", timeout=10)
            if response.status_code == 200:
                logs = response.json().get("data", [])
                log_text = "\n".join([f"[{log.get('timestamp')}] {log.get('message')}" for log in logs])
                self.logs_display.setText(log_text)
            else:
                self.logs_display.setText("No sync logs available")
        except Exception as e:
            logger.warning(f"Failed to load sync logs: {str(e)}")
            self.logs_display.setText("Sync logs unavailable - Server may be offline.\nWorking in offline mode.")
    
    def sync_now(self):
        """Trigger immediate sync"""
        try:
            response = requests.post(f"{self.api_url}/sync/now", timeout=30)
            if response.status_code == 200:
                QMessageBox.information(self, "Success", "Sync completed")
                self.load_sync_logs()
            else:
                QMessageBox.warning(self, "Error", "Sync failed")
        except Exception as e:
            logger.warning(f"Server unavailable - Working in offline mode: {str(e)}")
            QMessageBox.information(self, "Offline Mode", "Server is not available.\nChanges will be synced when the server becomes available.")
    
    def clear_logs(self):
        """Clear sync logs"""
        reply = QMessageBox.question(
            self,
            "Confirm",
            "Clear all logs?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            self.logs_display.clear()
    
    def refresh(self):
        """Refresh all admin panel data"""
        try:
            self.load_forms_list()
            self.load_users_list()
            # Update sync status if available
            self.last_sync_label.setText("Refreshed at " + 
                                         __import__('datetime').datetime.now().strftime('%H:%M:%S'))
        except Exception as e:
            QMessageBox.warning(self, "Refresh Error", f"Failed to refresh: {str(e)}")

    def close_panel(self):
        """Close admin panel"""
        self.close_requested.emit()
        self.close()
