import requests
from typing import Optional, Dict, Any, List
from .models import AuthRequest, SignatureRequest
from .exceptions import SkribbleAuthError, SkribbleAPIError
import base64

class SkribbleClient:
    BASE_URL: str = "https://api.skribble.com/v2"

    def __init__(self, username: str, api_key: str):
        """
        Initialize the Skribble client.

        Args:
            username (str): The API username.
            api_key (str): The API key.
        """
        self.username: str = username
        self.api_key: str = api_key
        self.session: requests.Session = requests.Session()

    def _authenticate(self) -> str:
        """
        Authenticate with the Skribble API and return the access token.

        Returns:
            str: The access token.

        Raises:
            SkribbleAuthError: If authentication fails.
        """
        auth_data = AuthRequest(username=self.username, **{"api-key": self.api_key})
        response = self.session.post(f"{self.BASE_URL}/access/login", json=auth_data.dict(by_alias=True))

        if response.status_code == 200:
            return response.text.strip()
        else:
            raise SkribbleAuthError(f"Authentication failed: {response.text}")

    def _make_request(self, method: str, endpoint: str, data: Optional[Dict[str, Any]] = None, params: Optional[Dict[str, Any]] = None) -> Any:
        """
        Make an authenticated request to the Skribble API.

        Args:
            method (str): The HTTP method to use.
            endpoint (str): The API endpoint.
            data (Optional[Dict[str, Any]]): The request data.
            params (Optional[Dict[str, Any]]): The request parameters.

        Returns:
            Any: The JSON response from the API or None for empty responses.

        Raises:
            SkribbleAPIError: If the API request fails.
        """
        access_token = self._authenticate()
        headers = {"Authorization": f"Bearer {access_token}"}

        response = self.session.request(method, f"{self.BASE_URL}{endpoint}", json=data, headers=headers, params=params)

        if response.status_code >= 200 and response.status_code < 300:
            return response.json() if response.text else None
        else:
            raise SkribbleAPIError(f"API request failed: {response.text}")

    def create_signature_request(self, signature_request: Dict[str, Any]) -> Dict[str, Any]:
        return self._make_request("POST", "/signature-requests", data=signature_request)

    def get_signature_request(self, signature_request_id: str) -> Dict[str, Any]:
        return self._make_request("GET", f"/signature-requests/{signature_request_id}")

    def delete_signature_request(self, signature_request_id: str) -> Dict[str, Any]:
        """
        Delete a signature request.

        Args:
            signature_request_id (str): The ID of the signature request to delete.

        Returns:
            Dict[str, Any]: A dictionary containing the status and message of the delete operation.
        """
        try:
            self._make_request("DELETE", f"/signature-requests/{signature_request_id}")
            return {"status": "success", "message": f"Signature request {signature_request_id} deleted successfully"}
        except SkribbleAPIError as e:
            return {"status": "error", "message": f"Failed to delete signature request: {str(e)}"}

    def list_signature_requests(self, limit: int = 20, offset: int = 0) -> List[Dict[str, Any]]:
        params = {"limit": limit, "offset": offset}
        return self._make_request("GET", "/signature-requests", params=params)

    def update_signature_request(self, updated_data: Dict[str, Any]) -> Dict[str, Any]:
        return self._make_request("PUT", "/signature-requests", data=updated_data)

    def add_signer_to_signature_request(self, signature_request_id: str, signer_data: Dict[str, Any]) -> Dict[str, Any]:
        return self._make_request("POST", f"/signature-requests/{signature_request_id}/signatures", data=signer_data)

    def remove_signer_from_signature_request(self, signature_request_id: str, signer_id: str) -> None:
        self._make_request("DELETE", f"/signature-requests/{signature_request_id}/signatures/{signer_id}")

    def remind_signature_request(self, signature_request_id: str) -> None:
        self._make_request("POST", f"/signature-requests/{signature_request_id}/remind")

    def withdraw_signature_request(self, signature_request_id: str, message: Optional[str] = None) -> Dict[str, Any]:
        """
        Withdraw a signature request.

        Args:
            signature_request_id (str): The ID of the signature request to withdraw.
            message (Optional[str]): An optional message explaining the reason for withdrawal.

        Returns:
            Dict[str, Any]: A dictionary containing the status of the withdrawal operation.
        """
        data = {"message": message} if message else None
        response = self._make_request("POST", f"/signature-requests/{signature_request_id}/withdraw", data=data)
        if response is None:
            return {"status": "success", "message": "Signature request withdrawn successfully"}
        return response

    def get_signature_request_attachment(self, signature_request_id: str, attachment_id: str) -> bytes:
        response = self.session.get(f"{self.BASE_URL}/signature-requests/{signature_request_id}/attachments/{attachment_id}/content", headers={"Authorization": f"Bearer {self._authenticate()}"})
        if response.status_code == 200:
            return response.content
        else:
            raise SkribbleAPIError(f"Failed to get attachment: {response.text}")

    # Add these new methods to the SkribbleClient class

    def add_signature_request_attachment(self, signature_request_id: str, filename: str, content_type: str, content: bytes) -> Dict[str, Any]:
        data = {
            "filename": filename,
            "content_type": content_type,
            "content": base64.b64encode(content).decode('utf-8')
        }
        return self._make_request("POST", f"/signature-requests/{signature_request_id}/attachments", data=data)

    def get_signature_request_attachment(self, signature_request_id: str, attachment_id: str) -> bytes:
        response = self.session.get(f"{self.BASE_URL}/signature-requests/{signature_request_id}/attachments/{attachment_id}/content", headers={"Authorization": f"Bearer {self._authenticate()}"})
        if response.status_code == 200:
            return response.content
        else:
            raise SkribbleAPIError(f"Failed to get attachment: {response.text}")

    def delete_signature_request_attachment(self, signature_request_id: str, attachment_id: str) -> None:
        response = self.session.delete(f"{self.BASE_URL}/signature-requests/{signature_request_id}/attachments/{attachment_id}", headers={"Authorization": f"Bearer {self._authenticate()}"})
        if response.status_code not in [204, 200]:
            raise SkribbleAPIError(f"Failed to delete attachment: {response.text}")

    # Add more methods for other API endpoints as needed

    def get_document(self, document_id: str) -> Dict[str, Any]:
        return self._make_request("GET", f"/documents/{document_id}")

    def delete_document(self, document_id: str) -> Dict[str, Any]:
        """
        Delete a document.

        Args:
            document_id (str): The ID of the document to delete.

        Returns:
            Dict[str, Any]: A dictionary containing the status and message of the delete operation.
        """
        try:
            self._make_request("DELETE", f"/documents/{document_id}")
            return {"status": "success", "message": f"Document {document_id} deleted successfully"}
        except SkribbleAPIError as e:
            return {"status": "error", "message": f"Failed to delete document: {str(e)}"}

    def get_documents(self, limit: int = 20, offset: int = 0) -> List[Dict[str, Any]]:
        params = {"limit": limit, "offset": offset}
        return self._make_request("GET", "/documents", params=params)

    def get_document_meta(self, document_id: str) -> Dict[str, Any]:
        return self._make_request("GET", f"/documents/{document_id}")

    def delete_document(self, document_id: str) -> None:
        self._make_request("DELETE", f"/documents/{document_id}")

    def add_document(self, document_data: Dict[str, Any]) -> Dict[str, Any]:
        return self._make_request("POST", "/documents", data=document_data)

    def download_document(self, document_id: str) -> bytes:
        response = self.session.get(f"{self.BASE_URL}/documents/{document_id}/content", headers={"Authorization": f"Bearer {self._authenticate()}"})
        if response.status_code == 200:
            return response.content
        else:
            raise SkribbleAPIError(f"Failed to download document: {response.text}")

    def get_document_preview(self, document_id: str, page_id: int, scale: int) -> bytes:
        response = self.session.get(f"{self.BASE_URL}/documents/{document_id}/pages/{page_id}?scale={scale}", headers={"Authorization": f"Bearer {self._authenticate()}"})
        if response.status_code == 200:
            return response.content
        else:
            raise SkribbleAPIError(f"Failed to get document preview: {response.text}")

    # ... (rest of the class remains the same)

    def create_seal(self, seal_data: Dict[str, Any]) -> Dict[str, Any]:
        return self._make_request("POST", "/seal", data=seal_data)

    def create_specific_seal(self, seal_data: Dict[str, Any]) -> Dict[str, Any]:
        return self._make_request("POST", "/seal", data=seal_data)

    # ... (rest of the class remains the same)