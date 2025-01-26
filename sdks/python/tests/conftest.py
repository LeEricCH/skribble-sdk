"""Common test fixtures for skribble-sdk tests."""
import pytest
from skribble import init

@pytest.fixture
def mock_credentials():
    """Mock credentials for testing."""
    return {
        'username': 'test_user',
        'api_key': 'test_api_key',
        'access_token': 'test_access_token'
    }

@pytest.fixture
def mock_skribble_client(requests_mock, mock_credentials):
    """Mock skribble client with authenticated session."""
    # Mock the authentication endpoint with correct URL and response format
    requests_mock.post(
        'https://api.skribble.com/v2/access/login',
        text=mock_credentials['access_token']  # API returns raw token string
    )
    
    # Initialize the client with mock credentials
    access_token = init(
        username=mock_credentials['username'],
        api_key=mock_credentials['api_key']
    )
    
    return access_token

@pytest.fixture
def sample_pdf_content():
    """Sample PDF content for testing."""
    return b'%PDF-1.4\n...'  # Minimal valid PDF content

@pytest.fixture
def sample_signature_request():
    """Sample signature request data for testing."""
    return {
        "title": "Test Signature Request",
        "message": "Please sign this test document",
        "file_url": "https://example.com/test.pdf",
        "signatures": [
            {
                "account_email": "signer1@example.com",
                "signer_identity_data": {
                    "email_address": "signer1@example.com",
                    "mobile_number": "1234567890",
                    "first_name": "John",
                    "last_name": "Doe",
                    "language": "en"
                },
                "sequence": 1,
            }
        ]
    }

@pytest.fixture
def sample_document_data(sample_pdf_content):
    """Sample document data for testing."""
    import base64
    return {
        "title": "Test Document",
        "content_type": "application/pdf",
        "content": base64.b64encode(sample_pdf_content).decode('utf-8')
    } 