import unittest
from unittest.mock import patch, MagicMock
from skribble.attachment import operations
from skribble.exceptions import SkribbleValidationError, SkribbleAPIError

class TestAttachment(unittest.TestCase):

    @patch('skribble.attachment.operations.get_client')
    def test_add_attachment(self, mock_get_client):
        mock_client = MagicMock()
        mock_get_client.return_value = mock_client
        mock_client.add_signature_request_attachment.return_value = {"attachment_id": "test_id"}

        result = operations.add("test_sig_req_id", "test.pdf", "application/pdf", b"test content")
        self.assertEqual(result, {"attachment_id": "test_id"})
        mock_client.add_signature_request_attachment.assert_called_once_with(
            "test_sig_req_id", "test.pdf", "application/pdf", b"test content"
        )

    @patch('skribble.attachment.operations.get_client')
    def test_get_attachment(self, mock_get_client):
        mock_client = MagicMock()
        mock_get_client.return_value = mock_client
        mock_client.get_signature_request_attachment.return_value = b"test content"

        result = operations.get("test_sig_req_id", "test_attachment_id")
        self.assertEqual(result, b"test content")

    @patch('skribble.attachment.operations.get_client')
    def test_delete_attachment(self, mock_get_client):
        mock_client = MagicMock()
        mock_get_client.return_value = mock_client
        mock_client.delete_signature_request_attachment.return_value = None  # Assuming successful deletion returns None

        result = operations.delete("test_sig_req_id", "test_attachment_id")
        self.assertIsNone(result)
        mock_client.delete_signature_request_attachment.assert_called_once_with("test_sig_req_id", "test_attachment_id")

    @patch('skribble.attachment.operations.get_client')
    def test_delete_attachment_error(self, mock_get_client):
        mock_client = MagicMock()
        mock_get_client.return_value = mock_client
        mock_client.delete_signature_request_attachment.side_effect = SkribbleAPIError("Test error")

        with self.assertRaises(SkribbleAPIError):
            operations.delete("test_sig_req_id", "test_attachment_id")

if __name__ == '__main__':
    unittest.main()