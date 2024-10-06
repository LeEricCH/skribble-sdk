from typing import Dict, Any, List, Optional
import time
from ..client_manager import get_client
from ..exceptions import SkribbleValidationError, SkribbleOperationError, SkribbleAPIError
from ..models import Document, DocumentRequest

def list(limit: Optional[int] = None) -> List[Dict[str, Any]]:
    """
    List all documents.

    :param limit: The maximum number of documents to return. If None, returns all documents.
    :type limit: Optional[int]
    :return: A list of documents.
    :rtype: List[Dict[str, Any]]

    Example:
        >>> documents = skribble.document.list(limit=5)
        >>> print(len(documents))
        5
    """
    response = get_client()._make_request("GET", "/documents")
    
    if limit is not None:
        return response[:limit]
    return response

def get(document_id: str) -> Dict[str, Any]:
    """
    Get the document metadata.

    :param document_id: The ID of the document to retrieve.
    :type document_id: str
    :return: The document metadata.
    :rtype: Dict[str, Any]

    Example:
        >>> metadata = skribble.document.get("5c33d0cb-84...")
        >>> print(metadata['title'])
        'Sample Document'
    """
    response = get_client()._make_request("GET", f"/documents/{document_id}")
    return Document(**response).model_dump()

def delete(document_id: str) -> Dict[str, Any]:
    """
    Delete a document.

    :param document_id: The ID of the document to delete.
    :type document_id: str
    :return: A dictionary containing the status and message of the delete operation.
    :rtype: Dict[str, Any]

    Example:
        >>> result = skribble.document.delete("5c33d0cb-84...")
        >>> print(result['status'])
        'success'
    """
    try:
        get_client()._make_request("DELETE", f"/documents/{document_id}")
        return {"status": "success", "message": f"Document {document_id} deleted successfully"}
    except SkribbleAPIError as e:
        return {"status": "error", "message": f"Failed to delete document: {str(e)}"}

def add(document_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Add a new document.

    :param document_data: The document data.
    :type document_data: Dict[str, Any]
    :return: The created document details.
    :rtype: Dict[str, Any]

    Example:
        >>> document_data = {
        ...     "title": "New Document",
        ...     "content_type": "application/pdf",
        ...     "content": "base64_encoded_pdf_content"
        ... }
        >>> result = skribble.document.add(document_data)
        >>> print(result['id'])
        'doc_789'
    """
    validated_request = DocumentRequest(**document_data)
    return get_client()._make_request("POST", "/documents", data=validated_request.model_dump(exclude_none=True))

def download(document_id: str) -> bytes:
    """
    Download the document content.

    :param document_id: The ID of the document to download.
    :type document_id: str
    :return: The document content.
    :rtype: bytes

    Example:
        >>> content = skribble.document.download("5c33d0cb-84...")
        >>> print(len(content))
        12345
    """
    client = get_client()
    response = client.session.get(f"{client.BASE_URL}/documents/{document_id}/content", headers={"Authorization": f"Bearer {client._authenticate()}"})
    if response.status_code == 200:
        return response.content
    else:
        raise SkribbleAPIError(f"Failed to download document: {response.text}")

def preview(document_id: str, page_id: int, scale: int = 20, max_retries: int = 5, retry_delay: int = 2) -> bytes:
    """
    Get the document page preview with retry mechanism since the preview generation might take some time for newly added documents

    :param document_id: The ID of the document.
    :type document_id: str
    :param page_id: The page number (starting from 0).
    :type page_id: int
    :param scale: The scale of the preview (20 for thumbnail, 100 for full size).
    :type scale: int
    :param max_retries: Maximum number of retries for polling.
    :type max_retries: int
    :param retry_delay: Delay between retries in seconds.
    :type retry_delay: int
    :return: The preview image content.
    :rtype: bytes

    Example:
        >>> preview = skribble.document.preview("5c33d0cb-84...", page_id=0, scale=20)
        >>> print(len(preview))
        5678
    """
    client = get_client()
    url = f"{client.BASE_URL}/documents/{document_id}/pages/{page_id}?scale={scale}"
    
    for attempt in range(max_retries):
        response = client.session.get(url, headers={"Authorization": f"Bearer {client._authenticate()}"})
        
        if response.status_code == 200:
            content_type = response.headers.get('Content-Type')
            if content_type in ['image/png', 'image/webp']:
                if response.content:
                    return response.content
                else:
                    raise SkribbleAPIError("Received empty response for document preview")
            else:
                raise SkribbleAPIError(f"Unexpected content type: {content_type}")
        elif response.status_code == 202:
            # If the response status is 202, it means the preview image is still generating
            # Wait for the specified retry_delay and try again
            time.sleep(retry_delay)
        else:
            error_message = response.text if response.text else "No error message provided"
            raise SkribbleAPIError(f"Failed to get document preview. Status code: {response.status_code}. Error: {error_message}")
    
    raise SkribbleAPIError(f"Failed to get document preview after {max_retries} attempts")