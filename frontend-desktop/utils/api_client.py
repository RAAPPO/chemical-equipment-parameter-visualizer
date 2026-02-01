import requests
from typing import Optional, Dict, Any
import json


class APIClient:
    """Client for communicating with Django backend API."""
    
    def __init__(self, base_url: str = "http://127.0.0.1:8100/api"):
        self.base_url = base_url
        self.access_token: Optional[str] = None
        self.refresh_token: Optional[str] = None
        self.session = requests.Session()
    
    def login(self, username: str, password: str) -> Dict[str, Any]:
        """Authenticate user and store tokens."""
        try:
            response = self.session.post(
                f"{self.base_url}/auth/token/",
                json={"username": username, "password": password}
            )
            response.raise_for_status()
            data = response.json()
            
            self.access_token = data.get("access")
            self.refresh_token = data.get("refresh")
            
            return {"success": True, "data": data}
        except requests.exceptions.RequestException as e:
            return {"success": False, "error": str(e)}
    
    def _get_headers(self) -> Dict[str, str]:
        """Get headers with authorization token."""
        headers = {"Content-Type": "application/json"}
        if self.access_token:
            headers["Authorization"] = f"Bearer {self.access_token}"
        return headers
    
    def get_datasets(self) -> Dict[str, Any]:
        """Get all datasets."""
        try:
            response = self.session.get(
                f"{self.base_url}/datasets/",
                headers=self._get_headers()
            )
            response.raise_for_status()
            data = response.json()
            
            # Handle paginated response
            datasets = data.get("results", data) if isinstance(data, dict) else data
            return {"success": True, "data": datasets}
        except requests.exceptions.RequestException as e:
            return {"success": False, "error": str(e)}
    
    def get_dataset_detail(self, dataset_id: str) -> Dict[str, Any]:
        """Get dataset details."""
        try:
            response = self.session.get(
                f"{self.base_url}/datasets/{dataset_id}/",
                headers=self._get_headers()
            )
            response.raise_for_status()
            return {"success": True, "data": response.json()}
        except requests.exceptions.RequestException as e:
            return {"success": False, "error": str(e)}
    
    def get_analytics(self, dataset_id: str) -> Dict[str, Any]:
        """Get analytics for a dataset."""
        try:
            response = self.session.get(
                f"{self.base_url}/datasets/{dataset_id}/analytics/",
                headers=self._get_headers()
            )
            response.raise_for_status()
            return {"success": True, "data": response.json()}
        except requests.exceptions.RequestException as e:
            return {"success": False, "error": str(e)}
    
    def get_equipment(self, dataset_id: str) -> Dict[str, Any]:
        """Get equipment for a dataset."""
        try:
            response = self.session.get(
                f"{self.base_url}/equipment/",
                params={"dataset_id": dataset_id},
                headers=self._get_headers()
            )
            response.raise_for_status()
            data = response.json()
            
            # Handle paginated response
            equipment = data.get("results", data) if isinstance(data, dict) else data
            return {"success": True, "data": equipment}
        except requests.exceptions.RequestException as e:
            return {"success": False, "error": str(e)}
    
    def upload_csv(self, file_path: str) -> Dict[str, Any]:
        """Upload CSV file."""
        try:
            with open(file_path, 'rb') as f:
                files = {'file': f}
                headers = {}
                if self.access_token:
                    headers["Authorization"] = f"Bearer {self.access_token}"
                
                response = self.session.post(
                    f"{self.base_url}/upload/",
                    files=files,
                    headers=headers
                )
                response.raise_for_status()
                return {"success": True, "data": response.json()}
        except requests.exceptions.RequestException as e:
            return {"success": False, "error": str(e)}
    
    def download_pdf(self, dataset_id: str, save_path: str) -> Dict[str, Any]:
        """Download PDF report."""
        try:
            response = self.session.get(
                f"{self.base_url}/datasets/{dataset_id}/pdf/",
                headers=self._get_headers(),
                stream=True
            )
            response.raise_for_status()
            
            with open(save_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            return {"success": True, "path": save_path}
        except requests.exceptions.RequestException as e:
            return {"success": False, "error": str(e)}
