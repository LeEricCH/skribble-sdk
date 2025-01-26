"""Tests for authentication operations."""
import pytest
from skribble import auth
from skribble.exceptions import SkribbleAuthError, SkribbleAPIError

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

def test_login(requests_mock, mock_validation_request):
    """Test successful login."""
    mock_token = "test_access_token_123"
    requests_mock.post(
        'https://api.skribble.com/v2/access/login',
        text=mock_token
    )
    
    response = auth.login("test_user", "test_api_key")
    assert response == mock_token

def test_login_invalid_credentials(requests_mock):
    """Test login with invalid credentials."""
    requests_mock.post(
        'https://api.skribble.com/v2/access/login',
        status_code=401,
        json={
            "error": "invalid_credentials",
            "message": "Invalid username or API key"
        }
    )
    
    with pytest.raises(SkribbleAuthError) as exc_info:
        auth.login("invalid_user", "invalid_key")
    assert "Invalid credentials" in str(exc_info.value)

def test_login_server_error(requests_mock):
    """Test login with server error."""
    requests_mock.post(
        'https://api.skribble.com/v2/access/login',
        status_code=500,
        json={
            "error": "server_error",
            "message": "Internal server error"
        }
    )
    
    with pytest.raises(SkribbleAPIError) as exc_info:
        auth.login("test_user", "test_api_key")
    assert "Internal server error" in str(exc_info.value)

def test_login_missing_credentials():
    """Test login with missing credentials."""
    with pytest.raises(ValueError) as exc_info:
        auth.login(None, None)
    assert "Username and API key are required" in str(exc_info.value)

    with pytest.raises(ValueError) as exc_info:
        auth.login("", "")
    assert "Username and API key are required" in str(exc_info.value) 