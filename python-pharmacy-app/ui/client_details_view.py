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
    
    form_requested = pyqtSignal(dict)
    close_requested = pyqtSignal()
    
    def __init__(self, client_data):
        super().__init__()
        self.client_data = client_data
        self.init_ui()
    
    def init_ui(self):
        """Initialize UI components with dynamic data display"""
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
        
        # Create tabs
        tabs = QTabWidget()
        
        # All Details Tab (dynamic)
        details_tab = self.create_all_details_tab()
        tabs.addTab(details_tab, "All Details")
        
        # Filled Forms Tab
        forms_tab = self.create_filled_forms_tab()
        tabs.addTab(forms_tab, "Filled Forms")
        
        layout.addWidget(tabs)
        
        # Action buttons
        button_layout = QHBoxLayout()
        
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
        self.setGeometry(100, 100, 800, 700)
    
    def create_all_details_tab(self):
        """Create a tab showing all client details dynamically"""
        widget = QWidget()
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        
        # Create a container widget for the scroll area
        container = QWidget()
        layout = QGridLayout(container)
        
        row = 0
        
        # Display all fields from client_data dynamically
        if isinstance(self.client_data, dict):
            for key, value in self.client_data.items():
                # Format the key as a readable label
                label_text = self.format_key_as_label(key)
                label = QLabel(f"{label_text}:")
                label_font = QFont()
                label_font.setBold(True)
                label.setFont(label_font)
                
                # Format the value based on its type
                value_text = self.format_value(value)
                value_label = QLabel(value_text)
                value_label.setWordWrap(True)
                
                layout.addWidget(label, row, 0, alignment=Qt.AlignmentFlag.AlignTop)
                layout.addWidget(value_label, row, 1)
                row += 1
        
        # Add stretch at the bottom
        layout.addWidget(QLabel(""), row, 0)
        layout.setRowStretch(row, 1)
        
        scroll_area.setWidget(container)
        
        main_layout = QVBoxLayout(widget)
        main_layout.addWidget(scroll_area)
        
        return widget
    
    def create_filled_forms_tab(self):
        """Create tab for filled forms"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        forms_label = QLabel("Filled Forms for this Client:")
        forms_font = QFont()
        forms_font.setBold(True)
        forms_label.setFont(forms_font)
        layout.addWidget(forms_label)
        
        # Placeholder for filled forms list
        info_label = QLabel("No filled forms available")
        info_label.setStyleSheet("color: #999; font-style: italic;")
        layout.addWidget(info_label)
        
        layout.addStretch()
        
        widget.setLayout(layout)
        return widget
    
    def format_key_as_label(self, key):
        """Convert snake_case or camelCase key to readable label"""
        # Handle camelCase
        import re
        s1 = re.sub('(.)([A-Z][a-z]+)', r'\1 \2', key)
        result = re.sub('([a-z0-9])([A-Z])', r'\1 \2', s1)
        # Handle snake_case
        result = result.replace('_', ' ')
        # Capitalize each word
        return result.title()
    
    def format_value(self, value):
        """Format value for display"""
        if value is None:
            return "N/A"
        
        if isinstance(value, bool):
            return "Yes" if value else "No"
        
        if isinstance(value, (list, dict)):
            return json.dumps(value, indent=2)
        
        return str(value)
    
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
