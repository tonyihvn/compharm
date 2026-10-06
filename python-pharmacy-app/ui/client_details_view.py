"""
Client Details View - Display full client information
"""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QScrollArea, QGridLayout, QFrame, QMessageBox, QTabWidget
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont
import json


class ClientDetailsView(QWidget):
    """View for displaying detailed client information"""
    
    form_requested = pyqtSignal(dict)  # Emit when form is requested
    close_requested = pyqtSignal()
    
    def __init__(self, client_data):
        super().__init__()
        self.client_data = client_data
        self.init_ui()
    
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
        
        layout.addWidget(tabs)
        
        # Action buttons
        button_layout = QHBoxLayout()
        
        edit_btn = QPushButton("Edit Information")
        edit_btn.clicked.connect(self.edit_client_info)
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
        fill_form_btn.clicked.connect(self.request_form)
        button_layout.addWidget(fill_form_btn)
        
        sync_btn = QPushButton("Sync")
        sync_btn.clicked.connect(self.sync_client)
        button_layout.addWidget(sync_btn)
        
        button_layout.addStretch()
        
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.close_details)
        button_layout.addWidget(close_btn)
        
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
        self.setGeometry(100, 100, 700, 600)
    
    def create_personal_info_tab(self):
        """Create personal information tab"""
        widget = QWidget()
        layout = QGridLayout()
        
        row = 0
        fields = [
            ("PEPFARID", "pepfarId"),
            ("Full Name", "fullName"),
            ("Date of Birth", "dob"),
            ("Gender", "gender"),
            ("Age", "age"),
        ]
        
        for label_text, field_key in fields:
            label = QLabel(f"{label_text}:")
            label_font = QFont()
            label_font.setBold(True)
            label.setFont(label_font)
            
            value = QLabel(str(self.client_data.get(field_key, "N/A")))
            
            layout.addWidget(label, row, 0)
            layout.addWidget(value, row, 1)
            row += 1
        
        layout.addWidget(QLabel(""), row, 0)  # Spacer
        layout.setRowStretch(row, 1)
        
        widget.setLayout(layout)
        return widget
    
    def create_contact_info_tab(self):
        """Create contact information tab"""
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
            
            layout.addWidget(label, row, 0)
            layout.addWidget(value, row, 1)
            row += 1
        
        layout.addWidget(QLabel(""), row, 0)  # Spacer
        layout.setRowStretch(row, 1)
        
        widget.setLayout(layout)
        return widget
    
    def create_medical_history_tab(self):
        """Create medical history tab"""
        widget = QWidget()
        layout = QGridLayout()
        
        row = 0
        fields = [
            ("HIV Status", "hivStatus"),
            ("CD4 Count", "cd4Count"),
            ("Viral Load", "viralLoad"),
            ("Current ARVs", "currentARVs"),
            ("Allergies", "allergies"),
            ("Chronic Conditions", "chronicConditions"),
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
        
        layout.addWidget(QLabel(""), row, 0)  # Spacer
        layout.setRowStretch(row, 1)
        
        widget.setLayout(layout)
        return widget
    
    def create_additional_info_tab(self):
        """Create additional information tab"""
        widget = QWidget()
        layout = QGridLayout()
        
        row = 0
        fields = [
            ("Facility", "facility"),
            ("Assigned Pharmacy", "assignedPharmacy"),
            ("Status", "status"),
            ("Last Sync", "lastSync"),
            ("Created At", "createdAt"),
            ("Updated At", "updatedAt"),
        ]
        
        for label_text, field_key in fields:
            label = QLabel(f"{label_text}:")
            label_font = QFont()
            label_font.setBold(True)
            label.setFont(label_font)
            
            value = QLabel(str(self.client_data.get(field_key, "N/A")))
            
            layout.addWidget(label, row, 0)
            layout.addWidget(value, row, 1)
            row += 1
        
        layout.addWidget(QLabel(""), row, 0)  # Spacer
        layout.setRowStretch(row, 1)
        
        widget.setLayout(layout)
        return widget
    
    def edit_client_info(self):
        """Edit client information"""
        QMessageBox.information(self, "Edit", "Edit functionality coming soon")
    
    def request_form(self):
        """Request to fill form for this client"""
        self.form_requested.emit(self.client_data)
    
    def sync_client(self):
        """Sync client data"""
        QMessageBox.information(self, "Sync", "Syncing client data...")
    
    def close_details(self):
        """Close the details view"""
        self.close_requested.emit()
        self.close()
