"""
Modern Main Window - Professional pharmacy app with Admin UI theme
Redesigned with modern sidebar and professional layout
"""

import logging
from datetime import datetime
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QStackedWidget,
    QPushButton, QLabel, QStatusBar, QFrame, QScrollArea
)
from PyQt6.QtCore import Qt, pyqtSignal, QTimer, QThread, QSize
from PyQt6.QtGui import QIcon, QFont, QColor, QPixmap
from PyQt6.QtCore import QPropertyAnimation, QEasingCurve

from config.settings import settings
from database.db_manager import DatabaseManager
from services.api_client import CentralServerClient
from ui.widgets.client_list_view import ClientListView
from ui.widgets.enhanced_client_list import EnhancedClientListView
from ui.widgets.client_detail_view import ClientDetailView
from ui.client_full_details_view import ClientDetailsView as ClientFullDetailsView
from ui.widgets.form_viewer import FormViewer
from ui.widgets.forms_list_view import FormsListView
from ui.widgets.admin_panel import AdminPanel
from ui.widgets.sync_worker import SyncWorker
from ui.widgets.sync_status_widget import SyncStatusIndicator, SyncProgressDialog

logger = logging.getLogger(__name__)


class ModernMainWindow(QMainWindow):
    """Modern main application window with professional sidebar."""

    def __init__(self, db_manager: DatabaseManager, settings: object):
        """Initialize modern main window."""
        super().__init__()
        self.db_manager = db_manager
        self.settings = settings
        self.current_user = None
        self.current_client = None
        self.sync_thread = None
        self.sync_worker = None
        self.sidebar_expanded = True
        self.sync_progress_dialog = None
        
        # Initialize API client with offline support
        try:
            self.api_client = CentralServerClient()
            # Check if server is reachable
            self.online_mode = self.api_client.is_online()
            if not self.online_mode:
                logger.warning("Server not reachable - running in offline mode")
        except Exception as e:
            logger.warning(f"Failed to initialize API client: {e} - offline mode enabled")
            self.api_client = CentralServerClient()
            self.online_mode = False

        # Setup UI
        self.init_ui()
        self.apply_styles()

    def init_ui(self):
        """Initialize user interface with modern design."""
        self.setWindowTitle(self.settings.APP_NAME)
        self.setGeometry(100, 100, self.settings.WINDOW_WIDTH, self.settings.WINDOW_HEIGHT)
        self.setWindowIcon(self.create_app_icon())

        # Create central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Create main layout (sidebar + content)
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Create sidebar
        self.sidebar = self.create_sidebar()
        main_layout.addWidget(self.sidebar)

        # Create stacked widget for different views
        self.stacked_widget = QStackedWidget()

        # Initialize views
        self.client_list_view = EnhancedClientListView(
            self.settings.CENTRAL_SERVER_URL, 
            self.current_user, 
            self.db_manager
        )
        self.client_detail_view = ClientFullDetailsView({"fullName": "Select a client"}, self.db_manager)
        self.form_viewer = FormViewer(
            {"name": "Select a form"}, 
            {}, 
            self.settings.CENTRAL_SERVER_URL
        )
        self.forms_list_view = FormsListView(
            self.settings.CENTRAL_SERVER_URL,
            self.current_user,
            self.db_manager
        )
        self.admin_panel = AdminPanel(
            self.settings.CENTRAL_SERVER_URL, 
            self.current_user,
            self.db_manager
        )

        # Add views to stacked widget
        self.stacked_widget.addWidget(self.client_list_view)       # Index 0
        self.stacked_widget.addWidget(self.client_detail_view)     # Index 1
        self.stacked_widget.addWidget(self.form_viewer)             # Index 2
        self.stacked_widget.addWidget(self.forms_list_view)         # Index 3
        self.stacked_widget.addWidget(self.admin_panel)             # Index 4

        main_layout.addWidget(self.stacked_widget, 1)

        # Create status bar
        self.status_bar = self.statusBar()
        self.status_label = QLabel("Ready")
        self.sync_status_label = QLabel("Sync: Idle")
        self.user_label = QLabel("")
        self.status_bar.addWidget(self.status_label)
        self.status_bar.addPermanentWidget(self.sync_status_label)
        self.status_bar.addPermanentWidget(self.user_label)

        # Connect signals
        self.connect_signals()

    def create_sidebar(self) -> QFrame:
        """Create modern professional sidebar."""
        sidebar = QFrame()
        sidebar.setObjectName("sidebar")
        sidebar.setFixedWidth(250)
        sidebar.setFrameShape(QFrame.Shape.StyledPanel)

        layout = QVBoxLayout(sidebar)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Header section
        header_frame = QFrame()
        header_frame.setObjectName("sidebar_header")
        header_layout = QVBoxLayout(header_frame)
        header_layout.setContentsMargins(15, 15, 15, 15)

        app_title = QLabel(self.settings.APP_NAME)
        title_font = QFont()
        title_font.setPointSize(14)
        title_font.setBold(True)
        app_title.setFont(title_font)
        app_title.setAlignment(Qt.AlignmentFlag.AlignCenter)

        app_subtitle = QLabel("Admin Dashboard")
        subtitle_font = QFont()
        subtitle_font.setPointSize(9)
        app_subtitle.setFont(subtitle_font)
        app_subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        app_subtitle.setStyleSheet("color: #888;")

        header_layout.addWidget(app_title)
        header_layout.addWidget(app_subtitle)
        header_frame.setLayout(header_layout)
        layout.addWidget(header_frame)

        # Divider
        divider = QFrame()
        divider.setFrameShape(QFrame.Shape.HLine)
        divider.setLineWidth(1)
        layout.addWidget(divider)

        # Sync status indicator
        self.sync_status_indicator = SyncStatusIndicator()
        layout.addWidget(self.sync_status_indicator)
        
        # Divider
        divider1_5 = QFrame()
        divider1_5.setFrameShape(QFrame.Shape.HLine)
        divider1_5.setLineWidth(1)
        layout.addWidget(divider1_5)

        # Navigation buttons
        nav_buttons = [
            ("👥 Clients", self.show_client_list),
            ("📋 Forms", self.show_forms_list),
            ("⚙️ Admin Panel", self.show_admin_panel),
            ("⚡ Sync Now", self.sync_data),
        ]

        for btn_text, slot in nav_buttons:
            btn = self.create_nav_button(btn_text, slot)
            layout.addWidget(btn)

        # Stretch spacer
        layout.addStretch()

        # User info section
        user_info_frame = QFrame()
        user_info_frame.setObjectName("user_info")
        user_info_layout = QVBoxLayout(user_info_frame)
        user_info_layout.setContentsMargins(15, 15, 15, 15)

        divider2 = QFrame()
        divider2.setFrameShape(QFrame.Shape.HLine)
        divider2.setLineWidth(1)
        user_info_layout.addWidget(divider2)

        self.user_info_label = QLabel("User: Not logged in")
        self.user_info_label.setFont(QFont("Arial", 9))
        self.user_info_label.setWordWrap(True)
        user_info_layout.addWidget(self.user_info_label)

        self.role_label = QLabel("Role: --")
        self.role_label.setFont(QFont("Arial", 9))
        self.role_label.setStyleSheet("color: #666;")
        user_info_layout.addWidget(self.role_label)

        # Logout button
        logout_btn = QPushButton("Logout")
        logout_btn.setObjectName("logout_btn")
        logout_btn.clicked.connect(self.logout)
        user_info_layout.addWidget(logout_btn)

        user_info_frame.setLayout(user_info_layout)
        layout.addWidget(user_info_frame)

        sidebar.setLayout(layout)
        return sidebar

    def create_nav_button(self, text: str, slot) -> QPushButton:
        """Create a styled navigation button."""
        btn = QPushButton(text)
        btn.setObjectName("nav_button")
        btn.setCursor(Qt.CursorShape.PointingHandCursor)
        btn.setMinimumHeight(50)
        btn.setFont(QFont("Arial", 11))
        btn.clicked.connect(slot)
        btn.setIconSize(QSize(20, 20))
        return btn

    def create_app_icon(self) -> QIcon:
        """Create application icon."""
        pixmap = QPixmap(64, 64)
        pixmap.fill(QColor(76, 175, 80))  # Green color
        icon = QIcon(pixmap)
        return icon

    def apply_styles(self):
        """Apply modern admin UI theme."""
        style_sheet = """
        QMainWindow {
            background-color: #f5f5f5;
        }

        #sidebar {
            background-color: #2c3e50;
            color: white;
        }

        #sidebar_header {
            background-color: #1a252f;
        }

        #sidebar_header QLabel {
            color: white;
        }

        #user_info {
            background-color: #1a252f;
            border-top: 1px solid #34495e;
        }

        #user_info QLabel {
            color: white;
        }

        QFrame {
            border-color: #bdbdbd;
        }

        #nav_button {
            background-color: #34495e;
            color: white;
            border: none;
            border-left: 4px solid transparent;
            padding: 12px 15px;
            text-align: left;
            font-weight: 500;
            margin: 5px 10px;
            border-radius: 3px;
        }

        #nav_button:hover {
            background-color: #45627b;
            border-left: 4px solid #4CAF50;
        }

        #nav_button:pressed {
            background-color: #3d5a73;
        }

        #logout_btn {
            background-color: #e74c3c;
            color: white;
            border: none;
            padding: 10px;
            border-radius: 3px;
            font-weight: bold;
            margin-top: 10px;
        }

        #logout_btn:hover {
            background-color: #c0392b;
        }

        QStatusBar {
            background-color: #2c3e50;
            color: white;
            border-top: 1px solid #34495e;
        }

        QStatusBar::item {
            border: none;
        }

        QLabel {
            color: #333;
        }

        QPushButton {
            background-color: #4CAF50;
            color: white;
            border: none;
            padding: 8px 16px;
            border-radius: 4px;
            font-weight: bold;
        }

        QPushButton:hover {
            background-color: #45a049;
        }

        QPushButton:pressed {
            background-color: #3d8b40;
        }

        QLineEdit, QTextEdit, QComboBox {
            background-color: white;
            color: #333;
            border: 1px solid #bdbdbd;
            padding: 5px;
            border-radius: 3px;
        }

        QLineEdit:focus, QTextEdit:focus, QComboBox:focus {
            border: 2px solid #4CAF50;
            padding: 4px;
        }

        QTabWidget::pane {
            border: 1px solid #bdbdbd;
        }

        QTabBar::tab {
            background-color: #ecf0f1;
            color: #333;
            padding: 8px 20px;
            border: 1px solid #bdbdbd;
        }

        QTabBar::tab:selected {
            background-color: #4CAF50;
            color: white;
        }

        QTabBar::tab:hover {
            background-color: #34495e;
            color: white;
        }

        QGroupBox {
            color: #333;
            border: 1px solid #bdbdbd;
            border-radius: 4px;
            margin-top: 8px;
            padding-top: 8px;
        }

        QGroupBox::title {
            subcontrol-origin: margin;
            left: 10px;
            padding: 0px 5px 0px 5px;
        }

        QMessageBox QLabel {
            color: #333;
        }

        QMessageBox QPushButton {
            min-width: 60px;
        }
        """
        self.setStyleSheet(style_sheet)

    def connect_signals(self):
        """Connect UI signals."""
        # Enhanced client list signals
        self.client_list_view.fill_form_requested.connect(self.on_fill_form_requested)
        self.client_list_view.view_details_requested.connect(self.on_view_details_requested)
        self.client_list_view.edit_client_requested.connect(self.on_edit_client_requested)
        self.client_list_view.delete_client_requested.connect(self.on_delete_client_requested)
        
        # Client detail view signals
        self.client_detail_view.close_requested.connect(self.show_client_list)
        self.client_detail_view.fill_form_requested.connect(self.on_fill_form_requested)
        
        # Form viewer signals
        self.form_viewer.close_requested.connect(self.on_form_viewer_back)
        self.form_viewer.form_submitted.connect(self.on_form_submitted)
        
        # Forms list view signals
        self.forms_list_view.close_requested.connect(self.show_client_list)
        self.forms_list_view.form_selected.connect(self.on_forms_list_form_selected)
        
        # Admin panel signals
        self.admin_panel.close_requested.connect(self.show_client_list)

    def update_user_info(self):
        """Update user info display from current_user."""
        if self.current_user:
            username = self.current_user.get('full_name', 
                      self.current_user.get('username', 'Unknown'))
            role = self.current_user.get('role', 'user')
            is_admin = self.current_user.get('is_superuser', False) or role == 'admin'

            self.user_info_label.setText(f"User: {username}")
            self.user_label.setText(f"{username} ({role})")

            if is_admin:
                self.role_label.setText("Role: 👑 Administrator")
                self.role_label.setStyleSheet("color: #FFB800;")
            else:
                self.role_label.setText(f"Role: {role}")
                self.role_label.setStyleSheet("color: #666;")
        else:
            self.user_info_label.setText("User: Not logged in")
            self.role_label.setText("Role: --")
            self.user_label.setText("")

    def on_view_details_requested(self, client_data: dict):
        """Handle view details request from enhanced client list."""
        try:
            client_id = client_data.get('id')
            from database.models import Client
            session = self.db_manager.get_session()
            self.current_client = session.query(Client).filter_by(id=client_id).first()
            session.close()

            if self.current_client:
                self.client_detail_view.load_client(client_id, client_data)
                self.show_client_detail()
        except Exception as e:
            logger.error(f"Error viewing client details: {str(e)}")
            from PyQt6.QtWidgets import QMessageBox
            QMessageBox.warning(self, "Error", f"Failed to load client details: {str(e)}")

    def on_fill_form_requested(self, client_data: dict):
        """Handle fill form request from enhanced client list or detail view."""
        try:
            from PyQt6.QtWidgets import QMessageBox
            from ui.widgets.form_selector_dialog import FormSelectorDialog
            from ui.form_filling_dialog import FormFillingDialog
            
            # Show form selector dialog
            form_selector = FormSelectorDialog(client_data, self.db_manager, self)
            
            if form_selector.exec() == FormSelectorDialog.DialogCode.Accepted:
                selected_form = form_selector.selected_form
                
                if not selected_form:
                    QMessageBox.warning(self, "Error", "No form selected")
                    return
                
                # Get auth token
                auth_token = None
                try:
                    from services.auth import AuthService
                    auth_service = AuthService(self.db_manager)
                    auth_token = auth_service.get_current_token()
                except:
                    pass
                
                # Open form filling dialog
                form_filling_dialog = FormFillingDialog(
                    selected_form.get('definition', {}),
                    client_data,
                    settings.API_URL or 'http://localhost:3000',
                    self.db_manager,
                    auth_token,
                    self
                )
                
                form_filling_dialog.form_submitted.connect(
                    self.on_form_submitted
                )
                form_filling_dialog.exec()
            
            self.current_client = type('obj', (object,), {'id': client_data.get('id')})()
            self.status_label.setText(f"Ready to fill form for {client_data.get('fullName')}")
        
        except Exception as e:
            logger.error(f"Error preparing to fill form: {str(e)}")
            from PyQt6.QtWidgets import QMessageBox
            QMessageBox.warning(self, "Error", f"Failed to prepare form: {str(e)}")

    def on_edit_client_requested(self, client_data: dict):
        """Handle edit client request from enhanced client list."""
        try:
            from PyQt6.QtWidgets import QMessageBox
            QMessageBox.information(
                self,
                "Edit Client",
                f"Edit functionality for {client_data.get('fullName')} coming soon!"
            )
        except Exception as e:
            logger.error(f"Error handling edit client: {str(e)}")

    def on_delete_client_requested(self, client_id: str):
        """Handle delete client request from enhanced client list."""
        try:
            from PyQt6.QtWidgets import QMessageBox
            reply = QMessageBox.question(
                self,
                "Confirm Delete",
                "Are you sure you want to delete this client? This action cannot be undone.",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            
            if reply == QMessageBox.StandardButton.Yes:
                # Delete from database
                from database.models import Client
                session = self.db_manager.get_session()
                try:
                    client = session.query(Client).filter_by(id=client_id).first()
                    if client:
                        session.delete(client)
                        session.commit()
                        self.client_list_view.load_clients()
                        QMessageBox.information(self, "Success", "Client deleted successfully")
                        self.status_label.setText("Client deleted successfully")
                finally:
                    session.close()
        except Exception as e:
            logger.error(f"Error deleting client: {str(e)}")
            from PyQt6.QtWidgets import QMessageBox
            QMessageBox.critical(self, "Error", f"Failed to delete client: {str(e)}")

    def on_client_selected(self, client_id: int):
        """Handle client selection (legacy)."""
        try:
            from database.models import Client
            session = self.db_manager.get_session()
            self.current_client = session.query(Client).filter_by(id=client_id).first()
            session.close()

            if self.current_client:
                self.client_detail_view.load_client(client_id)
                self.show_client_detail()
        except Exception as e:
            logger.error(f"Error selecting client: {str(e)}")

    def on_form_requested(self, form_data: dict):
        """Handle form request from client details."""
        form_id = form_data.get('id')
        client_id = self.current_client.id if self.current_client else None
        self.form_viewer.load_form(form_id, client_id)
        self.show_form_viewer()

    def on_form_viewer_back(self):
        """Handle back from form viewer."""
        self.show_client_detail()

    def on_form_submitted(self, submission_data: dict):
        """Handle form submission."""
        self.status_label.setText("Form submitted successfully!")
        self.show_client_detail()

    def on_forms_list_form_selected(self, form_data: dict, client_data: dict):
        """Handle form selection from forms list view."""
        self.current_client = type('obj', (object,), {'id': client_data.get('id')})()
        
        form_id = form_data.get('id')
        client_id = client_data.get('id')
        
        try:
            # Load form data
            response = self.api_client.session.get(
                f"{self.settings.CENTRAL_SERVER_URL}/api/forms/{form_id}",
                timeout=10
            )
            if response.status_code == 200:
                form_data = response.json().get('data', form_data)
            
            # Load form in viewer
            self.form_viewer.load_form(form_id, client_id)
            self.show_form_viewer()
        except Exception as e:
            logger.error(f"Error loading form: {str(e)}")
            from PyQt6.QtWidgets import QMessageBox
            QMessageBox.warning(self, "Error", f"Failed to load form: {str(e)}")

    def show_client_list(self):
        """Show client list view."""
        self.stacked_widget.setCurrentIndex(0)
        self.status_label.setText("Viewing Clients")

    def show_client_detail(self):
        """Show client detail view."""
        self.stacked_widget.setCurrentIndex(1)
        self.status_label.setText("Viewing Client Details")

    def show_form_viewer(self):
        """Show form viewer."""
        self.stacked_widget.setCurrentIndex(2)
        self.status_label.setText("Filling Form")

    def show_forms_list(self):
        """Show forms management view."""
        self.stacked_widget.setCurrentIndex(3)
        self.forms_list_view.load_data()
        self.status_label.setText("Forms Management")

    def show_sync_status(self):
        """Show sync status information."""
        if self.sync_worker:
            status = self.sync_worker.get_sync_status()
            self.sync_status_indicator.set_success(status)
        else:
            self.sync_status_indicator.set_idle()

    def sync_data(self):
        """Manually trigger sync with progress dialog."""
        if self.sync_worker is None:
            from PyQt6.QtWidgets import QMessageBox
            QMessageBox.warning(self, "Sync Error", 
                              "Sync worker not initialized. Please restart the application.")
            return
        
        # Check if already syncing
        if self.sync_worker.is_syncing:
            from PyQt6.QtWidgets import QMessageBox
            QMessageBox.information(self, "Sync in Progress", 
                                  "A sync operation is already in progress.")
            return
        
        # Show progress dialog
        self.sync_progress_dialog = SyncProgressDialog(self)
        
        # Connect signals
        self.sync_worker.sync_progress.connect(self.sync_progress_dialog.update_progress)
        self.sync_worker.sync_completed.connect(self.on_sync_completed_manual)
        self.sync_worker.sync_error.connect(self.on_sync_error_manual)
        
        # Trigger sync
        self.sync_worker.trigger_sync()
        
        # Show dialog
        self.sync_progress_dialog.exec()

    def show_admin_panel(self):
        """Show admin panel."""
        if self.current_user and (self.current_user.get('is_superuser') or 
                                   self.current_user.get('role') == 'admin'):
            self.stacked_widget.setCurrentIndex(4)
            self.admin_panel.refresh()
            self.status_label.setText("Admin Panel")
        else:
            from PyQt6.QtWidgets import QMessageBox
            QMessageBox.warning(self, "Access Denied", 
                              "Admin access required. You must be logged in as an administrator.")

    def on_sync_started(self):
        """Handle sync started."""
        self.sync_status_label.setText("Sync: In Progress...")
        self.sync_status_indicator.set_syncing()

    def on_sync_completed(self, result):
        """Handle auto-sync completed."""
        message = (f"Sync: "
                  f"{result.get('clients_synced', 0)} clients, "
                  f"{result.get('forms_synced', 0)} forms")
        self.status_label.setText(message)
        self.sync_status_label.setText("Sync: Completed ✓")
        self.sync_status_indicator.set_success(self.sync_worker.get_sync_status())
        logger.info(f"Auto-sync completed: {result}")

    def on_sync_completed_manual(self, result):
        """Handle manual sync completed."""
        self.on_sync_completed(result)
        if self.sync_progress_dialog:
            self.sync_progress_dialog.sync_completed(result)

    def on_sync_error(self, error_msg: str):
        """Handle sync error."""
        self.status_label.setText(f"Sync Error: {error_msg[:50]}")
        self.sync_status_label.setText("Sync: Error")
        self.sync_status_indicator.set_error(error_msg)
        logger.error(f"Sync error: {error_msg}")

    def on_sync_error_manual(self, error_msg: str):
        """Handle manual sync error."""
        self.on_sync_error(error_msg)
        if self.sync_progress_dialog:
            self.sync_progress_dialog.sync_error(error_msg)

    def setup_sync_worker(self):
        """Setup background sync worker (only call after login)."""
        try:
            if self.sync_worker is None:
                # Read sync interval from settings (in minutes)
                sync_interval_minutes = settings.SYNC_INTERVAL
                sync_interval_seconds = max(60, sync_interval_minutes * 60)  # Minimum 60 seconds
                
                logger.info(f"Setting up sync worker with interval: {sync_interval_minutes} minutes")
                
                self.sync_worker = SyncWorker(
                    self.api_client, 
                    self.db_manager, 
                    sync_interval=sync_interval_seconds
                )
                
                # Connect signals
                self.sync_worker.sync_started.connect(self.on_sync_started)
                self.sync_worker.sync_completed.connect(self.on_sync_completed)
                self.sync_worker.sync_error.connect(self.on_sync_error)
                
                # Start background sync thread
                self.sync_worker.start()
                logger.info("Sync worker started successfully")
                
                # Show initial status
                self.sync_status_indicator.set_idle()
        except Exception as e:
            logger.warning(f"Failed to setup sync worker: {str(e)}")
            self.sync_status_indicator.set_error("Failed to initialize sync")

    def logout(self):
        """Logout user and return to login screen."""
        from PyQt6.QtWidgets import QMessageBox
        reply = QMessageBox.question(self, "Logout", 
                                    "Are you sure you want to logout?",
                                    QMessageBox.StandardButton.Yes | 
                                    QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            self.current_user = None
            self.close()

    def closeEvent(self, event):
        """Handle window close."""
        if self.sync_worker:
            self.sync_worker.stop()
        event.accept()
