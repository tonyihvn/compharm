"""
Form Editor - Edit and modify form definitions
"""
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QLineEdit,
    QTextEdit, QMessageBox, QTableWidget, QTableWidgetItem, QComboBox,
    QSpinBox, QCheckBox, QHeaderView
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
import requests
import json
import logging

logger = logging.getLogger(__name__)


class FormEditorDialog(QDialog):
    """Dialog for editing form definitions"""
    
    def __init__(self, parent, form_data, api_url, token, form_id):
        super().__init__(parent)
        self.form_data = form_data
        self.api_url = api_url
        self.token = token
        self.form_id = form_id
        self.init_ui()
        self.setWindowTitle(f"Edit Form: {form_data.get('form_name', 'Form')}")
        self.setGeometry(100, 100, 900, 600)
    
    def init_ui(self):
        """Initialize UI components"""
        layout = QVBoxLayout()
        
        # Form name
        name_layout = QHBoxLayout()
        name_layout.addWidget(QLabel("Form Name:"))
        self.name_input = QLineEdit()
        self.name_input.setText(self.form_data.get("form_name", ""))
        name_layout.addWidget(self.name_input)
        layout.addLayout(name_layout)
        
        # Form description
        desc_layout = QHBoxLayout()
        desc_layout.addWidget(QLabel("Description:"))
        self.desc_input = QTextEdit()
        self.desc_input.setText(self.form_data.get("description", ""))
        self.desc_input.setMaximumHeight(80)
        desc_layout.addWidget(self.desc_input)
        layout.addLayout(desc_layout)
        
        # Form fields section
        fields_label = QLabel("Form Fields")
        fields_font = QFont()
        fields_font.setBold(True)
        fields_label.setFont(fields_font)
        layout.addWidget(fields_label)
        
        # Fields table
        self.fields_table = QTableWidget()
        self.fields_table.setColumnCount(4)
        self.fields_table.setHorizontalHeaderLabels(["Field Name", "Type", "Required", "Actions"])
        self.fields_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        
        # Load fields from form schema
        form_schema = self.form_data.get("form_schema", {})
        if isinstance(form_schema, str):
            try:
                form_schema = json.loads(form_schema)
            except:
                form_schema = {}
        
        sections = form_schema.get("sections", [])
        row = 0
        for section in sections:
            fields = section.get("fields", [])
            for field in fields:
                self.fields_table.insertRow(row)
                
                # Field name
                name_item = QTableWidgetItem(field.get("name", ""))
                self.fields_table.setItem(row, 0, name_item)
                
                # Field type
                type_combo = QComboBox()
                type_combo.addItems(["text", "number", "date", "dropdown", "checkbox", "textarea"])
                type_combo.setCurrentText(field.get("type", "text"))
                self.fields_table.setCellWidget(row, 1, type_combo)
                
                # Required checkbox
                required_check = QCheckBox()
                required_check.setChecked(field.get("required", False))
                self.fields_table.setCellWidget(row, 2, required_check)
                
                # Actions button
                remove_btn = QPushButton("Remove")
                remove_btn.clicked.connect(lambda checked=False, r=row: self.remove_field(r))
                self.fields_table.setCellWidget(row, 3, remove_btn)
                
                row += 1
        
        layout.addWidget(self.fields_table)
        
        # Add field button
        add_field_layout = QHBoxLayout()
        self.field_name_input = QLineEdit()
        self.field_name_input.setPlaceholderText("New field name")
        add_field_layout.addWidget(self.field_name_input)
        
        self.field_type_combo = QComboBox()
        self.field_type_combo.addItems(["text", "number", "date", "dropdown", "checkbox", "textarea"])
        add_field_layout.addWidget(self.field_type_combo)
        
        add_field_btn = QPushButton("Add Field")
        add_field_btn.clicked.connect(self.add_field)
        add_field_layout.addWidget(add_field_btn)
        
        layout.addLayout(add_field_layout)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        save_btn = QPushButton("Save Changes")
        save_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                padding: 8px;
            }
        """)
        save_btn.clicked.connect(self.save_form)
        button_layout.addWidget(save_btn)
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)
        
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
    
    def add_field(self):
        """Add new field to form"""
        field_name = self.field_name_input.text().strip()
        field_type = self.field_type_combo.currentText()
        
        if not field_name:
            QMessageBox.warning(self, "Validation Error", "Please enter a field name")
            return
        
        row = self.fields_table.rowCount()
        self.fields_table.insertRow(row)
        
        # Field name
        name_item = QTableWidgetItem(field_name)
        self.fields_table.setItem(row, 0, name_item)
        
        # Field type
        type_combo = QComboBox()
        type_combo.addItems(["text", "number", "date", "dropdown", "checkbox", "textarea"])
        type_combo.setCurrentText(field_type)
        self.fields_table.setCellWidget(row, 1, type_combo)
        
        # Required checkbox
        required_check = QCheckBox()
        self.fields_table.setCellWidget(row, 2, required_check)
        
        # Remove button
        remove_btn = QPushButton("Remove")
        remove_btn.clicked.connect(lambda checked=False, r=row: self.remove_field(r))
        self.fields_table.setCellWidget(row, 3, remove_btn)
        
        # Clear input
        self.field_name_input.clear()
    
    def remove_field(self, row):
        """Remove field from form"""
        self.fields_table.removeRow(row)
    
    def save_form(self):
        """Save form changes to server"""
        try:
            # Collect form data
            form_name = self.name_input.text().strip()
            description = self.desc_input.toPlainText()
            
            if not form_name:
                QMessageBox.warning(self, "Validation Error", "Please enter a form name")
                return
            
            # Collect fields
            fields = []
            for row in range(self.fields_table.rowCount()):
                field_name = self.fields_table.item(row, 0).text()
                field_type = self.fields_table.cellWidget(row, 1).currentText()
                required = self.fields_table.cellWidget(row, 2).isChecked()
                
                fields.append({
                    "name": field_name,
                    "type": field_type,
                    "required": required
                })
            
            # Build form schema
            form_schema = {
                "name": form_name,
                "description": description,
                "sections": [
                    {
                        "name": "Main",
                        "fields": fields
                    }
                ]
            }
            
            # Send to server
            headers = {
                "Authorization": f"Bearer {self.token}",
                "Content-Type": "application/json"
            }
            
            response = requests.put(
                f"{self.api_url}/api/forms/{self.form_id}",
                json=form_schema,
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
