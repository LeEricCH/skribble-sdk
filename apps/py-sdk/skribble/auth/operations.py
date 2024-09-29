from ..client_manager import get_client
from ..exceptions import SkribbleAuthError

def login() -> str:
    """
    Authenticate with the Skribble API and return the access token.

    Returns:
        str: The access token for authenticated requests.

    Raises:
        SkribbleAuthError: If authentication fails.
    """
    try:
        client = get_client()
        return client._authenticate()
    except Exception as e:
        raise SkribbleAuthError(f"Authentication failed: {str(e)}")