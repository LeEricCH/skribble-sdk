from typing import Dict, Any
from ..client_manager import get_client
from ..exceptions import SkribbleValidationError, SkribbleAPIError

def add(signature_request_id: str, filename: str, content_type: str, content: bytes) -> Dict[str, Any]:
    """
    Add an attachment to a signature request.

    Args:
        signature_request_id (str): The ID of the signature request.
        filename (str): The name of the file to attach.
        content_type (str): The MIME type of the file.
        content (bytes): The content of the file.

    Returns:
        Dict[str, Any]: The response from the API, including the attachment ID.
    """
    return get_client().add_signature_request_attachment(signature_request_id, filename, content_type, content)

def get(signature_request_id: str, attachment_id: str) -> bytes:
    """
    Download a specific attached file from a signature request.

    Args:
        signature_request_id (str): The ID of the signature request.
        attachment_id (str): The ID of the attachment to download.

    Returns:
        bytes: The content of the attachment file.
    """
    return get_client().get_signature_request_attachment(signature_request_id, attachment_id)

def delete(signature_request_id: str, attachment_id: str) -> None:
    """
    Remove an attachment from a signature request.

    Args:
        signature_request_id (str): The ID of the signature request.
        attachment_id (str): The ID of the attachment to remove.

    Returns:
        None

    Raises:
        SkribbleAPIError: If the deletion fails.
    """
    try:
        get_client().delete_signature_request_attachment(signature_request_id, attachment_id)
    except SkribbleAPIError as e:
        print(f"Error deleting attachment: {str(e)}")
        raise