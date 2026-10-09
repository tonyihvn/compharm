"""Forms list view widget - Display available forms and manage submissions."""

import logging
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QListWidget,
    QListWidgetItem, QMessageBox, QScrollArea, QFrame, QSpinBox, QDialog,
    QProgressBar, QTabWidget, QLineEdit, QComboBox, QGroupBox, QCheckBox
)
from PyQt6.QtCore import Qt, pyqtSignal, QThread, QTimer, QDateTime
from PyQt6.QtGui import QFont, QIcon, QColor
from services.api_client import CentralServerClient
from config.settings import settings
import json
from datetime import datetime

logger = logging.getLogger(__name__)


class FormsListView(QWidget):
    """View for displaying available forms and selecting a client/form to work with."""
    
    form_selected = pyqtSignal(dict, dict)  # Emit form_data and client_data when a form is selected
    close_requested = pyqtSignal()
    form_download_started = pyqtSignal(str)
    form_download_completed = pyqtSignal(str, bool)
    
    def __init__(self, api_url, current_user, db_manager):
        super().__init__()
        self.api_url = api_url
        self.current_user = current_user
        self.db_manager = db_manager
        self.api_client = CentralServerClient(api_url=api_url)
        self.forms = []
        self.clients = []
        self.selected_form = None
        self.selected_client = None
        self.init_ui()
        self.load_data()
    
    def init_ui(self):
        """Initialize UI components."""
        layout = QVBoxLayout()
        
        # Title
        title = QLabel("Forms Management")
        title_font = QFont()
        title_font.setPointSize(14)
        title_font.setBold(True)
        title.setFont(title_font)
        layout.addWidget(title)
        
        # Create tabs for Forms and Submissions
        self.tabs = QTabWidget()
        
        # Forms tab (new)
        forms_tab = self.create_forms_tab()
        self.tabs.addTab(forms_tab, "Available Forms")
        
        # Forms tab
        forms_widget = self.create_forms_tab()
        self.tabs.addTab(forms_widget, "Available Forms")
        
        # Submissions tab
        submissions_widget = self.create_submissions_tab()
        self.tabs.addTab(submissions_widget, "Form Submissions")
        
        layout.addWidget(self.tabs)
        
        # Action buttons
        button_layout = QHBoxLayout()
        
        refresh_btn = QPushButton("Refresh")
        refresh_btn.clicked.connect(self.load_data)
        button_layout.addWidget(refresh_btn)
        
        button_layout.addStretch()
        
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.close_requested.emit)
        button_layout.addWidget(close_btn)
        
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
    
    def create_forms_tab(self) -> QWidget:
        """Create the forms tab."""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # Forms list label
        label = QLabel("Available Forms:")
        label_font = QFont()
        label_font.setBold(True)
        label.setFont(label_font)
        layout.addWidget(label)
        
        # Forms list widget
        self.forms_list = QListWidget()
        self.forms_list.itemSelectionChanged.connect(self.on_form_selected)
        layout.addWidget(self.forms_list)
        
        # Form details section
        self.form_details_label = QLabel("Select a form to see details")
        self.form_details_label.setWordWrap(True)
        self.form_details_label.setMaximumHeight(100)
        layout.addWidget(self.form_details_label)
        
        # Clients section
        clients_label = QLabel("Select Client to Fill Form:")
        clients_label_font = QFont()
        clients_label_font.setBold(True)
        clients_label.setFont(clients_label_font)
        layout.addWidget(clients_label)
        
        # Clients list widget
        self.clients_list = QListWidget()
        self.clients_list.itemSelectionChanged.connect(self.on_client_selected)
        layout.addWidget(self.clients_list)
        
        # Action buttons
        action_layout = QHBoxLayout()
        
        fill_form_btn = QPushButton("Fill Form")
        fill_form_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                padding: 8px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QPushButton:disabled {
                background-color: #ccc;
            }
        """)
        fill_form_btn.clicked.connect(self.fill_selected_form)
        self.fill_form_btn = fill_form_btn
        action_layout.addWidget(fill_form_btn)
        
        action_layout.addStretch()
        
        layout.addLayout(action_layout)
        
        widget.setLayout(layout)
        return widget
    
    def create_submissions_tab(self) -> QWidget:
        """Create the submissions tab."""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # Submissions list label
        label = QLabel("Recent Form Submissions:")
        label_font = QFont()
        label_font.setBold(True)
        label.setFont(label_font)
        layout.addWidget(label)
        
        # Submissions list widget
        self.submissions_list = QListWidget()
        layout.addWidget(self.submissions_list)
        
        # Submission details
        self.submission_details_label = QLabel("Select a submission to see details")
        self.submission_details_label.setWordWrap(True)
        self.submission_details_label.setMaximumHeight(100)
        layout.addWidget(self.submission_details_label)
        
        # Action buttons
        action_layout = QHBoxLayout()
        
        view_submission_btn = QPushButton("View Details")
        view_submission_btn.clicked.connect(self.view_submission_details)
        action_layout.addWidget(view_submission_btn)
        
        action_layout.addStretch()
        
        layout.addLayout(action_layout)
        
        widget.setLayout(layout)
        return widget
    
    def load_data(self):
        """Load forms and clients from server."""
        try:
            # Load forms
            self.forms = self.api_client.fetch_available_forms()
            self.refresh_forms_list()
            
            # Load clients
            self.clients = self.api_client.fetch_clients()
            self.refresh_clients_list()
            
            # Load submissions
            self.load_submissions()
            
        except Exception as e:
            logger.debug(f"Error loading data on startup: {str(e)} - app will continue offline")
    
    def refresh_forms_list(self):
        """Refresh the forms list widget."""
        self.forms_list.clear()
        
        if not self.forms:
            self.forms_list.addItem("No forms available")
            return
        
        for form in self.forms:
            form_name = form.get('form_name') or form.get('name', 'Unknown Form')
            item = QListWidgetItem(form_name)
            item.setData(Qt.ItemDataRole.UserRole, form)
            self.forms_list.addItem(item)
    
    def refresh_clients_list(self):
        """Refresh the clients list widget."""
        self.clients_list.clear()
        
        if not self.clients:
            self.clients_list.addItem("No clients available")
            return
        
        for client in self.clients:
            client_name = client.get('fullName') or client.get('name', 'Unknown Client')
            item = QListWidgetItem(client_name)
            item.setData(Qt.ItemDataRole.UserRole, client)
            self.clients_list.addItem(item)
    
    def load_submissions(self):
        """Load recent form submissions."""
        try:
            self.submissions_list.clear()
            
            response = self.api_client.session.get(
                f"{self.api_url}/api/submissions",
                params={"limit": 50, "page": 1},
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                submissions = data.get('submissions', [])
                
                if not submissions:
                    self.submissions_list.addItem("No submissions found")
                    return
                
                for submission in submissions:
                    form_name = submission.get('form_name', 'Unknown')
                    client_name = submission.get('client_name', 'Unknown')
                    status = submission.get('status', 'pending')
                    
                    display_text = f"{form_name} - {client_name} ({status})"
                    item = QListWidgetItem(display_text)
                    item.setData(Qt.ItemDataRole.UserRole, submission)
                    self.submissions_list.addItem(item)
        
        except Exception as e:
            logger.error(f"Error loading submissions: {str(e)}")
    
    def on_form_selected(self):
        """Handle form selection."""
        selected_items = self.forms_list.selectedItems()
        if not selected_items:
            return
        
        item = selected_items[0]
        self.selected_form = item.data(Qt.ItemDataRole.UserRole)
        
        # Update form details
        if self.selected_form:
            description = self.selected_form.get('description', 'No description available')
            self.form_details_label.setText(description)
            self.fill_form_btn.setEnabled(True)
        else:
            self.form_details_label.setText("Select a form to see details")
            self.fill_form_btn.setEnabled(False)
    
    def on_client_selected(self):
        """Handle client selection."""
        selected_items = self.clients_list.selectedItems()
        if not selected_items:
            return
        
        item = selected_items[0]
        self.selected_client = item.data(Qt.ItemDataRole.UserRole)
    
    def fill_selected_form(self):
        """Fill the selected form for the selected client."""
        if not self.selected_form:
            QMessageBox.warning(self, "Error", "Please select a form first")
            return
        
        if not self.selected_client:
            QMessageBox.warning(self, "Error", "Please select a client first")
            return
        
        # Emit signal to switch to form viewer
        self.form_selected.emit(self.selected_form, self.selected_client)
    
    def view_submission_details(self):
        """View details of a selected submission."""
        selected_items = self.submissions_list.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "Error", "Please select a submission first")
            return
        
        item = selected_items[0]
        submission = item.data(Qt.ItemDataRole.UserRole)
        
        if submission:
            details = f"""
Form: {submission.get('form_name', 'Unknown')}
Client: {submission.get('client_name', 'Unknown')}
Facility: {submission.get('facility_name', 'Unknown')}
Status: {submission.get('status', 'Unknown')}
Submitted By: {submission.get('submitted_by', 'Unknown')}
Submitted At: {submission.get('createdAt', 'Unknown')}
            """
            self.submission_details_label.setText(details)
