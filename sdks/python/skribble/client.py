import requests
from typing import Optional, Dict, Any, List, TypeVar, Generic, Union
from .models import (
    AuthRequest,
    SignatureRequestResponse,
    SignatureResponse,
    DocumentResponse
)
from .exceptions import SkribbleAuthError, SkribbleValidationError, SkribbleAPIError

T = TypeVar('T')

class SkribbleClient:
    BASE_URL: str = "https://api.skribble.com/v2"

    def __init__(self, username: Optional[str] = None, api_key: Optional[str] = None, access_token: Optional[str] = None):
        """
        Initialize the Skribble client.

        Args:
            username (str, optional): The API username.
            api_key (str, optional): The API key.
            access_token (str, optional): A pre-authenticated access token.
        """
        self.username: Optional[str] = username
        self.api_key: Optional[str] = api_key
        self.access_token: Optional[str] = access_token
        self.session: requests.Session = requests.Session()

    def _authenticate(self) -> str:
        if self.access_token:
            return self.access_token
        
        if not self.username or not self.api_key:
            raise SkribbleAuthError("Username and API key are required for authentication")

        auth_data = {
            "username": self.username,
            "api-key": self.api_key
        }
        
        response = self.session.post(f"{self.BASE_URL}/access/login", json=auth_data)

        if response.status_code == 200:
            # The API returns just the raw token string
            self.access_token = response.text.strip()
            return self.access_token
        elif response.status_code in [401, 403]:
            raise SkribbleAuthError("Invalid credentials")
        else:
            try:
                error_detail = response.json()
                raise SkribbleAPIError(error_detail.get("message", response.text), status_code=response.status_code)
            except ValueError:
                raise SkribbleAPIError(response.text, status_code=response.status_code)

    def _make_request(
        self,
        method: str,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,
        binary_response: bool = False
    ) -> Union[SignatureRequestResponse, SignatureResponse, DocumentResponse, Dict[str, Any], List[Dict[str, Any]], bytes, None]:
        if not self.access_token:
            self.access_token = self._authenticate()
        
        headers = {"Authorization": f"Bearer {self.access_token}"}

        try:
            response = self.session.request(method, f"{self.BASE_URL}{endpoint}", json=data, headers=headers, params=params)
            response.raise_for_status()  # This will raise an HTTPError for bad responses

            if response.status_code >= 200 and response.status_code < 300:
                if binary_response:
                    return response.content
                return response.json() if response.text else None
        except requests.exceptions.HTTPError as http_err:
            error_message = f"HTTP error occurred: {http_err}. "
            try:
                error_detail = response.json()
                error_message += f"Error details: {error_detail}"
            except ValueError:
                error_message += f"Response text: {response.text}"

            if response.status_code in [401, 403]:
                raise SkribbleAuthError(f"Invalid or expired token. {error_message}")
            elif response.status_code == 400:
                # Only raise SkribbleValidationError if it's actually a validation error e.g. invalid data
                try:
                    error_detail = response.json()
                    if error_detail.get("error") == "validation_error":
                        raise SkribbleValidationError(f"Validation error: {error_message}")
                except (ValueError, KeyError):
                    pass
                # For all other 400 errors, raise SkribbleAPIError
                raise SkribbleAPIError(error_message, status_code=response.status_code)
            elif response.status_code == 404:
                raise SkribbleAPIError(error_message, status_code=response.status_code)
            else:
                raise SkribbleAPIError(error_message, status_code=response.status_code)
        except requests.exceptions.RequestException as req_err:
            raise SkribbleAPIError(f"Request failed: {str(req_err)}")

