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
from ui.widgets.client_detail_view import ClientDetailView
from ui.widgets.form_viewer import FormViewer
from ui.widgets.admin_panel import AdminPanel
from ui.widgets.sync_worker import SyncWorker

logger = logging.getLogger(__name__)


class ModernMainWindow(QMainWindow):
    """Modern main application window with professional sidebar."""

    def __init__(self, db_manager: DatabaseManager, settings: object):
        """Initialize modern main window."""
        super().__init__()
        self.db_manager = db_manager
        self.settings = settings
        self.api_client = CentralServerClient()
        self.current_user = None
        self.current_client = None
        self.sync_thread = None
        self.sync_worker = None
        self.sidebar_expanded = True

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
        self.client_list_view = ClientListView(
            self.settings.CENTRAL_SERVER_URL, 
            self.current_user, 
            self.db_manager
        )
        self.client_detail_view = ClientDetailView({"fullName": "Select a client"})
        self.form_viewer = FormViewer(
            {"name": "Select a form"}, 
            {}, 
            self.settings.CENTRAL_SERVER_URL
        )
        self.admin_panel = AdminPanel(
            self.settings.CENTRAL_SERVER_URL, 
            self.current_user
        )

        # Add views to stacked widget
        self.stacked_widget.addWidget(self.client_list_view)       # Index 0
        self.stacked_widget.addWidget(self.client_detail_view)     # Index 1
        self.stacked_widget.addWidget(self.form_viewer)             # Index 2
        self.stacked_widget.addWidget(self.admin_panel)             # Index 3

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

        # Navigation buttons
        nav_buttons = [
            ("👥 Clients", self.show_client_list),
            ("📋 Forms", self.show_forms_list),
            ("⚙️ Admin Panel", self.show_admin_panel),
            ("📊 Sync Status", self.show_sync_status),
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
        self.client_list_view.client_selected.connect(self.on_client_selected)
        self.client_detail_view.close_requested.connect(self.show_client_list)
        self.client_detail_view.form_requested.connect(self.on_form_requested)
        self.form_viewer.close_requested.connect(self.on_form_viewer_back)
        self.form_viewer.form_submitted.connect(self.on_form_submitted)
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

    def on_client_selected(self, client_id: int):
        """Handle client selection."""
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
        """Show forms list (placeholder)."""
        self.status_label.setText("Forms management coming soon")
        from PyQt6.QtWidgets import QMessageBox
        QMessageBox.information(self, "Forms", "Forms management coming soon")

    def show_sync_status(self):
        """Show sync status (placeholder)."""
        self.status_label.setText("Sync status: Idle")
        from PyQt6.QtWidgets import QMessageBox
        QMessageBox.information(self, "Sync Status", "Last sync: 5 minutes ago")

    def show_admin_panel(self):
        """Show admin panel."""
        if self.current_user and (self.current_user.get('is_superuser') or 
                                   self.current_user.get('role') == 'admin'):
            self.stacked_widget.setCurrentIndex(3)
            self.admin_panel.refresh()
            self.status_label.setText("Admin Panel")
        else:
            from PyQt6.QtWidgets import QMessageBox
            QMessageBox.warning(self, "Access Denied", 
                              "Admin access required. You must be logged in as an administrator.")

    def sync_data(self):
        """Manually trigger sync."""
        self.status_label.setText("Syncing...")
        self.sync_status_label.setText("Sync: In Progress...")

    def on_sync_started(self):
        """Handle sync started."""
        self.sync_status_label.setText("Sync: In Progress...")

    def on_sync_completed(self, result):
        """Handle sync completed."""
        message = (f"Sync completed: "
                  f"{result.get('clients_synced', 0)} clients, "
                  f"{result.get('forms_synced', 0)} forms")
        self.status_label.setText(message)
        self.sync_status_label.setText("Sync: Completed")
        logger.info(f"Sync result: {result}")

    def on_sync_error(self, error_msg: str):
        """Handle sync error."""
        self.status_label.setText(f"Sync Error: {error_msg}")
        self.sync_status_label.setText("Sync: Error")
        logger.error(f"Sync error: {error_msg}")

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
