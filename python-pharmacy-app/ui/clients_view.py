"""
Clients List View - Display downloaded clients
"""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QTableWidget,
    QTableWidgetItem, QLineEdit, QLabel, QComboBox, QMessageBox, QProgressDialog
)
from PyQt6.QtCore import Qt, pyqtSignal, QTimer, QThread
from PyQt6.QtGui import QFont, QColor
import requests
import json
from database.models import Client


class ClientsListView(QWidget):
    """View for displaying and managing clients"""
    
    client_selected = pyqtSignal(dict)  # Emit selected client data
    
    def __init__(self, api_url, current_user, db_manager=None):
        super().__init__()
        self.api_url = api_url
        self.current_user = current_user
        self.db_manager = db_manager
        self.clients = []
        self.init_ui()
        # Don't load clients on init - only load when explicitly requested after login
        # self.load_clients()
    
    
    def init_ui(self):
        """Initialize UI components"""
        layout = QVBoxLayout()
        
        # Title
        title = QLabel("Clients Management")
        title_font = QFont()
        title_font.setPointSize(14)
        title_font.setBold(True)
        title.setFont(title_font)
        layout.addWidget(title)
        
        # Top toolbar
        toolbar = QHBoxLayout()
        
        # Search
        search_label = QLabel("Search:")
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search by PEPFARID, name, or phone...")
        self.search_input.textChanged.connect(self.filter_clients)
        toolbar.addWidget(search_label)
        toolbar.addWidget(self.search_input)
        
        # Status filter
        status_label = QLabel("Status:")
        self.status_combo = QComboBox()
        self.status_combo.addItems(["All", "Active", "Inactive", "Transferred"])
        self.status_combo.currentTextChanged.connect(self.filter_clients)
        toolbar.addWidget(status_label)
        toolbar.addWidget(self.status_combo)
        
        # Refresh button
        refresh_btn = QPushButton("Refresh")
        refresh_btn.clicked.connect(self.load_clients)
        toolbar.addWidget(refresh_btn)
        
        # Download new button
        download_btn = QPushButton("Download New Clients")
        download_btn.clicked.connect(self.download_clients)
        toolbar.addWidget(download_btn)
        
        toolbar.addStretch()
        layout.addLayout(toolbar)
        
        # Clients table
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels([
            "PEPFARID", "Full Name", "Phone", "Facility", "Status", "Last Updated"
        ])
        self.table.setColumnWidth(0, 120)
        self.table.setColumnWidth(1, 200)
        self.table.setColumnWidth(2, 120)
        self.table.setColumnWidth(3, 150)
        self.table.setColumnWidth(4, 100)
        self.table.setColumnWidth(5, 150)
        self.table.itemClicked.connect(self.on_client_selected)
        self.table.setAlternatingRowColors(True)
        layout.addWidget(self.table)
        
        # Bottom action buttons
        bottom_layout = QHBoxLayout()
        
        view_btn = QPushButton("View Details")
        view_btn.clicked.connect(self.view_selected_client)
        bottom_layout.addWidget(view_btn)
        
        fill_form_btn = QPushButton("Fill Form")
        fill_form_btn.clicked.connect(self.fill_form_for_client)
        bottom_layout.addWidget(fill_form_btn)
        
        sync_btn = QPushButton("Sync Selected")
        sync_btn.clicked.connect(self.sync_selected_client)
        bottom_layout.addWidget(sync_btn)
        
        bottom_layout.addStretch()
        layout.addLayout(bottom_layout)
        
        self.setLayout(layout)
    
    def load_clients(self):
        """Load clients from local database (offline first)"""
        try:
            if self.db_manager is None:
                QMessageBox.warning(self, "Error", "Database manager not available")
                return
            
            session = self.db_manager.get_session()
            try:
                # Load all active clients from local database
                clients_db = session.query(Client).filter_by(status='active').all()
                
                if not clients_db:
                    QMessageBox.information(self, "No Clients", 
                                          "No clients found locally. Use 'Download New Clients' to sync from server.")
                    return
                
                # Convert ORM objects to dictionaries for display
                self.clients = []
                for client in clients_db:
                    self.clients.append({
                        "id": client.id,
                        "pepfarId": client.pepfar_id,
                        "fullName": client.full_name,
                        "phone": client.phone_number or "",
                        "facility": client.facility_id or "Unknown",
                        "status": client.status,
                        "updatedAt": client.updated_locally_at.strftime('%Y-%m-%d %H:%M') if client.updated_locally_at else ""
                    })
                
                self.display_clients(self.clients)
                
            finally:
                session.close()
                
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error loading clients: {str(e)}")
    
    def display_clients(self, clients):
        """Display clients in table"""
        self.table.setRowCount(len(clients))
        
        for row, client in enumerate(clients):
            self.table.setItem(row, 0, QTableWidgetItem(client.get("pepfarId", "")))
            self.table.setItem(row, 1, QTableWidgetItem(client.get("fullName", "")))
            self.table.setItem(row, 2, QTableWidgetItem(client.get("phone", "")))
            self.table.setItem(row, 3, QTableWidgetItem(client.get("facility", "")))
            
            status = client.get("status", "Active")
            status_item = QTableWidgetItem(status)
            if status == "Active":
                status_item.setForeground(QColor("green"))
            elif status == "Inactive":
                status_item.setForeground(QColor("red"))
            else:
                status_item.setForeground(QColor("orange"))
            self.table.setItem(row, 4, status_item)
            
            self.table.setItem(row, 5, QTableWidgetItem(client.get("updatedAt", "")))
    
    def filter_clients(self):
        """Filter clients based on search and status"""
        search_text = self.search_input.text().lower()
        status_filter = self.status_combo.currentText()
        
        filtered = []
        for client in self.clients:
            # Status filter
            if status_filter != "All" and client.get("status") != status_filter:
                continue
            
            # Search filter
            if search_text:
                search_fields = [
                    client.get("pepfarId", ""),
                    client.get("fullName", ""),
                    client.get("phone", "")
                ]
                if not any(search_text in field.lower() for field in search_fields):
                    continue
            
            filtered.append(client)
        
        self.display_clients(filtered)
    
    def on_client_selected(self, item):
        """Handle client selection"""
        row = self.table.row(item)
        if row < len(self.clients):
            self.selected_client = self.clients[row]
    
    def view_selected_client(self):
        """View details of selected client"""
        try:
            selected_row = self.table.currentRow()
            if selected_row >= 0:
                client = self.clients[selected_row]
                self.client_selected.emit(client)
            else:
                QMessageBox.warning(self, "Selection Error", "Please select a client")
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))
    
    def fill_form_for_client(self):
        """Fill form for selected client"""
        try:
            selected_row = self.table.currentRow()
            if selected_row >= 0:
                # This will be handled by main window
                pass
            else:
                QMessageBox.warning(self, "Selection Error", "Please select a client")
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))
    
    def sync_selected_client(self):
        """Sync selected client with server"""
        try:
            selected_row = self.table.currentRow()
            if selected_row >= 0:
                client = self.clients[selected_row]
                # Trigger sync
                QMessageBox.information(self, "Sync", "Client sync initiated")
            else:
                QMessageBox.warning(self, "Selection Error", "Please select a client")
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))
    
    def download_clients(self):
        """Download new clients from server"""
        progress = QProgressDialog("Downloading clients...", "Cancel", 0, 0, self)
        progress.setWindowModality(Qt.WindowModality.WindowModal)
        progress.show()
        
        try:
            response = requests.post(
                f"{self.api_url}/clients/sync",
                timeout=30
            )
            
            if response.status_code == 200:
                self.load_clients()
                QMessageBox.information(self, "Success", "Clients downloaded successfully")
            else:
                QMessageBox.warning(self, "Error", "Failed to download clients")
        
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Download error: {str(e)}")
        
        finally:
            progress.close()
