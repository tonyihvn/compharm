"""
Offline Mode Support
Handles graceful degradation when backend server is unavailable
"""

import logging
import socket
from typing import Tuple

logger = logging.getLogger(__name__)


class OfflineMode:
    """Manages offline mode detection and handling"""
    
    @staticmethod
    def check_connectivity(host: str = "8.8.8.8", port: int = 53, timeout: int = 3) -> bool:
        """
        Check internet connectivity using DNS
        
        Args:
            host: DNS server to check (default: Google DNS)
            port: DNS port (default: 53)
            timeout: Connection timeout in seconds
            
        Returns:
            bool: True if internet connected, False otherwise
        """
        try:
            socket.setdefaulttimeout(timeout)
            socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect((host, port))
            logger.info("Internet connectivity detected")
            return True
        except Exception as e:
            logger.warning(f"No internet connectivity: {str(e)}")
            return False
    
    @staticmethod
    def check_server(url: str, timeout: int = 5) -> bool:
        """
        Check if server is reachable
        
        Args:
            url: Server URL to check
            timeout: Connection timeout in seconds
            
        Returns:
            bool: True if server is reachable, False otherwise
        """
        try:
            import requests
            response = requests.head(url, timeout=timeout)
            is_online = response.status_code < 500
            if is_online:
                logger.info(f"Server reachable: {url}")
            else:
                logger.warning(f"Server error: {url} returned {response.status_code}")
            return is_online
        except Exception as e:
            logger.warning(f"Server not reachable ({url}): {str(e)}")
            return False
    
    @staticmethod
    def handle_offline_error(error: Exception, operation: str = "operation") -> dict:
        """
        Create offline mode error response
        
        Args:
            error: The exception that occurred
            operation: Description of operation that failed
            
        Returns:
            dict: Offline mode response
        """
        logger.warning(f"Offline mode: {operation} failed - {str(error)}")
        return {
            "offline": True,
            "error": str(error),
            "message": f"Running in offline mode. {operation} unavailable.",
            "data": []
        }
