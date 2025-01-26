"""Tests for document operations."""
import pytest
from skribble import document
from skribble.exceptions import SkribbleAPIError, SkribbleValidationError

@pytest.fixture
def sample_document_request():
    """Sample document request data."""
    return {
        "title": "Test Document",
        "content_type": "application/pdf",
        "content": "base64_encoded_pdf_content"
    }

def test_add_document(requests_mock, mock_skribble_client, sample_document_request):
    """Test adding a new document."""
    mock_response = {
        "id": "2db4ade9-cb56-a32d-aa37-7489ee67f72d",
        "title": "Test Document",
        "content_type": "application/pdf",
        "size": 12345,
        "page_count": 2,
        "page_width": 595,
        "page_height": 842,
        "owner": "api_demo_skribbleag_42b4_6",
        "read_access": ["api_demo_skribbleag_42b4_6"],
        "write_access": ["api_demo_skribbleag_42b4_6"],
        "created_at": "2024-03-26T12:00:00Z",
        "updated_at": "2024-03-26T12:00:00Z",
        "signature_fields": [
            {
                "name": "signature1",
                "status": "UNSIGNED",
                "position": {
                    "x": 100,
                    "y": 100,
                    "width": 200,
                    "height": 100,
                    "page": "1"
                }
            }
        ]
    }
    requests_mock.post(
        'https://api.skribble.com/v2/documents',
        json=mock_response
    )
    
    response = document.add(sample_document_request)
    
    assert response.id == "2db4ade9-cb56-a32d-aa37-7489ee67f72d"
    assert response.title == "Test Document"
    assert response.content_type == "application/pdf"
    assert response.page_count == 2
    assert len(response.signature_fields) == 1

def test_get_document(requests_mock, mock_skribble_client):
    """Test getting a document."""
    document_id = "2db4ade9-cb56-a32d-aa37-7489ee67f72d"
    mock_response = {
        "id": document_id,
        "title": "Test Document",
        "content_type": "application/pdf",
        "size": 12345,
        "page_count": 2,
        "page_width": 595,
        "page_height": 842,
        "owner": "api_demo_skribbleag_42b4_6",
        "read_access": ["api_demo_skribbleag_42b4_6"],
        "write_access": ["api_demo_skribbleag_42b4_6"],
        "created_at": "2024-03-26T12:00:00Z",
        "updated_at": "2024-03-26T12:00:00Z"
    }
    requests_mock.get(
        f'https://api.skribble.com/v2/documents/{document_id}',
        json=mock_response
    )
    
    response = document.get(document_id)
    
    assert response.id == document_id
    assert response.title == "Test Document"
    assert response.size == 12345

def test_list_documents(requests_mock, mock_skribble_client):
    """Test listing documents."""
    mock_response = [
        {
            "id": "2db4ade9-cb56-a32d-aa37-7489ee67f72d",
            "title": "Test Document 1",
            "content_type": "application/pdf",
            "size": 12345,
            "owner": "api_demo_skribbleag_42b4_6",
            "read_access": ["api_demo_skribbleag_42b4_6"],
            "write_access": ["api_demo_skribbleag_42b4_6"],
            "created_at": "2024-03-26T12:00:00Z",
            "updated_at": "2024-03-26T12:00:00Z"
        },
        {
            "id": "3ec5bdf4-dc67-b43e-bbfe-86feba44ed3f",
            "title": "Test Document 2",
            "content_type": "application/pdf",
            "size": 67890,
            "owner": "api_demo_skribbleag_42b4_6",
            "read_access": ["api_demo_skribbleag_42b4_6"],
            "write_access": ["api_demo_skribbleag_42b4_6"],
            "created_at": "2024-03-26T12:00:00Z",
            "updated_at": "2024-03-26T12:00:00Z"
        }
    ]
    requests_mock.get(
        'https://api.skribble.com/v2/documents',
        json=mock_response
    )
    
    response = document.list(limit=2)
    
    assert len(response) == 2
    assert response[0].id == "2db4ade9-cb56-a32d-aa37-7489ee67f72d"
    assert response[1].title == "Test Document 2"

def test_delete_document(requests_mock, mock_skribble_client):
    """Test deleting a document."""
    document_id = "2db4ade9-cb56-a32d-aa37-7489ee67f72d"
    
    requests_mock.delete(
        f'https://api.skribble.com/v2/documents/{document_id}',
        status_code=204
    )
    
    response = document.delete(document_id)
    
    assert response["status"] == "success"
    assert response["message"] == f"Document {document_id} deleted successfully"

def test_download_document(requests_mock, mock_skribble_client):
    """Test downloading a document."""
    document_id = "2db4ade9-cb56-a32d-aa37-7489ee67f72d"
    mock_content = b"mock pdf content"
    
    requests_mock.get(
        f'https://api.skribble.com/v2/documents/{document_id}/content',
        content=mock_content
    )
    
    # Test blob download
    blob_response = document.download(document_id, content_type="blob")
    assert blob_response == mock_content
    
    # Test base64 download
    base64_response = document.download(document_id, content_type="base64")
    import base64
    assert base64.b64decode(base64_response) == mock_content

def test_preview_document(requests_mock, mock_skribble_client):
    """Test getting a document preview."""
    document_id = "2db4ade9-cb56-a32d-aa37-7489ee67f72d"
    page_id = 0
    mock_content = b"mock preview image"
    
    # Mock successful preview response
    requests_mock.get(
        f'https://api.skribble.com/v2/documents/{document_id}/pages/{page_id}?scale=20',
        content=mock_content,
        headers={'Content-Type': 'image/png'}
    )
    
    response = document.preview(document_id, page_id)
    assert response == mock_content
    
    # Test preview generation in progress
    requests_mock.get(
        f'https://api.skribble.com/v2/documents/{document_id}/pages/{page_id}?scale=20',
        [
            {'status_code': 202},  # First attempt - still generating
            {'status_code': 200, 'content': mock_content, 'headers': {'Content-Type': 'image/png'}}  # Second attempt - ready
        ]
    )
    
    response = document.preview(document_id, page_id, max_retries=2, retry_delay=0)
    assert response == mock_content

def test_document_error_handling(requests_mock, mock_skribble_client):
    """Test error handling for document operations."""
    # Test Pydantic validation error - empty data
    with pytest.raises(SkribbleValidationError) as exc_info:
        document.add({})
    assert "title" in str(exc_info.value)
    
    # Test API validation error
    invalid_doc = {
        "title": "Test Document",
        "content_type": "application/pdf",
        "content": "invalid_base64_content"
    }
    requests_mock.post(
        'https://api.skribble.com/v2/documents',
        status_code=400,
        json={
            "error": "validation_error",
            "message": "Invalid base64 content"
        }
    )
    with pytest.raises(SkribbleValidationError) as exc_info:
        document.add(invalid_doc)
    assert "Invalid base64 content" in str(exc_info.value)
    
    # Test API error
    document_id = "2db4ade9-cb56-a32d-aa37-7489ee67f72d"
    requests_mock.get(
        f'https://api.skribble.com/v2/documents/{document_id}',
        status_code=404,
        json={
            "error": "not_found",
            "message": "Document not found"
        }
    )
    
    with pytest.raises(SkribbleAPIError) as exc_info:
        document.get(document_id)
    assert "Document not found" in str(exc_info.value)
    
    # Test preview error with invalid content type
    requests_mock.get(
        f'https://api.skribble.com/v2/documents/{document_id}/pages/0?scale=20',
        headers={'Content-Type': 'application/json'},
        json={"error": "Invalid content type"}
    )
    
    with pytest.raises(SkribbleAPIError) as exc_info:
        document.preview(document_id, 0)
    assert "Unexpected content type" in str(exc_info.value) 