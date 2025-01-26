"""Tests for exception classes."""
import pytest
from pydantic import ValidationError, BaseModel
from skribble.exceptions import (
    SkribbleError,
    SkribbleAuthError,
    SkribbleAPIError,
    SkribbleValidationError,
    SkribbleOperationError
)

def test_base_exception():
    """Test base SkribbleError."""
    message = "Test error message"
    error = SkribbleError(message)
    assert str(error) == message
    assert error.message == message

def test_auth_error():
    """Test SkribbleAuthError."""
    message = "Invalid credentials"
    error = SkribbleAuthError(message)
    assert str(error) == message
    assert error.message == message
    assert isinstance(error, SkribbleError)

def test_api_error_with_json():
    """Test SkribbleAPIError with JSON message."""
    json_message = '{"message": "API error occurred", "code": "error_code"}'
    error = SkribbleAPIError(json_message, status_code=400)
    assert error.message == "API error occurred"
    assert error.status_code == 400
    assert isinstance(error, SkribbleError)

def test_api_error_with_plain_message():
    """Test SkribbleAPIError with plain text message."""
    message = "Plain text error"
    error = SkribbleAPIError(message, status_code=500)
    assert error.message == message
    assert error.status_code == 500

def test_validation_error_with_message():
    """Test SkribbleValidationError with string message."""
    message = "Validation failed"
    errors = [{"loc": ["field1"], "msg": "Field is required"}]
    error = SkribbleValidationError(message, errors)
    assert error.message == message
    assert error.errors == errors
    assert isinstance(error, SkribbleError)

def test_validation_error_with_pydantic():
    """Test SkribbleValidationError with Pydantic ValidationError."""
    class TestModel(BaseModel):
        required_field: str
        positive_number: int

    # Create a Pydantic validation error
    with pytest.raises(ValidationError) as exc_info:
        TestModel(required_field=None, positive_number=-1)
    
    error = SkribbleValidationError(exc_info.value)
    assert "Validation Error:" in error.message
    assert "required_field" in error.message
    assert isinstance(error, SkribbleError)

def test_operation_error_with_message():
    """Test SkribbleOperationError with string message."""
    operation = "test_operation"
    message = "Operation failed"
    error = SkribbleOperationError(operation, message)
    assert error.operation == operation
    assert "Error in 'test_operation': Operation failed" in str(error)
    assert isinstance(error, SkribbleError)

def test_operation_error_with_validation():
    """Test SkribbleOperationError with validation error."""
    class TestModel(BaseModel):
        required_field: str

    # Create a Pydantic validation error
    with pytest.raises(ValidationError) as exc_info:
        TestModel(required_field=None)
    
    error = SkribbleOperationError("test_operation", "Validation failed", exc_info.value)
    assert error.operation == "test_operation"
    assert "Validation error in 'test_operation':" in str(error)
    assert "required_field" in str(error)
    assert isinstance(error, SkribbleError)

def test_operation_error_with_nested():
    """Test SkribbleOperationError with nested original error."""
    original_error = ValueError("Original error")
    error = SkribbleOperationError("test_operation", "Operation failed", original_error)
    assert error.operation == "test_operation"
    assert error.original_error == original_error
    assert "Error in 'test_operation': Operation failed" in str(error) 