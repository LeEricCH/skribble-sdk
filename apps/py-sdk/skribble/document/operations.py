from typing import Dict, Any, List
from ..client_manager import get_client
from ..exceptions import SkribbleValidationError, SkribbleOperationError
from ..models import Document, DocumentRequest

def list(limit: int = 20, offset: int = 0) -> List[Dict[str, Any]]:
    """
    List all documents with pagination.

    :param limit: The maximum number of documents to return. Default is 20.
    :type limit: int
    :param offset: The number of documents to skip. Default is 0.
    :type offset: int
    :return: A list of documents.
    :rtype: List[Dict[str, Any]]

    Example:
        >>> documents = skribble.document.list(limit=5, offset=0)
        >>> print(len(documents))
        5
    """
    return get_client().get_documents(limit, offset)

def get(document_id: str) -> Dict[str, Any]:
    """
    Get the document metadata.

    :param document_id: The ID of the document to retrieve.
    :type document_id: str
    :return: The document metadata.
    :rtype: Dict[str, Any]

    Example:
        >>> metadata = skribble.document.get("doc_123")
        >>> print(metadata['title'])
        'Sample Document'
    """
    response = get_client().get_document_meta(document_id)
    return Document(**response).model_dump()

def delete(document_id: str) -> Dict[str, Any]:
    """
    Delete a document.

    :param document_id: The ID of the document to delete.
    :type document_id: str
    :return: A dictionary containing the status and message of the delete operation.
    :rtype: Dict[str, Any]

    Example:
        >>> result = skribble.document.delete("doc_123")
        >>> print(result['status'])
        'success'
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

    :param document_data: The document data.
    :type document_data: Dict[str, Any]
    :return: The created document details.
    :rtype: Dict[str, Any]

    Example:
        >>> document_data = {
        ...     "title": "New Document",
        ...     "content_type": "application/pdf",
        ...     "content": "base64_encoded_pdf_content"
        ... }
        >>> result = skribble.document.add(document_data)
        >>> print(result['id'])
        'doc_789'
    """
    validated_request = DocumentRequest(**document_data)
    return get_client().add_document(validated_request.model_dump(exclude_none=True))

def download(document_id: str) -> bytes:
    """
    Download the document content.

    :param document_id: The ID of the document to download.
    :type document_id: str
    :return: The document content.
    :rtype: bytes

    Example:
        >>> content = skribble.document.download("doc_123")
        >>> print(len(content))
        12345
    """
    return get_client().download_document(document_id)

def preview(document_id: str, page_id: int, scale: int = 20) -> bytes:
    """
    Get the document page preview.

    :param document_id: The ID of the document.
    :type document_id: str
    :param page_id: The page number (starting from 0).
    :type page_id: int
    :param scale: The scale of the preview (20 for thumbnail, 100 for full size).
    :type scale: int
    :return: The preview image content.
    :rtype: bytes

    Example:
        >>> preview = skribble.document.preview("doc_123", page_id=0, scale=20)
        >>> print(len(preview))
        5678
    """
    return get_client().get_document_preview(document_id, page_id, scale)