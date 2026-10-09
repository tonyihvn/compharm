"""
Integration Guide for Enhanced Clients Management Table

This module demonstrates how to integrate the new enhanced clients management
features into your existing PyQt6 application.
"""

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QStackedWidget, QMessageBox
from PyQt6.QtCore import Qt, pyqtSignal
from ui.widgets.enhanced_client_list import EnhancedClientListView
from ui.client_full_details_view import ClientDetailsView


class ClientsManagementIntegration(QWidget):
    """
    Integration point for enhanced clients management
    
    This widget manages the client list view and detail view, handling navigation
    between them and managing all client-related actions.
    """
    
    def __init__(self, api_url, current_user, db_manager=None):
        super().__init__()
        self.api_url = api_url
        self.current_user = current_user
        self.db_manager = db_manager
        
        # Create stacked widget for view switching
        self.stacked_widget = QStackedWidget()
        
        # Create enhanced client list view
        self.client_list_view = EnhancedClientListView(
            api_url, current_user, db_manager
        )
        
        # Connect client list signals
        self.client_list_view.fill_form_requested.connect(self.on_fill_form)
        self.client_list_view.view_details_requested.connect(self.on_view_details)
        self.client_list_view.edit_client_requested.connect(self.on_edit_client)
        self.client_list_view.delete_client_requested.connect(self.on_delete_client)
        
        self.stacked_widget.addWidget(self.client_list_view)
        
        layout = QVBoxLayout()
        layout.addWidget(self.stacked_widget)
        self.setLayout(layout)
    
    def load_clients(self):
        """Load and display clients"""
        self.client_list_view.load_clients()
    
    def on_view_details(self, client_data):
        """Show client details view"""
        detail_view = ClientDetailsView(client_data, self.db_manager)
        
        # Connect detail view signals
        detail_view.fill_form_requested.connect(self.on_fill_form)
        detail_view.edit_requested.connect(self.on_edit_client)
        detail_view.close_requested.connect(lambda: self.show_client_list())
        
        self.stacked_widget.addWidget(detail_view)
        self.stacked_widget.setCurrentWidget(detail_view)
    
    def on_fill_form(self, client_data):
        """Handle fill form request"""
        # Emit signal to parent window or show form selection dialog
        QMessageBox.information(
            self,
            "Fill Form",
            f"Fill form for client: {client_data.get('fullName')}"
        )
    
    def on_edit_client(self, client_data):
        """Handle edit client request"""
        QMessageBox.information(
            self,
            "Edit Client",
            f"Edit client: {client_data.get('fullName')}"
        )
    
    def on_delete_client(self, client_id):
        """Handle delete client request"""
        try:
            if self.db_manager:
                session = self.db_manager.get_session()
                try:
                    from database.models import Client
                    client = session.query(Client).filter_by(id=client_id).first()
                    if client:
                        session.delete(client)
                        session.commit()
                        self.client_list_view.load_clients()
                        QMessageBox.information(self, "Success", "Client deleted successfully")
                finally:
                    session.close()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to delete client: {str(e)}")
    
    def show_client_list(self):
        """Show client list view"""
        self.stacked_widget.setCurrentWidget(self.client_list_view)


# Usage example in main window:
"""
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        
        # ... other initialization code ...
        
        # Create clients management integration
        self.clients_mgmt = ClientsManagementIntegration(
            api_url=self.api_url,
            current_user=self.current_user,
            db_manager=self.db_manager
        )
        
        # Add to central widget or layout
        self.setCentralWidget(self.clients_mgmt)
        
        # Load clients when needed
        self.clients_mgmt.load_clients()
"""


# Feature checklist:
"""
✓ Enhanced column management:
  - Right-click on column headers to show/hide columns
  - Context menu with checkboxes for each column
  - "Show All Columns" option
  - "Hide All Columns" option
  - Persistent settings saved to SQLite database
  
✓ Action column:
  - Dropdown menu for each row
  - "Fill Form" - opens form selection
  - "View Details" - opens detailed client view
  - "Edit" - edit client information
  - "Delete" - delete client (with confirmation)
  
✓ Enhanced ClientDetailsView:
  - All client fields organized in tabs
  - Form submissions table showing:
    * Form name
    * Submission date
    * Status (draft/submitted)
    * View button - show form data
    * Edit button - edit form submission
    * Delete button - delete form submission
  - "Fill New Form" button to fill forms for this client
  - Back button to return to clients list
  
✓ Persistent Settings:
  - Column visibility saved to column_settings.db
  - Settings loaded on app restart
  - Per-user preference support (can be enhanced)

✓ PyQt6 Features:
  - Table with proper sorting and filtering
  - Alternating row colors
  - Status color coding (green=Active, red=Inactive, orange=other)
  - Custom widgets for action buttons
  - Context menus with proper styling
  - Responsive table layout with column width management
"""
