class SkribbleError(Exception):
    """Base exception for Skribble SDK"""

class SkribbleAuthError(SkribbleError):
    """Raised when authentication fails"""

class SkribbleAPIError(SkribbleError):
    """Raised when an API request fails"""

class SkribbleValidationError(SkribbleError):
    """Raised when input validation fails"""
    def __init__(self, message, errors=None):
        super().__init__(message)
        self.errors = errors or []

class SkribbleOperationError(Exception):
    def __init__(self, operation: str, message: str, original_error: Exception = None):
        self.operation = operation
        self.message = message
        self.original_error = original_error
        super().__init__(f"Error in operation '{operation}': {message}")