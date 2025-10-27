"""Client for communicating with data-management-service."""

import requests
import logging
from typing import List, Dict, Any, Optional
import os

logger = logging.getLogger(__name__)


class DataManagementClient:
    """Client for data-management-service."""
    
    def __init__(self, base_url: str = None):
        """Initialize client with base URL."""
        self.base_url = base_url or os.getenv(
            'DATA_MANAGEMENT_SERVICE_URL', 
            'http://data-management-service:5001'
        )
        self.timeout = 30
    
    def get_data_types(self) -> List[Dict[str, Any]]:
        """Fetch all data types from data-management-service."""
        try:
            response = requests.get(
                f"{self.base_url}/data-types",
                timeout=self.timeout
            )
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            logger.error(f"Failed to fetch data types: {e}")
            raise Exception(f"Failed to fetch data types from data-management-service: {str(e)}")
    
    def get_data_type(self, data_type: str) -> Optional[Dict[str, Any]]:
        """Fetch a specific data type by identifier."""
        try:
            response = requests.get(
                f"{self.base_url}/data-types/{data_type}",
                timeout=self.timeout
            )
            if response.status_code == 404:
                return None
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            logger.error(f"Failed to fetch data type '{data_type}': {e}")
            raise Exception(f"Failed to fetch data type from data-management-service: {str(e)}")
    
    def health_check(self) -> bool:
        """Check if data-management-service is healthy."""
        try:
            response = requests.get(
                f"{self.base_url}/health",
                timeout=self.timeout
            )
            return response.status_code == 200
        except requests.RequestException as e:
            logger.error(f"Health check failed: {e}")
            return False

