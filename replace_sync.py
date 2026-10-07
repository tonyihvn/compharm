#!/usr/bin/env python3
import re

file_path = r"C:\Users\ginte\OneDrive\Desktop\PROJECTS\PYTHON\compharm\python-pharmacy-app\ui\admin_panel.py"

with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# New sync_now function
new_sync_now = '''    def sync_now(self):
        """Trigger immediate sync with detailed report"""
        try:
            # Get the API client and ensure authentication
            api_client = get_api_client()
            if not api_client.authenticate():
                QMessageBox.warning(self, "Error", "Failed to authenticate with backend server.\\nPlease check System Settings.")
                return
            
            # Show progress
            self.logs_display.setText("=" * 70 + "\\n")
            self.logs_display.append("SYNC IN PROGRESS\\n")
            self.logs_display.append("=" * 70 + "\\n\\n")
            
            # Get configured pharmacy ID
            pharmacy_id = settings.PHARMACY_ID
            self.logs_display.append(f"[{datetime.now().strftime('%H:%M:%S')}] Starting sync...\\n")
            self.logs_display.append(f"Pharmacy ID: {pharmacy_id}\\n")
            self.logs_display.append(f"Pharmacy Name: {settings.PHARMACY_NAME}\\n")
            self.logs_display.append(f"Backend Server: {api_client.base_url}\\n\\n")
            
            self.logs_display.append(f"Fetching clients for pharmacy: {pharmacy_id}...\\n")
            
            # Call the backend API with pharmacy_id filter
            clients_data = api_client.get_clients(pharmacy_id=pharmacy_id, limit=1000)
            
            if clients_data is None:
                self.logs_display.append("\\n✗ ERROR: Failed to connect to backend server\\n")
                self.logs_display.append("Troubleshooting:\\n")
                self.logs_display.append("  1. Verify backend server is running\\n")
                self.logs_display.append("  2. Check System Settings credentials\\n")
                self.logs_display.append("  3. Verify network connectivity\\n")
                QMessageBox.critical(self, "Sync Failed", "Could not connect to backend server")
                return
            
            clients = clients_data.get('clients', [])
            
            if len(clients) == 0:
                self.logs_display.append(f"\\n⚠ NO CLIENTS FOUND\\n\\n")
                self.logs_display.append(f"Expected Pharmacy Code: {pharmacy_id}\\n\\n")
                self.logs_display.append("TROUBLESHOOTING:\\n")
                self.logs_display.append(f"1. Verify client exists in backend with PharmacyID = '{pharmacy_id}'\\n")
                self.logs_display.append(f"2. Check Python app System Settings > Pharmacy ID = '{pharmacy_id}'\\n")
                self.logs_display.append("3. Create client in React web UI with matching PharmacyID\\n")
                self.logs_display.append("4. Verify backend server running: " + api_client.base_url + "\\n")
                self.logs_display.append("\\n" + "=" * 70 + "\\n")
                QMessageBox.warning(self, "No Clients", f"No clients found for pharmacy: {pharmacy_id}")
                return
            
            # Display synced clients
            self.logs_display.append(f"\\n✓ Found {len(clients)} client(s):\\n\\n")
            
            for i, client_data in enumerate(clients, 1):
                name = client_data.get('name', 'N/A')
                pepfar_id = client_data.get('pepfarId', 'N/A')
                pharmacy_code = client_data.get('pharmacyCode', 'N/A')
                
                self.logs_display.append(f"  [{i}] {name} | PEPFAR: {pepfar_id} | Pharmacy: {pharmacy_code}\\n")
            
            # Final report
            self.logs_display.append("\\n" + "=" * 70 + "\\n")
            self.logs_display.append("SYNC REPORT\\n")
            self.logs_display.append("=" * 70 + "\\n")
            self.logs_display.append(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\\n")
            self.logs_display.append(f"Pharmacy: {settings.PHARMACY_NAME} ({pharmacy_id})\\n")
            self.logs_display.append(f"Total Clients: {len(clients)}\\n")
            self.logs_display.append("Status: ✓ SUCCESS\\n")
            self.logs_display.append("=" * 70 + "\\n")
            
            # Update last sync time
            self.last_sync_label.setText(f"Last sync: {datetime.now().strftime('%H:%M:%S')} ✓")
            
            # Show success message
            QMessageBox.information(
                self, 
                "Sync Successful", 
                f"Successfully synced {len(clients)} client(s) for pharmacy: {pharmacy_id}"
            )
            
        except Exception as e:
            error_msg = f"Sync error: {str(e)}"
            logger.warning(error_msg)
            self.logs_display.append(f"\\n✗ ERROR: {error_msg}\\n")
            QMessageBox.critical(self, "Sync Error", error_msg)'''

# Replace using regex to match the function properly
pattern = r'    def sync_now\(self\):.*?(?=\n    def )'
replacement = new_sync_now + '\n'

content = re.sub(pattern, replacement, content, flags=re.DOTALL)

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("[OK] sync_now function replaced successfully!")
