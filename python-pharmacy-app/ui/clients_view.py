"""
Clients List View - Display downloaded clients
"""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QTableWidget,
    QTableWidgetItem, QLineEdit, QLabel, QComboBox, QMessageBox, QProgressDialog
)
from PyQt6.QtCore import Qt, pyqtSignal, QTimer, QThread
from PyQt6.QtGui import QFont, QColor
import json
import requests
from database.models import Client
from api.backend_client import get_api_client, ensure_authenticated


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
        # Don't set columns here - they will be set dynamically when data is loaded
        self.table.setColumnCount(0)
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
                # Load all clients from local database (not just 'active')
                clients_db = session.query(Client).all()
                
                if not clients_db:
                    self.clients = []
                    self.display_clients([])
                    return
                
                # Convert ORM objects to dictionaries for display
                self.clients = []
                for client in clients_db:
                    client_dict = {
                        "id": str(client.id),
                        "pepfarId": client.pepfar_id or "",
                        "fullName": client.full_name or "",
                        "phone": client.phone_number or "",
                        "email": client.email or "",
                        "address": client.address or "",
                        "gender": client.gender or "",
                        "dateOfBirth": client.date_of_birth.strftime('%Y-%m-%d') if client.date_of_birth else "",
                        "weight": str(client.weight) if client.weight else "",
                        "height": str(client.height) if client.height else "",
                        "bmi": str(client.bmi) if client.bmi else "",
                        "facilityId": client.facility_id or "Unknown",
                        "status": client.status or "Active",
                        "hivStatus": client.hiv_status or "",
                        "artStatus": client.art_status or "",
                        "cd4": str(client.current_cd4) if client.current_cd4 else "",
                        "viralLoad": str(client.current_viral_load) if client.current_viral_load else "",
                        "lastVisitDate": client.last_visit_date.strftime('%Y-%m-%d') if client.last_visit_date else "",
                        "updatedAt": client.updated_locally_at.strftime('%Y-%m-%d %H:%M') if client.updated_locally_at else ""
                    }
                    self.clients.append(client_dict)
                
                self.display_clients(self.clients)
                
            finally:
                session.close()
                
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error loading clients: {str(e)}")
    
    def display_clients(self, clients):
        """Display clients in table with dynamically generated headers"""
        if not clients:
            self.table.setRowCount(0)
            return
        
        # Get all unique keys from all clients
        all_keys = set()
        for client in clients:
            all_keys.update(client.keys())
        
        # Define preferred column order
        preferred_order = ['pepfarId', 'fullName', 'phone', 'facility', 'status', 'updatedAt']
        
        # Sort keys: preferred first, then alphabetically
        sorted_keys = []
        for key in preferred_order:
            if key in all_keys:
                sorted_keys.append(key)
                all_keys.discard(key)
        sorted_keys.extend(sorted(all_keys))
        
        # Set up table with dynamic columns
        self.table.setColumnCount(len(sorted_keys))
        
        # Create human-readable headers
        headers = []
        for key in sorted_keys:
            # Convert camelCase to Title Case
            header = ''.join([' ' + c if c.isupper() else c for c in key]).strip()
            headers.append(header.replace('Pepfar', 'PEPFAR').replace('Id', 'ID'))
        
        self.table.setHorizontalHeaderLabels(headers)
        
        # Adjust column widths
        for i in range(len(sorted_keys)):
            self.table.setColumnWidth(i, 150)
        
        # Populate table with data
        self.table.setRowCount(len(clients))
        
        for row, client in enumerate(clients):
            for col, key in enumerate(sorted_keys):
                value = client.get(key, '')
                # Handle None values
                if value is None:
                    value = ''
                self.table.setItem(row, col, QTableWidgetItem(str(value)))
                
                # Color code status column
                if key == 'status' and col < self.table.columnCount():
                    item = self.table.item(row, col)
                    if str(value) == 'Active':
                        item.setForeground(QColor("green"))
                    elif str(value) == 'Inactive':
                        item.setForeground(QColor("red"))
                    else:
                        item.setForeground(QColor("orange"))
    
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
            # Get auth token from API client
            try:
                api_client = get_api_client()
                if not api_client or not api_client.authenticated:
                    raise ValueError("Not authenticated. Please login first.")
                token = api_client.auth_token
            except Exception as e:
                QMessageBox.warning(self, "Authentication Error", f"Failed to get auth token: {str(e)}")
                progress.close()
                return
            
            import requests
            headers = {
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json"
            }
            
            # Get configured pharmacy code from settings
            from config.settings import settings
            pharmacy_code = settings.PHARMACY_ID
            
            # Use the pharmacyId filter to get clients for this pharmacy
            response = requests.get(
                f"{self.api_url}/api/clients?pharmacyId={pharmacy_code}",
                headers=headers,
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                clients = data.get("data", data.get("clients", []))
                
                if not clients:
                    QMessageBox.information(self, "No Clients", "No clients found for this pharmacy")
                    progress.close()
                    return
                
                # Save to local database
                if self.db_manager:
                    session = self.db_manager.get_session()
                    try:
                        for client_data in clients:
                            pepfar_id = client_data.get('pepfarId') or client_data.get('pepfar_id') or client_data.get('id')
                            if not pepfar_id:
                                continue

                            existing = session.query(Client).filter_by(pepfar_id=pepfar_id).first()
                            if existing:
                                continue

                            facility_id = client_data.get('facilityId') or client_data.get('facilityCode') or 'Unknown'
                            pharmacy_id = client_data.get('pharmacyId') or client_data.get('pharmacyCode') or settings.PHARMACY_ID

                            client = Client(
                                pepfar_id=str(pepfar_id),
                                full_name=client_data.get('fullName') or client_data.get('name') or 'Unknown Client',
                                phone_number=client_data.get('phone'),
                                email=client_data.get('email'),
                                address=client_data.get('address'),
                                gender=client_data.get('gender'),
                                facility_id=str(facility_id),
                                pharmacy_id=str(pharmacy_id),
                                status='active',
                                additional_data=client_data,
                                server_client_id=str(client_data.get('id')) if client_data.get('id') is not None else None
                            )
                            session.add(client)

                        session.commit()
                        self.load_clients()
                        QMessageBox.information(self, "Success", f"Downloaded {len(clients)} clients successfully")
                    except Exception as e:
                        session.rollback()
                        QMessageBox.critical(self, "Database Error", f"Failed to save clients: {str(e)}")
                    finally:
                        session.close()
                else:
                    QMessageBox.warning(self, "Error", "Database manager not available")
            else:
                try:
                    error_msg = response.json().get("message", response.text)
                except:
                    error_msg = response.text
                QMessageBox.warning(self, "Error", f"Failed to download clients: {error_msg}")
        
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Download error: {str(e)}")
        
        finally:
            progress.close()


