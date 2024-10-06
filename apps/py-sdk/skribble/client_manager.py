from .client import SkribbleClient
from .models import SignatureRequest, UpdateSignatureRequest, DocumentRequest, SealRequest, SignerRequest
from .exceptions import SkribbleAuthError, SkribbleValidationError, SkribbleAPIError
from typing import Optional, Dict, Any, List

_client = None

def init(username: Optional[str] = None, api_key: Optional[str] = None, access_token: Optional[str] = None) -> str:
    """
    Initialize the Skribble SDK client and return the access token.

    This function can be called in two ways:
    1. With username and api_key for initial authentication.
    2. With a pre-authenticated access_token for subsequent requests.

    Args:
        username (str, optional): The API username.
        api_key (str, optional): The API key.
        access_token (str, optional): A pre-authenticated access token.

    Returns:
        str: The access token.

    Raises:
        SkribbleValidationError: If neither (username, api_key) pair nor access_token is provided.

    Examples:
        # Initialize with username and API key
        token = skribble.init(username="your_username", api_key="your_api_key")
        print(f"Access token: {token}")

        # Initialize with access token
        token = skribble.init(access_token="your_access_token")
        print(f"Access token: {token}")

    Note:
        You must call this function before using any other SDK operations.
    """
    global _client
    try:
        if access_token:
            _client = SkribbleClient(access_token=access_token)
            try:
                # Perform a test request to verify the token
                _client._make_request("GET", "/signature-requests", params={"limit": 1})
                return access_token
            except SkribbleAPIError as api_err:
                if api_err.status_code == 500:
                    raise SkribbleAuthError("Unable to validate access token. It may be expired or invalid.")
                raise
        elif username and api_key:
            _client = SkribbleClient(username=username, api_key=api_key)
            return _client._authenticate()
        else:
            raise SkribbleValidationError("Either (username, api_key) or access_token must be provided")
    except SkribbleAuthError as auth_err:
        raise SkribbleAuthError(f"{str(auth_err)}")
    except SkribbleAPIError as api_err:
        raise SkribbleAPIError(f"API error during initialization: {str(api_err)}", status_code=api_err.status_code)

def get_client() -> SkribbleClient:
    if _client is None:
        raise SkribbleValidationError("Skribble SDK not initialized. Call skribble.init(...) first.")
    return _client