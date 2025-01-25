from ..client_manager import get_client
from ..exceptions import SkribbleAuthError
from ..models import AuthResponse

def login() -> AuthResponse:
    """
    Authenticate with the Skribble API and return the access token.

    Returns:
        AuthResponse: The authentication response containing the access token.

    Raises:
        SkribbleAuthError: If authentication fails.
    """
    try:
        client = get_client()
        token = client._authenticate()
        return AuthResponse(access_token=token)
    except Exception as e:
        raise SkribbleAuthError(f"Authentication failed: {str(e)}")