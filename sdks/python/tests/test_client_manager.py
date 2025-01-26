"""Tests for client manager."""
import pytest
from skribble.client_manager import init, get_client, reset_client
from skribble.exceptions import SkribbleAuthError, SkribbleValidationError
from skribble.client import SkribbleClient

@pytest.fixture
def mock_validation_request(requests_mock):
    """Mock the validation request that checks token validity."""
    requests_mock.get(
        'https://api.skribble.com/v2/signature-requests',
        json=[{
            "id": "test-id",
            "title": "Test Request",
            "document_id": "test-doc-id",
            "status_overall": "OPEN",
            "signatures": [{"sid": "test-sig", "status_code": "OPEN"}],
            "owner": "test-owner"
        }],
        status_code=200
    )

def test_init_with_credentials(requests_mock, mock_validation_request):
    """Test initialization with username and API key."""
    # Mock the auth endpoint
    requests_mock.post(
        'https://api.skribble.com/v2/access/login',
        text="test_token"
    )
    
    access_token = init(username="test_user", api_key="test_api_key")
    assert access_token is not None
    
    client = get_client()
    assert isinstance(client, SkribbleClient)
    assert client.username == "test_user"
    assert client.api_key == "test_api_key"

def test_init_with_token(mock_validation_request):
    """Test initialization with access token."""
    test_token = "test_access_token_123"
    access_token = init(access_token=test_token)
    assert access_token == test_token
    
    client = get_client()
    assert isinstance(client, SkribbleClient)
    assert client.access_token == test_token

def test_init_missing_credentials():
    """Test initialization with missing credentials."""
    with pytest.raises(SkribbleValidationError) as exc_info:
        init()
    assert "Either (username, api_key) or access_token must be provided" in str(exc_info.value)

def test_get_client_without_init():
    """Test getting client without initialization."""
    reset_client()  # Clear any existing client
    with pytest.raises(SkribbleValidationError) as exc_info:
        get_client()
    assert "Skribble SDK not initialized" in str(exc_info.value)

def test_reset_client(mock_validation_request):
    """Test resetting client."""
    # Initialize client
    init(access_token="test_token")
    assert get_client() is not None
    
    # Reset client
    reset_client()
    with pytest.raises(SkribbleValidationError) as exc_info:
        get_client()
    assert "Skribble SDK not initialized" in str(exc_info.value)

def test_multiple_init(mock_validation_request):
    """Test multiple initializations."""
    # First initialization
    token1 = init(access_token="token1")
    client1 = get_client()
    
    # Second initialization
    token2 = init(access_token="token2")
    client2 = get_client()
    
    # Should be different instances
    assert token1 != token2
    assert client1 != client2
    assert client2.access_token == "token2" 