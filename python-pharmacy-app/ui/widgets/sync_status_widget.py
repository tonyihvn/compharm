"""Sync Status Widget for displaying sync information in UI."""

import logging
from datetime import datetime
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QProgressBar,
    QPushButton, QDialog, QMessageBox, QFrame
)
from PyQt6.QtCore import Qt, pyqtSignal, QTimer, QDateTime
from PyQt6.QtGui import QFont, QColor

logger = logging.getLogger(__name__)


class SyncStatusIndicator(QFrame):
    """Status indicator showing current sync state."""
    
    def __init__(self, parent=None):
        """Initialize sync status indicator."""
        super().__init__(parent)
        self.setObjectName("sync_status_indicator")
        self.init_ui()
        self.set_idle()
    
    def init_ui(self):
        """Initialize UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 5, 10, 5)
        layout.setSpacing(5)
        
        # Status line
        status_layout = QHBoxLayout()
        self.status_label = QLabel("● Idle")
        self.status_label.setFont(QFont("Arial", 10))
        status_layout.addWidget(self.status_label)
        status_layout.addStretch()
        layout.addLayout(status_layout)
        
        # Last sync time
        self.time_label = QLabel("Last sync: Never")
        self.time_label.setFont(QFont("Arial", 9))
        self.time_label.setStyleSheet("color: #666;")
        layout.addWidget(self.time_label)
        
        # Sync stats
        self.stats_label = QLabel("")
        self.stats_label.setFont(QFont("Arial", 9))
        self.stats_label.setStyleSheet("color: #666;")
        self.stats_label.setWordWrap(True)
        layout.addWidget(self.stats_label)
        
        self.setLayout(layout)
        self.setFrameShape(QFrame.Shape.StyledPanel)
        self.setStyleSheet("""
            QFrame {
                background-color: #f0f0f0;
                border: 1px solid #ddd;
                border-radius: 4px;
                padding: 8px;
            }
        """)
    
    def set_idle(self):
        """Set status to idle."""
        self.status_label.setText("● Idle")
        self.status_label.setStyleSheet("color: #888;")
    
    def set_syncing(self):
        """Set status to syncing."""
        self.status_label.setText("● Syncing...")
        self.status_label.setStyleSheet("color: #ff9800;")
    
    def set_success(self, result: dict):
        """Set status to success with result details."""
        self.status_label.setText("✓ Synced Successfully")
        self.status_label.setStyleSheet("color: #4caf50;")
        
        if result.get('last_sync_time'):
            time_str = result['last_sync_time'].strftime("%H:%M:%S")
            self.time_label.setText(f"Last sync: {time_str}")
        
        if result.get('last_sync_result'):
            res = result['last_sync_result']
            stats = f"Clients: {res.get('clients_synced', 0)}, Forms: {res.get('forms_synced', 0)}"
            self.stats_label.setText(stats)
    
    def set_error(self, error_msg: str):
        """Set status to error."""
        self.status_label.setText("✗ Sync Failed")
        self.status_label.setStyleSheet("color: #f44336;")
        self.stats_label.setText(f"Error: {error_msg[:100]}")


class SyncProgressDialog(QDialog):
    """Dialog showing sync progress."""
    
    def __init__(self, parent=None):
        """Initialize progress dialog."""
        super().__init__(parent)
        self.setWindowTitle("Syncing Data")
        self.setGeometry(100, 100, 400, 250)
        self.setModal(True)
        self.init_ui()
    
    def init_ui(self):
        """Initialize UI."""
        layout = QVBoxLayout(self)
        
        # Title
        title = QLabel("Synchronizing with Server")
        title_font = QFont()
        title_font.setPointSize(11)
        title_font.setBold(True)
        title.setFont(title_font)
        layout.addWidget(title)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setMinimum(0)
        self.progress_bar.setMaximum(0)  # Indeterminate
        layout.addWidget(self.progress_bar)
        
        # Status message
        self.message_label = QLabel("Connecting to server...")
        self.message_label.setWordWrap(True)
        self.message_label.setFont(QFont("Arial", 9))
        layout.addWidget(self.message_label)
        
        # Details
        self.details_label = QLabel("")
        self.details_label.setWordWrap(True)
        self.details_label.setFont(QFont("Arial", 8))
        self.details_label.setStyleSheet("color: #666;")
        layout.addWidget(self.details_label)
        
        layout.addStretch()
        
        # Close button (disabled until sync completes)
        self.close_btn = QPushButton("Close")
        self.close_btn.clicked.connect(self.accept)
        self.close_btn.setEnabled(False)
        layout.addWidget(self.close_btn)
        
        self.setLayout(layout)
    
    def update_progress(self, message: str):
        """Update progress message."""
        self.message_label.setText(message)
    
    def sync_completed(self, result: dict):
        """Handle sync completion."""
        self.progress_bar.setMaximum(1)
        self.progress_bar.setValue(1)
        
        clients = result.get('clients_synced', 0)
        forms = result.get('forms_synced', 0)
        submissions = result.get('submissions_sent', 0)
        
        status = result.get('status', 'success')
        
        if status == 'success':
            self.message_label.setText("✓ Sync Completed Successfully")
            self.message_label.setStyleSheet("color: #4caf50;")
            details = f"Synced: {clients} clients, {forms} forms\nSent: {submissions} submissions"
            self.details_label.setText(details)
        else:
            self.message_label.setText("✗ Sync Failed")
            self.message_label.setStyleSheet("color: #f44336;")
            error = result.get('error', 'Unknown error')
            self.details_label.setText(f"Error: {error}")
        
        self.close_btn.setEnabled(True)
    
    def sync_error(self, error_msg: str):
        """Handle sync error."""
        self.progress_bar.setMaximum(1)
        self.message_label.setText("✗ Sync Failed")
        self.message_label.setStyleSheet("color: #f44336;")
        self.details_label.setText(f"Error: {error_msg}")
        self.close_btn.setEnabled(True)
