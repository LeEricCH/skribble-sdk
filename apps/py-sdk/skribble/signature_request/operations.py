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
        'sig_req_123'
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
    
    response = get_client().create_signature_request(validated_request.model_dump(exclude_none=True, by_alias=True))
    
    # Log the response for debugging
    print("Create response:", response)
    
    return response

def get(signature_request_id: str) -> Dict[str, Any]:
    """
    Get details of a specific signature request.

    :param signature_request_id: The ID of the signature request to retrieve.
    :type signature_request_id: str
    :return: The signature request details.
    :rtype: Dict[str, Any]

    Example:
        >>> details = skribble.signature_request.get("sig_req_123")
        >>> print(details['title'])
        'Test Request'
    """
    return get_client().get_signature_request(signature_request_id)

def delete(signature_request_id: str) -> Dict[str, Any]:
    """
    Delete a specific signature request.

    :param signature_request_id: The ID of the signature request to delete.
    :type signature_request_id: str
    :return: A dictionary containing the status and message of the delete operation.
    :rtype: Dict[str, Any]

    Example:
        >>> result = skribble.signature_request.delete("sig_req_123")
        >>> print(result['status'])
        'success'
    """
    return get_client().delete_signature_request(signature_request_id)

def list(limit: int = 20, offset: int = 0) -> List[Dict[str, Any]]:
    """
    List signature requests.

    :param limit: The maximum number of signature requests to return. Default is 20.
    :type limit: int
    :param offset: The number of signature requests to skip. Default is 0.
    :type offset: int
    :return: A list of signature request details.
    :rtype: List[Dict[str, Any]]

    Example:
        >>> requests = skribble.signature_request.list(limit=5, offset=0)
        >>> print(len(requests))
        5
    """
    return get_client().list_signature_requests(limit, offset)

def update(signature_request_id: str, updated_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Update a signature request.

    Args:
        signature_request_id (str): The ID of the signature request to update.
        updated_data (Dict[str, Any]): The updated data for the signature request.

    Returns:
        Dict[str, Any]: The updated signature request details.
    """
    return get_client().update_signature_request(signature_request_id, updated_data)

def add_signer(signature_request_id: str, email: str, first_name: Optional[str] = None, last_name: Optional[str] = None, mobile_number: Optional[str] = None, language: Optional[str] = None) -> Dict[str, Any]:
    """
    Add a signer to a signature request.

    :param signature_request_id: The ID of the signature request.
    :type signature_request_id: str
    :param email: The email address of the signer.
    :type email: str
    :param first_name: The first name of the signer (optional).
    :type first_name: Optional[str]
    :param last_name: The last name of the signer (optional).
    :type last_name: Optional[str]
    :param mobile_number: The mobile number of the signer (optional).
    :type mobile_number: Optional[str]
    :param language: The preferred language of the signer (optional).
    :type language: Optional[str]
    :return: The response containing the added signer details.
    :rtype: Dict[str, Any]
    :raises SkribbleOperationError: If the operation fails.

    Example:
        >>> result = skribble.signature_request.add_signer("sig_req_123", "new_signer@example.com", first_name="John", last_name="Doe")
        >>> print(result['sid'])
        'signer_456'
    """
    try:
        client = get_client()

        # Get the signature request and check if any of the signers status_code is SIGNED if so return
        signature_request = client.get_signature_request(signature_request_id)
        for signer in signature_request['signatures']:
            if signer.get('status_code') == 'SIGNED':
                raise SkribbleOperationError("add_signer", "One of the signers has already signed the document", None)

        signer_data = {
            "account_email": email,
            "signer_identity_data": {
                "email_address": email
            }
        }
        if first_name:
            signer_data["signer_identity_data"]["first_name"] = first_name
        if last_name:
            signer_data["signer_identity_data"]["last_name"] = last_name
        if mobile_number:
            signer_data["signer_identity_data"]["mobile_number"] = mobile_number
        if language:
            signer_data["signer_identity_data"]["language"] = language
        
        response = client.add_signer_to_signature_request(signature_request_id, signer_data)
        
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
        >>> result = skribble.signature_request.remove_signer("sig_req_123", "signer_456")
        >>> print(result['status'])
        'success'
    """
    try:
        client = get_client()

        # Get the signature request and check if any of the signers status_code is SIGNED if so return
        signature_request = client.get_signature_request(signature_request_id)
        for signer in signature_request['signatures']:
            if signer.get('status_code') == 'SIGNED':
                raise SkribbleOperationError("remove_signer", "One of the signers has already signed the document", None)

        response = client.remove_signer_from_signature_request(signature_request_id, signer_id)
        
        if response is None:
            return {"status": "success", "message": f"Signer with ID {signer_id} removed successfully"}
        return response
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
        >>> result = skribble.signature_request.replace_signers("sig_req_123", new_signers)
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
        signature_request = client.get_signature_request(signature_request_id)
        for signer in signature_request['signatures']:
            if signer.get('status_code') == 'SIGNED':
                raise SkribbleOperationError("replace_signers", "Cannot replace signers: One or more signers have already signed the document", None)

        # Prepare the update data
        update_data = {
            "id": signature_request_id,
            "signatures": signatures
        }

        # Update the signature request
        response = client.update_signature_request(update_data)
        
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
    get_client().remind_signature_request(signature_request_id)

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
        >>> result = skribble.signature_request.withdraw("sig_req_123", message="Document updated")
        >>> print(result['status'])
        'success'
    """
    return get_client().withdraw_signature_request(signature_request_id, message)

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
        return get_client().get_signature_request_attachment(signature_request_id, attachment_id)
    except Exception as e:
        print(f"Error getting attachment: {str(e)}")
        return b''