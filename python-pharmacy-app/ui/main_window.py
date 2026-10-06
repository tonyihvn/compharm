"""Main window for the pharmacy application."""

import logging
from datetime import datetime
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QStackedWidget, QMenuBar, QMenu, QMessageBox,
    QStatusBar, QPushButton, QLabel
)
from PyQt6.QtCore import Qt, pyqtSignal, QTimer, QThread
from PyQt6.QtGui import QIcon, QFont

from config.settings import settings
from database.db_manager import DatabaseManager
from services.api_client import CentralServerClient
from ui.widgets.client_list_view import ClientListView
from ui.widgets.client_detail_view import ClientDetailView
from ui.widgets.form_viewer import FormViewer
from ui.widgets.admin_panel import AdminPanel
from ui.widgets.sync_worker import SyncWorker

logger = logging.getLogger(__name__)


class MainWindow(QMainWindow):
    """Main application window."""

    def __init__(self, db_manager: DatabaseManager, settings: object):
        """Initialize main window."""
        super().__init__()
        self.db_manager = db_manager
        self.settings = settings
        self.api_client = CentralServerClient()
        self.current_user = None
        self.current_client = None
        self.sync_thread = None
        self.sync_worker = None

        # Setup UI
        self.init_ui()
        self.apply_styles()
        
        # Don't setup sync worker on startup - do it after login
        # self.setup_sync_worker()

    def init_ui(self):
        """Initialize user interface."""
        self.setWindowTitle(self.settings.APP_NAME)
        self.setGeometry(100, 100, self.settings.WINDOW_WIDTH, self.settings.WINDOW_HEIGHT)

        # Create central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Create main layout
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Create stacked widget for different views
        self.stacked_widget = QStackedWidget()

        # Initialize views
        self.client_list_view = ClientListView(self.settings.CENTRAL_SERVER_URL, self.current_user, self.db_manager)
        # Create placeholder detail view (will be updated when client is selected)
        self.client_detail_view = ClientDetailView({"fullName": "Select a client"})
        # Create placeholder form viewer (will be updated when form is selected)
        self.form_viewer = FormViewer({"name": "Select a form"}, {}, self.settings.CENTRAL_SERVER_URL)
        # Create admin panel
        self.admin_panel = AdminPanel(self.settings.CENTRAL_SERVER_URL, self.current_user)

        # Add views to stacked widget
        self.stacked_widget.addWidget(self.client_list_view)      # Index 0
        self.stacked_widget.addWidget(self.client_detail_view)    # Index 1
        self.stacked_widget.addWidget(self.form_viewer)            # Index 2
        self.stacked_widget.addWidget(self.admin_panel)            # Index 3

        main_layout.addWidget(self.stacked_widget)

        # Create menu bar
        self.create_menu_bar()

        # Create status bar
        self.status_bar = self.statusBar()
        self.status_label = QLabel("Ready")
        self.sync_status_label = QLabel("Sync: Idle")
        self.status_bar.addWidget(self.status_label)
        self.status_bar.addPermanentWidget(self.sync_status_label)

        # Connect signals
        self.connect_signals()

        # Show welcome/placeholder view initially (will be replaced with client list after login)
        # self.show_client_list()  # Don't auto-load clients - wait for explicit call after login

    def create_menu_bar(self):
        """Create application menu bar."""
        menubar = self.menuBar()

        # File menu
        file_menu = menubar.addMenu("&File")
        
        sync_action = file_menu.addAction("&Sync Data")
        sync_action.triggered.connect(self.sync_data)
        file_menu.addSeparator()
        
        exit_action = file_menu.addAction("E&xit")
        exit_action.triggered.connect(self.close)

        # View menu
        view_menu = menubar.addMenu("&View")
        
        clients_action = view_menu.addAction("&Clients")
        clients_action.triggered.connect(self.show_client_list)
        
        admin_action = view_menu.addAction("&Admin Panel")
        admin_action.triggered.connect(self.show_admin_panel)

        # Help menu
        help_menu = menubar.addMenu("&Help")
        
        about_action = help_menu.addAction("&About")
        about_action.triggered.connect(self.show_about)

    def connect_signals(self):
        """Connect UI signals."""
        # Client list view signals
        self.client_list_view.client_selected.connect(self.on_client_selected)
        
        # Client detail view signals
        self.client_detail_view.close_requested.connect(self.show_client_list)
        self.client_detail_view.form_requested.connect(self.on_form_requested)
        
        # Form viewer signals
        self.form_viewer.close_requested.connect(self.on_form_viewer_back)
        self.form_viewer.form_submitted.connect(self.on_form_submitted)
        
        # Admin panel signals
        self.admin_panel.close_requested.connect(self.show_client_list)

    def on_client_selected(self, client_id: int):
        """Handle client selection."""
        self.current_client = self.db_manager.get_session().query(
            self.db_manager.SessionLocal
        ).filter_by(id=client_id).first()
        self.client_detail_view.load_client(client_id)
        self.show_client_detail()

    def on_form_requested(self, form_data: dict):
        """Handle form request from client details."""
        form_id = form_data.get('id')
        self.form_viewer.load_form(form_id, self.current_client.id if self.current_client else None)
        self.show_form_viewer()

    def on_form_viewer_back(self):
        """Handle back from form viewer."""
        self.show_client_detail()

    def on_form_submitted(self, submission_data: dict):
        """Handle form submission."""
        self.status_label.setText("Form submitted successfully!")
        self.show_client_detail()

    def show_client_list(self):
        """Show client list view."""
        self.stacked_widget.setCurrentIndex(0)
        # Don't auto-load clients - let user manually load via button click

    def show_client_detail(self):
        """Show client detail view."""
        self.stacked_widget.setCurrentIndex(1)

    def show_form_viewer(self):
        """Show form viewer."""
        self.stacked_widget.setCurrentIndex(2)

    def show_admin_panel(self):
        """Show admin panel."""
        self.stacked_widget.setCurrentIndex(3)
        self.admin_panel.refresh()

    def setup_sync_worker(self):
        """Setup background sync worker (only call after login)."""
        try:
            if self.sync_worker is None:
                self.sync_worker = SyncWorker(self.api_client, self.db_manager)
                self.sync_worker.sync_started.connect(self.on_sync_started)
                self.sync_worker.sync_completed.connect(self.on_sync_completed)
                self.sync_worker.sync_error.connect(self.on_sync_error)
                self.sync_worker.start()
        except Exception as e:
            logger.warning(f"Failed to setup sync worker: {str(e)}")
            # App can continue without sync worker

    def on_sync_started(self):
        """Handle sync started."""
        self.sync_status_label.setText("Sync: In Progress...")

    def on_sync_completed(self, result):
        """Handle sync completed."""
        self.sync_status_label.setText("Sync: Completed")
        self.status_label.setText("Data synced successfully!")

    def on_sync_error(self, error_msg):
        """Handle sync error."""
        self.sync_status_label.setText("Sync: Error")
        self.status_label.setText(f"Sync error: {error_msg}")

    def sync_data(self):
        """Trigger manual data sync."""
        self.sync_status_label.setText("Sync: In Progress...")
        # The sync worker runs continuously in background

    def on_sync_finished(self, result: dict):
        """Handle sync completion."""
        self.sync_status_label.setText(
            f"Sync: OK (Last: {datetime.now().strftime('%H:%M')})"
        )
        logger.info(f"Sync completed: {result}")

    def on_sync_progress(self, message: str):
        """Handle sync progress update."""
        self.status_label.setText(f"Syncing... {message}")

    def apply_styles(self):
        """Apply application styles."""
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f5f5f5;
            }
            QMenuBar {
                background-color: #2c3e50;
                color: white;
            }
            QMenuBar::item:selected {
                background-color: #34495e;
            }
            QMenu {
                background-color: #ecf0f1;
                color: #2c3e50;
            }
            QStatusBar {
                background-color: #ecf0f1;
                color: #2c3e50;
            }
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
            QPushButton:pressed {
                background-color: #1f618d;
            }
        """)

    def show_about(self):
        """Show about dialog."""
        QMessageBox.about(
            self,
            "About",
            f"{self.settings.APP_NAME}\nVersion {self.settings.APP_VERSION}\n\n"
            "A professional community pharmacy management system.\n"
            "© 2024 All rights reserved."
        )

    def closeEvent(self, event):
        """Handle window close event."""
        if self.sync_thread:
            self.sync_thread.quit()
            self.sync_thread.wait()
        self.db_manager.close()
        event.accept()
