"""

Admin Panel - Settings and configuration for administrators

"""

from PyQt6.QtWidgets import (

    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,

    QFileDialog, QMessageBox, QTabWidget, QListWidget, QListWidgetItem,

    QLineEdit, QComboBox, QCheckBox, QSpinBox, QTextEdit, QGroupBox,

    QDialog, QScrollArea, QFrame, QDateEdit, QDoubleSpinBox,

    QPlainTextEdit, QSplitter

)

from PyQt6.QtCore import Qt, pyqtSignal, QDate

from PyQt6.QtGui import QFont, QColor, QTextCursor

import requests

import json

import logging

from pathlib import Path

from .system_settings import SystemSettingsDialog
from .user_dialogs import AddUserDialog, EditUserDialog, ResetPasswordDialog
from api.backend_client import get_api_client, ensure_authenticated

from config.settings import settings

from datetime import datetime

from database.models import Client, Pharmacy, Facility



logger = logging.getLogger(__name__)





class AdminPanel(QWidget):

    """Admin panel for system configuration and management"""

    

    close_requested = pyqtSignal()

    

    def __init__(self, api_url, current_user, db_manager=None):

        super().__init__()

        self.api_url = api_url

        self.current_user = current_user

        self.db_manager = db_manager

        self.auth_token = None

        self.init_ui()

    

    def get_auth_token(self):

        """Get authentication token from stored or backend API client"""

        try:

            # First, try to use locally stored token (from login)

            if self.auth_token:

                return self.auth_token

            

            # If not stored locally, try to get from backend API client

            api_client = get_api_client()

            if api_client and api_client.authenticated and api_client.auth_token:

                self.auth_token = api_client.auth_token

                return self.auth_token

            

            # Fallback: try to re-authenticate with backend

            if api_client:

                if api_client.authenticate():

                    self.auth_token = api_client.auth_token

                    return api_client.auth_token

            

            logger.error("Unable to obtain authentication token")

            raise ValueError("Authentication token not available. Please login again.")

        except Exception as e:

            logger.error(f"Error getting auth token: {str(e)}")

            raise

    

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

        

        # Forms list and details split

        splitter = QSplitter(Qt.Orientation.Horizontal)

        

        # Left side - Forms list

        left_layout = QVBoxLayout()

        list_label = QLabel("Available Forms:")

        left_layout.addWidget(list_label)

        

        self.forms_list = QListWidget()

        self.forms_list.itemSelectionChanged.connect(self.on_form_selected)

        left_layout.addWidget(self.forms_list)

        

        left_widget = QWidget()

        left_widget.setLayout(left_layout)

        splitter.addWidget(left_widget)

        

        # Right side - Form details and buttons

        right_layout = QVBoxLayout()

        

        # Form details

        details_label = QLabel("Form Details:")

        right_layout.addWidget(details_label)

        

        self.form_details = QPlainTextEdit()

        self.form_details.setReadOnly(True)

        self.form_details.setMaximumHeight(150)

        right_layout.addWidget(self.form_details)

        

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

        

        download_btn = QPushButton("Download Form")

        download_btn.setStyleSheet("""

            QPushButton {

                background-color: #2196F3;

                color: white;

                padding: 8px;

                border-radius: 4px;

            }

        """)

        download_btn.clicked.connect(self.download_form)

        self.download_btn = download_btn

        button_layout.addWidget(download_btn)

        

        preview_btn = QPushButton("Preview")

        preview_btn.clicked.connect(self.preview_form)

        self.preview_btn = preview_btn

        button_layout.addWidget(preview_btn)

        

        edit_btn = QPushButton("Edit")

        edit_btn.clicked.connect(self.edit_form)

        self.edit_btn = edit_btn

        button_layout.addWidget(edit_btn)

        

        delete_btn = QPushButton("Delete")

        delete_btn.setStyleSheet("color: red;")

        delete_btn.clicked.connect(self.delete_form)

        self.delete_btn = delete_btn

        button_layout.addWidget(delete_btn)

        

        button_layout.addStretch()

        

        right_layout.addLayout(button_layout)

        

        right_widget = QWidget()

        right_widget.setLayout(right_layout)

        splitter.addWidget(right_widget)

        

        # Set splitter sizes

        splitter.setSizes([300, 400])

        layout.addWidget(splitter)

        

        # Load forms list

        self.load_forms_list()

        self.update_form_buttons()

        

        widget.setLayout(layout)

        return widget

    

    def on_form_selected(self):

        """Handle form selection to update details panel"""

        current_item = self.forms_list.currentItem()

        if not current_item:

            self.form_details.clear()

            self.update_form_buttons()

            return

        

        item_data = current_item.data(Qt.ItemDataRole.UserRole)

        form_data = item_data.get('form_data', {})

        

        # Display details

        details_text = f"""

Name: {form_data.get('form_name') or form_data.get('name', 'Unknown')}

Version: {form_data.get('version', '1.0')}

Form ID: {item_data.get('id')}

Status: {'Local' if item_data.get('is_local') else 'Remote'}

Description: {form_data.get('description', 'No description')}

        """.strip()

        

        self.form_details.setPlainText(details_text)

        self.update_form_buttons()

    

    def update_form_buttons(self):

        """Update button states based on form selection"""

        current_item = self.forms_list.currentItem()

        if not current_item:

            self.download_btn.setEnabled(False)

            self.preview_btn.setEnabled(False)

            self.edit_btn.setEnabled(False)

            self.delete_btn.setEnabled(False)

            return

        

        item_data = current_item.data(Qt.ItemDataRole.UserRole)

        is_local = item_data.get('is_local', False)

        is_remote = item_data.get('is_remote', False)

        

        # Download button: enabled only if remote and not local

        self.download_btn.setEnabled(is_remote and not is_local)

        

        # Other buttons work with local forms

        self.preview_btn.setEnabled(is_local)

        self.edit_btn.setEnabled(is_remote)

        self.delete_btn.setEnabled(True)

    

    def download_form(self):

        """Download form from remote server to local storage"""

        current_item = self.forms_list.currentItem()

        if not current_item:

            QMessageBox.warning(self, "Selection Error", "Please select a form to download")

            return

        

        item_data = current_item.data(Qt.ItemDataRole.UserRole)

        form_id = item_data.get('id')

        form_name = item_data.get('form_data', {}).get('form_name', 'Unknown')

        

        try:

            token = self.get_auth_token()

            headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}

            

            response = requests.get(

                f"{self.api_url}/api/forms/{form_id}",

                headers=headers,

                timeout=10

            )

            

            if response.status_code == 200:

                form_data = response.json().get('data', response.json())

                

                # Store in local database

                if self.db_manager:

                    success = self.db_manager.store_form(

                        form_id=form_id,

                        form_name=form_name,

                        form_definition=form_data,

                        version=item_data.get('form_data', {}).get('version', '1.0'),

                        description=item_data.get('form_data', {}).get('description', '')

                    )

                    

                    if success:

                        QMessageBox.information(self, "Success", f"Form '{form_name}' downloaded successfully")

                        self.load_forms_list()

                    else:

                        QMessageBox.warning(self, "Error", "Failed to store form locally")

            else:

                error_msg = response.json().get('message', 'Unknown error')

                QMessageBox.warning(self, "Error", f"Failed to download form: {error_msg}")

                

        except Exception as e:

            QMessageBox.critical(self, "Error", f"Error downloading form: {str(e)}")

    

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

        """Load list of uploaded forms from remote and local storage"""

        self.forms_list.clear()

        

        remote_forms = {}

        local_forms = {}

        

        try:

            # Load remote forms from React backend

            token = self.get_auth_token()

            headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}

            response = requests.get(f"{self.api_url}/api/forms", headers=headers, timeout=10)

            if response.status_code == 200:

                data = response.json()

                forms = data.get("data", [])

                for form in forms:

                    form_id = form.get("id") or form.get("form_uuid")

                    remote_forms[form_id] = form

                logger.info(f"Loaded {len(remote_forms)} remote forms")

        except Exception as e:

            logger.warning(f"Failed to load remote forms: {str(e)}")

        

        try:

            # Load local forms from database

            if self.db_manager:

                local_form_list = self.db_manager.get_all_forms()

                for form in local_form_list:

                    local_forms[form['uuid']] = form

                logger.info(f"Loaded {len(local_forms)} local forms")

        except Exception as e:

            logger.warning(f"Failed to load local forms: {str(e)}")

        

        # Combine and display forms

        all_form_ids = set(remote_forms.keys()) | set(local_forms.keys())

        

        for form_id in sorted(all_form_ids):

            remote_form = remote_forms.get(form_id)

            local_form = local_forms.get(form_id)

            

            # Use whichever source has the form

            form_data = remote_form or local_form or {}

            form_name = form_data.get("form_name") or form_data.get("name", "Unknown")

            version = form_data.get("version", "1.0")

            

            # Create display text with status indicators

            display_text = f"{form_name} (v{version})"

            if local_form:

                display_text += " [Local]"

            if remote_form:

                display_text += " [Remote]"

            

            item = QListWidgetItem(display_text)

            item_data = {

                'id': form_id,

                'form_data': form_data,

                'is_local': bool(local_form),

                'is_remote': bool(remote_form)

            }

            item.setData(Qt.ItemDataRole.UserRole, item_data)

            

            # Color code items

            if local_form and remote_form:

                item.setBackground(QColor("#c8e6c9"))  # Light green - synced

            elif local_form:

                item.setBackground(QColor("#fff9c4"))  # Light yellow - local only

            

            self.forms_list.addItem(item)

        

        logger.info(f"Displayed {len(all_form_ids)} forms in list")

    

    def submit_form_with_validation(self, form_id: str, fields: dict) -> tuple[bool, str]:

        """

        Submit a form with field permission validation.

        Returns (success, message)

        """

        try:

            api_client = get_api_client()

            if not api_client.authenticated:

                if not api_client.authenticate():

                    return False, "Not authenticated"

            

            # Validate fields against permissions

            user_role = self.current_user.get('role', 'pharmacy_staff') if isinstance(self.current_user, dict) else 'pharmacy_staff'

            all_valid, invalid_fields = api_client.validate_submission_fields(form_id, fields, user_role)

            

            if not all_valid:

                error_msg = "Cannot submit form. Restricted fields:\n"

                for invalid in invalid_fields:

                    error_msg += f"  • {invalid['field']}: {invalid['reason']}\n"

                logger.warning(f"Form submission validation failed: {error_msg}")

                return False, error_msg.strip()

            

            # Submit to backend

            submission_data = {

                'formId': form_id,

                'clientId': None,  # Should be set by caller

                'fields': fields

            }

            

            result = api_client.submit_form(submission_data)

            if result and result.get('submissionId'):

                logger.info(f"Form {form_id} submitted successfully: {result.get('submissionId')}")

                return True, f"Form submitted successfully (ID: {result.get('submissionId')})"

            else:

                error = result.get('message', 'Unknown error') if result else "No response"

                logger.error(f"Form submission failed: {error}")

                return False, f"Submission failed: {error}"

        except Exception as e:

            logger.error(f"Form submission error: {str(e)}")

            return False, f"Error during submission: {str(e)}"



    

    def load_users_list(self):

        """Load list of users"""

        self.users_list.clear()

        try:

            token = self.get_auth_token()

            if not token:

                logger.debug("Authentication token not available - users list will be empty in offline mode")

                return



            headers = {

                "Authorization": "Bearer " + token,

                "Content-Type": "application/json"

            }

            response = requests.get(f"{self.api_url}/api/users", headers=headers, timeout=10)

            if response.status_code == 200:

                payload = response.json()

                users = payload.get("users", payload.get("data", []))

                for user in users:

                    item = QListWidgetItem(f"{user.get('username')} ({user.get('role')})")

                    item.setData(Qt.ItemDataRole.UserRole, user.get("id"))

                    self.users_list.addItem(item)

            else:

                error_msg = response.text

                try:

                    body = response.json()

                    error_msg = body.get("message") or body.get("error") or response.text

                except Exception:

                    pass

                logger.debug(f"Failed to load users from server: {response.status_code}: {error_msg} - continuing in offline mode")

        except Exception as e:

            logger.debug(f"Error loading users on startup: {str(e)} - app will continue offline")

    

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
        
        item_data = current_item.data(Qt.ItemDataRole.UserRole)
        form_id = item_data.get('id') if isinstance(item_data, dict) else item_data
        form_name = current_item.text()
        
        try:
            token = self.get_auth_token()
            if not token:
                # Try to use local cached data if available
                if isinstance(item_data, dict) and 'form_data' in item_data:
                    editor = FormEditorWithPreviewDialog(self, item_data.get('form_data', {}), self.api_url, None, form_id)
                    if editor.exec():
                        self.load_forms_list()
                    return
                QMessageBox.warning(self, "Error", "Authentication token not available and no cached form data")
                return
            
            headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
            
            # Add retry logic for connection issues
            max_retries = 2
            form_data = None
            
            for attempt in range(max_retries):
                try:
                    response = requests.get(
                        f"{self.api_url}/api/forms/{form_id}",
                        headers=headers,
                        timeout=15
                    )
                    
                    if response.status_code == 200:
                        data = response.json()
                        form_data = data.get("data", {})
                        break
                    else:
                        if response.status_code == 404:
                            QMessageBox.warning(self, "Error", "Form not found on server")
                            return
                        else:
                            try:
                                error_msg = response.json().get("message", "Unknown error")
                            except:
                                error_msg = response.text
                            if attempt == max_retries - 1:
                                QMessageBox.warning(self, "Error", f"Failed to load form: {error_msg}")
                                return
                            
                except (ConnectionError, ConnectionResetError, requests.ConnectionError) as ce:
                    if attempt < max_retries - 1:
                        logger.warning(f"Connection error on attempt {attempt+1}, retrying...")
                        import time
                        time.sleep(1)
                        continue
                    else:
                        QMessageBox.critical(self, "Connection Error", f"Failed to connect to server: {str(ce)}")
                        return
            
            if not form_data:
                # Try to use cached form data from item
                if isinstance(item_data, dict) and 'form_data' in item_data:
                    logger.info("Using cached form data")
                    form_data = item_data.get('form_data', {})
                else:
                    QMessageBox.warning(self, "Error", "Could not load form data")
                    return
            
            # Open enhanced form editor with preview
            editor = FormEditorWithPreviewDialog(self, form_data, self.api_url, token, form_id)
            if editor.exec():
                self.load_forms_list()
                
        except Exception as e:
            logger.error(f"Error in edit_form: {str(e)}")
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

                token = self.get_auth_token()

                headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}

                response = requests.delete(f"{self.api_url}/api/forms/{form_id}", headers=headers, timeout=10)

                if response.status_code == 200:

                    QMessageBox.information(self, "Success", "Form deleted")

                    self.load_forms_list()

                else:

                    error_msg = response.json().get("message", "Unknown error")

                    QMessageBox.warning(self, "Error", f"Failed to delete form: {error_msg}")

            except Exception as e:

                QMessageBox.critical(self, "Error", f"Delete error: {str(e)}")

    

    def preview_form(self):
        """Preview selected form"""
        current_item = self.forms_list.currentItem()
        if not current_item:
            QMessageBox.warning(self, "Selection Error", "Please select a form")
            return
        
        item_data = current_item.data(Qt.ItemDataRole.UserRole)
        form_id = item_data.get('id') if isinstance(item_data, dict) else item_data
        form_name = current_item.text()
        
        try:
            token = self.get_auth_token()
            if not token:
                # Try to use local cached data if available
                if isinstance(item_data, dict) and 'form_data' in item_data:
                    preview_dialog = FormPreviewDialog(self, item_data.get('form_data', {}), form_name)
                    preview_dialog.exec()
                    return
                QMessageBox.warning(self, "Error", "Authentication token not available and no cached form data")
                return
            
            headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
            
            # Add retry logic for connection issues
            max_retries = 2
            for attempt in range(max_retries):
                try:
                    response = requests.get(
                        f"{self.api_url}/api/forms/{form_id}",
                        headers=headers,
                        timeout=15
                    )
                    
                    if response.status_code == 200:
                        data = response.json()
                        form_data = data.get("data", {})
                        
                        # Open form preview dialog
                        preview_dialog = FormPreviewDialog(self, form_data, form_name)
                        preview_dialog.exec()
                        return
                    else:
                        if response.status_code == 404:
                            QMessageBox.warning(self, "Error", "Form not found on server")
                            return
                        else:
                            try:
                                error_msg = response.json().get("message", "Unknown error")
                            except:
                                error_msg = response.text
                            QMessageBox.warning(self, "Error", f"Failed to load form: {error_msg}")
                            return
                            
                except (ConnectionError, ConnectionResetError, requests.ConnectionError) as ce:
                    if attempt < max_retries - 1:
                        logger.warning(f"Connection error on attempt {attempt+1}, retrying...")
                        import time
                        time.sleep(1)
                        continue
                    else:
                        # Try to use cached form data from item
                        if isinstance(item_data, dict) and 'form_data' in item_data:
                            logger.info("Using cached form data due to connection error")
                            preview_dialog = FormPreviewDialog(self, item_data.get('form_data', {}), form_name)
                            preview_dialog.exec()
                            return
                        QMessageBox.critical(self, "Connection Error", f"Failed to connect to server: {str(ce)}")
                        return
                        
        except Exception as e:
            logger.error(f"Error in preview_form: {str(e)}")
            QMessageBox.critical(self, "Error", f"Error loading form: {str(e)}")

    def add_user(self):
        """Add new user"""
        dialog = AddUserDialog(self)
        if dialog.exec():
            self.load_users_list()
    
    def edit_user(self):
        """Edit selected user"""
        current_item = self.users_list.currentItem()
        if not current_item:
            QMessageBox.warning(self, "Selection Error", "Please select a user to edit")
            return
        
        user_id = current_item.data(Qt.ItemDataRole.UserRole)
        dialog = EditUserDialog(self, user_id, self.api_url)
        if dialog.exec():
            self.load_users_list()
    
    def delete_user(self):
        """Delete selected user"""
        current_item = self.users_list.currentItem()
        if not current_item:
            QMessageBox.warning(self, "Selection Error", "Please select a user to delete")
            return
        
        reply = QMessageBox.question(
            self, "Delete User",
            f"Are you sure you want to delete {current_item.text()}?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            user_id = current_item.data(Qt.ItemDataRole.UserRole)
            try:
                token = self.get_auth_token()
                if not token:
                    QMessageBox.warning(self, "Error", "Authentication token not available")
                    return
                
                headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
                response = requests.delete(
                    f"{self.api_url}/api/users/{user_id}",
                    headers=headers,
                    timeout=10
                )
                
                if response.status_code == 200:
                    QMessageBox.information(self, "Success", "User deleted successfully")
                    self.load_users_list()
                else:
                    error_msg = response.json().get("message", "Unknown error")
                    QMessageBox.warning(self, "Error", f"Failed to delete user: {error_msg}")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Delete error: {str(e)}")
    
    def reset_user_password(self):
        """Reset user password"""
        current_item = self.users_list.currentItem()
        if not current_item:
            QMessageBox.warning(self, "Selection Error", "Please select a user")
            return
        
        user_id = current_item.data(Qt.ItemDataRole.UserRole)
        dialog = ResetPasswordDialog(self, user_id, self.api_url)
        if dialog.exec():
            QMessageBox.information(self, "Success", "Password reset successfully")
            self.load_users_list()

    

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

        """Trigger immediate sync with detailed report - downloads and saves clients"""

        try:

            # Get the API client and ensure authentication

            api_client = get_api_client()

            if not api_client.authenticate():

                QMessageBox.warning(self, "Error", "Failed to authenticate with backend server.\nPlease check System Settings.")

                return

            

            # Check if db_manager is available

            if not self.db_manager:

                QMessageBox.warning(self, "Error", "Database manager not available. Cannot save clients.")

                return

            

            # Show progress

            self.logs_display.setText("=" * 70 + "\n")

            self.logs_display.append("SYNC IN PROGRESS\n")

            self.logs_display.append("=" * 70 + "\n")

            

            # Get configured pharmacy ID

            pharmacy_id = settings.PHARMACY_ID

            self.logs_display.append(f"[{datetime.now().strftime('%H:%M:%S')}] Starting sync...\n")

            self.logs_display.append(f"Pharmacy ID: {pharmacy_id}\n")

            self.logs_display.append(f"Pharmacy Name: {settings.PHARMACY_NAME}\n")

            self.logs_display.append(f"Backend Server: {api_client.base_url}\n\n")

            

            self.logs_display.append(f"Fetching clients for pharmacy: {pharmacy_id}...\n")

            

            # Call the backend API with pharmacy_id filter

            clients_data = api_client.get_clients(pharmacy_id=pharmacy_id, limit=1000)

            

            if clients_data is None:

                self.logs_display.append("\n✗ ERROR: Failed to connect to backend server\n")

                self.logs_display.append("Troubleshooting:\n")

                self.logs_display.append("  1. Verify backend server is running\n")

                self.logs_display.append("  2. Check System Settings credentials\n")

                self.logs_display.append("  3. Verify network connectivity\n")

                QMessageBox.critical(self, "Sync Failed", "Could not connect to backend server")

                return

            

            clients = clients_data.get('clients', [])

            

            if len(clients) == 0:

                self.logs_display.append(f"\n⚠ NO CLIENTS FOUND\n\n")

                self.logs_display.append(f"Expected Pharmacy Code: {pharmacy_id}\n\n")

                self.logs_display.append("TROUBLESHOOTING:\n")

                self.logs_display.append(f"1. Verify client exists in backend with PharmacyID = '{pharmacy_id}'\n")

                self.logs_display.append(f"2. Check Python app System Settings > Pharmacy ID = '{pharmacy_id}'\n")

                self.logs_display.append("3. Create client in React web UI with matching PharmacyID\n")

                self.logs_display.append("4. Verify backend server running: " + api_client.base_url + "\n")

                self.logs_display.append("\n" + "=" * 70 + "\n")

                QMessageBox.warning(self, "No Clients", f"No clients found for pharmacy: {pharmacy_id}")

                return

            

            # Display synced clients and save to database

            self.logs_display.append(f"\n✓ Found {len(clients)} client(s):\n")

            self.logs_display.append("Saving to database...\n\n")

            

            session = self.db_manager.get_session()

            try:

                # Ensure pharmacy exists in database

                pharmacy = session.query(Pharmacy).filter(Pharmacy.code == pharmacy_id).first()

                if not pharmacy:

                    pharmacy = Pharmacy(

                        code=pharmacy_id,

                        name=settings.PHARMACY_NAME,

                        is_active=True,

                        api_key=settings.PHARMACY_ID

                    )

                    session.add(pharmacy)

                    session.commit()

                    self.logs_display.append(f"Created pharmacy record: {pharmacy_id}\n")

                

                # Ensure default facility exists

                facility = session.query(Facility).filter(Facility.code == "DEFAULT").first()

                if not facility:

                    facility = Facility(

                        code="DEFAULT",

                        name="Default Facility",

                        is_active=True

                    )

                    session.add(facility)

                    session.commit()

                    self.logs_display.append("Created default facility record\n")

                

                # Save each client to database

                saved_count = 0

                updated_count = 0

                error_count = 0

                

                for i, client_data in enumerate(clients, 1):

                    try:

                        pepfar_id = client_data.get('pepfarId') or client_data.get('id')

                        if not pepfar_id:

                            self.logs_display.append(f"  [{i}] ✗ Missing PEPFAR ID - skipping\n")

                            error_count += 1

                            continue

                        

                        name = client_data.get('name', client_data.get('fullName', 'Unknown'))

                        

                        # Check if client already exists

                        existing_client = session.query(Client).filter(Client.pepfar_id == pepfar_id).first()

                        

                        if existing_client:

                            # Update existing client

                            existing_client.full_name = name

                            existing_client.facility_id = "DEFAULT"

                            existing_client.pharmacy_id = pharmacy_id

                            existing_client.server_client_id = client_data.get('id')

                            existing_client.last_updated_from_server = datetime.now()

                            existing_client.status = client_data.get('status', 'active')

                            existing_client.gender = client_data.get('gender')

                            existing_client.phone_number = client_data.get('phone') or client_data.get('phoneNumber')

                            existing_client.email = client_data.get('email')

                            existing_client.address = client_data.get('address')

                            existing_client.hiv_status = client_data.get('hivStatus')

                            existing_client.art_status = client_data.get('artStatus')

                            updated_count += 1

                            self.logs_display.append(f"  [{i}] ✓ Updated: {name} | PEPFAR: {pepfar_id}\n")

                        else:

                            # Create new client

                            new_client = Client(

                                pepfar_id=pepfar_id,

                                full_name=name,

                                facility_id="DEFAULT",

                                pharmacy_id=pharmacy_id,

                                server_client_id=client_data.get('id'),

                                last_updated_from_server=datetime.now(),

                                status=client_data.get('status', 'active'),

                                gender=client_data.get('gender'),

                                phone_number=client_data.get('phone') or client_data.get('phoneNumber'),

                                email=client_data.get('email'),

                                address=client_data.get('address'),

                                hiv_status=client_data.get('hivStatus'),

                                art_status=client_data.get('artStatus'),

                                created_locally_at=datetime.now(),

                                updated_locally_at=datetime.now()

                            )

                            session.add(new_client)

                            saved_count += 1

                            self.logs_display.append(f"  [{i}] ✓ Saved: {name} | PEPFAR: {pepfar_id}\n")

                    

                    except Exception as e:

                        error_count += 1

                        self.logs_display.append(f"  [{i}] ✗ Error: {str(e)}\n")

                        logger.error(f"Error saving client: {str(e)}")

                

                # Commit all changes

                session.commit()

                

                # Final report

                self.logs_display.append("\n" + "=" * 70 + "\n")

                self.logs_display.append("SYNC REPORT\n")

                self.logs_display.append("=" * 70 + "\n")

                self.logs_display.append(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

                self.logs_display.append(f"Pharmacy: {settings.PHARMACY_NAME} ({pharmacy_id})\n")

                self.logs_display.append(f"Total Clients: {len(clients)}\n")

                self.logs_display.append(f"Saved: {saved_count} | Updated: {updated_count} | Errors: {error_count}\n")

                self.logs_display.append("Status: ✓ SUCCESS\n")

                self.logs_display.append("=" * 70 + "\n")

                self.logs_display.append("Clients are now available in Clients Management\n")

                

                # Update last sync time

                self.last_sync_label.setText(f"Last sync: {datetime.now().strftime('%H:%M:%S')} ✓")

                

                # Show success message

                QMessageBox.information(

                    self, 

                    "Sync Successful", 

                    f"Successfully synced {len(clients)} client(s)\n"

                    f"Saved: {saved_count}, Updated: {updated_count}\n"

                    f"Clients now available in Clients Management page"

                )

            

            finally:

                session.close()

            

        except Exception as e:

            error_msg = f"Sync error: {str(e)}"

            logger.error(error_msg)

            self.logs_display.append(f"\n✗ ERROR: {error_msg}\n")

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





class FormPreviewDialog(QDialog):

    """Dialog for previewing forms without editing"""

    

    def __init__(self, parent, form_data, form_name):

        super().__init__(parent)

        self.form_data = form_data

        self.form_name = form_name

        self.init_ui()

        self.setWindowTitle(f"Preview Form: {form_name}")

        self.setGeometry(100, 100, 1000, 700)

    

    def init_ui(self):

        """Initialize UI components"""

        layout = QVBoxLayout()

        

        # Title and description section

        header_layout = QVBoxLayout()

        

        title = QLabel(self.form_data.get("name", self.form_name))

        title_font = QFont()

        title_font.setPointSize(14)

        title_font.setBold(True)

        title.setFont(title_font)

        header_layout.addWidget(title)

        

        if self.form_data.get("description"):

            desc = QLabel(self.form_data["description"])

            desc.setWordWrap(True)

            desc.setStyleSheet("color: #666; margin: 5px 0px;")

            header_layout.addWidget(desc)

        

        # Form metadata

        metadata_layout = QHBoxLayout()

        

        # Version

        if self.form_data.get("version"):

            metadata_layout.addWidget(QLabel(f"Version: {self.form_data['version']}"))

        

        # Status

        status = "Published" if self.form_data.get("published", False) else "Draft"

        status_label = QLabel(f"Status: {status}")

        status_label.setStyleSheet("font-weight: bold;")

        metadata_layout.addWidget(status_label)

        

        metadata_layout.addStretch()

        header_layout.addLayout(metadata_layout)

        

        layout.addLayout(header_layout)

        

        # Separator

        separator = QFrame()

        separator.setFrameShape(QFrame.Shape.HLine)

        layout.addWidget(separator)

        

        # Scroll area for form content

        scroll = QScrollArea()

        scroll.setWidgetResizable(True)

        scroll_content = QWidget()

        form_layout = QVBoxLayout()

        

        # Display form sections and questions

        self.render_form_preview(form_layout)

        

        form_layout.addStretch()

        scroll_content.setLayout(form_layout)

        scroll.setWidget(scroll_content)

        layout.addWidget(scroll)

        

        # Close button

        button_layout = QHBoxLayout()

        button_layout.addStretch()

        close_btn = QPushButton("Close")

        close_btn.clicked.connect(self.accept)

        button_layout.addWidget(close_btn)

        layout.addLayout(button_layout)

        

        self.setLayout(layout)

    

    def render_form_preview(self, layout):

        """Render form sections and questions as read-only preview"""

        # Handle both new format (pages/sections) and old format

        pages = self.form_data.get("pages", [])

        

        if pages:

            # New format with pages

            for page in pages:

                sections = page.get("sections", [])

                for section in sections:

                    self.render_section(layout, section)

        else:

            # Fallback to direct sections

            sections = self.form_data.get("sections", [])

            for section in sections:

                self.render_section(layout, section)

    

    def render_section(self, layout, section):

        """Render a form section"""

        section_name = section.get("label") or section.get("name", "Section")

        

        # Section header

        section_label = QLabel(section_name)

        section_font = QFont()

        section_font.setPointSize(12)

        section_font.setBold(True)

        section_label.setFont(section_font)

        layout.addWidget(section_label)

        

        # Section separator

        separator = QFrame()

        separator.setFrameShape(QFrame.Shape.HLine)

        layout.addWidget(separator)

        

        # Questions/fields

        questions = section.get("questions", [])

        for question in questions:

            self.render_question(layout, question)

        

        layout.addSpacing(15)

    

    def render_question(self, layout, question):

        """Render a single question/field"""

        # Create a container for the field

        field_group = QGroupBox()

        field_layout = QVBoxLayout()

        

        label_text = question.get("label", question.get("id", "Field"))

        required = question.get("required", False)

        if required:

            label_text += " *"

        

        label = QLabel(label_text)

        label_font = QFont()

        label_font.setBold(True)

        label.setFont(label_font)

        field_layout.addWidget(label)

        

        # Field type and details

        field_type = question.get("type", "text")

        rendering = question.get("questionOptions", {}).get("rendering", field_type)

        

        type_str = f"Type: {rendering or field_type}"

        type_label = QLabel(type_str)

        type_label.setStyleSheet("color: #666; font-size: 10px;")

        field_layout.addWidget(type_label)

        

        # Field ID

        if question.get("id"):

            id_label = QLabel(f"ID: {question['id']}")

            id_label.setStyleSheet("color: #999; font-size: 9px;")

            field_layout.addWidget(id_label)

        

        # Display options if applicable

        options_list = question.get("questionOptions", {}).get("answers", [])

        if options_list:

            options_label = QLabel("Options:")

            options_label.setStyleSheet("font-weight: bold; margin-top: 5px;")

            field_layout.addWidget(options_label)

            

            for option in options_list:

                option_label = option.get("label", option.get("concept", ""))

                option_item = QLabel(f"  • {option_label}")

                field_layout.addWidget(option_item)

        

        # Display validators if present

        validators = question.get("validators", [])

        if validators:

            validators_label = QLabel("Validation:")

            validators_label.setStyleSheet("font-weight: bold; margin-top: 5px; color: #0066cc;")

            field_layout.addWidget(validators_label)

            

            for validator in validators:

                validator_type = validator.get("type", "unknown")

                message = validator.get("message", f"Validates: {validator_type}")

                validator_item = QLabel(f"  • {message}")

                validator_item.setStyleSheet("color: #0066cc; font-size: 10px;")

                field_layout.addWidget(validator_item)

        

        # Display placeholder if present

        if question.get("placeholder"):

            placeholder_label = QLabel(f"Placeholder: {question['placeholder']}")

            placeholder_label.setStyleSheet("color: #999; font-style: italic; font-size: 10px;")

            field_layout.addWidget(placeholder_label)

        

        # Display hide/show logic if present

        if question.get("hide"):

            hide_label = QLabel("Has conditional display logic")

            hide_label.setStyleSheet("color: #ff6600; font-size: 10px;")

            field_layout.addWidget(hide_label)

        

        field_group.setLayout(field_layout)

        layout.addWidget(field_group)





class FormEditorWithPreviewDialog(QDialog):

    """Dialog for editing forms with live preview"""

    

    def __init__(self, parent, form_data, api_url, token, form_id):

        super().__init__(parent)

        self.form_data = form_data

        self.api_url = api_url

        self.token = token

        self.form_id = form_id

        self.original_json = json.dumps(form_data, indent=2)

        self.init_ui()

        self.setWindowTitle(f"Edit Form: {form_data.get('name', 'Form')}")

        self.setGeometry(100, 100, 1400, 800)

    

    def init_ui(self):

        """Initialize UI with split view: JSON editor and preview"""

        layout = QVBoxLayout()

        

        # Title

        title = QLabel(f"Edit: {self.form_data.get('name', 'Form')}")

        title_font = QFont()

        title_font.setPointSize(12)

        title_font.setBold(True)

        title.setFont(title_font)

        layout.addWidget(title)

        

        # Splitter for JSON editor and preview

        splitter = QSplitter(Qt.Orientation.Horizontal)

        

        # Left side: JSON Editor

        left_widget = QWidget()

        left_layout = QVBoxLayout()

        

        editor_label = QLabel("JSON Editor")

        editor_font = QFont()

        editor_font.setBold(True)

        editor_label.setFont(editor_font)

        left_layout.addWidget(editor_label)

        

        self.json_editor = QPlainTextEdit()

        self.json_editor.setPlainText(self.original_json)

        self.json_editor.setFont(QFont("Courier", 9))

        self.json_editor.textChanged.connect(self.on_json_changed)

        left_layout.addWidget(self.json_editor)

        

        # JSON validation status

        self.json_status = QLabel("✓ Valid JSON")

        self.json_status.setStyleSheet("color: green; font-weight: bold;")

        left_layout.addWidget(self.json_status)

        

        left_widget.setLayout(left_layout)

        splitter.addWidget(left_widget)

        

        # Right side: Live Preview

        right_widget = QWidget()

        right_layout = QVBoxLayout()

        

        preview_label = QLabel("Live Preview")

        preview_font = QFont()

        preview_font.setBold(True)

        preview_label.setFont(preview_font)

        right_layout.addWidget(preview_label)

        

        self.preview_scroll = QScrollArea()

        self.preview_scroll.setWidgetResizable(True)

        self.preview_content = QWidget()

        self.preview_layout = QVBoxLayout()

        self.preview_content.setLayout(self.preview_layout)

        self.preview_scroll.setWidget(self.preview_content)

        right_layout.addWidget(self.preview_scroll)

        

        right_widget.setLayout(right_layout)

        splitter.addWidget(right_widget)

        

        # Set initial sizes

        splitter.setSizes([600, 600])

        layout.addWidget(splitter)

        

        # Action buttons

        button_layout = QHBoxLayout()

        

        save_btn = QPushButton("Save Changes")

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

        save_btn.clicked.connect(self.save_form)

        button_layout.addWidget(save_btn)

        

        reset_btn = QPushButton("Reset")

        reset_btn.clicked.connect(self.reset_json)

        button_layout.addWidget(reset_btn)

        

        button_layout.addStretch()

        

        cancel_btn = QPushButton("Cancel")

        cancel_btn.clicked.connect(self.reject)

        button_layout.addWidget(cancel_btn)

        

        layout.addLayout(button_layout)

        

        self.setLayout(layout)

        

        # Load initial preview

        self.on_json_changed()

    

    def on_json_changed(self):

        """Update preview when JSON is edited"""

        json_text = self.json_editor.toPlainText()

        

        try:

            form_data = json.loads(json_text)

            self.json_status.setText("✓ Valid JSON")

            self.json_status.setStyleSheet("color: green; font-weight: bold;")

            

            # Update preview

            self.update_preview(form_data)

        

        except json.JSONDecodeError as e:

            self.json_status.setText(f"✗ Invalid JSON: {str(e)}")

            self.json_status.setStyleSheet("color: red; font-weight: bold;")

            

            # Clear preview

            self.clear_preview()

    

    def clear_preview(self):

        """Clear the preview area"""

        while self.preview_layout.count():

            item = self.preview_layout.takeAt(0)

            if item.widget():

                item.widget().deleteLater()

        

        error_label = QLabel("Invalid JSON - Cannot preview")

        error_label.setStyleSheet("color: red; font-style: italic;")

        self.preview_layout.addWidget(error_label)

    

    def update_preview(self, form_data):

        """Update preview with current form data"""

        # Clear existing preview

        while self.preview_layout.count():

            item = self.preview_layout.takeAt(0)

            if item.widget():

                item.widget().deleteLater()

        

        # Add title

        title = QLabel(form_data.get("name", "Form"))

        title_font = QFont()

        title_font.setPointSize(12)

        title_font.setBold(True)

        title.setFont(title_font)

        self.preview_layout.addWidget(title)

        

        if form_data.get("description"):

            desc = QLabel(form_data["description"])

            desc.setWordWrap(True)

            desc.setStyleSheet("color: #666; margin: 5px 0px;")

            self.preview_layout.addWidget(desc)

        

        # Separator

        separator = QFrame()

        separator.setFrameShape(QFrame.Shape.HLine)

        self.preview_layout.addWidget(separator)

        

        # Render form preview

        pages = form_data.get("pages", [])

        if pages:

            for page in pages:

                sections = page.get("sections", [])

                for section in sections:

                    self.render_preview_section(section)

        else:

            sections = form_data.get("sections", [])

            for section in sections:

                self.render_preview_section(section)

        

        self.preview_layout.addStretch()

    

    def render_preview_section(self, section):

        """Render section in preview"""

        section_name = section.get("label") or section.get("name", "Section")

        

        section_label = QLabel(section_name)

        section_font = QFont()

        section_font.setPointSize(11)

        section_font.setBold(True)

        section_label.setFont(section_font)

        self.preview_layout.addWidget(section_label)

        

        separator = QFrame()

        separator.setFrameShape(QFrame.Shape.HLine)

        self.preview_layout.addWidget(separator)

        

        questions = section.get("questions", [])

        for question in questions:

            self.render_preview_question(question)

        

        self.preview_layout.addSpacing(10)

    

    def render_preview_question(self, question):

        """Render question in preview"""

        label_text = question.get("label", question.get("id", "Field"))

        if question.get("required"):

            label_text += " *"

        

        label = QLabel(label_text)

        label_font = QFont()

        label_font.setBold(True)

        label.setFont(label_font)

        self.preview_layout.addWidget(label)

        

        field_type = question.get("type", "text")

        rendering = question.get("questionOptions", {}).get("rendering", field_type)

        type_info = QLabel(f"Type: {rendering or field_type}")

        type_info.setStyleSheet("color: #666; font-size: 10px;")

        self.preview_layout.addWidget(type_info)

        

        # Show options if present

        options_list = question.get("questionOptions", {}).get("answers", [])

        if options_list:

            for option in options_list:

                option_text = option.get("label", option.get("concept", ""))

                option_widget = QLabel(f"  ○ {option_text}")

                self.preview_layout.addWidget(option_widget)

        

        self.preview_layout.addSpacing(5)

    

    def reset_json(self):

        """Reset JSON to original"""

        self.json_editor.setPlainText(self.original_json)

    

    def save_form(self):

        """Save form with updated JSON"""

        json_text = self.json_editor.toPlainText()

        

        try:

            form_data = json.loads(json_text)

        except json.JSONDecodeError as e:

            QMessageBox.critical(self, "Invalid JSON", f"Cannot save: {str(e)}")

            return

        

        try:

            headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}

            response = requests.put(

                f"{self.api_url}/api/forms/{self.form_id}",

                json=form_data,

                headers=headers,

                timeout=10

            )

            

            if response.status_code in [200, 201]:

                QMessageBox.information(self, "Success", "Form saved successfully")

                self.accept()

            else:

                error_msg = response.json().get("message", "Unknown error")

                QMessageBox.warning(self, "Error", f"Failed to save form: {error_msg}")

        

        except Exception as e:

            QMessageBox.critical(self, "Error", f"Save error: {str(e)}")









class FormPreviewDialog(QDialog):

    """Dialog for previewing forms without editing"""

    

    def __init__(self, parent, form_data, form_name):

        super().__init__(parent)

        self.form_data = form_data

        self.form_name = form_name

        self.init_ui()

        self.setWindowTitle(f"Preview Form: {form_name}")

        self.setGeometry(100, 100, 1000, 700)

    

    def init_ui(self):

        """Initialize UI components"""

        layout = QVBoxLayout()

        

        # Title and description section

        header_layout = QVBoxLayout()

        

        title = QLabel(self.form_data.get("name", self.form_name))

        title_font = QFont()

        title_font.setPointSize(14)

        title_font.setBold(True)

        title.setFont(title_font)

        header_layout.addWidget(title)

        

        if self.form_data.get("description"):

            desc = QLabel(self.form_data["description"])

            desc.setWordWrap(True)

            desc.setStyleSheet("color: #666; margin: 5px 0px;")

            header_layout.addWidget(desc)

        

        # Form metadata

        metadata_layout = QHBoxLayout()

        

        # Version

        if self.form_data.get("version"):

            metadata_layout.addWidget(QLabel(f"Version: {self.form_data['version']}"))

        

        # Status

        status = "Published" if self.form_data.get("published", False) else "Draft"

        status_label = QLabel(f"Status: {status}")

        status_label.setStyleSheet("font-weight: bold;")

        metadata_layout.addWidget(status_label)

        

        metadata_layout.addStretch()

        header_layout.addLayout(metadata_layout)

        

        layout.addLayout(header_layout)

        

        # Separator

        separator = QFrame()

        separator.setFrameShape(QFrame.Shape.HLine)

        layout.addWidget(separator)

        

        # Scroll area for form content

        scroll = QScrollArea()

        scroll.setWidgetResizable(True)

        scroll_content = QWidget()

        form_layout = QVBoxLayout()

        

        # Display form sections and questions

        self.render_form_preview(form_layout)

        

        form_layout.addStretch()

        scroll_content.setLayout(form_layout)

        scroll.setWidget(scroll_content)

        layout.addWidget(scroll)

        

        # Close button

        button_layout = QHBoxLayout()

        button_layout.addStretch()

        close_btn = QPushButton("Close")

        close_btn.clicked.connect(self.accept)

        button_layout.addWidget(close_btn)

        layout.addLayout(button_layout)

        

        self.setLayout(layout)

    

    def render_form_preview(self, layout):

        """Render form sections and questions as read-only preview"""

        # Handle both new format (pages/sections) and old format

        pages = self.form_data.get("pages", [])

        

        if pages:

            # New format with pages

            for page in pages:

                sections = page.get("sections", [])

                for section in sections:

                    self.render_section(layout, section)

        else:

            # Fallback to direct sections

            sections = self.form_data.get("sections", [])

            for section in sections:

                self.render_section(layout, section)

    

    def render_section(self, layout, section):

        """Render a form section"""

        section_name = section.get("label") or section.get("name", "Section")

        

        # Section header

        section_label = QLabel(section_name)

        section_font = QFont()

        section_font.setPointSize(12)

        section_font.setBold(True)

        section_label.setFont(section_font)

        layout.addWidget(section_label)

        

        # Section separator

        separator = QFrame()

        separator.setFrameShape(QFrame.Shape.HLine)

        layout.addWidget(separator)

        

        # Questions/fields

        questions = section.get("questions", [])

        for question in questions:

            self.render_question(layout, question)

        

        layout.addSpacing(15)

    

    def render_question(self, layout, question):

        """Render a single question/field"""

        # Create a container for the field

        field_group = QGroupBox()

        field_layout = QVBoxLayout()

        

        label_text = question.get("label", question.get("id", "Field"))

        required = question.get("required", False)

        if required:

            label_text += " *"

        

        label = QLabel(label_text)

        label_font = QFont()

        label_font.setBold(True)

        label.setFont(label_font)

        field_layout.addWidget(label)

        

        # Field type and details

        field_type = question.get("type", "text")

        rendering = question.get("questionOptions", {}).get("rendering", field_type)

        

        type_str = f"Type: {rendering or field_type}"

        type_label = QLabel(type_str)

        type_label.setStyleSheet("color: #666; font-size: 10px;")

        field_layout.addWidget(type_label)

        

        # Field ID

        if question.get("id"):

            id_label = QLabel(f"ID: {question['id']}")

            id_label.setStyleSheet("color: #999; font-size: 9px;")

            field_layout.addWidget(id_label)

        

        # Display options if applicable

        options_list = question.get("questionOptions", {}).get("answers", [])

        if options_list:

            options_label = QLabel("Options:")

            options_label.setStyleSheet("font-weight: bold; margin-top: 5px;")

            field_layout.addWidget(options_label)

            

            for option in options_list:

                option_label = option.get("label", option.get("concept", ""))

                option_item = QLabel(f"  • {option_label}")

                field_layout.addWidget(option_item)

        

        # Display validators if present

        validators = question.get("validators", [])

        if validators:

            validators_label = QLabel("Validation:")

            validators_label.setStyleSheet("font-weight: bold; margin-top: 5px; color: #0066cc;")

            field_layout.addWidget(validators_label)

            

            for validator in validators:

                validator_type = validator.get("type", "unknown")

                message = validator.get("message", f"Validates: {validator_type}")

                validator_item = QLabel(f"  • {message}")

                validator_item.setStyleSheet("color: #0066cc; font-size: 10px;")

                field_layout.addWidget(validator_item)

        

        # Display placeholder if present

        if question.get("placeholder"):

            placeholder_label = QLabel(f"Placeholder: {question['placeholder']}")

            placeholder_label.setStyleSheet("color: #999; font-style: italic; font-size: 10px;")

            field_layout.addWidget(placeholder_label)

        

        # Display hide/show logic if present

        if question.get("hide"):

            hide_label = QLabel("Has conditional display logic")

            hide_label.setStyleSheet("color: #ff6600; font-size: 10px;")

            field_layout.addWidget(hide_label)

        

        field_group.setLayout(field_layout)

        layout.addWidget(field_group)





class FormEditorWithPreviewDialog(QDialog):

    """Dialog for editing forms with live preview"""

    

    def __init__(self, parent, form_data, api_url, token, form_id):

        super().__init__(parent)

        self.form_data = form_data

        self.api_url = api_url

        self.token = token

        self.form_id = form_id

        self.original_json = json.dumps(form_data, indent=2)

        self.init_ui()

        self.setWindowTitle(f"Edit Form: {form_data.get('name', 'Form')}")

        self.setGeometry(100, 100, 1400, 800)

    

    def init_ui(self):

        """Initialize UI with split view: JSON editor and preview"""

        layout = QVBoxLayout()

        

        # Title

        title = QLabel(f"Edit: {self.form_data.get('name', 'Form')}")

        title_font = QFont()

        title_font.setPointSize(12)

        title_font.setBold(True)

        title.setFont(title_font)

        layout.addWidget(title)

        

        # Splitter for JSON editor and preview

        splitter = QSplitter(Qt.Orientation.Horizontal)

        

        # Left side: JSON Editor

        left_widget = QWidget()

        left_layout = QVBoxLayout()

        

        editor_label = QLabel("JSON Editor")

        editor_font = QFont()

        editor_font.setBold(True)

        editor_label.setFont(editor_font)

        left_layout.addWidget(editor_label)

        

        self.json_editor = QPlainTextEdit()

        self.json_editor.setPlainText(self.original_json)

        self.json_editor.setFont(QFont("Courier", 9))

        self.json_editor.textChanged.connect(self.on_json_changed)

        left_layout.addWidget(self.json_editor)

        

        # JSON validation status

        self.json_status = QLabel("✓ Valid JSON")

        self.json_status.setStyleSheet("color: green; font-weight: bold;")

        left_layout.addWidget(self.json_status)

        

        left_widget.setLayout(left_layout)

        splitter.addWidget(left_widget)

        

        # Right side: Live Preview

        right_widget = QWidget()

        right_layout = QVBoxLayout()

        

        preview_label = QLabel("Live Preview")

        preview_font = QFont()

        preview_font.setBold(True)

        preview_label.setFont(preview_font)

        right_layout.addWidget(preview_label)

        

        self.preview_scroll = QScrollArea()

        self.preview_scroll.setWidgetResizable(True)

        self.preview_content = QWidget()

        self.preview_layout = QVBoxLayout()

        self.preview_content.setLayout(self.preview_layout)

        self.preview_scroll.setWidget(self.preview_content)

        right_layout.addWidget(self.preview_scroll)

        

        right_widget.setLayout(right_layout)

        splitter.addWidget(right_widget)

        

        # Set initial sizes

        splitter.setSizes([600, 600])

        layout.addWidget(splitter)

        

        # Action buttons

        button_layout = QHBoxLayout()

        

        save_btn = QPushButton("Save Changes")

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

        save_btn.clicked.connect(self.save_form)

        button_layout.addWidget(save_btn)

        

        reset_btn = QPushButton("Reset")

        reset_btn.clicked.connect(self.reset_json)

        button_layout.addWidget(reset_btn)

        

        button_layout.addStretch()

        

        cancel_btn = QPushButton("Cancel")

        cancel_btn.clicked.connect(self.reject)

        button_layout.addWidget(cancel_btn)

        

        layout.addLayout(button_layout)

        

        self.setLayout(layout)

        

        # Load initial preview

        self.on_json_changed()

    

    def on_json_changed(self):

        """Update preview when JSON is edited"""

        json_text = self.json_editor.toPlainText()

        

        try:

            form_data = json.loads(json_text)

            self.json_status.setText("✓ Valid JSON")

            self.json_status.setStyleSheet("color: green; font-weight: bold;")

            

            # Update preview

            self.update_preview(form_data)

        

        except json.JSONDecodeError as e:

            self.json_status.setText(f"✗ Invalid JSON: {str(e)}")

            self.json_status.setStyleSheet("color: red; font-weight: bold;")

            

            # Clear preview

            self.clear_preview()

    

    def clear_preview(self):

        """Clear the preview area"""

        while self.preview_layout.count():

            item = self.preview_layout.takeAt(0)

            if item.widget():

                item.widget().deleteLater()

        

        error_label = QLabel("Invalid JSON - Cannot preview")

        error_label.setStyleSheet("color: red; font-style: italic;")

        self.preview_layout.addWidget(error_label)

    

    def update_preview(self, form_data):

        """Update preview with current form data"""

        # Clear existing preview

        while self.preview_layout.count():

            item = self.preview_layout.takeAt(0)

            if item.widget():

                item.widget().deleteLater()

        

        # Add title

        title = QLabel(form_data.get("name", "Form"))

        title_font = QFont()

        title_font.setPointSize(12)

        title_font.setBold(True)

        title.setFont(title_font)

        self.preview_layout.addWidget(title)

        

        if form_data.get("description"):

            desc = QLabel(form_data["description"])

            desc.setWordWrap(True)

            desc.setStyleSheet("color: #666; margin: 5px 0px;")

            self.preview_layout.addWidget(desc)

        

        # Separator

        separator = QFrame()

        separator.setFrameShape(QFrame.Shape.HLine)

        self.preview_layout.addWidget(separator)

        

        # Render form preview

        pages = form_data.get("pages", [])

        if pages:

            for page in pages:

                sections = page.get("sections", [])

                for section in sections:

                    self.render_preview_section(section)

        else:

            sections = form_data.get("sections", [])

            for section in sections:

                self.render_preview_section(section)

        

        self.preview_layout.addStretch()

    

    def render_preview_section(self, section):

        """Render section in preview"""

        section_name = section.get("label") or section.get("name", "Section")

        

        section_label = QLabel(section_name)

        section_font = QFont()

        section_font.setPointSize(11)

        section_font.setBold(True)

        section_label.setFont(section_font)

        self.preview_layout.addWidget(section_label)

        

        separator = QFrame()

        separator.setFrameShape(QFrame.Shape.HLine)

        self.preview_layout.addWidget(separator)

        

        questions = section.get("questions", [])

        for question in questions:

            self.render_preview_question(question)

        

        self.preview_layout.addSpacing(10)

    

    def render_preview_question(self, question):

        """Render question in preview"""

        label_text = question.get("label", question.get("id", "Field"))

        if question.get("required"):

            label_text += " *"

        

        label = QLabel(label_text)

        label_font = QFont()

        label_font.setBold(True)

        label.setFont(label_font)

        self.preview_layout.addWidget(label)

        

        field_type = question.get("type", "text")

        rendering = question.get("questionOptions", {}).get("rendering", field_type)

        type_info = QLabel(f"Type: {rendering or field_type}")

        type_info.setStyleSheet("color: #666; font-size: 10px;")

        self.preview_layout.addWidget(type_info)

        

        # Show options if present

        options_list = question.get("questionOptions", {}).get("answers", [])

        if options_list:

            for option in options_list:

                option_text = option.get("label", option.get("concept", ""))

                option_widget = QLabel(f"  ○ {option_text}")

                self.preview_layout.addWidget(option_widget)

        

        self.preview_layout.addSpacing(5)

    

    def reset_json(self):

        """Reset JSON to original"""

        self.json_editor.setPlainText(self.original_json)

    

    def save_form(self):

        """Save form with updated JSON"""

        json_text = self.json_editor.toPlainText()

        

        try:

            form_data = json.loads(json_text)

        except json.JSONDecodeError as e:

            QMessageBox.critical(self, "Invalid JSON", f"Cannot save: {str(e)}")

            return

        

        try:

            headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}

            response = requests.put(

                f"{self.api_url}/api/forms/{self.form_id}",

                json=form_data,

                headers=headers,

                timeout=10

            )

            

            if response.status_code in [200, 201]:

                QMessageBox.information(self, "Success", "Form saved successfully")

                self.accept()

            else:

                error_msg = response.json().get("message", "Unknown error")

                QMessageBox.warning(self, "Error", f"Failed to save form: {error_msg}")

        

        except Exception as e:

            QMessageBox.critical(self, "Error", f"Save error: {str(e)}")















