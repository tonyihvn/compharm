"""
Admin Panel - Settings and configuration for administrators
"""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
    QFileDialog, QMessageBox, QTabWidget, QListWidget, QListWidgetItem,
    QLineEdit, QComboBox, QCheckBox, QSpinBox, QTextEdit, QGroupBox
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont
import requests
import json
import logging
from pathlib import Path
from .system_settings import SystemSettingsDialog
from api.backend_client import get_api_client, ensure_authenticated
from config.settings import settings
from datetime import datetime

logger = logging.getLogger(__name__)


class AdminPanel(QWidget):
    """Admin panel for system configuration and management"""
    
    close_requested = pyqtSignal()
    
    def __init__(self, api_url, current_user):
        super().__init__()
        self.api_url = api_url
        self.current_user = current_user
        self.auth_token = None
        self.init_ui()
    
    def get_auth_token(self):
        """Get authentication token"""
        if not self.auth_token:
            # Try to get from environment or settings
            import os
            self.auth_token = os.environ.get('AUTH_TOKEN', '')
            
            # If not available, prompt user to login or return empty
            if not self.auth_token:
                # For now, return empty - will fail gracefully
                logger.warning("No auth token available")
        return self.auth_token
    
    def set_auth_token(self, token):
        """Set authentication token"""
        self.auth_token = token
    
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
        
        # Title
        title = QLabel("System Settings")
        title_font = QFont()
        title_font.setPointSize(12)
        title_font.setBold(True)
        title.setFont(title_font)
        layout.addWidget(title)
        
        # Description
        description = QLabel(
            "Configure backend server credentials, pharmacy settings, and synchronization options.\n"
            "Click 'Advanced Settings' to open the full configuration dialog."
        )
        description.setStyleSheet("color: #666; margin: 10px 0px;")
        layout.addWidget(description)
        
        # Quick settings section
        quick_settings = QGroupBox("Quick Settings")
        quick_layout = QVBoxLayout()
        
        # Server Configuration
        server_label = QLabel("Server Configuration")
        server_label_font = QFont()
        server_label_font.setBold(True)
        server_label.setFont(server_label_font)
        quick_layout.addWidget(server_label)
        
        # Server URL
        server_url_layout = QHBoxLayout()
        server_url_layout.addWidget(QLabel("Server URL:"))
        self.server_url_input = QLineEdit()
        self.server_url_input.setText(self.api_url)
        self.server_url_input.setReadOnly(True)
        server_url_layout.addWidget(self.server_url_input)
        quick_layout.addLayout(server_url_layout)
        
        # Sync Configuration
        sync_label = QLabel("Sync Configuration")
        sync_label_font = QFont()
        sync_label_font.setBold(True)
        sync_label.setFont(sync_label_font)
        quick_layout.addWidget(sync_label)
        
        # Auto-sync enabled
        auto_sync_layout = QHBoxLayout()
        self.auto_sync_check = QCheckBox("Enable Auto-sync")
        self.auto_sync_check.setChecked(True)
        auto_sync_layout.addWidget(self.auto_sync_check)
        quick_layout.addLayout(auto_sync_layout)
        
        # Sync interval
        sync_interval_layout = QHBoxLayout()
        sync_interval_layout.addWidget(QLabel("Sync Interval (minutes):"))
        self.sync_interval_spin = QSpinBox()
        self.sync_interval_spin.setValue(5)
        self.sync_interval_spin.setMinimum(1)
        self.sync_interval_spin.setMaximum(120)
        sync_interval_layout.addWidget(self.sync_interval_spin)
        sync_interval_layout.addStretch()
        quick_layout.addLayout(sync_interval_layout)
        
        quick_settings.setLayout(quick_layout)
        layout.addWidget(quick_settings)
        
        # Advanced Settings Button
        advanced_settings_layout = QHBoxLayout()
        advanced_settings_layout.addStretch()
        
        advanced_btn = QPushButton("Advanced Settings")
        advanced_btn.setStyleSheet("""
            QPushButton {
                background-color: #2196F3;
                color: white;
                padding: 10px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #1976D2;
            }
        """)
        advanced_btn.clicked.connect(self.open_system_settings_dialog)
        advanced_settings_layout.addWidget(advanced_btn)
        
        # Save settings button
        save_btn = QPushButton("Save Quick Settings")
        save_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                padding: 10px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        save_btn.clicked.connect(self.save_settings)
        advanced_settings_layout.addWidget(save_btn)
        
        layout.addLayout(advanced_settings_layout)
        
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
            token = self.get_auth_token()
            headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
            response = requests.get(f"{self.api_url}/api/forms", headers=headers, timeout=10)
            if response.status_code == 200:
                data = response.json()
                forms = data.get("data", [])
                for form in forms:
                    form_name = form.get("form_name", form.get("name", "Unknown"))
                    form_id = form.get("id")
                    item = QListWidgetItem(form_name)
                    item.setData(Qt.ItemDataRole.UserRole, form_id)
                    self.forms_list.addItem(item)
        except Exception as e:
            logger.warning(f"Failed to load forms: {str(e)}")
            QMessageBox.warning(self, "Warning", f"Could not load forms: {str(e)}\nWorking offline")
    
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
                
                token = self.get_auth_token()
                headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
                response = requests.post(
                    f"{self.api_url}/api/forms/upload",
                    json=form_data,
                    headers=headers,
                    timeout=10
                )
                
                if response.status_code in [200, 201]:
                    QMessageBox.information(self, "Success", "Form uploaded successfully")
                    self.load_forms_list()
                else:
                    error_msg = response.json().get("message", "Unknown error")
                    QMessageBox.warning(self, "Error", f"Failed to upload form: {error_msg}")
            
            except json.JSONDecodeError:
                QMessageBox.critical(self, "Error", "Invalid JSON file format")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Upload error: {str(e)}")
    
    def edit_form(self):
        """Edit selected form"""
        current_item = self.forms_list.currentItem()
        if not current_item:
            QMessageBox.warning(self, "Selection Error", "Please select a form")
            return
        
        form_id = current_item.data(Qt.ItemDataRole.UserRole)
        form_name = current_item.text()
        
        try:
            token = self.get_auth_token()
            headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
            response = requests.get(
                f"{self.api_url}/api/forms/{form_id}",
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                form_data = data.get("data", {})
                
                # Open form editor dialog
                from .form_editor import FormEditorDialog
                editor = FormEditorDialog(self, form_data, self.api_url, token, form_id)
                if editor.exec():
                    self.load_forms_list()
            else:
                QMessageBox.warning(self, "Error", "Failed to load form")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error loading form: {str(e)}")
    
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
            token = self.get_auth_token()
            headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
            response = requests.get(
                f"{self.api_url}/api/sync/logs",
                headers=headers,
                timeout=10
            )
            if response.status_code == 200:
                data = response.json()
                logs = data.get("data", [])
                log_text = "\n".join([
                    f"[{log.get('created_at', 'N/A')}] {log.get('sync_type', 'Unknown')}: {log.get('error_message', 'Success')}"
                    for log in logs[:20]  # Show last 20 logs
                ])
                self.logs_display.setText(log_text if log_text else "No sync logs available")
                
                # Update last sync time
                if logs:
                    self.last_sync_label.setText(logs[0].get('created_at', 'Never'))
            else:
                self.logs_display.setText("No sync logs available")
        except Exception as e:
            logger.warning(f"Failed to load sync logs: {str(e)}")
            self.logs_display.setText("Sync logs unavailable - Server may be offline.\nWorking in offline mode.")
    
    def sync_now(self):
        """Trigger immediate sync with detailed report"""
        try:
            # Get the API client and ensure authentication
            api_client = get_api_client()
            if not api_client.authenticate():
                QMessageBox.warning(self, "Error", "Failed to authenticate with backend server.
Please check System Settings.")
                return
            
            # Show progress
            self.logs_display.setText("=" * 70 + "
")
            self.logs_display.append("SYNC IN PROGRESS
")
            self.logs_display.append("=" * 70 + "

")
            
            # Get configured pharmacy ID
            pharmacy_id = settings.PHARMACY_ID
            self.logs_display.append(f"[{datetime.now().strftime('%H:%M:%S')}] Starting sync...
")
            self.logs_display.append(f"Pharmacy ID: {pharmacy_id}
")
            self.logs_display.append(f"Pharmacy Name: {settings.PHARMACY_NAME}
")
            self.logs_display.append(f"Backend Server: {api_client.base_url}

")
            
            self.logs_display.append(f"Fetching clients for pharmacy: {pharmacy_id}...
")
            
            # Call the backend API with pharmacy_id filter
            clients_data = api_client.get_clients(pharmacy_id=pharmacy_id, limit=1000)
            
            if clients_data is None:
                self.logs_display.append("
✗ ERROR: Failed to connect to backend server
")
                self.logs_display.append("Troubleshooting:
")
                self.logs_display.append("  1. Verify backend server is running
")
                self.logs_display.append("  2. Check System Settings credentials
")
                self.logs_display.append("  3. Verify network connectivity
")
                QMessageBox.critical(self, "Sync Failed", "Could not connect to backend server")
                return
            
            clients = clients_data.get('clients', [])
            
            if len(clients) == 0:
                self.logs_display.append(f"
⚠ NO CLIENTS FOUND

")
                self.logs_display.append(f"Expected Pharmacy Code: {pharmacy_id}

")
                self.logs_display.append("TROUBLESHOOTING:
")
                self.logs_display.append(f"1. Verify client exists in backend with PharmacyID = '{pharmacy_id}'
")
                self.logs_display.append(f"2. Check Python app System Settings > Pharmacy ID = '{pharmacy_id}'
")
                self.logs_display.append("3. Create client in React web UI with matching PharmacyID
")
                self.logs_display.append("4. Verify backend server running: " + api_client.base_url + "
")
                self.logs_display.append("
" + "=" * 70 + "
")
                QMessageBox.warning(self, "No Clients", f"No clients found for pharmacy: {pharmacy_id}")
                return
            
            # Display synced clients
            self.logs_display.append(f"
✓ Found {len(clients)} client(s):

")
            
            for i, client_data in enumerate(clients, 1):
                name = client_data.get('name', 'N/A')
                pepfar_id = client_data.get('pepfarId', 'N/A')
                pharmacy_code = client_data.get('pharmacyCode', 'N/A')
                
                self.logs_display.append(f"  [{i}] {name} | PEPFAR: {pepfar_id} | Pharmacy: {pharmacy_code}
")
            
            # Final report
            self.logs_display.append("
" + "=" * 70 + "
")
            self.logs_display.append("SYNC REPORT
")
            self.logs_display.append("=" * 70 + "
")
            self.logs_display.append(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
")
            self.logs_display.append(f"Pharmacy: {settings.PHARMACY_NAME} ({pharmacy_id})
")
            self.logs_display.append(f"Total Clients: {len(clients)}
")
            self.logs_display.append("Status: ✓ SUCCESS
")
            self.logs_display.append("=" * 70 + "
")
            
            # Update last sync time
            self.last_sync_label.setText(f"Last sync: {datetime.now().strftime('%H:%M:%S')} ✓")
            
            # Show success message
            QMessageBox.information(
                self, 
                "Sync Successful", 
                f"Successfully synced {len(clients)} client(s) for pharmacy: {pharmacy_id}"
            )
            
        except Exception as e:
            error_msg = f"Sync error: {str(e)}"
            logger.warning(error_msg)
            self.logs_display.append(f"
✗ ERROR: {error_msg}
")
            QMessageBox.critical(self, "Sync Error", error_msg)

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
    
    def open_system_settings_dialog(self):
        """Open the advanced system settings dialog"""
        dialog = SystemSettingsDialog(self)
        dialog.exec()

    def close_panel(self):
        """Close admin panel"""
        self.close_requested.emit()
        self.close()
