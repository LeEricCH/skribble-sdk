from typing import Optional
from ..client_manager import init
from ..exceptions import SkribbleAuthError

def login(username: str, api_key: str) -> str:
    """
    Login to Skribble API and get an access token.

    Args:
        username (str): The API username
        api_key (str): The API key

    Returns:
        str: The access token

    Raises:
        SkribbleAuthError: If login fails due to invalid credentials
        SkribbleAPIError: If login fails due to API error
    """
    if not username or not api_key:
        raise ValueError("Username and API key are required")
    
    return init(username=username, api_key=api_key)