from typing import Dict, Any, List, Optional
from ..models import SignatureRequest, Signature, SignerIdentityData
from ..client_manager import get_client
from ..exceptions import SkribbleValidationError, SkribbleAPIError, SkribbleOperationError
from pydantic import ValidationError

def create(signature_request: Dict[str, Any]) -> Dict[str, Any]:
    """
    Create a new signature request.

    :param signature_request: The signature request data.
    :type signature_request: Dict[str, Any]
    :return: The created signature request details.
    :rtype: Dict[str, Any]
    :raises SkribbleValidationError: If the input data is invalid.

    Example:
        >>> request_data = {
        ...     "title": "Test Request",
        ...     "message": "Please sign",
        ...     "file_url": "https://example.com/document.pdf",
        ...     "signatures": [{"account_email": "signer@example.com"}]
        ... }
        >>> result = skribble.signature_request.create(request_data)
        >>> print(result['id'])
        '5c33d0cb-84...'
    """
    try:
        # Validate signatures separately
        validated_signatures = []
        for signature in signature_request.get('signatures', []):
            try:
                validated_signature = Signature(**signature)
                validated_signatures.append(validated_signature.model_dump(exclude_none=True))
            except ValidationError as e:
                raise SkribbleValidationError(f"Invalid signature data: {e}")

        # Replace the original signatures with validated ones
        signature_request['signatures'] = validated_signatures

        # Validate the entire signature request
        validated_request = SignatureRequest(**signature_request)
    except ValidationError as e:
        raise SkribbleValidationError("Invalid signature request data", e.errors())
    
    return get_client()._make_request("POST", "/signature-requests", data=validated_request.model_dump(exclude_none=True, by_alias=True))

def get(signature_request_id: str) -> Dict[str, Any]:
    """
    Get details of a specific signature request.

    :param signature_request_id: The ID of the signature request to retrieve.
    :type signature_request_id: str
    :return: The signature request details.
    :rtype: Dict[str, Any]

    Example:
        >>> details = skribble.signature_request.get("5c33d0cb-84...")
        >>> print(details['title'])
        'Test Request'
    """
    return get_client()._make_request("GET", f"/signature-requests/{signature_request_id}")

def delete(signature_request_id: str) -> Dict[str, Any]:
    """
    Delete a specific signature request.

    :param signature_request_id: The ID of the signature request to delete.
    :type signature_request_id: str
    :return: A dictionary containing the status and message of the delete operation.
    :rtype: Dict[str, Any]

    Example:
        >>> result = skribble.signature_request.delete("5c33d0cb-84...")
        >>> print(result['status'])
        'success'
    """
    try:
        get_client()._make_request("DELETE", f"/signature-requests/{signature_request_id}")
        return {"status": "success", "message": f"Signature request {signature_request_id} deleted successfully"}
    except SkribbleAPIError as e:
        return {"status": "error", "message": f"Failed to delete signature request: {str(e)}"}

def list(
    account_email: Optional[str] = None,
    search: Optional[str] = None,
    signature_status: Optional[str] = None,
    status_overall: Optional[str] = None,
    page_number: Optional[int] = None,
    page_size: int = 50
) -> List[Dict[str, Any]]:
    """
    List signature requests with optional filtering and pagination.

    :param account_email: Filter on the field signatures[].account_email
    :type account_email: Optional[str]
    :param search: Filter on the field title to search for documents containing the search term
    :type search: Optional[str]
    :param signature_status: Filter on the field signatures[].status_code with one of the valid Signature states
    :type signature_status: Optional[str]
    :param status_overall: Filter on the field status_overall with one of the valid Signature states
    :type status_overall: Optional[str]
    :param page_number: Page number for pagination (must be greater than or equal to 0)
    :type page_number: Optional[int]
    :param page_size: Number of items per page (must be greater than or equal to 0, default is 50)
    :type page_size: int
    :return: A list of signature request details.
    :rtype: List[Dict[str, Any]]

    Example:
        >>> requests = skribble.signature_request.list(
        ...     account_email="john.doe@example.com",
        ...     search="Contract",
        ...     signature_status="OPEN",
        ...     page_number=1,
        ...     page_size=10
        ... )
        >>> print(len(requests))
        10
    """
    params = {
        "account_email": account_email,
        "search": search,
        "signature_status": signature_status,
        "status_overall": status_overall,
    }
    # Remove None values from params
    params = {k: v for k, v in params.items() if v is not None}
    
    all_requests = get_client()._make_request("GET", "/signature-requests", params=params)
    
    # Apply pagination on the client side
    start_index = (page_number or 0) * page_size
    end_index = start_index + page_size
    
    return all_requests[start_index:end_index]

def update(signature_request_id: str, updated_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Update a signature request.

    Args:
        signature_request_id (str): The ID of the signature request to update.
        updated_data (Dict[str, Any]): The updated data for the signature request.

    Returns:
        Dict[str, Any]: The updated signature request details.
    """
    updated_data["id"] = signature_request_id
    return get_client()._make_request("PUT", "/signature-requests", data=updated_data)

def add_signer(signature_request_id: str, signer_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Add a signer to a signature request.

    :param signature_request_id: The ID of the signature request.
    :type signature_request_id: str
    :param signer_data: The signer data including email, name, etc.
    :type signer_data: Dict[str, Any]
    :return: The response containing the added signer details.
    :rtype: Dict[str, Any]
    :raises SkribbleOperationError: If the operation fails.

    Example:
        >>> signer_data = {
        ...     "account_email": "new_signer@example.com",
        ...     "signer_identity_data": {
        ...         "email_address": "new_signer@example.com",
        ...         "first_name": "John",
        ...         "last_name": "Doe"
        ...     }
        ... }
        >>> result = skribble.signature_request.add_signer("5c33d0cb-84...", signer_data)
        >>> print(result['sid'])
        'signer_456'
    """
    try:
        client = get_client()

        # Get the signature request and check if any of the signers status_code is SIGNED if so return
        signature_request = client._make_request("GET", f"/signature-requests/{signature_request_id}")
        for signer in signature_request.get('signatures', []):
            if signer.get('status_code') == 'SIGNED':
                raise SkribbleOperationError("add_signer", "One of the signers has already signed the document", None)

        response = client._make_request("POST", f"/signature-requests/{signature_request_id}/signatures", data=signer_data)
        
        return response
    except SkribbleAPIError as e:
        raise SkribbleOperationError("add_signer", str(e), e)
    except Exception as e:
        raise SkribbleOperationError("add_signer", f"Unexpected error: {str(e)}", e)

def remove_signer(signature_request_id: str, signer_id: str) -> Dict[str, Any]:
    """
    Remove a signer from a signature request.

    :param signature_request_id: The ID of the signature request.
    :type signature_request_id: str
    :param signer_id: The ID of the signer to remove.
    :type signer_id: str
    :return: A dictionary containing the status and message of the remove operation.
    :rtype: Dict[str, Any]
    :raises SkribbleOperationError: If the operation fails.

    Example:
        >>> result = skribble.signature_request.remove_signer("5c33d0cb-84...", "signer_456")
        >>> print(result['status'])
        'success'
    """
    try:
        client = get_client()

        # Get the signature request and check if any of the signers status_code is SIGNED if so return
        signature_request = client._make_request("GET", f"/signature-requests/{signature_request_id}")
        for signer in signature_request['signatures']:
            if signer.get('status_code') == 'SIGNED':
                raise SkribbleOperationError("remove_signer", "One of the signers has already signed the document", None)

        client._make_request("DELETE", f"/signature-requests/{signature_request_id}/signatures/{signer_id}")
        
        return {"status": "success", "message": f"Signer with ID {signer_id} removed successfully"}
    except SkribbleAPIError as e:
        raise SkribbleOperationError("remove_signer", str(e), e)
    except Exception as e:
        raise SkribbleOperationError("remove_signer", f"Unexpected error: {str(e)}", e)

def replace_signers(signature_request_id: str, signatures: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Replace all signers in a signature request.

    :param signature_request_id: The ID of the signature request.
    :type signature_request_id: str
    :param signatures: A list of dictionaries containing signer information.
    :type signatures: List[Dict[str, Any]]
    :return: The updated signature request details.
    :rtype: Dict[str, Any]
    :raises SkribbleOperationError: If the operation fails.

    Example:
        >>> new_signers = [
        ...     {"account_email": "signer1@example.com"},
        ...     {"account_email": "signer2@example.com"}
        ... ]
        >>> result = skribble.signature_request.replace_signers("5c33d0cb-84...", new_signers)
        >>> print(len(result['signatures']))
        2

    Note:
        This operation will replace all existing signers. Any signers not included
        in the new signatures list will be removed from the signature request.
        Ensure that you include all desired signers, including existing ones you
        wish to keep.
    """
    try:
        client = get_client()

        # Get the signature request and check if any of the signers have already signed
        signature_request = client._make_request("GET", f"/signature-requests/{signature_request_id}")
        for signer in signature_request['signatures']:
            if signer.get('status_code') == 'SIGNED':
                raise SkribbleOperationError("replace_signers", "Cannot replace signers: One or more signers have already signed the document", None)

        # Prepare the update data
        update_data = {
            "id": signature_request_id,
            "signatures": signatures
        }

        # Update the signature request
        response = client._make_request("PUT", "/signature-requests", data=update_data)
        
        return response
    except SkribbleAPIError as e:
        raise SkribbleOperationError("replace_signers", str(e), e)
    except Exception as e:
        raise SkribbleOperationError("replace_signers", f"Unexpected error: {str(e)}", e)

def remind(signature_request_id: str) -> None:
    """
    Send a reminder to open signers of a signature request.

    Args:
        signature_request_id (str): The ID of the signature request.

    Returns:
        None
    """
    get_client()._make_request("POST", f"/signature-requests/{signature_request_id}/remind")

def withdraw(signature_request_id: str, message: Optional[str] = None) -> Dict[str, Any]:
    """
    Withdraw a signature request.

    :param signature_request_id: The ID of the signature request to withdraw.
    :type signature_request_id: str
    :param message: An optional message explaining the reason for withdrawal.
    :type message: Optional[str]
    :return: A dictionary containing the status of the withdrawal operation.
    :rtype: Dict[str, Any]

    Example:
        >>> result = skribble.signature_request.withdraw("5c33d0cb-84...", message="Document updated")
        >>> print(result['status'])
        'success'
    """
    client = get_client()
    data = {"message": message} if message else None
    response = client._make_request("POST", f"/signature-requests/{signature_request_id}/withdraw", data=data)
    if response is None:
        return {"status": "success", "message": "Signature request withdrawn successfully"}
    return response

def get_attachment(signature_request_id: str, attachment_id: str) -> bytes:
    """
    Download a specific attached file from a signature request.

    Args:
        signature_request_id (str): The ID of the signature request.
        attachment_id (str): The ID of the attachment to download.

    Returns:
        bytes: The content of the attachment file.
    """
    try:
        client = get_client()
        response = client.session.get(f"{client.BASE_URL}/signature-requests/{signature_request_id}/attachments/{attachment_id}/content", headers={"Authorization": f"Bearer {client._authenticate()}"})
        if response.status_code == 200:
            return response.content
        else:
            raise SkribbleAPIError(f"Failed to get attachment: {response.text}")
    except Exception as e:
        print(f"Error getting attachment: {str(e)}")
        return b''