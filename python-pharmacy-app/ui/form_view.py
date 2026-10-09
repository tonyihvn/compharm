"""
Form View - Dynamic OpenMRS-style form display and submission
"""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QLineEdit,
    QComboBox, QCheckBox, QDateEdit, QTextEdit, QScrollArea, QMessageBox,
    QSpinBox, QDoubleSpinBox, QFileDialog, QFrame, QStackedWidget
)
from PyQt6.QtCore import Qt, pyqtSignal, QDate, QTimer
from PyQt6.QtGui import QFont, QPixmap, QIcon
import requests
import json
import logging
from pathlib import Path

logger = logging.getLogger(__name__)


class FormView(QWidget):
    """Dynamic form view for OpenMRS-style forms"""
    
    form_submitted = pyqtSignal(dict)  # Emit form data when submitted
    close_requested = pyqtSignal()
    
    def __init__(self, form_definition, client_data, api_url):
        super().__init__()
        self.form_definition = form_definition
        self.client_data = client_data
        self.api_url = api_url
        self.form_data = {}
        self.widgets_map = {}
        self.form_id = None
        self.client_id = None
        self.init_ui()
    
    def load_form(self, form_id: str, client_id: str):
        """Load a form from server by ID."""
        try:
            # Fetch form definition
            response = requests.get(
                f"{self.api_url}/api/forms/{form_id}",
                timeout=10
            )
            
            if response.status_code == 200:
                form_data = response.json().get('data', {})
                self.form_definition = form_data
                self.form_id = form_id
                self.client_id = client_id
                
                # Fetch client details
                if client_id:
                    client_response = requests.get(
                        f"{self.api_url}/api/clients/{client_id}",
                        timeout=10
                    )
                    if client_response.status_code == 200:
                        self.client_data = client_response.json().get('data', {})
                
                # Refresh UI
                self.refresh_form_ui()
            else:
                logger.error(f"Failed to fetch form: {response.status_code}")
        except Exception as e:
            logger.error(f"Error loading form: {str(e)}")
            raise
    
    def refresh_form_ui(self):
        """Refresh the form UI with current form definition and client data."""
        # Clear all existing widgets
        while self.layout().count() > 0:
            item = self.layout().takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        self.widgets_map = {}
        self.init_ui()
    
    def init_ui(self):
        """Initialize UI components"""
        layout = QVBoxLayout()
        
        # Title
        form_name = self.form_definition.get("name", "Form")
        title = QLabel(f"Form: {form_name}")
        title_font = QFont()
        title_font.setPointSize(14)
        title_font.setBold(True)
        title.setFont(title_font)
        layout.addWidget(title)
        
        # Description
        if self.form_definition.get("description"):
            desc = QLabel(self.form_definition["description"])
            desc.setWordWrap(True)
            layout.addWidget(desc)
        
        # Scroll area for form fields
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll_content = QWidget()
        form_layout = QVBoxLayout()
        
        # Build form fields dynamically
        sections = self.form_definition.get("sections", [])
        for section in sections:
            section_label = QLabel(section.get("name", ""))
            section_font = QFont()
            section_font.setPointSize(12)
            section_font.setBold(True)
            section_label.setFont(section_font)
            form_layout.addWidget(section_label)
            
            # Add separator
            separator = QFrame()
            separator.setFrameShape(QFrame.Shape.HLine)
            form_layout.addWidget(separator)
            
            # Process questions in section
            questions = section.get("questions", [])
            for question in questions:
                self.add_form_field(form_layout, question)
            
            form_layout.addSpacing(15)
        
        form_layout.addStretch()
        scroll_content.setLayout(form_layout)
        scroll.setWidget(scroll_content)
        layout.addWidget(scroll)
        
        # Action buttons
        button_layout = QHBoxLayout()
        
        save_btn = QPushButton("Save Draft")
        save_btn.setStyleSheet("""
            QPushButton {
                background-color: #2196F3;
                color: white;
                padding: 8px;
                border-radius: 4px;
            }
        """)
        save_btn.clicked.connect(self.save_draft)
        button_layout.addWidget(save_btn)
        
        submit_btn = QPushButton("Submit Form")
        submit_btn.setStyleSheet("""
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
        submit_btn.clicked.connect(self.submit_form)
        button_layout.addWidget(submit_btn)
        
        button_layout.addStretch()
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.cancel_form)
        button_layout.addWidget(cancel_btn)
        
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
        self.setGeometry(100, 100, 800, 700)
    
    def add_form_field(self, layout, question):
        """Add a form field based on question type"""
        field_id = question.get("id")
        field_type = question.get("type", "text")
        label_text = question.get("label", "")
        required = question.get("required", False)
        
        # Create label
        label = QLabel(label_text)
        if required:
            label.setText(label_text + " *")
            label_font = QFont()
            label_font.setBold(True)
            label.setFont(label_font)
        
        layout.addWidget(label)
        
        # Create appropriate widget based on type
        widget = None
        
        if field_type == "text":
            widget = QLineEdit()
            widget.setPlaceholderText(question.get("placeholder", ""))
        
        elif field_type == "textarea":
            widget = QTextEdit()
            widget.setPlaceholderText(question.get("placeholder", ""))
            widget.setMaximumHeight(100)
        
        elif field_type == "number":
            if question.get("decimal"):
                widget = QDoubleSpinBox()
                widget.setRange(-999999, 999999)
            else:
                widget = QSpinBox()
                widget.setRange(-999999, 999999)
        
        elif field_type == "date":
            widget = QDateEdit()
            widget.setDate(QDate.currentDate())
            widget.setCalendarPopup(True)
        
        elif field_type == "select":
            widget = QComboBox()
            options = question.get("options", [])
            for opt in options:
                if isinstance(opt, dict):
                    widget.addItem(opt.get("label", ""), opt.get("value", ""))
                else:
                    widget.addItem(str(opt))
        
        elif field_type == "multiselect":
            # For demo, using combobox; in production use custom widget
            widget = QComboBox()
            options = question.get("options", [])
            for opt in options:
                if isinstance(opt, dict):
                    widget.addItem(opt.get("label", ""), opt.get("value", ""))
                else:
                    widget.addItem(str(opt))
        
        elif field_type == "checkbox":
            widget = QCheckBox(question.get("label", ""))
        
        elif field_type == "file":
            widget = QPushButton("Upload File")
            widget.clicked.connect(lambda: self.upload_file(field_id))
        
        if widget:
            self.widgets_map[field_id] = {
                "widget": widget,
                "type": field_type,
                "required": required,
                "question": question
            }
            layout.addWidget(widget)
        
        layout.addSpacing(10)
    
    def upload_file(self, field_id):
        """Handle file upload"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select File",
            "",
            "All Files (*.*)"
        )
        if file_path:
            QMessageBox.information(self, "File", f"File selected: {Path(file_path).name}")
    
    def collect_form_data(self):
        """Collect all form data from widgets"""
        data = {
            "form_id": self.form_definition.get("id"),
            "client_id": self.client_data.get("id"),
            "pepfar_id": self.client_data.get("pepfarId"),
            "pharmacy_client_id": self.client_data.get("pharmacyClientId") or self.client_data.get("id"),
            "timestamp": str(QDate.currentDate()),
            "form_data": {}
        }
        
        for field_id, field_info in self.widgets_map.items():
            widget = field_info["widget"]
            field_type = field_info["type"]
            
            value = None
            if field_type == "text":
                value = widget.text()
            elif field_type == "textarea":
                value = widget.toPlainText()
            elif field_type in ["number"]:
                value = widget.value()
            elif field_type == "date":
                value = widget.date().toString(Qt.DateFormat.ISODate)
            elif field_type == "select":
                value = widget.currentData() or widget.currentText()
            elif field_type == "checkbox":
                value = widget.isChecked()
            
            if field_info["required"] and not value:
                raise ValueError(f"Required field '{field_id}' is empty")
            
            data["form_data"][field_id] = value
        
        return data
    
    def save_draft(self):
        """Save form as draft"""
        try:
            data = self.collect_form_data()
            data["status"] = "draft"
            
            # Get auth token
            import os
            token = os.environ.get('AUTH_TOKEN', '')
            headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
            
            response = requests.post(
                f"{self.api_url}/api/submissions",
                json=data,
                headers=headers,
                timeout=10
            )
            
            if response.status_code in [200, 201]:
                QMessageBox.information(self, "Success", "Form saved as draft")
            else:
                error_msg = response.json().get("message", "Failed to save draft")
                QMessageBox.warning(self, "Error", error_msg)
        
        except ValueError as ve:
            QMessageBox.warning(self, "Validation Error", str(ve))
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Save error: {str(e)}")
    
    def submit_form(self):
        """Submit the form"""
        try:
            data = self.collect_form_data()
            data["status"] = "submitted"
            
            # Get auth token
            import os
            token = os.environ.get('AUTH_TOKEN', '')
            headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
            
            response = requests.post(
                f"{self.api_url}/api/submissions",
                json=data,
                headers=headers,
                timeout=10
            )
            
            if response.status_code in [200, 201]:
                QMessageBox.information(self, "Success", "Form submitted successfully")
                self.form_submitted.emit(data)
                self.close()
            else:
                error_msg = response.json().get("message", "Submission failed")
                QMessageBox.warning(self, "Error", error_msg)
        
        except ValueError as ve:
            QMessageBox.warning(self, "Validation Error", str(ve))
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Submission error: {str(e)}")
    
    def cancel_form(self):
        """Cancel form and close"""
        reply = QMessageBox.question(
            self,
            "Confirm",
            "Are you sure you want to close this form? Unsaved changes will be lost.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            self.close_requested.emit()
            self.close()
