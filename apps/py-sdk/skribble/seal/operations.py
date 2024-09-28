from typing import Dict, Any, Optional
from ..client_manager import get_client
from ..exceptions import SkribbleValidationError
from ..models import Seal

def create(seal_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Create a seal for a document.

    Args:
        seal_data (Dict[str, Any]): The seal data.

    Returns:
        Dict[str, Any]: The created seal details.

    Raises:
        SkribbleValidationError: If the input data is invalid.
    """
    try:
        validated_seal = Seal(**seal_data)
    except ValueError as e:
        raise SkribbleValidationError("Invalid seal data", str(e))
    
    return get_client().create_seal(validated_seal.model_dump(exclude_none=True))

def create_specific(content: str, account_name: Optional[str] = None) -> Dict[str, Any]:
    """
    Create a seal for a document with a specific seal.

    Args:
        content (str): Base64 encoded PDF file.
        account_name (Optional[str]): The name of the account Skribble set up for your organization seal.

    Returns:
        Dict[str, Any]: The created seal details.

    Raises:
        SkribbleValidationError: If the input data is invalid.
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