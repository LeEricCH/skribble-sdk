from .client import SkribbleClient
from typing import Optional

_client = None

def init(username: Optional[str] = None, api_key: Optional[str] = None, access_token: Optional[str] = None):
    """
    Initialize the Skribble SDK client.

    This function can be called in two ways:
    1. With username and api_key for initial authentication.
    2. With a pre-authenticated access_token for subsequent requests.

    Args:
        username (str, optional): The API username.
        api_key (str, optional): The API key.
        access_token (str, optional): A pre-authenticated access token.

    Raises:
        ValueError: If neither (username, api_key) pair nor access_token is provided.

    Examples:
        # Initialize with username and API key
        skribble.init(username="your_username", api_key="your_api_key")

        # Initialize with access token
        skribble.init(access_token="your_access_token")

    Note:
        You must call this function before using any other SDK operations.
    """
    global _client
    if access_token:
        _client = SkribbleClient(access_token=access_token)
    elif username and api_key:
        _client = SkribbleClient(username=username, api_key=api_key)
    else:
        raise ValueError("Either (username, api_key) or access_token must be provided")

def get_client() -> SkribbleClient:
    if _client is None:
        raise ValueError("Skribble SDK not initialized. Call skribble.init(...) first.")
    return _client