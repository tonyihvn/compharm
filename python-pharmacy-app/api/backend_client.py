"""
Backend API Client
Handles all API requests to the ComPharm backend server with automatic authentication
"""

import requests
from config.settings import settings
import logging
from typing import Dict, Any, Optional
import os

logger = logging.getLogger(__name__)


class BackendAPIClient:
    """Client for communicating with the ComPharm backend server"""
    
    def __init__(self):
        self.base_url = settings.CENTRAL_SERVER_URL
        self.timeout = settings.API_TIMEOUT
        self.auth_token = None
        self.authenticated = False
    
    def authenticate(self) -> bool:
        """
        Authenticate with the backend server using stored credentials
        
        Returns:
            bool: True if authentication successful, False otherwise
        """
        if not settings.BACKEND_USERNAME or not settings.BACKEND_PASSWORD:
            logger.warning("Backend credentials not configured in System Settings")
            return False
        
        try:
            response = requests.post(
                f"{self.base_url}/api/auth/login",
                json={
                    "username": settings.BACKEND_USERNAME,
                    "password": settings.BACKEND_PASSWORD
                },
                timeout=self.timeout
            )
            
            if response.status_code == 200:
                data = response.json()
                self.auth_token = data.get('token')
                self.authenticated = True
                logger.info("Successfully authenticated with backend server")
                return True
            else:
                logger.error(f"Authentication failed: {response.json().get('message')}")
                self.authenticated = False
                return False
        except requests.exceptions.ConnectionError:
            logger.error(f"Cannot connect to backend server at {self.base_url}")
            self.authenticated = False
            return False
        except Exception as e:
            logger.error(f"Authentication error: {str(e)}")
            self.authenticated = False
            return False
    
    def get_headers(self) -> Dict[str, str]:
        """Get headers with authentication token"""
        headers = {"Content-Type": "application/json"}
        if self.auth_token:
            headers["Authorization"] = f"Bearer {self.auth_token}"
        return headers
    
    def request(self, method: str, endpoint: str, data: Optional[Dict] = None, **kwargs) -> Optional[Dict]:
        """
        Make an authenticated request to the backend
        
        Args:
            method: HTTP method (GET, POST, PUT, DELETE)
            endpoint: API endpoint (without base URL)
            data: JSON data for POST/PUT requests
            **kwargs: Additional arguments for requests.request
        
        Returns:
            Dict: Response JSON data, or None if error
        """
        # Ensure authentication
        if not self.authenticated:
            if not self.authenticate():
                return None
        
        url = f"{self.base_url}{endpoint}"
        headers = self.get_headers()
        
        try:
            if method.upper() == 'GET':
                response = requests.get(url, headers=headers, timeout=self.timeout, **kwargs)
            elif method.upper() == 'POST':
                response = requests.post(url, json=data, headers=headers, timeout=self.timeout, **kwargs)
            elif method.upper() == 'PUT':
                response = requests.put(url, json=data, headers=headers, timeout=self.timeout, **kwargs)
            elif method.upper() == 'DELETE':
                response = requests.delete(url, headers=headers, timeout=self.timeout, **kwargs)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")
            
            if response.status_code == 401:
                # Token expired, re-authenticate
                logger.info("Token expired, re-authenticating...")
                if self.authenticate():
                    headers = self.get_headers()
                    # Retry the request
                    if method.upper() == 'GET':
                        response = requests.get(url, headers=headers, timeout=self.timeout, **kwargs)
                    elif method.upper() == 'POST':
                        response = requests.post(url, json=data, headers=headers, timeout=self.timeout, **kwargs)
                    elif method.upper() == 'PUT':
                        response = requests.put(url, json=data, headers=headers, timeout=self.timeout, **kwargs)
                    elif method.upper() == 'DELETE':
                        response = requests.delete(url, headers=headers, timeout=self.timeout, **kwargs)
            
            if response.status_code in [200, 201]:
                return response.json()
            else:
                logger.error(f"Request failed: {response.status_code} - {response.text}")
                return None
        except requests.exceptions.Timeout:
            logger.error(f"Request timeout to {endpoint}")
            return None
        except requests.exceptions.ConnectionError:
            logger.error(f"Connection error to {self.base_url}")
            return None
        except Exception as e:
            logger.error(f"Request error: {str(e)}")
            return None
    
    # Client API Methods
    
    def get_clients(self, page: int = 1, limit: int = 50, pharmacy_id: str = None, **kwargs) -> Optional[Dict]:
        """
        Get list of clients
        
        Args:
            page: Page number
            limit: Items per page
            pharmacy_id: Optional pharmacy code to filter by
            **kwargs: Additional query parameters
        """
        params = {"page": page, "limit": limit}
        if pharmacy_id:
            params["pharmacyCode"] = pharmacy_id
        params.update(kwargs)
        return self.request('GET', '/api/clients', params=params)
    
    def get_client(self, client_id: str) -> Optional[Dict]:
        """Get a single client by ID"""
        return self.request('GET', f'/api/clients/{client_id}')
    
    def create_client(self, data: Dict) -> Optional[Dict]:
        """Create a new client"""
        return self.request('POST', '/api/clients', data=data)
    
    def update_client(self, client_id: str, data: Dict) -> Optional[Dict]:
        """Update an existing client"""
        return self.request('PUT', f'/api/clients/{client_id}', data=data)
    
    def delete_client(self, client_id: str) -> Optional[Dict]:
        """Delete a client"""
        return self.request('DELETE', f'/api/clients/{client_id}')
    
    # Form API Methods
    
    def get_forms(self) -> Optional[Dict]:
        """Get list of available forms"""
        return self.request('GET', '/api/forms')
    
    def upload_form(self, form_file: bytes, name: str, description: str = "") -> Optional[Dict]:
        """Upload a new form"""
        # Note: This is a file upload, so it needs multipart/form-data
        # We'll handle this separately if needed
        pass
    
    def submit_form(self, submission_data: Dict) -> Optional[Dict]:
        """Submit a filled form"""
        return self.request('POST', '/api/submissions', data=submission_data)
    
    def get_submissions(self, page: int = 1, limit: int = 50, **kwargs) -> Optional[Dict]:
        """Get list of form submissions"""
        params = {"page": page, "limit": limit}
        params.update(kwargs)
        return self.request('GET', '/api/submissions', params=params)
    
    # Field API Methods
    
    def get_fields(self) -> Optional[Dict]:
        """Get client field definitions"""
        return self.request('GET', '/api/fields')
    
    def create_field(self, data: Dict) -> Optional[Dict]:
        """Create a new client field"""
        return self.request('POST', '/api/fields', data=data)
    
    def update_field(self, field_id: str, data: Dict) -> Optional[Dict]:
        """Update a client field"""
        return self.request('PUT', f'/api/fields/{field_id}', data=data)
    
    def delete_field(self, field_id: str) -> Optional[Dict]:
        """Delete a client field"""
        return self.request('DELETE', f'/api/fields/{field_id}')
    
    # Sync API Methods
    
    def trigger_sync(self) -> Optional[Dict]:
        """Trigger manual synchronization"""
        return self.request('POST', '/api/sync/trigger-sync', data={})
    
    def get_sync_logs(self) -> Optional[Dict]:
        """Get synchronization logs"""
        return self.request('GET', '/api/sync/logs')
    
    def get_sync_status(self) -> Optional[Dict]:
        """Get current sync status"""
        return self.request('GET', '/api/sync/status')


# Global client instance
api_client = BackendAPIClient()


def get_api_client() -> BackendAPIClient:
    """Get the global API client instance"""
    return api_client


def ensure_authenticated() -> bool:
    """Ensure the API client is authenticated"""
    if not api_client.authenticated:
        return api_client.authenticate()
    return True


if __name__ == "__main__":
    # Test the API client
    logging.basicConfig(level=logging.INFO)
    
    client = BackendAPIClient()
    
    print("Testing backend API client...")
    print(f"Backend URL: {settings.CENTRAL_SERVER_URL}")
    print(f"Username: {settings.BACKEND_USERNAME}")
    
    if client.authenticate():
        print("✓ Authentication successful")
        
        # Test getting clients
        clients_data = client.get_clients()
        if clients_data:
            print(f"✓ Retrieved {clients_data.get('total', 0)} clients")
        else:
            print("✗ Failed to retrieve clients")
    else:
        print("✗ Authentication failed")
        print("Please configure backend credentials in System Settings")
