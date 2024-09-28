from typing import Dict, Any, List, Optional
from ..models import SignatureRequest, Signature, SignerIdentityData
from ..client_manager import get_client
from ..exceptions import SkribbleValidationError, SkribbleAPIError, SkribbleOperationError
from pydantic import ValidationError

def create(signature_request: Dict[str, Any]) -> Dict[str, Any]:
    """
    Create a new signature request.

    Args:
        signature_request (Dict[str, Any]): The signature request data.

    Returns:
        Dict[str, Any]: The created signature request details.

    Raises:
        SkribbleValidationError: If the input data is invalid.
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

    Args:
        signature_request_id (str): The ID of the signature request to retrieve.

    Returns:
        Dict[str, Any]: The signature request details.
    """
    return get_client().get_signature_request(signature_request_id)

def delete(signature_request_id: str) -> Dict[str, Any]:
    """
    Delete a specific signature request.

    Args:
        signature_request_id (str): The ID of the signature request to delete.

    Returns:
        Dict[str, Any]: A dictionary containing the status and message of the delete operation.
    """
    return get_client().delete_signature_request(signature_request_id)

def list(limit: int = 20, offset: int = 0) -> List[Dict[str, Any]]:
    """
    List signature requests.

    Args:
        limit (int): The maximum number of signature requests to return. Default is 20.
        offset (int): The number of signature requests to skip. Default is 0.

    Returns:
        List[Dict[str, Any]]: A list of signature request details.
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

    Args:
        signature_request_id (str): The ID of the signature request to withdraw.
        message (Optional[str]): An optional message explaining the reason for withdrawal.

    Returns:
        Dict[str, Any]: A dictionary containing the status of the withdrawal operation.
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