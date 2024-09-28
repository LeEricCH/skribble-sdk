from typing import Dict, Any, Optional
from ..client_manager import get_client
from ..exceptions import SkribbleValidationError
from ..models import Seal

def create(seal_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Create a seal for a document.

    :param seal_data: The seal data.
    :type seal_data: Dict[str, Any]
    :return: The created seal details.
    :rtype: Dict[str, Any]
    :raises SkribbleValidationError: If the input data is invalid.

    Example:
        >>> seal_data = {
        ...     "content": "base64_encoded_pdf_content",
        ...     "visual_signature": {
        ...         "position": {"x": 20, "y": 20, "width": 260, "height": 120, "page": "0"},
        ...         "image": {"content_type": "image/png", "content": "base64_encoded_image_content"}
        ...     }
        ... }
        >>> result = skribble.seal.create(seal_data)
        >>> print(result)
        {'document_id': 'doc_123', 'status': 'success'}
    """
    try:
        validated_seal = Seal(**seal_data)
    except ValueError as e:
        raise SkribbleValidationError("Invalid seal data", str(e))
    
    return get_client().create_seal(validated_seal.model_dump(exclude_none=True))

def create_specific(content: str, account_name: Optional[str] = None) -> Dict[str, Any]:
    """
    Create a seal for a document with a specific seal.

    :param content: Base64 encoded PDF file.
    :type content: str
    :param account_name: The name of the account Skribble set up for your organization seal.
    :type account_name: Optional[str]
    :return: The created seal details.
    :rtype: Dict[str, Any]
    :raises SkribbleValidationError: If the input data is invalid.

    Example:
        >>> content = "base64_encoded_pdf_content"
        >>> account_name = "company_seal_department_a"
        >>> result = skribble.seal.create_specific(content, account_name)
        >>> print(result)
        {'document_id': 'doc_456', 'status': 'success'}
    """
    seal_data = {
        "content": content,
        "account_name": account_name
    }
    try:
        validated_seal = Seal(**seal_data)
    except ValueError as e:
        raise SkribbleValidationError("Invalid seal data", str(e))
    
    return get_client().create_specific_seal(validated_seal.model_dump(exclude_none=True))