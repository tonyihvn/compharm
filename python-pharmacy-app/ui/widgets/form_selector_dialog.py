"""
Form Selector Dialog - Allow users to select and fill forms for clients
"""
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QPushButton, QListWidget,
    QListWidgetItem, QLabel, QMessageBox, QScrollArea
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont
import logging

logger = logging.getLogger(__name__)


class FormSelectorDialog(QDialog):
    """Dialog for selecting a form to fill for a client"""
    
    form_selected = pyqtSignal(dict)  # Emit selected form
    
    def __init__(self, client_data, db_manager, parent=None):
        super().__init__(parent)
        self.client_data = client_data
        self.db_manager = db_manager
        self.selected_form = None
        
        self.setWindowTitle(f"Select Form for {client_data.get('fullName', 'Client')}")
        self.setGeometry(100, 100, 600, 400)
        self.init_ui()
        self.load_forms()
    
    def init_ui(self):
        """Initialize UI components"""
        layout = QVBoxLayout()
        
        # Title
        title = QLabel(f"Select a form to fill for {self.client_data.get('fullName', 'Client')}")
        title_font = QFont()
        title_font.setPointSize(12)
        title_font.setBold(True)
        title.setFont(title_font)
        layout.addWidget(title)
        
        # Instructions
        instructions = QLabel(
            "Select a form from the list below and click 'Open' to fill it.\n"
            "Form responses will be saved and synced to the server."
        )
        instructions.setWordWrap(True)
        layout.addWidget(instructions)
        
        # Forms list
        self.forms_list = QListWidget()
        self.forms_list.itemDoubleClicked.connect(self.on_open_form)
        layout.addWidget(self.forms_list)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        open_btn = QPushButton("Open")
        open_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        open_btn.clicked.connect(self.on_open_form)
        button_layout.addWidget(open_btn)
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.setStyleSheet("""
            QPushButton {
                background-color: #f44336;
                color: white;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #da190b;
            }
        """)
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)
        
        layout.addLayout(button_layout)
        self.setLayout(layout)
    
    def load_forms(self):
        """Load available forms from database"""
        try:
            forms = self.db_manager.get_all_forms()
            
            if not forms:
                self.forms_list.addItem("No forms available")
                return
            
            for form in forms:
                item_text = f"{form.get('name', 'Unknown')} (v{form.get('version', '1.0')})"
                item = QListWidgetItem(item_text)
                item.setData(Qt.ItemDataRole.UserRole, form)
                self.forms_list.addItem(item)
            
            logger.info(f"Loaded {len(forms)} forms from database")
        except Exception as e:
            logger.error(f"Error loading forms: {str(e)}")
            QMessageBox.warning(self, "Error", f"Failed to load forms: {str(e)}")
    
    def on_open_form(self):
        """Handle opening a form"""
        current_item = self.forms_list.currentItem()
        
        if not current_item:
            QMessageBox.warning(self, "Warning", "Please select a form first")
            return
        
        form_data = current_item.data(Qt.ItemDataRole.UserRole)
        
        if not form_data or form_data == "No forms available":
            QMessageBox.warning(self, "Warning", "No form data available")
            return
        
        self.selected_form = form_data
        self.form_selected.emit(form_data)
        self.accept()
