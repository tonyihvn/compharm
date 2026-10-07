# Quick Integration Guide - Python App System Settings

## 5-Minute Setup

### Step 1: Prepare Backend Server Credentials
You need admin access to the ComPharm backend server. Create or identify a user account:
- Username: `pharmacy_staff` (or your username)
- Password: (your password from React web UI login)
- Role: Must be admin or pharmacy_staff

**From React Web UI:**
1. Login as admin
2. Go to Users Management
3. Create user with:
   - Role: "pharmacy_staff"
   - PharmacyID: Your pharmacy ID (e.g., PHARM-IKOYI-001)
4. Copy username and password

### Step 2: Launch Python App

```bash
cd python-pharmacy-app
python main.py
```

### Step 3: Open Admin Panel
1. From main window, click "Admin Panel" button
2. Go to "System Settings" tab

### Step 4: Configure Backend Credentials
Click "Advanced Settings" button and fill in:

| Field | Example |
|-------|---------|
| Server URL | `http://localhost:3001` |
| Username | `pharmacy_staff` |
| Password | (from step 1) |
| Pharmacy ID | `PHARM-IKOYI-001` |
| Pharmacy Name | `Ikoyi Pharmacy` |

### Step 5: Test Connection
Click "Test Connection" - you should see:
```
✓ Successfully connected to backend server!
User: pharmacy_staff@compharm.org
Role: pharmacy_staff
```

### Step 6: Save & Restart
1. Click "Save Settings"
2. Restart the application
3. Done! Settings are persistent

## Common Operations

### Download Clients
1. Go to "Clients View"
2. Click "Download New Clients"
3. Clients matching your Pharmacy ID will appear in the table

### Submit Forms
1. Select a client from the Clients View
2. Click "Fill Form"
3. Complete the form
4. Click "Submit"
5. Form data is sent to backend with client's pepfar_id and pharmacy_client_id

### Sync Data
1. Go to Admin Panel → Sync Status
2. Click "Sync Now"
3. View logs to confirm success

### Check Sync Logs
1. Go to Admin Panel → Sync Status
2. Logs show all sync operations and any errors

## Troubleshooting

| Problem | Solution |
|---------|----------|
| "Test Connection Failed" | Check username/password match React web UI login |
| "No Clients Downloaded" | Verify Pharmacy ID is correct and clients exist on server |
| "Download Failed" | Click "Test Connection" to diagnose auth issue |
| "Settings Not Saved" | Check that all required fields are filled |

## Python API Examples

### Using the Backend Client in Your Code

```python
from api.backend_client import get_api_client, ensure_authenticated
from config.settings import settings

# Ensure authentication (uses stored credentials)
if ensure_authenticated():
    api_client = get_api_client()
    
    # Download clients for this pharmacy
    clients = api_client.get_clients(
        pharmacy_id=settings.PHARMACY_ID
    )
    
    if clients:
        for client in clients.get('data', []):
            print(f"Client: {client['name']} - {client['pepfarId']}")
    
    # Submit a form
    submission = {
        'form_id': 'patient-intake',
        'pepfar_id': 'PEPFAR-123',
        'pharmacy_client_id': 'PC-456',
        'data': {
            'temperature': '37.5',
            'symptoms': 'Cough'
        }
    }
    
    result = api_client.submit_form(submission)
    if result:
        print(f"Form submitted successfully")
else:
    print("Authentication failed - check System Settings")
```

### Getting Settings in Your Code

```python
from config.settings import settings

print(f"Backend URL: {settings.CENTRAL_SERVER_URL}")
print(f"Pharmacy ID: {settings.PHARMACY_ID}")
print(f"Pharmacy Name: {settings.PHARMACY_NAME}")
print(f"Sync Interval: {settings.SYNC_INTERVAL} minutes")
```

## Backend Server Requirements

The ComPharm backend server must have:

1. **Running on configured URL** (default: `http://localhost:3001`)
2. **Auth Endpoint**: `POST /api/auth/login` with username/password
3. **Client Endpoints**:
   - `GET /api/clients` - List clients (with optional pharmacy_id filter)
   - `POST /api/clients` - Create client
4. **Form Endpoints**:
   - `GET /api/forms` - List forms
   - `POST /api/submissions` - Submit form
5. **Sync Endpoints**:
   - `POST /api/sync/trigger-sync` - Trigger sync
   - `GET /api/sync/logs` - Get sync logs

## Configuration Files

### .env File (Auto-generated)
Location: `python-pharmacy-app/.env`

```
CENTRAL_SERVER_URL=http://localhost:3001
BACKEND_USERNAME=pharmacy_staff
BACKEND_PASSWORD=password123
PHARMACY_ID=PHARM-IKOYI-001
PHARMACY_NAME=Ikoyi Pharmacy
SYNC_INTERVAL=5
SYNC_BATCH_SIZE=100
```

Edit this file directly if needed, then restart the app.

### Environment Variables
You can also set via environment variables (takes precedence over .env):

```bash
export CENTRAL_SERVER_URL=http://localhost:3001
export BACKEND_USERNAME=pharmacy_staff
export BACKEND_PASSWORD=password123
export PHARMACY_ID=PHARM-IKOYI-001

python main.py
```

## Testing the Integration

### Test 1: Authentication
```python
from api.backend_client import BackendAPIClient

client = BackendAPIClient()
if client.authenticate():
    print("✓ Authentication successful")
    print(f"✓ Token: {client.auth_token[:20]}...")
else:
    print("✗ Authentication failed")
```

### Test 2: Download Clients
```python
from api.backend_client import get_api_client, ensure_authenticated
from config.settings import settings

if ensure_authenticated():
    api_client = get_api_client()
    clients = api_client.get_clients(pharmacy_id=settings.PHARMACY_ID)
    
    if clients and clients.get('data'):
        print(f"✓ Downloaded {len(clients['data'])} clients")
        for c in clients['data'][:3]:
            print(f"  - {c['name']} ({c['pepfarId']})")
    else:
        print("✗ No clients found")
else:
    print("✗ Authentication failed")
```

### Test 3: Submit Form
```python
from api.backend_client import get_api_client, ensure_authenticated

if ensure_authenticated():
    api_client = get_api_client()
    
    submission = {
        'form_id': 'test-form',
        'pepfar_id': 'TEST-001',
        'pharmacy_client_id': 'TEST-PC-001',
        'data': {'test_field': 'test_value'}
    }
    
    result = api_client.submit_form(submission)
    if result and result.get('success'):
        print("✓ Form submitted successfully")
    else:
        print(f"✗ Form submission failed: {result}")
else:
    print("✗ Authentication failed")
```

## Advanced Configuration

### SSL/TLS for HTTPS

For production with HTTPS:

```python
# In api/backend_client.py, modify requests:
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

session = requests.Session()
retry = Retry(connect=3, backoff_factor=0.5)
adapter = HTTPAdapter(max_retries=retry)
session.mount('https://', adapter)

# Use session for requests
response = session.get(url, verify='/path/to/ca-bundle.crt')
```

### Custom Request Headers

Add custom headers for specific backends:

```python
class CustomBackendAPIClient(BackendAPIClient):
    def get_headers(self):
        headers = super().get_headers()
        headers['X-Custom-Header'] = 'value'
        headers['X-API-Version'] = '1.0'
        return headers
```

### Retry Policy

Configure retry behavior:

```python
from api.backend_client import get_api_client

api_client = get_api_client()
api_client.timeout = 60  # Increase timeout for slow networks
# Retries are automatic on 401 responses
```

## Logs & Debugging

### Enable Debug Logging

```python
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger('api.backend_client')
logger.setLevel(logging.DEBUG)

# Now all API calls will be logged
```

### Check Logs

Logs are saved to: `~/.pharmacy/app.log`

```bash
# On Linux/Mac
tail -f ~/.pharmacy/app.log

# On Windows PowerShell
Get-Content $env:USERPROFILE\.pharmacy\app.log -Wait
```

### View Sync Logs in UI
Admin Panel → Sync Status tab shows all sync operations

## Production Deployment

### Security Checklist

- [ ] Use HTTPS URLs (https://api.compharm.org)
- [ ] Store credentials in environment variables, not .env file
- [ ] Use strong passwords (min 12 characters)
- [ ] Enable logging and audit trails
- [ ] Regularly update credentials
- [ ] Test connection periodically
- [ ] Monitor sync logs for errors
- [ ] Keep app and dependencies updated

### Configuration for Production

```bash
export CENTRAL_SERVER_URL=https://api.compharm.org
export BACKEND_USERNAME=ikoyi_pharmacy
export BACKEND_PASSWORD=$(aws secretsmanager get-secret-value --secret-id backend-password --query SecretString --output text)
export PHARMACY_ID=PHARM-IKOYI-001
export SYNC_INTERVAL=30
DEBUG=False

python main.py
```

## Support Resources

- **Documentation**: See `PYTHON_APP_SYSTEM_SETTINGS.md` for detailed docs
- **API Reference**: See `COMPLETE_SYSTEM_GUIDE.md` for API endpoints
- **Testing Guide**: See `TESTING_GUIDE.md` for test procedures
- **Backend API**: Check backend server logs for API errors
- **Logs**: Check `~/.pharmacy/app.log` for application errors

## Next Steps

1. ✅ Setup backend credentials (System Settings)
2. ✅ Download clients (Clients View)
3. ✅ Fill and submit forms (Form View)
4. ✅ Monitor sync status (Admin Panel → Sync Status)
5. ✅ Review logs and troubleshoot (Admin Panel)

Congratulations! Your Python Pharmacy App is now integrated with the ComPharm backend server.
