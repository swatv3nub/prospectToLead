"""
Tool integrations for external APIs.
"""
import requests
from typing import Dict, Any, List, Optional
from tenacity import retry, stop_after_attempt, wait_exponential
import time


class APIClient:
    """Base class for API clients with retry logic."""
    
    def __init__(self, api_key: str, base_url: str):
        self.api_key = api_key
        self.base_url = base_url
        self.session = requests.Session()
    
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    def _request(self, method: str, endpoint: str, **kwargs) -> Dict[str, Any]:
        """Make HTTP request with retry logic."""
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        response = self.session.request(method, url, **kwargs)
        response.raise_for_status()
        return response.json()


class ClayAPIClient(APIClient):
    """Clay API client for prospect search."""
    
    def __init__(self, api_key: str):
        super().__init__(api_key, "https://api.clay.com")
    
    def search_companies(self, filters: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Search for companies matching filters."""
        # Note: This is a mock implementation since Clay API docs are not public
        # Replace with actual Clay API calls when available
        headers = {"Authorization": f"Bearer {self.api_key}"}
        
        try:
            response = self._request(
                "POST",
                "/search",
                headers=headers,
                json={"filters": filters}
            )
            return response.get("results", [])
        except Exception as e:
            print(f"Clay API Error: {e}")
            return []


class ApolloAPIClient(APIClient):
    """Apollo.io API client for prospect search and enrichment."""
    
    def __init__(self, api_key: str):
        super().__init__(api_key, "https://api.apollo.io/v1")
    
    def mixed_people_search(self, 
                           titles: List[str] = None,
                           organization_locations: List[str] = None,
                           organization_num_employees_ranges: List[str] = None,
                           revenue_range: Dict[str, int] = None,
                           per_page: int = 50) -> List[Dict[str, Any]]:
        """Search for contacts using Apollo's mixed search."""
        headers = {
            "Content-Type": "application/json",
            "Cache-Control": "no-cache"
        }
        
        payload = {
            "api_key": self.api_key,
            "per_page": per_page,
            "person_titles": titles or ["VP", "Director", "Head", "Chief"],
            "organization_locations": organization_locations or ["United States"],
        }
        
        if organization_num_employees_ranges:
            payload["organization_num_employees_ranges"] = organization_num_employees_ranges
        
        try:
            response = self._request(
                "POST",
                "/mixed_people/search",
                headers=headers,
                json=payload
            )
            return response.get("people", [])
        except Exception as e:
            print(f"Apollo API Error: {e}")
            return []
    
    def enrich_person(self, email: str) -> Optional[Dict[str, Any]]:
        """Enrich person data by email."""
        try:
            response = self._request(
                "GET",
                f"/people/match?api_key={self.api_key}&email={email}"
            )
            return response.get("person")
        except Exception as e:
            print(f"Apollo Enrichment Error: {e}")
            return None


class ClearbitClient(APIClient):
    """Clearbit API client for data enrichment."""
    
    def __init__(self, api_key: str):
        super().__init__(api_key, "https://person.clearbit.com/v2")
    
    def enrich_person(self, email: str) -> Optional[Dict[str, Any]]:
        """Enrich person data using Clearbit."""
        try:
            response = self._request(
                "GET",
                f"/combined/find?email={email}",
                auth=(self.api_key, '')
            )
            return response
        except Exception as e:
            print(f"Clearbit Error: {e}")
            return None


class PeopleDataLabsClient(APIClient):
    """PeopleDataLabs API client for enrichment."""
    
    def __init__(self, api_key: str):
        super().__init__(api_key, "https://api.peopledatalabs.com/v5")
    
    def enrich_person(self, email: str = None, profile: str = None) -> Optional[Dict[str, Any]]:
        """Enrich person data."""
        headers = {"X-Api-Key": self.api_key}
        params = {}
        
        if email:
            params["email"] = email
        if profile:
            params["profile"] = profile
        
        try:
            response = self._request(
                "GET",
                "/person/enrich",
                headers=headers,
                params=params
            )
            return response.get("data")
        except Exception as e:
            print(f"PeopleDataLabs Error: {e}")
            return None


class SendGridClient:
    """SendGrid email client."""
    
    def __init__(self, api_key: str, from_email: str):
        self.api_key = api_key
        self.from_email = from_email
    
    def send_email(self, to_email: str, subject: str, body: str) -> Dict[str, Any]:
        """Send an email using SendGrid."""
        from sendgrid import SendGridAPIClient
        from sendgrid.helpers.mail import Mail
        
        message = Mail(
            from_email=self.from_email,
            to_emails=to_email,
            subject=subject,
            html_content=body
        )
        
        try:
            sg = SendGridAPIClient(self.api_key)
            response = sg.send(message)
            return {
                "status": "sent",
                "status_code": response.status_code,
                "message_id": response.headers.get("X-Message-Id")
            }
        except Exception as e:
            print(f"SendGrid Error: {e}")
            return {"status": "failed", "error": str(e)}


class GoogleSheetsClient:
    """Google Sheets client for feedback logging."""
    
    def __init__(self, credentials_file: str, sheet_id: str):
        import gspread
        from google.oauth2.service_account import Credentials
        
        scopes = [
            'https://www.googleapis.com/auth/spreadsheets',
            'https://www.googleapis.com/auth/drive'
        ]
        
        try:
            creds = Credentials.from_service_account_file(credentials_file, scopes=scopes)
            self.client = gspread.authorize(creds)
            self.sheet_id = sheet_id
        except Exception as e:
            print(f"Google Sheets Auth Error: {e}")
            self.client = None
    
    def append_rows(self, worksheet_name: str, rows: List[List[Any]]):
        """Append rows to a worksheet."""
        if not self.client:
            print("Google Sheets client not initialized")
            return
        
        try:
            spreadsheet = self.client.open_by_key(self.sheet_id)
            worksheet = spreadsheet.worksheet(worksheet_name)
            worksheet.append_rows(rows)
        except Exception as e:
            print(f"Error appending to sheet: {e}")
    
    def create_worksheet(self, worksheet_name: str, rows: int = 100, cols: int = 20):
        """Create a new worksheet."""
        if not self.client:
            return
        
        try:
            spreadsheet = self.client.open_by_key(self.sheet_id)
            spreadsheet.add_worksheet(title=worksheet_name, rows=rows, cols=cols)
        except Exception as e:
            print(f"Error creating worksheet: {e}")
