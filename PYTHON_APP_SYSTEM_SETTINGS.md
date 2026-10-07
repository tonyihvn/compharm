# Python App System Settings & Backend API Integration

## Overview

The Python Pharmacy App now includes a complete system settings interface that allows users to configure backend server credentials, pharmacy information, and synchronization settings. This replaces hardcoded settings and enables dynamic authentication with the ComPharm backend server.

## Architecture

### 1. Configuration Management (`config/settings.py`)

The application settings are centralized in a Pydantic Settings class that supports environment variables and .env files.

**New Fields Added:**
- `BACKEND_USERNAME`: Backend server username
- `BACKEND_PASSWORD`: Backend server password

**Usage:**
```python
from config.settings import settings

# Access settings
print(settings.CENTRAL_SERVER_URL)
print(settings.PHARMACY_ID)
print(settings.BACKEND_USERNAME)
```

### 2. Backend API Client (`api/backend_client.py`)

A new `BackendAPIClient` class handles all communication with the backend server with automatic authentication.

**Features:**
- Automatic token-based authentication using stored credentials
- Automatic token refresh on 401 responses
- Error handling and connection error management
- Structured API methods for all common operations
- Logging for debugging

**Class Methods:**

```python
# Authentication
api_client.authenticate() -> bool
api_client.get_headers() -> Dict[str, str]
api_client.request(method, endpoint, data=None, **kwargs) -> Optional[Dict]

# Client Management
api_client.get_clients(page=1, limit=50, **kwargs) -> Optional[Dict]
api_client.get_client(client_id: str) -> Optional[Dict]
api_client.create_client(data: Dict) -> Optional[Dict]
api_client.update_client(client_id: str, data: Dict) -> Optional[Dict]
api_client.delete_client(client_id: str) -> Optional[Dict]

# Form Management
api_client.get_forms() -> Optional[Dict]
api_client.submit_form(submission_data: Dict) -> Optional[Dict]
api_client.get_submissions(page=1, limit=50, **kwargs) -> Optional[Dict]

# Field Management
api_client.get_fields() -> Optional[Dict]
api_client.create_field(data: Dict) -> Optional[Dict]
api_client.update_field(field_id: str, data: Dict) -> Optional[Dict]
api_client.delete_field(field_id: str) -> Optional[Dict]

# Synchronization
api_client.trigger_sync() -> Optional[Dict]
api_client.get_sync_logs() -> Optional[Dict]
api_client.get_sync_status() -> Optional[Dict]
```

**Usage Examples:**

```python
from api.backend_client import get_api_client, ensure_authenticated

# Ensure client is authenticated
if ensure_authenticated():
    api_client = get_api_client()
    
    # Download clients
    clients = api_client.get_clients(pharmacy_id='PHARM-001')
    
    # Submit form
    submission = {
        'form_id': 'contact-form',
        'pepfar_id': 'PEPFAR-123',
        'pharmacy_client_id': 'PC-456',
        'data': { 'name': 'John', 'age': 30 }
    }
    result = api_client.submit_form(submission)
else:
    print("Authentication failed - check System Settings credentials")
```

### 3. System Settings Dialog (`ui/system_settings.py`)

A comprehensive PyQt6 dialog for managing all system configuration.

**Sections:**

1. **Backend Server Configuration**
   - Server URL
   - Username
   - Password
   - Test Connection button

2. **Pharmacy Configuration**
   - Pharmacy ID
   - Pharmacy Name

3. **Synchronization Settings**
   - Auto Sync Interval (minutes)
   - Sync Batch Size

**Features:**
- Save settings to .env file
- Reset to defaults
- Test connection with validation
- User-friendly error messages

**Opening the Dialog:**

From Admin Panel → System Settings → Click "Advanced Settings"

Or programmatically:
```python
from ui.system_settings import SystemSettingsDialog

dialog = SystemSettingsDialog(parent_window)
if dialog.exec():
    print("Settings saved")
```

### 4. Admin Panel Integration

The Admin Panel now features a redesigned System Settings tab:

- **Quick Settings Section**: Basic configuration options
- **Advanced Settings Button**: Opens the full SystemSettingsDialog
- Connection status and credential management
- Test connection functionality

**Path in UI:** Admin Panel → System Settings Tab

## Implementation Details

### API Authentication Flow

1. **First Request:**
   - BackendAPIClient checks if authenticated
   - If not, calls `authenticate()` using stored credentials
   - Receives JWT token from backend
   - Stores token for subsequent requests

2. **Subsequent Requests:**
   - Uses stored token in `Authorization: Bearer <token>` header
   - If server returns 401, re-authenticates automatically
   - Retries the original request with new token

3. **Error Handling:**
   - Connection errors are logged and None is returned
   - Authentication failures log warning
   - Timeout errors are caught and logged
   - All errors are gracefully handled without crashing

### Credentials Storage

Credentials are stored in a `.env` file in the application root directory:

```
CENTRAL_SERVER_URL=http://localhost:3001
BACKEND_USERNAME=pharmacy_staff
BACKEND_PASSWORD=secret_password
PHARMACY_ID=PHARM-IKOYI-001
PHARMACY_NAME=Ikoyi Pharmacy
SYNC_INTERVAL=5
SYNC_BATCH_SIZE=100
AUTO_SYNC_ENABLED=True
THEME=light
DEBUG=False
```

**Security Note:** In production, consider:
- Using environment variables instead of .env file
- Encrypting credentials in database
- Using system keyring for secure storage
- Implementing role-based credential management

### Updated Modules

**1. clients_view.py**
- Replaced direct HTTP requests with BackendAPIClient
- Automatic authentication before API calls
- Better error messages for auth failures
- Updated field names (pepfarId → pepfarId, facilityCode → facilityId)

**2. admin_panel.py**
- New import: `from .system_settings import SystemSettingsDialog`
- New method: `open_system_settings_dialog()`
- System Settings tab now shows "Advanced Settings" button
- Better organization of settings sections

## Usage Workflow

### Initial Setup

1. Launch Python Pharmacy App
2. Login with local credentials
3. Go to Admin Panel → System Settings
4. Click "Advanced Settings"
5. Fill in:
   - Backend Server URL (e.g., `http://localhost:3001`)
   - Backend Username (e.g., pharmacy_staff user from React web UI)
   - Backend Password
   - Pharmacy ID (e.g., PHARM-IKOYI-001)
   - Pharmacy Name (e.g., Ikoyi Pharmacy)
   - Sync Interval (default: 5 minutes)
6. Click "Test Connection" to verify settings
7. Click "Save Settings"

### Downloading Clients

1. Go to Clients View
2. Click "Download New Clients"
3. System automatically:
   - Authenticates using stored credentials
   - Filters clients by configured Pharmacy ID
   - Downloads and saves to local database
   - Displays downloaded count

### Syncing Data

1. Go to Admin Panel → Sync Status
2. Click "Sync Now"
3. System automatically:
   - Authenticates using stored credentials
   - Uploads pending form submissions
   - Downloads updated client data
   - Logs all sync activities

## API Response Handling

### Successful Client Download

```python
{
    "success": True,
    "data": [
        {
            "id": "client-uuid",
            "pepfarId": "PEPFAR-123",
            "name": "John Doe",
            "phone": "+234-123-456",
            "email": "john@example.com",
            "address": "123 Main St",
            "gender": "M",
            "facilityId": "FAC-001",
            "pharmacyId": "PHARM-001",
            "pharmacyClientId": "PC-123",
            "status": "active"
        }
    ],
    "total": 1,
    "page": 1,
    "limit": 50
}
```

### Authentication Error Response

```python
{
    "success": False,
    "error": "Invalid credentials",
    "message": "Username or password incorrect"
}
```

### Connection Error Handling

```python
# In BackendAPIClient.authenticate()
except requests.exceptions.ConnectionError:
    logger.error(f"Cannot connect to backend server at {self.base_url}")
    return False  # Graceful failure
```

## Error Messages & Troubleshooting

### "Authentication Error - Failed to authenticate with backend server"
**Cause:** Credentials in System Settings are incorrect
**Solution:** 
1. Verify username and password in React web UI
2. Go to Admin Panel → System Settings
3. Update credentials
4. Click "Test Connection" to verify
5. Retry download

### "Configuration Error - Pharmacy ID not configured"
**Cause:** Pharmacy ID field is empty
**Solution:**
1. Go to Admin Panel → System Settings
2. Enter your Pharmacy ID (e.g., PHARM-IKOYI-001)
3. Save settings
4. Retry

### "Connection Error - Cannot connect to backend server"
**Cause:** Backend server is not running or URL is incorrect
**Solution:**
1. Verify backend server is running
2. Check CENTRAL_SERVER_URL in System Settings
3. Click "Test Connection" to diagnose
4. Check network connectivity

### "No Clients Found for This Pharmacy"
**Cause:** No clients exist for the configured Pharmacy ID in the backend
**Solution:**
1. Verify Pharmacy ID matches what's in React web UI
2. Check if clients were created in React web UI for this pharmacy
3. Contact admin to verify data exists on server

## Testing the Integration

### Manual Testing

```python
# Test API client authentication
from api.backend_client import BackendAPIClient
from config.settings import settings

client = BackendAPIClient()
if client.authenticate():
    print("✓ Authentication successful")
    
    # Test downloading clients
    clients = client.get_clients(pharmacy_id='PHARM-001')
    if clients:
        print(f"✓ Retrieved {clients['total']} clients")
else:
    print("✗ Authentication failed")
    print(f"URL: {settings.CENTRAL_SERVER_URL}")
    print(f"Username: {settings.BACKEND_USERNAME}")
```

### Test Cases

1. **Credentials Configuration**
   - Save credentials via System Settings dialog
   - Verify .env file is created
   - Verify settings are loaded on app restart

2. **Authentication**
   - Test with valid credentials
   - Test with invalid credentials (should show error)
   - Test connection after credential change

3. **Client Download**
   - Download clients for known pharmacy
   - Verify clients appear in Clients View
   - Check that dynamic headers are generated correctly

4. **Form Submission**
   - Fill and submit a form
   - Verify submission reaches backend
   - Check sync logs show successful sync

5. **Error Handling**
   - Disconnect network, try sync (should show error)
   - Change credentials to invalid, try download (should prompt for retry)
   - Test with server offline (should fail gracefully)

## Configuration Examples

### Local Development
```ini
CENTRAL_SERVER_URL=http://localhost:3001
BACKEND_USERNAME=pharmacy_staff
BACKEND_PASSWORD=password123
PHARMACY_ID=test-pharmacy-001
PHARMACY_NAME=Test Pharmacy
SYNC_INTERVAL=5
SYNC_BATCH_SIZE=100
```

### Remote Server
```ini
CENTRAL_SERVER_URL=https://api.compharm.org
BACKEND_USERNAME=ikoyi_pharmacy
BACKEND_PASSWORD=secure_password
PHARMACY_ID=PHARM-IKOYI-001
PHARMACY_NAME=Ikoyi Pharmacy
SYNC_INTERVAL=15
SYNC_BATCH_SIZE=50
```

### Production
```ini
CENTRAL_SERVER_URL=https://api.compharm.org
BACKEND_USERNAME=${BACKEND_USERNAME}  # From environment
BACKEND_PASSWORD=${BACKEND_PASSWORD}  # From environment
PHARMACY_ID=${PHARMACY_ID}             # From environment
PHARMACY_NAME=${PHARMACY_NAME}         # From environment
SYNC_INTERVAL=30
SYNC_BATCH_SIZE=200
DEBUG=False
```

## Security Considerations

1. **Credential Storage**: Currently stored in plaintext .env file
   - In production, use environment variables
   - Consider database encryption
   - Use OS-level credential storage (Windows Credential Manager, etc.)

2. **Token Security**
   - JWT tokens are stored in memory
   - Tokens are not written to logs
   - Tokens expire and are refreshed automatically

3. **HTTPS**: Always use HTTPS in production
   - Configure CENTRAL_SERVER_URL with https://
   - Implement SSL certificate validation

4. **Audit Trail**: All API requests are logged
   - Enable DEBUG mode to see detailed logs
   - Review sync logs in Admin Panel

## Future Enhancements

1. **Credential Encryption**: 
   - Encrypt credentials in .env file or database
   - Use Python cryptography library

2. **OAuth/SSO Integration**:
   - Connect to organization's OAuth provider
   - Automatic credential refresh

3. **Multi-user Support**:
   - Store credentials per user
   - Role-based credential management

4. **Offline Mode**:
   - Queue operations when offline
   - Auto-sync when connection restored

5. **Advanced Logging**:
   - Detailed audit trail
   - User action logging
   - Security event alerts

## API Documentation

See [COMPLETE_SYSTEM_GUIDE.md](./COMPLETE_SYSTEM_GUIDE.md) for full API documentation and examples.

## Support

For issues or questions:
1. Check error messages and logs
2. Review troubleshooting section above
3. Test connection in System Settings
4. Check backend server logs
5. Review API response in browser developer tools (for debugging)
