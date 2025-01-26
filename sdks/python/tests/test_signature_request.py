"""Tests for signature request operations."""
import pytest
from skribble import signature_request
from skribble.exceptions import SkribbleAPIError, SkribbleValidationError

@pytest.fixture
def sample_signature_request():
    """Sample signature request data."""
    return {
        "title": "Test Signature Request",
        "message": "Please sign this document",
        "file_url": "https://example.com/document.pdf",
        "signatures": [
            {
                "account_email": "signer1@example.com",
                "signer_identity_data": {
                    "email_address": "signer1@example.com",
                    "first_name": "John",
                    "last_name": "Doe",
                    "language": "en"
                },
                "sequence": 1
            }
        ]
    }

@pytest.fixture
def mock_response_base():
    """Base mock response with required fields."""
    return {
        "id": "d332f1c3-3a1f-d669-ecad-75febea33cc2",
        "title": "Test Signature Request",
        "document_id": "2db4ade9-cb56-a32d-aa37-7489ee67f72d",
        "status_overall": "OPEN",
        "signatures": [
            {
                "sid": "7db0f4b9-a79f-0a4d-e9f3-dcdc3cbd12a0",
                "account_email": "signer1@example.com",
                "status_code": "OPEN"
            }
        ],
        "owner": "api_demo_skribbleag_42b4_6",
        "created_at": "2024-03-26T12:00:00Z",
        "updated_at": "2024-03-26T12:00:00Z"
    }

def test_create_signature_request(requests_mock, mock_skribble_client, sample_signature_request):
    """Test creating a signature request."""
    mock_response = {
        "id": "d332f1c3-3a1f-d669-ecad-75febea33cc2",
        "title": "Test Signature Request",
        "message": "Please sign this document",
        "document_id": "2db4ade9-cb56-a32d-aa37-7489ee67f72d",
        "status_overall": "OPEN",
        "signatures": [
            {
                "sid": "7db0f4b9-a79f-0a4d-e9f3-dcdc3cbd12a0",
                "account_email": "signer1@example.com",
                "status_code": "OPEN"
            }
        ],
        "owner": "api_demo_skribbleag_42b4_6",
        "created_at": "2024-03-26T12:00:00Z",
        "updated_at": "2024-03-26T12:00:00Z"
    }
    requests_mock.post(
        'https://api.skribble.com/v2/signature-requests',
        json=mock_response
    )
    
    response = signature_request.create(sample_signature_request)
    
    assert response.id == "d332f1c3-3a1f-d669-ecad-75febea33cc2"
    assert response.status_overall == "OPEN"
    assert len(response.signatures) == 1

def test_create_signature_request_with_attachments(requests_mock, mock_skribble_client, sample_signature_request, mock_response_base):
    """Test creating a signature request with attachments."""
    sample_signature_request["attachments"] = [
        {
            "filename": "terms.pdf",
            "content_type": "application/pdf",
            "content": "base64_encoded_content"
        }
    ]
    
    mock_response = {**mock_response_base, "attachments": [
        {
            "attachment_id": "att123",
            "filename": "terms.pdf"
        }
    ]}
    requests_mock.post(
        'https://api.skribble.com/v2/signature-requests',
        json=mock_response
    )
    
    response = signature_request.create(sample_signature_request)
    assert len(response.attachments) == 1
    assert response.attachments[0].filename == "terms.pdf"

def test_get_signature_request(requests_mock, mock_skribble_client, mock_response_base):
    """Test getting a signature request."""
    signature_request_id = mock_response_base["id"]
    requests_mock.get(
        f'https://api.skribble.com/v2/signature-requests/{signature_request_id}',
        json=mock_response_base
    )
    
    response = signature_request.get(signature_request_id)
    assert response.id == signature_request_id
    assert response.status_overall == "OPEN"

def test_list_signature_requests(requests_mock, mock_skribble_client, mock_response_base):
    """Test listing signature requests."""
    mock_response = [
        mock_response_base,
        {
            **mock_response_base,
            "id": "e443g2d4-4b2g-e770-fdbe-86gfcb44ed4g",
            "title": "Test Request 2",
            "status_overall": "COMPLETED"
        }
    ]
    requests_mock.get(
        'https://api.skribble.com/v2/signature-requests',
        json=mock_response
    )
    
    response = signature_request.list(page_size=10)
    assert len(response) == 2
    assert response[0].status_overall == "OPEN"
    assert response[1].status_overall == "COMPLETED"

def test_withdraw_signature_request(requests_mock, mock_skribble_client, mock_response_base):
    """Test withdrawing a signature request."""
    signature_request_id = mock_response_base["id"]
    mock_response = {
        **mock_response_base,
        "status_overall": "WITHDRAWN"
    }
    requests_mock.post(
        f'https://api.skribble.com/v2/signature-requests/{signature_request_id}/withdraw',
        json=mock_response
    )
    
    response = signature_request.withdraw(signature_request_id, message="Withdrawing for testing")
    assert response.status_overall == "WITHDRAWN"

def test_delete_signature_request(requests_mock, mock_skribble_client):
    """Test deleting a signature request."""
    signature_request_id = "d332f1c3-3a1f-d669-ecad-75febea33cc2"
    
    requests_mock.delete(
        f'https://api.skribble.com/v2/signature-requests/{signature_request_id}',
        status_code=204
    )
    
    response = signature_request.delete(signature_request_id)
    assert response["status"] == "success"
    assert signature_request_id in response["message"]

def test_remind_signature_request(requests_mock, mock_skribble_client, mock_response_base):
    """Test reminding about a signature request."""
    signature_request_id = mock_response_base["id"]
    mock_response = {
        **mock_response_base,
        "status_overall": "OPEN",
        "message": "Reminder sent successfully"
    }
    requests_mock.post(
        f'https://api.skribble.com/v2/signature-requests/{signature_request_id}/remind',
        json=mock_response
    )
    
    response = signature_request.remind(signature_request_id)
    assert response.id == signature_request_id
    assert response.status_overall == "OPEN"

def test_error_handling(requests_mock, mock_skribble_client):
    """Test error handling for signature request operations."""
    # Test validation error
    with pytest.raises(SkribbleValidationError) as exc_info:
        signature_request.create({})
    assert "Invalid" in str(exc_info.value)
    
    # Test API error
    signature_request_id = "invalid_id"
    requests_mock.get(
        f'https://api.skribble.com/v2/signature-requests/{signature_request_id}',
        status_code=404,
        json={
            "error": "not_found",
            "message": "Signature request not found"
        }
    )
    
    with pytest.raises(SkribbleAPIError) as exc_info:
        signature_request.get(signature_request_id)
    assert "not found" in str(exc_info.value)

def test_signer_operations(requests_mock, mock_skribble_client, mock_response_base):
    """Test signer-related operations."""
    signature_request_id = mock_response_base["id"]
    signer_id = mock_response_base["signatures"][0]["sid"]
    
    # Mock GET request for signature request check
    requests_mock.get(
        f'https://api.skribble.com/v2/signature-requests/{signature_request_id}',
        json=mock_response_base
    )
    
    # Test adding a signer
    add_signer_response = {
        **mock_response_base,
        "signatures": [
            {
                "sid": signer_id,
                "account_email": "newsigner@example.com",
                "status_code": "OPEN"
            }
        ]
    }
    requests_mock.post(
        f'https://api.skribble.com/v2/signature-requests/{signature_request_id}/signatures',
        json=add_signer_response
    )
    
    new_signer = {
        "account_email": "newsigner@example.com",
        "signer_identity_data": {
            "email_address": "newsigner@example.com",
            "first_name": "New",
            "last_name": "Signer"
        }
    }
    response = signature_request.signer.add(signature_request_id, new_signer)
    assert response.signatures[0].account_email == "newsigner@example.com"
    
    # Test removing a signer
    requests_mock.delete(
        f'https://api.skribble.com/v2/signature-requests/{signature_request_id}/signatures/{signer_id}',
        status_code=204
    )
    
    response = signature_request.signer.remove(signature_request_id, signer_id)
    assert response["status"] == "success"
    
    # Test replacing signers
    replace_response = {
        **mock_response_base,
        "signatures": [
            {
                "sid": "new_signer_id",
                "account_email": "replacement@example.com",
                "status_code": "OPEN"
            }
        ]
    }
    requests_mock.put(
        'https://api.skribble.com/v2/signature-requests',
        json=replace_response
    )
    
    new_signers = [{
        "account_email": "replacement@example.com",
        "signer_identity_data": {
            "email_address": "replacement@example.com",
            "first_name": "Replacement",
            "last_name": "Signer"
        }
    }]
    response = signature_request.signer.replace(signature_request_id, new_signers)
    assert len(response.signatures) == 1
    assert response.signatures[0].account_email == "replacement@example.com" 