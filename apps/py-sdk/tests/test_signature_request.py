import unittest
from unittest.mock import patch, MagicMock
from skribble.signature_request import operations
from skribble.exceptions import SkribbleValidationError

class TestSignatureRequest(unittest.TestCase):

    @patch('skribble.signature_request.operations.get_client')
    def test_create_signature_request(self, mock_get_client):
        mock_client = MagicMock()
        mock_get_client.return_value = mock_client
        mock_client.create_signature_request.return_value = {"id": "test_id"}

        test_data = {
            "title": "Test Signature Request",
            "message": "Please sign this test document",
            "file_url": "https://example.com/test.pdf",
            "signatures": [
                {
                    "account_email": "signer1@example.com",
                    "signer_identity_data": {
                        "email_address": "signer1@example.com",
                        "first_name": "John",
                        "last_name": "Doe"
                    },
                    "sequence": 1
                },
                {
                    "account_email": "signer2@example.com",
                    "sequence": 2
                }
            ],
            "cc_email_addresses": ["cc@example.com"],
            "legislation": "ZERTES",
            "quality": "ADVANCED",
            "language": "en",
            "callback_url": "https://example.com/callback"
        }

        result = operations.create(test_data)
        self.assertEqual(result, {"id": "test_id"})

    @patch('skribble.signature_request.operations.get_client')
    def test_get_signature_request(self, mock_get_client):
        mock_client = MagicMock()
        mock_get_client.return_value = mock_client
        mock_client.get_signature_request.return_value = {"id": "test_id", "status": "OPEN"}

        result = operations.get("test_id")
        self.assertEqual(result, {"id": "test_id", "status": "OPEN"})

    @patch('skribble.signature_request.operations.get_client')
    def test_list_signature_requests(self, mock_get_client):
        mock_client = MagicMock()
        mock_get_client.return_value = mock_client
        mock_client.list_signature_requests.return_value = [{"id": "test_id1"}, {"id": "test_id2"}]

        result = operations.list(limit=10, offset=0)
        self.assertEqual(result, [{"id": "test_id1"}, {"id": "test_id2"}])

    @patch('skribble.signature_request.operations.get_client')
    def test_delete_signature_request(self, mock_get_client):
        mock_client = MagicMock()
        mock_get_client.return_value = mock_client
        mock_client.delete_signature_request.return_value = None

        result = operations.delete("test_id")
        self.assertIsNone(result)

    def test_create_signature_request_validation_error(self):
        invalid_data = {
            "title": "Test Signature Request",
            "message": "Please sign this test document",
            "signatures": [
                {
                    "invalid_field": "This should cause a validation error"
                }
            ]
        }

        with self.assertRaises(SkribbleValidationError):
            operations.create(invalid_data)

if __name__ == '__main__':
    unittest.main()