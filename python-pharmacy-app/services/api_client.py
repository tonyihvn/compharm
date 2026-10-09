"""API client for communicating with central server."""

import logging
import json
from typing import Dict, List, Optional, Any
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from config.settings import settings

logger = logging.getLogger(__name__)


class CentralServerClient:
    """Client for communicating with the central React backend server."""

    def __init__(self, api_url: str = None, api_key: str = None, timeout: int = None):
        """Initialize the API client."""
        self.api_url = api_url or settings.CENTRAL_SERVER_URL
        self.api_key = api_key or settings.PHARMACY_ID
        self.timeout = timeout or settings.API_TIMEOUT
        self.session = self._create_session()
        self.online_mode = True
        self.last_error = None

    def is_online(self) -> bool:
        """Check if server is reachable."""
        try:
            response = self.session.head(f"{self.api_url}/api/health", timeout=5)
            self.online_mode = response.status_code < 500
            return self.online_mode
        except Exception as e:
            logger.warning(f"Server not reachable: {str(e)}")
            self.online_mode = False
            self.last_error = str(e)
            return False

    def _create_session(self) -> requests.Session:
        """Create a requests session with retries."""
        session = requests.Session()
        
        # Configure retry strategy
        retry_strategy = Retry(
            total=3,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["HEAD", "GET", "OPTIONS", "POST", "PUT", "DELETE"],
            backoff_factor=1
        )
        
        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        
        # Set default headers
        session.headers.update({
            "Content-Type": "application/json",
            "X-Pharmacy-ID": settings.PHARMACY_ID
        })
        
        return session

    def _handle_response(self, response: requests.Response) -> Dict[str, Any]:
        """Handle API response."""
        try:
            if response.status_code == 200 or response.status_code == 201:
                return response.json()
            elif response.status_code == 204:
                return {"success": True}
            elif response.status_code == 401:
                logger.error("Unauthorized - invalid API key")
                raise AuthenticationError("Invalid API credentials")
            elif response.status_code == 404:
                return {"error": "Resource not found"}
            else:
                error_msg = response.text
                try:
                    error_msg = response.json().get("message", response.text)
                except:
                    pass
                logger.error(f"API Error {response.status_code}: {error_msg}")
                raise APIError(f"API Error {response.status_code}: {error_msg}")
        except requests.exceptions.RequestException as e:
            logger.error(f"Request failed: {str(e)}")
            raise NetworkError(f"Network request failed: {str(e)}")

    # Client Management
    def fetch_clients(self, facility_id: str = None, skip: int = 0, limit: int = 100) -> List[Dict]:
        """Fetch clients assigned to this pharmacy."""
        try:
            # Check if online first
            if not self.is_online():
                logger.warning("Offline mode: returning empty client list")
                return []
            
            params = {
                "pharmacy_id": settings.PHARMACY_ID,
                "skip": skip,
                "limit": limit
            }
            if facility_id:
                params["facility_id"] = facility_id

            response = self.session.get(
                f"{self.api_url}/api/clients",
                params=params,
                timeout=self.timeout
            )
            data = self._handle_response(response)
            return data.get("clients", []) if isinstance(data, dict) else data
        except Exception as e:
            logger.warning(f"Failed to fetch clients (offline mode): {str(e)}")
            return []  # Return empty list for offline mode
    
    def get_clients(self, facility_id: str = None, skip: int = 0, limit: int = 100) -> List[Dict]:
        """Alias for fetch_clients for compatibility."""
        return self.fetch_clients(facility_id, skip, limit)

    def get_client_details(self, client_id: str) -> Dict:
        """Get detailed client information."""
        try:
            response = self.session.get(
                f"{self.api_url}/api/clients/{client_id}",
                timeout=self.timeout
            )
            return self._handle_response(response)
        except Exception as e:
            logger.error(f"Failed to fetch client details: {str(e)}")
            raise

    def update_client_data(self, client_id: str, data: Dict) -> Dict:
        """Update client data (used for syncing updates back)."""
        try:
            response = self.session.put(
                f"{self.api_url}/api/clients/{client_id}",
                json=data,
                timeout=self.timeout
            )
            return self._handle_response(response)
        except Exception as e:
            logger.error(f"Failed to update client: {str(e)}")
            raise

    # Forms Management
    def fetch_available_forms(self) -> List[Dict]:
        """Fetch list of available forms from server."""
        try:
            # Check if online first
            if not self.is_online():
                logger.warning("Offline mode: returning empty forms list")
                return []
            
            response = self.session.get(
                f"{self.api_url}/api/forms",
                timeout=self.timeout
            )
            data = self._handle_response(response)
            
            # Handle different API response formats
            if isinstance(data, dict):
                # Try to get forms from 'data' field first (React backend format)
                if "data" in data:
                    forms = data.get("data", [])
                    return forms if isinstance(forms, list) else []
                # Fallback to 'forms' field
                elif "forms" in data:
                    return data.get("forms", [])
                # If dict itself contains form data
                else:
                    return [data] if "form_name" in data or "name" in data else []
            elif isinstance(data, list):
                return data
            else:
                return []
        except Exception as e:
            logger.warning(f"Failed to fetch forms (offline mode): {str(e)}")
            return []  # Return empty list for offline mode

    def get_forms(self) -> List[Dict]:
        """Alias for fetch_available_forms for compatibility."""
        return self.fetch_available_forms()

    def upload_form(self, form_data: Dict) -> Dict:
        """Upload a new form definition (Admin only)."""
        try:
            response = self.session.post(
                f"{self.api_url}/api/forms",
                json=form_data,
                timeout=self.timeout
            )
            return self._handle_response(response)
        except Exception as e:
            logger.error(f"Failed to upload form: {str(e)}")
            raise

    # Form Submissions
    def submit_form(self, client_id: str, form_id: str, submission_data: Dict) -> Dict:
        """Submit a form for a client."""
        try:
            payload = {
                "client_id": client_id,
                "form_id": form_id,
                "form_data": submission_data,
                "submitted_by": settings.PHARMACY_ID,
                "submitted_at": self._get_timestamp()
            }
            response = self.session.post(
                f"{self.api_url}/api/submissions",
                json=payload,
                timeout=self.timeout
            )
            return self._handle_response(response)
        except Exception as e:
            logger.error(f"Failed to submit form: {str(e)}")
            raise

    def get_submission_history(self, client_id: str) -> List[Dict]:
        """Get form submission history for a client."""
        try:
            response = self.session.get(
                f"{self.api_url}/api/clients/{client_id}/submissions",
                timeout=self.timeout
            )
            data = self._handle_response(response)
            return data.get("submissions", []) if isinstance(data, dict) else data
        except Exception as e:
            logger.error(f"Failed to fetch submission history: {str(e)}")
            raise

    # Sync Status
    def sync_health_check(self) -> bool:
        """Check if central server is accessible."""
        try:
            response = self.session.get(
                f"{self.api_url}/api/health",
                timeout=self.timeout
            )
            return response.status_code == 200
        except Exception as e:
            logger.warning(f"Health check failed: {str(e)}")
            return False

    @staticmethod
    def _get_timestamp() -> str:
        """Get current timestamp in ISO format."""
        from datetime import datetime
        return datetime.utcnow().isoformat() + "Z"


class AuthenticationError(Exception):
    """Raised when authentication fails."""
    pass


class NetworkError(Exception):
    """Raised when network request fails."""
    pass


class APIError(Exception):
    """Raised when API returns an error."""
    pass
