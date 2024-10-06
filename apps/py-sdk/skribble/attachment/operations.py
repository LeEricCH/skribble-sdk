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
        >>> result = skribble.attachment.add("5c33d0cb-84...", attachments)
        >>> print(result)
        [{'attachment_id': 'att_1'}, {'attachment_id': 'att_2'}]
    """
    client = get_client()
    attachment_responses = []
    for attachment in attachments:
        response = client._make_request("POST", f"/signature-requests/{signature_request_id}/attachments", data=attachment)
        attachment_responses.append(response)
    return attachment_responses

def get(signature_request_id: str, attachment_id: str) -> bytes:
    """
    Download a specific attached file from a signature request.

    Args:
        signature_request_id (str): The ID of the signature request.
        attachment_id (str): The ID of the attachment to download.

    Returns:
        bytes: The content of the attachment file.
    """
    client = get_client()
    response = client.session.get(f"{client.BASE_URL}/signature-requests/{signature_request_id}/attachments/{attachment_id}/content", headers={"Authorization": f"Bearer {client._authenticate()}"})
    if response.status_code == 200:
        return response.content
    else:
        raise SkribbleAPIError(f"Failed to get attachment: {response.text}")

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
    client = get_client()
    response = client.session.delete(f"{client.BASE_URL}/signature-requests/{signature_request_id}/attachments/{attachment_id}", headers={"Authorization": f"Bearer {client._authenticate()}"})
    if response.status_code not in [204, 200]:
        raise SkribbleAPIError(f"Failed to delete attachment: {response.text}")

def list(signature_request_id: str) -> List[Dict[str, str]]:
    """
    List all attachments for a signature request.

    Args:
        signature_request_id (str): The ID of the signature request.

    Returns:
        List[Dict[str, str]]: A list of dictionaries containing the attachment information.
        Each dictionary has 'attachment_id' and 'filename' keys.

    Raises:
        SkribbleAPIError: If the API request fails.
    """
    client = get_client()
    response = client._make_request("GET", f"/signature-requests/{signature_request_id}")
    
    if 'attachments' in response:
        return response['attachments']
    else:
        return []

