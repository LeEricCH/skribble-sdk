from typing import Optional, List, Dict, Any
import json
from pydantic import ValidationError

class SkribbleError(Exception):
    """Base exception for Skribble SDK"""
    def __init__(self, message):
        self.message = message
        super().__init__(self.message)

class SkribbleAuthError(SkribbleError):
    """Raised when authentication fails"""
    pass

class SkribbleAPIError(SkribbleError):
    """Raised for any API errors"""
    def __init__(self, message, status_code=None):
        try:
            error_dict = json.loads(message)
            self.message = error_dict.get('message', message)
        except json.JSONDecodeError:
            self.message = message
        self.status_code = status_code
        super().__init__(self.message)

class SkribbleValidationError(SkribbleError):
    """Raised when input validation fails or when the API returns a 400 error"""
    def __init__(self, message: str, errors: Optional[List[Dict[str, Any]]] = None):
        if isinstance(message, ValidationError):
            # Format Pydantic validation errors nicely
            error_messages = []
            for error in message.errors():
                field = " -> ".join(str(loc) for loc in error["loc"])
                msg = error["msg"]
                error_messages.append(f"  • {field}: {msg}")
            
            self.message = "Validation Error:\n" + "\n".join(error_messages)
        else:
            self.message = message
        self.errors = errors or []
        super().__init__(self.message)

class SkribbleOperationError(SkribbleError):
    def __init__(self, operation: str, message: str, original_error: Optional[Exception] = None):
        self.operation = operation
        if isinstance(original_error, ValidationError):
            # Format validation errors nicely when they occur in operations
            error_messages = []
            for error in original_error.errors():
                field = " -> ".join(str(loc) for loc in error["loc"])
                msg = error["msg"]
                error_messages.append(f"  • {field}: {msg}")
            
            self.message = f"Validation error in '{operation}':\n" + "\n".join(error_messages)
        else:
            self.message = f"Error in '{operation}': {message}"
        self.original_error = original_error
        super().__init__(self.message)