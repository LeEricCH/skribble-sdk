import unittest
import sys
import os

# Add the parent directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import all test modules
from tests.test_signature_request import TestSignatureRequest
from tests.test_attachment import TestAttachment
from tests.test_document import TestDocument
from tests.test_seal import TestSeal

if __name__ == '__main__':
    # Create a test suite
    test_suite = unittest.TestSuite()

    # Add test cases
    test_suite.addTest(unittest.TestLoader().loadTestsFromTestCase(TestSignatureRequest))
    test_suite.addTest(unittest.TestLoader().loadTestsFromTestCase(TestAttachment))
    test_suite.addTest(unittest.TestLoader().loadTestsFromTestCase(TestDocument))
    test_suite.addTest(unittest.TestLoader().loadTestsFromTestCase(TestSeal))

    # Run the tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)

    # Exit with non-zero status if there were failures
    sys.exit(not result.wasSuccessful())