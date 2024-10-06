import json

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
    def __init__(self, message, errors=None):
        if isinstance(message, str) and message.startswith('Validation error:'):
            try:
                error_dict = json.loads(message.split('Validation error:', 1)[1].strip())
                self.message = error_dict.get('message', message)
            except json.JSONDecodeError:
                self.message = message
        else:
            self.message = message
        self.errors = errors or []
        super().__init__(self.message)

class SkribbleOperationError(SkribbleError):
    def __init__(self, operation: str, message: str, original_error: Exception = None):
        self.operation = operation
        self.message = message
        self.original_error = original_error
        super().__init__(f"Error in operation '{operation}': {message}")