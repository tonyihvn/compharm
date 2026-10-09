"""
Enhanced Client Details View - Full client information with forms display
"""
import logging
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QScrollArea, QGridLayout, QFrame, QMessageBox, QTabWidget,
    QTableWidget, QTableWidgetItem, QHeaderView
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont, QColor
import json
from database.models import FormSubmission

logger = logging.getLogger(__name__)


class ClientDetailsView(QWidget):
    """Enhanced view for displaying detailed client information with forms"""
    
    form_requested = pyqtSignal(dict)
    edit_requested = pyqtSignal(dict)
    close_requested = pyqtSignal()
    fill_form_requested = pyqtSignal(dict)
    
    def __init__(self, client_data, db_manager=None):
        super().__init__()
        self.client_data = client_data
        self.db_manager = db_manager
        self.form_submissions = []
        self.init_ui()
        self.load_form_submissions()
    
    def load_client(self, client_id, client_data=None):
        """Load client data and refresh UI"""
        try:
            if client_data:
                self.client_data = client_data
            else:
                # Fetch from database if not provided
                from database.models import Client
                session = self.db_manager.get_session()
                try:
                    client = session.query(Client).filter_by(id=client_id).first()
                    if client:
                        # Convert model to dict
                        self.client_data = {
                            'id': client.id,
                            'fullName': client.full_name,
                            'pepfarId': getattr(client, 'pepfar_id', 'N/A'),
                            'dateOfBirth': str(getattr(client, 'date_of_birth', 'N/A')),
                            'gender': getattr(client, 'gender', 'N/A'),
                            'phone': getattr(client, 'phone', 'N/A'),
                            'email': getattr(client, 'email', 'N/A'),
                            'address': getattr(client, 'address', 'N/A'),
                            'city': getattr(client, 'city', 'N/A'),
                            'district': getattr(client, 'district', 'N/A'),
                            'country': getattr(client, 'country', 'N/A'),
                            'weight': getattr(client, 'weight', 'N/A'),
                            'height': getattr(client, 'height', 'N/A'),
                            'status': getattr(client, 'status', 'active'),
                        }
                finally:
                    session.close()
            
            # Refresh the form submissions
            self.load_form_submissions()
        except Exception as e:
            logger.error(f"Error loading client: {e}")

    
    def init_ui(self):
        """Initialize UI components"""
        layout = QVBoxLayout()
        
        # Title with client info
        title_layout = QHBoxLayout()
        title = QLabel(f"Client Details - {self.client_data.get('fullName', 'Unknown')}")
        title_font = QFont()
        title_font.setPointSize(14)
        title_font.setBold(True)
        title.setFont(title_font)
        title_layout.addWidget(title)
        title_layout.addStretch()
        layout.addLayout(title_layout)
        
        # Tabs for different sections
        tabs = QTabWidget()
        
        # Personal Information Tab
        personal_tab = self.create_personal_info_tab()
        tabs.addTab(personal_tab, "Personal Information")
        
        # Contact Information Tab
        contact_tab = self.create_contact_info_tab()
        tabs.addTab(contact_tab, "Contact Information")
        
        # Medical History Tab
        medical_tab = self.create_medical_history_tab()
        tabs.addTab(medical_tab, "Medical History")
        
        # Additional Information Tab
        additional_tab = self.create_additional_info_tab()
        tabs.addTab(additional_tab, "Additional Information")
        
        # Form Submissions Tab
        forms_tab = self.create_form_submissions_tab()
        tabs.addTab(forms_tab, "Form Submissions")
        
        layout.addWidget(tabs)
        
        # Action buttons
        button_layout = QHBoxLayout()
        
        edit_btn = QPushButton("Edit Information")
        edit_btn.clicked.connect(self.on_edit_client)
        button_layout.addWidget(edit_btn)
        
        fill_form_btn = QPushButton("Fill Form")
        fill_form_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                padding: 8px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        fill_form_btn.clicked.connect(self.on_fill_form)
        button_layout.addWidget(fill_form_btn)
        
        sync_btn = QPushButton("Sync")
        sync_btn.clicked.connect(self.on_sync_client)
        button_layout.addWidget(sync_btn)
        
        button_layout.addStretch()
        
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.on_close)
        button_layout.addWidget(close_btn)
        
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
        self.setGeometry(100, 100, 1000, 700)
    
    def create_personal_info_tab(self):
        """Create personal information tab with scrolling"""
        widget = QWidget()
        layout = QGridLayout()
        
        row = 0
        fields = [
            ("PEPFAR ID", "pepfarId"),
            ("Full Name", "fullName"),
            ("Date of Birth", "dateOfBirth"),
            ("Gender", "gender"),
            ("Weight (kg)", "weight"),
            ("Height (cm)", "height"),
            ("BMI", "bmi"),
        ]
        
        for label_text, field_key in fields:
            label = QLabel(f"{label_text}:")
            label_font = QFont()
            label_font.setBold(True)
            label.setFont(label_font)
            
            value = QLabel(str(self.client_data.get(field_key, "N/A")))
            value.setWordWrap(True)
            
            layout.addWidget(label, row, 0)
            layout.addWidget(value, row, 1)
            row += 1
        
        layout.setRowStretch(row, 1)
        
        scroll_area = QScrollArea()
        container = QWidget()
        container.setLayout(layout)
        scroll_area.setWidget(container)
        scroll_area.setWidgetResizable(True)
        
        tab_layout = QVBoxLayout()
        tab_layout.addWidget(scroll_area)
        widget.setLayout(tab_layout)
        return widget
    
    def create_contact_info_tab(self):
        """Create contact information tab with scrolling"""
        widget = QWidget()
        layout = QGridLayout()
        
        row = 0
        fields = [
            ("Phone", "phone"),
            ("Email", "email"),
            ("Address", "address"),
            ("City", "city"),
            ("District", "district"),
            ("Country", "country"),
        ]
        
        for label_text, field_key in fields:
            label = QLabel(f"{label_text}:")
            label_font = QFont()
            label_font.setBold(True)
            label.setFont(label_font)
            
            value = QLabel(str(self.client_data.get(field_key, "N/A")))
            value.setWordWrap(True)
            
            layout.addWidget(label, row, 0)
            layout.addWidget(value, row, 1)
            row += 1
        
        layout.setRowStretch(row, 1)
        
        scroll_area = QScrollArea()
        container = QWidget()
        container.setLayout(layout)
        scroll_area.setWidget(container)
        scroll_area.setWidgetResizable(True)
        
        tab_layout = QVBoxLayout()
        tab_layout.addWidget(scroll_area)
        widget.setLayout(tab_layout)
        return widget
    
    def create_medical_history_tab(self):
        """Create medical history tab with scrolling"""
        widget = QWidget()
        layout = QGridLayout()
        
        row = 0
        fields = [
            ("HIV Status", "hivStatus"),
            ("ART Status", "artStatus"),
            ("CD4 Count", "cd4"),
            ("Viral Load", "viralLoad"),
            ("Last Visit Date", "lastVisitDate"),
        ]
        
        for label_text, field_key in fields:
            label = QLabel(f"{label_text}:")
            label_font = QFont()
            label_font.setBold(True)
            label.setFont(label_font)
            
            value_data = self.client_data.get(field_key, "N/A")
            if isinstance(value_data, (list, dict)):
                value_text = json.dumps(value_data, indent=2)
            else:
                value_text = str(value_data)
            
            value = QLabel(value_text)
            value.setWordWrap(True)
            
            layout.addWidget(label, row, 0)
            layout.addWidget(value, row, 1)
            row += 1
        
        layout.setRowStretch(row, 1)
        
        scroll_area = QScrollArea()
        container = QWidget()
        container.setLayout(layout)
        scroll_area.setWidget(container)
        scroll_area.setWidgetResizable(True)
        
        tab_layout = QVBoxLayout()
        tab_layout.addWidget(scroll_area)
        widget.setLayout(tab_layout)
        return widget
    
    def create_additional_info_tab(self):
        """Create additional information tab with scrolling"""
        widget = QWidget()
        layout = QGridLayout()
        
        row = 0
        fields = [
            ("Facility ID", "facilityId"),
            ("Status", "status"),
            ("Updated At", "updatedAt"),
        ]
        
        for label_text, field_key in fields:
            label = QLabel(f"{label_text}:")
            label_font = QFont()
            label_font.setBold(True)
            label.setFont(label_font)
            
            value = QLabel(str(self.client_data.get(field_key, "N/A")))
            value.setWordWrap(True)
            
            layout.addWidget(label, row, 0)
            layout.addWidget(value, row, 1)
            row += 1
        
        layout.setRowStretch(row, 1)
        
        scroll_area = QScrollArea()
        container = QWidget()
        container.setLayout(layout)
        scroll_area.setWidget(container)
        scroll_area.setWidgetResizable(True)
        
        tab_layout = QVBoxLayout()
        tab_layout.addWidget(scroll_area)
        widget.setLayout(tab_layout)
        return widget
    
    def create_form_submissions_tab(self):
        """Create tab showing all form submissions for this client"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # Info label
        info_label = QLabel("Form Submissions for this Client:")
        info_font = QFont()
        info_font.setBold(True)
        info_label.setFont(info_font)
        layout.addWidget(info_label)
        
        # Forms table
        self.forms_table = QTableWidget()
        self.forms_table.setColumnCount(6)
        self.forms_table.setHorizontalHeaderLabels([
            "Form Name", "Submission Date", "Status", "View", "Edit", "Delete"
        ])
        
        # Set column widths
        header = self.forms_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(5, QHeaderView.ResizeMode.ResizeToContents)
        
        self.forms_table.setAlternatingRowColors(True)
        layout.addWidget(self.forms_table)
        
        # Fill Form button
        fill_form_btn = QPushButton("Fill New Form")
        fill_form_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                padding: 8px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        fill_form_btn.clicked.connect(self.on_fill_form)
        layout.addWidget(fill_form_btn)
        
        widget.setLayout(layout)
        return widget
    
    def load_form_submissions(self):
        """Load form submissions for this client"""
        try:
            if self.db_manager is None:
                return
            
            client_id = self.client_data.get('id')
            if not client_id:
                return
            
            session = self.db_manager.get_session()
            try:
                # Query form submissions for this client with related Form data
                from database.models import Form
                submissions = session.query(FormSubmission).filter_by(
                    client_id=client_id
                ).all()
                
                self.form_submissions = []
                for sub in submissions:
                    # Get form name from related Form object
                    form_name = 'Unknown'
                    if sub.form:
                        form_name = sub.form.name
                    
                    self.form_submissions.append({
                        'id': str(sub.id),
                        'form_name': form_name,
                        'submission_date': sub.filled_at.strftime('%Y-%m-%d %H:%M') if sub.filled_at else 'N/A',
                        'status': sub.status or 'draft',
                        'form_id': sub.form_id,
                        'data': sub.data
                    })
                
                self.display_form_submissions()
                
            finally:
                session.close()
        
        except Exception as e:
            print(f"Error loading form submissions: {e}")
    
    def display_form_submissions(self):
        """Display form submissions in table"""
        self.forms_table.setRowCount(len(self.form_submissions))
        
        for row, submission in enumerate(self.form_submissions):
            # Form Name
            name_item = QTableWidgetItem(submission['form_name'])
            self.forms_table.setItem(row, 0, name_item)
            
            # Submission Date
            date_item = QTableWidgetItem(submission['submission_date'])
            self.forms_table.setItem(row, 1, date_item)
            
            # Status
            status_item = QTableWidgetItem(submission['status'])
            if submission['status'] == 'submitted':
                status_item.setForeground(QColor("green"))
            else:
                status_item.setForeground(QColor("orange"))
            self.forms_table.setItem(row, 2, status_item)
            
            # View button
            view_btn = QPushButton("View")
            view_btn.clicked.connect(lambda checked, s=submission: self.on_view_form(s))
            self.forms_table.setCellWidget(row, 3, view_btn)
            
            # Edit button
            edit_btn = QPushButton("Edit")
            edit_btn.clicked.connect(lambda checked, s=submission: self.on_edit_form(s))
            self.forms_table.setCellWidget(row, 4, edit_btn)
            
            # Delete button
            delete_btn = QPushButton("Delete")
            delete_btn.setStyleSheet("color: red;")
            delete_btn.clicked.connect(lambda checked, s=submission: self.on_delete_form(s))
            self.forms_table.setCellWidget(row, 5, delete_btn)
    
    def on_view_form(self, submission):
        """View form submission"""
        QMessageBox.information(
            self, 
            f"View Form - {submission['form_name']}", 
            f"Form data:\n{json.dumps(submission['data'], indent=2)}"
        )
    
    def on_edit_form(self, submission):
        """Edit form submission"""
        QMessageBox.information(
            self, 
            f"Edit Form - {submission['form_name']}", 
            f"Edit functionality for form {submission['id']}"
        )
    
    def on_delete_form(self, submission):
        """Delete form submission"""
        reply = QMessageBox.question(
            self,
            "Delete Form",
            f"Are you sure you want to delete this form submission?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            try:
                if self.db_manager:
                    session = self.db_manager.get_session()
                    try:
                        sub = session.query(FormSubmission).filter_by(
                            id=submission['id']
                        ).first()
                        if sub:
                            session.delete(sub)
                            session.commit()
                            self.load_form_submissions()
                            QMessageBox.information(self, "Success", "Form deleted successfully")
                    finally:
                        session.close()
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to delete form: {str(e)}")
    
    def on_fill_form(self):
        """Fill form for this client"""
        self.fill_form_requested.emit(self.client_data)
    
    def on_edit_client(self):
        """Edit client information"""
        self.edit_requested.emit(self.client_data)
    
    def on_sync_client(self):
        """Sync client data"""
        QMessageBox.information(self, "Sync", "Syncing client data...")
    
    def on_close(self):
        """Close the details view"""
        self.close_requested.emit()
        self.close()
