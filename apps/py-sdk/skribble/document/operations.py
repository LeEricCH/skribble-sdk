from typing import Dict, Any, List
from ..client_manager import get_client
from ..exceptions import SkribbleValidationError, SkribbleOperationError
from ..models import Document, DocumentRequest

def list(limit: int = 20, offset: int = 0) -> List[Dict[str, Any]]:
    """
    List all documents with pagination.

    Args:
        limit (int): The maximum number of documents to return. Default is 20.
        offset (int): The number of documents to skip. Default is 0.

    Returns:
        List[Dict[str, Any]]: A list of documents.
    """
    return get_client().get_documents(limit, offset)

def get(document_id: str) -> Dict[str, Any]:
    """
    Get the document metadata.

    Args:
        document_id (str): The ID of the document to retrieve.

    Returns:
        Dict[str, Any]: The document metadata.
    """
    response = get_client().get_document_meta(document_id)
    return Document(**response).model_dump()

def delete(document_id: str) -> Dict[str, Any]:
    """
    Delete a document.

    Args:
        document_id (str): The ID of the document to delete.

    Returns:
        Dict[str, Any]: A dictionary containing the status and message of the delete operation.
    """
    try:
        result = get_client().delete_document(document_id)
        if result is None:
            return {"status": "success", "message": f"Document {document_id} deleted successfully"}
        return result
    except Exception as e:
        raise SkribbleOperationError("delete_document", str(e), e)

def add(document_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Add a new document.

    Args:
        document_data (Dict[str, Any]): The document data.

    Returns:
        Dict[str, Any]: The created document details.
    """
    validated_request = DocumentRequest(**document_data)
    return get_client().add_document(validated_request.model_dump(exclude_none=True))

def download(document_id: str) -> bytes:
    """
    Download the document content.

    Args:
        document_id (str): The ID of the document to download.

    Returns:
        bytes: The document content.
    """
    return get_client().download_document(document_id)

def preview(document_id: str, page_id: int, scale: int = 20) -> bytes:
    """
    Get the document page preview.

    Args:
        document_id (str): The ID of the document.
        page_id (int): The page number (starting from 0).
        scale (int): The scale of the preview (20 for thumbnail, 100 for full size).

    Returns:
        bytes: The preview image content.
    """
    return get_client().get_document_preview(document_id, page_id, scale)