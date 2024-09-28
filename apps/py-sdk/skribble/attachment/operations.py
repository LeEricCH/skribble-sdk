from typing import Dict, Any, List
from ..client_manager import get_client
from ..exceptions import SkribbleValidationError, SkribbleAPIError

def add(signature_request_id: str, attachments: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Add multiple attachments to a signature request.

    :param signature_request_id: The ID of the signature request.
    :type signature_request_id: str
    :param attachments: A list of dictionaries containing attachment information.
    :type attachments: List[Dict[str, Any]]
    :return: A list of dictionaries containing the added attachment IDs.
    :rtype: List[Dict[str, Any]]
    :raises SkribbleValidationError: If the input data is invalid.
    :raises SkribbleAPIError: If the API request fails.

    Example:
        >>> attachments = [
        ...     {"filename": "doc1.pdf", "content_type": "application/pdf", "content": "base64_content"},
        ...     {"filename": "doc2.pdf", "content_type": "application/pdf", "content": "base64_content"}
        ... ]
        >>> result = skribble.attachment.add("sig_req_123", attachments)
        >>> print(result)
        [{'attachment_id': 'att_1'}, {'attachment_id': 'att_2'}]
    """
    return get_client().add_signature_request_attachments(signature_request_id, attachments)

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