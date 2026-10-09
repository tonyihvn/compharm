"""
Enhanced Client List View - Advanced table with column management and actions
"""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QTableWidget,
    QTableWidgetItem, QLineEdit, QLabel, QComboBox, QMessageBox, 
    QProgressDialog, QMenu, QHeaderView, QAbstractItemView, QDialog,
    QCheckBox, QScrollArea, QFrame
)
from PyQt6.QtCore import Qt, pyqtSignal, QTimer, QPoint
from PyQt6.QtGui import QFont, QColor, QIcon
import json
import sqlite3
import logging
from pathlib import Path
from database.models import Client

logger = logging.getLogger(__name__)


class ColumnVisibilityMenu(QMenu):
    """Context menu for managing column visibility"""
    
    def __init__(self, column_names, visible_columns, parent=None):
        super().__init__(parent)
        self.column_names = column_names
        self.visible_columns = set(visible_columns)
        self.checkboxes = {}
        self.visibility_changed = False
        
        # Add checkboxes for each column
        for col_name in column_names:
            checkbox = QCheckBox(col_name)
            checkbox.setChecked(col_name in self.visible_columns)
            checkbox.toggled.connect(self.on_column_toggled)
            
            action = self.addAction("")
            action.setCheckable(False)
            action.setDefaultWidget(checkbox)
            
            self.checkboxes[col_name] = checkbox
        
        self.addSeparator()
        
        # Show All option
        show_all_action = self.addAction("Show All Columns")
        show_all_action.triggered.connect(self.show_all)
        
        # Hide All option (except Action)
        hide_all_action = self.addAction("Hide All Columns")
        hide_all_action.triggered.connect(self.hide_all)
    
    def on_column_toggled(self, checked):
        """Handle column checkbox toggle"""
        self.visibility_changed = True
        for col_name, checkbox in self.checkboxes.items():
            if checkbox.isChecked():
                self.visible_columns.add(col_name)
            else:
                self.visible_columns.discard(col_name)
    
    def show_all(self):
        """Show all columns"""
        self.visibility_changed = True
        for checkbox in self.checkboxes.values():
            checkbox.setChecked(True)
    
    def hide_all(self):
        """Hide all columns except Action"""
        self.visibility_changed = True
        for col_name, checkbox in self.checkboxes.items():
            if col_name != "Action":
                checkbox.setChecked(False)
    
    def get_visible_columns(self):
        """Get list of visible columns"""
        return list(self.visible_columns)


class ActionButtonWidget(QWidget):
    """Widget containing action dropdown menu for each row"""
    
    action_triggered = pyqtSignal(str, dict)  # action_name, client_data
    
    def __init__(self, client_data, parent=None):
        super().__init__(parent)
        self.client_data = client_data
        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        
        self.action_btn = QPushButton("Actions ▼")
        self.action_btn.setStyleSheet("""
            QPushButton {
                background-color: #2196F3;
                color: white;
                padding: 5px 10px;
                border-radius: 3px;
                border: none;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #1976D2;
            }
        """)
        self.action_btn.clicked.connect(self.show_menu)
        layout.addWidget(self.action_btn)
        self.setLayout(layout)
    
    def show_menu(self):
        """Show action menu"""
        menu = QMenu(self)
        
        fill_form_action = menu.addAction("Fill Form")
        fill_form_action.triggered.connect(lambda: self.action_triggered.emit("fill_form", self.client_data))
        
        view_details_action = menu.addAction("View Details")
        view_details_action.triggered.connect(lambda: self.action_triggered.emit("view_details", self.client_data))
        
        edit_action = menu.addAction("Edit")
        edit_action.triggered.connect(lambda: self.action_triggered.emit("edit", self.client_data))
        
        menu.addSeparator()
        
        delete_action = menu.addAction("Delete")
        # QAction doesn't support setForeground; styling is handled by the menu's appearance
        # Just connect the action without color styling
        delete_action.triggered.connect(lambda: self.action_triggered.emit("delete", self.client_data))
        
        menu.popup(self.action_btn.mapToGlobal(QPoint(0, self.action_btn.height())))


class EnhancedClientListView(QWidget):
    """Enhanced client list view with column management and inline actions"""
    
    client_selected = pyqtSignal(dict)
    action_requested = pyqtSignal(str, dict)  # action_name, client_data
    
    # Action signals
    fill_form_requested = pyqtSignal(dict)
    view_details_requested = pyqtSignal(dict)
    edit_client_requested = pyqtSignal(dict)
    delete_client_requested = pyqtSignal(str)  # client_id
    
    def __init__(self, api_url, current_user, db_manager=None):
        super().__init__()
        self.api_url = api_url
        self.current_user = current_user
        self.db_manager = db_manager
        self.clients = []
        self.all_column_names = []
        self.visible_columns = []
        self.column_to_client_index = {}  # Map display column index to client data key
        
        # Load column visibility settings
        self.load_column_settings()
        
        self.init_ui()
        
        # Load cached clients from database immediately on startup
        self.load_clients()
    
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
        self.table.setColumnCount(0)
        self.table.itemClicked.connect(self.on_client_selected)
        self.table.setAlternatingRowColors(True)
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        
        # Enable right-click on headers
        self.table.horizontalHeader().setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.table.horizontalHeader().customContextMenuRequested.connect(self.show_column_menu)
        
        layout.addWidget(self.table)
        
        # Info label
        self.info_label = QLabel("")
        layout.addWidget(self.info_label)
        
        self.setLayout(layout)
    
    def load_column_settings(self):
        """Load column visibility settings from database"""
        try:
            db_path = Path.cwd() / "column_settings.db"
            conn = sqlite3.connect(str(db_path))
            cursor = conn.cursor()
            
            # Create table if not exists
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS column_visibility (
                    id INTEGER PRIMARY KEY,
                    column_name TEXT UNIQUE,
                    is_visible BOOLEAN DEFAULT 1
                )
            """)
            conn.commit()
            
            # Load settings
            cursor.execute("SELECT column_name, is_visible FROM column_visibility")
            settings = {row[0]: bool(row[1]) for row in cursor.fetchall()}
            self.column_visibility_settings = settings
            
            conn.close()
        except Exception as e:
            print(f"Error loading column settings: {e}")
            self.column_visibility_settings = {}
    
    def save_column_settings(self):
        """Save column visibility settings to database"""
        try:
            db_path = Path.cwd() / "column_settings.db"
            conn = sqlite3.connect(str(db_path))
            cursor = conn.cursor()
            
            for col_name, is_visible in self.column_visibility_settings.items():
                cursor.execute(
                    "INSERT OR REPLACE INTO column_visibility (column_name, is_visible) VALUES (?, ?)",
                    (col_name, is_visible)
                )
            conn.commit()
            conn.close()
        except Exception as e:
            print(f"Error saving column settings: {e}")
    
    def show_column_menu(self, position):
        """Show column visibility context menu"""
        menu = ColumnVisibilityMenu(self.all_column_names, self.visible_columns, self)
        menu.exec(self.table.horizontalHeader().mapToGlobal(position))
        
        if menu.visibility_changed:
            self.visible_columns = menu.get_visible_columns()
            # Save settings
            for col_name in self.all_column_names:
                self.column_visibility_settings[col_name] = col_name in self.visible_columns
            self.save_column_settings()
            # Refresh display
            self.display_clients(self.clients)
    
    def load_clients(self):
        """Load clients from local database"""
        try:
            if self.db_manager is None:
                logger.debug("Database manager not available - skipping client load on startup")
                self.display_clients([])
                return
            
            session = self.db_manager.get_session()
            try:
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
                logger.info(f"Loaded {len(self.clients)} clients from database")
                
            finally:
                session.close()
                
        except Exception as e:
            logger.error(f"Error loading clients: {str(e)}")
            self.display_clients([])
    
    def display_clients(self, clients):
        """Display clients in table with enhanced column management"""
        if not clients:
            self.table.setRowCount(0)
            self.table.setColumnCount(0)
            self.info_label.setText(f"No clients found")
            return
        
        # Get all unique keys from all clients
        all_keys = set()
        for client in clients:
            all_keys.update(client.keys())
        
        # Define preferred column order
        preferred_order = ['pepfarId', 'fullName', 'phone', 'facilityId', 'status', 'updatedAt']
        
        # Sort keys: preferred first, then alphabetically
        sorted_keys = []
        for key in preferred_order:
            if key in all_keys:
                sorted_keys.append(key)
                all_keys.discard(key)
        sorted_keys.extend(sorted(all_keys))
        
        self.all_column_names = sorted_keys.copy()
        
        # Load visibility settings, defaulting to True for new columns
        visible_columns = []
        for col_name in sorted_keys:
            if col_name in self.column_visibility_settings:
                if self.column_visibility_settings[col_name]:
                    visible_columns.append(col_name)
            else:
                # Default: show preferred columns, hide others
                if col_name in preferred_order:
                    visible_columns.append(col_name)
                    self.column_visibility_settings[col_name] = True
                else:
                    self.column_visibility_settings[col_name] = False
        
        self.visible_columns = visible_columns
        
        # Add Action column
        visible_columns_with_action = visible_columns + ["Action"]
        
        # Set up table with visible columns + Action column
        self.table.setColumnCount(len(visible_columns_with_action))
        
        # Create human-readable headers
        headers = []
        self.column_to_client_index = {}
        for i, key in enumerate(visible_columns_with_action):
            if key == "Action":
                headers.append("Action")
                self.column_to_client_index[i] = None
            else:
                # Convert camelCase to Title Case
                header = ''.join([' ' + c if c.isupper() else c for c in key]).strip()
                headers.append(header.replace('Pepfar', 'PEPFAR').replace('Id', 'ID'))
                self.column_to_client_index[i] = key
        
        self.table.setHorizontalHeaderLabels(headers)
        
        # Adjust column widths
        for i in range(len(visible_columns_with_action)):
            if visible_columns_with_action[i] == "Action":
                self.table.setColumnWidth(i, 120)
            else:
                self.table.setColumnWidth(i, 150)
        
        # Populate table with data
        self.table.setRowCount(len(clients))
        
        for row, client in enumerate(clients):
            # Populate visible columns
            for col, key in enumerate(visible_columns):
                value = client.get(key, '')
                if value is None:
                    value = ''
                item = QTableWidgetItem(str(value))
                self.table.setItem(row, col, item)
                
                # Color code status column
                if key == 'status':
                    if str(value) == 'Active':
                        item.setForeground(QColor("green"))
                    elif str(value) == 'Inactive':
                        item.setForeground(QColor("red"))
                    else:
                        item.setForeground(QColor("orange"))
            
            # Add Action button in last column
            action_col = len(visible_columns)
            action_widget = ActionButtonWidget(client, self)
            action_widget.action_triggered.connect(self.on_action_triggered)
            self.table.setCellWidget(row, action_col, action_widget)
        
        self.info_label.setText(f"Showing {len(clients)} clients")
    
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
            self.client_selected.emit(self.selected_client)
    
    def on_action_triggered(self, action_name, client_data):
        """Handle action menu selection"""
        if action_name == "fill_form":
            self.fill_form_requested.emit(client_data)
        elif action_name == "view_details":
            self.view_details_requested.emit(client_data)
        elif action_name == "edit":
            self.edit_client_requested.emit(client_data)
        elif action_name == "delete":
            reply = QMessageBox.question(
                self, "Delete Client",
                f"Are you sure you want to delete {client_data.get('fullName')}?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            if reply == QMessageBox.StandardButton.Yes:
                self.delete_client_requested.emit(client_data.get("id"))
        
        self.action_requested.emit(action_name, client_data)
    
    def download_clients(self):
        """Download new clients from server"""
        progress = QProgressDialog("Downloading clients...", "Cancel", 0, 0, self)
        progress.setWindowModality(Qt.WindowModality.WindowModal)
        progress.show()
        
        try:
            from api.backend_client import get_api_client
            api_client = get_api_client()
            if not api_client or not api_client.authenticated:
                raise ValueError("Not authenticated. Please login first.")
            token = api_client.auth_token
            
            import requests
            headers = {
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json"
            }
            
            from config.settings import settings
            pharmacy_code = settings.PHARMACY_ID
            
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
