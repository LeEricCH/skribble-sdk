"""Tests for seal operations."""
import pytest
from skribble import seal
from skribble.exceptions import SkribbleAPIError, SkribbleValidationError

@pytest.fixture
def sample_seal_request():
    """Sample seal request data."""
    return {
        "content": "base64_encoded_pdf_content",
        "visual_signature": {
            "position": {
                "x": 20,
                "y": 20,
                "width": 260,
                "height": 120,
                "page": "0"
            },
            "image": {
                "content_type": "image/png",
                "content": "base64_encoded_image_content"
            }
        }
    }

def test_create_seal(requests_mock, mock_skribble_client, sample_seal_request):
    """Test creating a seal."""
    mock_response = {
        "document_id": "2db4ade9-cb56-a32d-aa37-7489ee67f72d"
    }
    requests_mock.post(
        'https://api.skribble.com/v2/seal',
        json=mock_response
    )
    
    response = seal.create(sample_seal_request)
    
    assert response.document_id == "2db4ade9-cb56-a32d-aa37-7489ee67f72d"

def test_create_specific_seal(requests_mock, mock_skribble_client):
    """Test creating a seal with specific account."""
    content = "base64_encoded_pdf_content"
    account_name = "company_seal_department_a"
    
    mock_response = {
        "document_id": "2db4ade9-cb56-a32d-aa37-7489ee67f72d"
    }
    requests_mock.post(
        'https://api.skribble.com/v2/seal',
        json=mock_response
    )
    
    response = seal.create_specific(content, account_name)
    
    assert response.document_id == "2db4ade9-cb56-a32d-aa37-7489ee67f72d"

def test_seal_error_handling(requests_mock, mock_skribble_client):
    """Test error handling for seal operations."""
    # Test validation error with empty data
    with pytest.raises(SkribbleValidationError) as exc_info:
        seal.create({})
    assert "Invalid seal data" in str(exc_info.value)
    
    # Test validation error with missing required fields
    requests_mock.post(
        'https://api.skribble.com/v2/seal',
        status_code=400,
        json={
            "error": "validation_error",
            "message": "Invalid seal data: missing visual_signature"
        }
    )
    with pytest.raises(SkribbleValidationError) as exc_info:
        seal.create({"content": "base64_content"})  # Missing visual_signature
    assert "Invalid seal data" in str(exc_info.value)
    
    # Test API error
    mock_request = {
        "content": "base64_encoded_pdf_content",
        "visual_signature": {
            "position": {
                "x": 20,
                "y": 20,
                "width": 260,
                "height": 120,
                "page": "0"
            }
        }
    }
    requests_mock.post(
        'https://api.skribble.com/v2/seal',
        status_code=400,
        json={
            "error": "invalid_content",
            "message": "Invalid PDF content provided"
        }
    )
    
    with pytest.raises(SkribbleAPIError) as exc_info:
        seal.create(mock_request)
    assert "Invalid PDF content" in str(exc_info.value)
    
    # Test specific seal creation with invalid account
    requests_mock.post(
        'https://api.skribble.com/v2/seal',
        status_code=404,
        json={
            "error": "not_found",
            "message": "Seal account not found"
        }
    )
    
    with pytest.raises(SkribbleAPIError) as exc_info:
        seal.create_specific("base64_content", "invalid_account")
    assert "Seal account not found" in str(exc_info.value) 