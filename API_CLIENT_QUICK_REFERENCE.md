# API Client Quick Reference

## Global Usage

```python
from api.backend_client import get_api_client, ensure_authenticated
from config.settings import settings

# Ensure authentication
if ensure_authenticated():
    client = get_api_client()
    # Use client...
else:
    print("Authentication failed")
```

## Client CRUD Operations

### List Clients
```python
# Get all clients
clients = client.get_clients(page=1, limit=50)

# Get clients for specific pharmacy
clients = client.get_clients(pharmacy_id='PHARM-001')

# Response format
# {
#   'data': [
#     {'id': '...', 'name': '...', 'pepfarId': '...', ...}
#   ],
#   'total': 100,
#   'page': 1,
#   'limit': 50
# }
```

### Get Single Client
```python
client_data = client.get_client('client-uuid-123')
# Returns: {'id': '...', 'name': '...', 'pepfarId': '...', ...}
```

### Create Client
```python
new_client = {
    'name': 'John Doe',
    'pepfarId': 'PEPFAR-123',
    'phone': '+234-123-456',
    'email': 'john@example.com',
    'facilityId': 'FAC-001',
    'pharmacyId': 'PHARM-001'
}
result = client.create_client(new_client)
# Returns: {'id': 'new-uuid', ...full client data...}
```

### Update Client
```python
update_data = {
    'name': 'Jane Doe',
    'phone': '+234-987-654'
}
result = client.update_client('client-uuid-123', update_data)
```

### Delete Client
```python
result = client.delete_client('client-uuid-123')
# Returns: {'success': True} or {'success': False, 'error': '...'}
```

## Form Operations

### List Forms
```python
forms = client.get_forms()
# Returns: {'data': [{'id': '...', 'name': '...', 'fields': [...]}, ...]}
```

### Submit Form
```python
submission = {
    'form_id': 'patient-intake',
    'pepfar_id': 'PEPFAR-123',
    'pharmacy_client_id': 'PC-456',
    'data': {
        'temperature': '37.5',
        'symptoms': 'Cough',
        'diagnosis': 'Common Cold'
    }
}
result = client.submit_form(submission)
```

### Get Form Submissions
```python
submissions = client.get_submissions(page=1, limit=50)
# Returns: {'data': [...], 'total': ..., 'page': 1, 'limit': 50}
```

## Field Management

### List Fields
```python
fields = client.get_fields()
# Returns: {'data': [{'id': '...', 'name': '...', 'type': '...', ...}]}
```

### Create Field
```python
new_field = {
    'name': 'Temperature',
    'field_name': 'temperature',
    'field_type': 'number',
    'required': True,
    'order_index': 1
}
result = client.create_field(new_field)
```

### Update Field
```python
update_data = {'required': False}
result = client.update_field('field-uuid', update_data)
```

### Delete Field
```python
result = client.delete_field('field-uuid')
```

## Synchronization

### Trigger Sync
```python
result = client.trigger_sync()
# Returns: {'success': True, 'message': '...', 'synced_items': 42}
```

### Get Sync Logs
```python
logs = client.get_sync_logs()
# Returns: {'data': [{'created_at': '...', 'sync_type': '...', ...}]}
```

### Get Sync Status
```python
status = client.get_sync_status()
# Returns: {'last_sync': '...', 'next_sync': '...', 'status': 'idle'}
```

## Error Handling

```python
from api.backend_client import get_api_client, ensure_authenticated

try:
    if not ensure_authenticated():
        print("Failed to authenticate")
        return
    
    client = get_api_client()
    clients = client.get_clients()
    
    if clients is None:
        print("Failed to retrieve clients")
        return
    
    print(f"Got {clients['total']} clients")

except Exception as e:
    print(f"Unexpected error: {e}")
```

## Configuration Access

```python
from config.settings import settings

# Access settings
print(f"Backend URL: {settings.CENTRAL_SERVER_URL}")
print(f"Pharmacy ID: {settings.PHARMACY_ID}")
print(f"Pharmacy Name: {settings.PHARMACY_NAME}")
print(f"Sync Interval: {settings.SYNC_INTERVAL}")
print(f"Timeout: {settings.API_TIMEOUT}")

# Settings are read-only after initialization
# To change: Update in System Settings dialog or .env file
```

## System Settings Dialog

```python
from ui.system_settings import SystemSettingsDialog

# Open settings dialog
dialog = SystemSettingsDialog(parent_window)
if dialog.exec():
    print("Settings saved")
    # App needs restart to load new settings from .env
else:
    print("User cancelled settings dialog")
```

## Advanced Examples

### Download and Process Clients

```python
from api.backend_client import get_api_client, ensure_authenticated
from config.settings import settings

def download_and_process():
    if not ensure_authenticated():
        print("Auth failed")
        return False
    
    client = get_api_client()
    
    # Download clients for this pharmacy
    result = client.get_clients(pharmacy_id=settings.PHARMACY_ID)
    
    if not result or not result.get('data'):
        print("No clients to download")
        return False
    
    # Process each client
    for client_data in result['data']:
        print(f"Processing: {client_data['name']}")
        # Save to database, update UI, etc.
    
    print(f"Processed {len(result['data'])} clients")
    return True
```

### Submit Form with Error Handling

```python
from api.backend_client import get_api_client, ensure_authenticated

def submit_patient_form(patient_id, form_data):
    if not ensure_authenticated():
        return {'success': False, 'error': 'Authentication failed'}
    
    client = get_api_client()
    
    submission = {
        'form_id': 'patient-intake',
        'pepfar_id': patient_id,
        'pharmacy_client_id': patient_id,  # Usually different
        'data': form_data
    }
    
    result = client.submit_form(submission)
    
    if result is None:
        return {'success': False, 'error': 'Network error'}
    
    if not result.get('success'):
        return {'success': False, 'error': result.get('error')}
    
    return {'success': True, 'submission_id': result.get('id')}
```

### Sync and Handle Errors

```python
from api.backend_client import get_api_client, ensure_authenticated
import time

def sync_with_retry(max_retries=3):
    for attempt in range(max_retries):
        try:
            if not ensure_authenticated():
                print(f"Attempt {attempt+1}: Authentication failed")
                if attempt < max_retries - 1:
                    time.sleep(5)
                continue
            
            client = get_api_client()
            result = client.trigger_sync()
            
            if result and result.get('success'):
                print(f"Sync successful: {result.get('synced_items')} items")
                return True
            else:
                print(f"Sync failed: {result.get('error', 'Unknown error')}")
        
        except Exception as e:
            print(f"Error during sync: {e}")
        
        if attempt < max_retries - 1:
            wait_time = (attempt + 1) * 5
            print(f"Retrying in {wait_time} seconds...")
            time.sleep(wait_time)
    
    return False
```

## Common Response Patterns

### Success Response
```python
{
    'success': True,
    'data': {...},  # or [...]
    'message': 'Operation completed'
}
```

### Error Response
```python
{
    'success': False,
    'error': 'error_code',
    'message': 'Detailed error message'
}
```

### List Response
```python
{
    'data': [...],
    'total': 100,
    'page': 1,
    'limit': 50,
    'success': True
}
```

## Logging

```python
import logging

# Enable debug logging
logging.basicConfig(level=logging.DEBUG)

# API client logs go to: ~/.pharmacy/app.log
# View with:
# tail -f ~/.pharmacy/app.log (Linux/Mac)
# Get-Content ~/.pharmacy/app.log -Wait (Windows)
```

## Testing

```python
# Quick test of API client
from api.backend_client import BackendAPIClient
from config.settings import settings

client = BackendAPIClient()

print(f"Testing connection to: {settings.CENTRAL_SERVER_URL}")
print(f"Username: {settings.BACKEND_USERNAME}")

if client.authenticate():
    print("✓ Authentication successful")
    
    clients = client.get_clients(pharmacy_id=settings.PHARMACY_ID)
    if clients:
        print(f"✓ Retrieved {clients['total']} clients")
    else:
        print("✗ No clients retrieved")
else:
    print("✗ Authentication failed")
```

## Troubleshooting

### "No auth token available"
```python
# Solution: Check and save System Settings
from config.settings import settings
print(f"Username: {settings.BACKEND_USERNAME}")
print(f"Password configured: {'Yes' if settings.BACKEND_PASSWORD else 'No'}")

# Go to Admin Panel → System Settings to configure
```

### "Cannot connect to backend server"
```python
# Solution: Verify URL and network
from config.settings import settings
print(f"Backend URL: {settings.CENTRAL_SERVER_URL}")

# Try: curl http://localhost:3001/api/health (or equivalent)
```

### "Invalid credentials"
```python
# Solution: Verify username and password
# In React web UI, login with same credentials
# If successful there but not here, check spelling/spacing
```

### API returns None
```python
# Solution: Check logs
import logging
logging.basicConfig(level=logging.DEBUG)

# All errors logged to ~/.pharmacy/app.log
# Check logs for detailed error messages
```

## Best Practices

1. **Always ensure authentication first**
   ```python
   if ensure_authenticated():
       client = get_api_client()
   ```

2. **Check for None responses**
   ```python
   data = client.get_clients()
   if data is None:
       # Connection error
   elif data.get('data') is None:
       # API error
   ```

3. **Handle errors gracefully**
   ```python
   try:
       result = client.submit_form(...)
   except Exception as e:
       logger.error(f"Form submission failed: {e}")
   ```

4. **Use settings for configuration**
   ```python
   from config.settings import settings
   
   pharmacy_id = settings.PHARMACY_ID  # Not hardcoded
   ```

5. **Log important operations**
   ```python
   logger.info(f"Downloaded {len(clients)} clients")
   logger.error(f"Sync failed: {error}")
   ```

## See Also

- [PYTHON_APP_SYSTEM_SETTINGS.md](./PYTHON_APP_SYSTEM_SETTINGS.md) - Full documentation
- [QUICK_INTEGRATION_GUIDE.md](./QUICK_INTEGRATION_GUIDE.md) - Setup guide
- [COMPLETE_SYSTEM_GUIDE.md](./COMPLETE_SYSTEM_GUIDE.md) - Backend API reference
