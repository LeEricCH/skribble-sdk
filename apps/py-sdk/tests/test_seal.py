import unittest
from unittest.mock import patch, MagicMock
from skribble.seal import operations
from skribble.exceptions import SkribbleValidationError

class TestSeal(unittest.TestCase):

    @patch('skribble.seal.operations.get_client')
    def test_create_seal(self, mock_get_client):
        mock_client = MagicMock()
        mock_get_client.return_value = mock_client
        mock_client.create_seal.return_value = {"document_id": "sealed_doc"}

        result = operations.create({"content": "base64_content"})
        self.assertEqual(result, {"document_id": "sealed_doc"})

    @patch('skribble.seal.operations.get_client')
    def test_create_specific_seal(self, mock_get_client):
        mock_client = MagicMock()
        mock_get_client.return_value = mock_client
        mock_client.create_specific_seal.return_value = {"document_id": "sealed_doc"}

        result = operations.create_specific("base64_content", "account_name")
        self.assertEqual(result, {"document_id": "sealed_doc"})

    def test_create_seal_validation_error(self):
        with self.assertRaises(SkribbleValidationError):
            operations.create({})  # Empty data should raise validation error

if __name__ == '__main__':
    unittest.main()