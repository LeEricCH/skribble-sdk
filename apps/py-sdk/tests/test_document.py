import unittest
from unittest.mock import patch, MagicMock
from skribble.document import operations
from skribble.exceptions import SkribbleValidationError

class TestDocument(unittest.TestCase):

    @patch('skribble.document.operations.get_client')
    def test_list_documents(self, mock_get_client):
        mock_client = MagicMock()
        mock_get_client.return_value = mock_client
        mock_client.get_documents.return_value = [{"id": "doc1"}, {"id": "doc2"}]

        result = operations.list(limit=2, offset=0)
        self.assertEqual(result, [{"id": "doc1"}, {"id": "doc2"}])

    @patch('skribble.document.operations.get_client')
    def test_get_document(self, mock_get_client):
        mock_client = MagicMock()
        mock_get_client.return_value = mock_client
        mock_client.get_document_meta.return_value = {
            "id": "doc1",
            "title": "Test Document",
            "content_type": "application/pdf",
            "size": 1024,
            "owner": "test_owner"
        }

        result = operations.get("doc1")
        self.assertEqual(result["id"], "doc1")
        self.assertEqual(result["title"], "Test Document")
        self.assertEqual(result["content_type"], "application/pdf")
        self.assertEqual(result["size"], 1024)
        self.assertEqual(result["owner"], "test_owner")

    @patch('skribble.document.operations.get_client')
    def test_delete_document(self, mock_get_client):
        mock_client = MagicMock()
        mock_get_client.return_value = mock_client

        operations.delete("doc1")
        mock_client.delete_document.assert_called_once_with("doc1")

    @patch('skribble.document.operations.get_client')
    def test_add_document(self, mock_get_client):
        mock_client = MagicMock()
        mock_get_client.return_value = mock_client
        mock_client.add_document.return_value = {"id": "new_doc"}

        result = operations.add({"title": "New Document", "content": "base64_content", "content_type": "application/pdf"})
        self.assertEqual(result, {"id": "new_doc"})

if __name__ == '__main__':
    unittest.main()