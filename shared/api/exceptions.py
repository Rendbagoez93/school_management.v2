"""API exceptions for School Management System."""


class ApiError(Exception):
    """Custom exception for API errors with structured response format.
    
    Used to signal HTTP errors from views or services.
    The ApiErrorMiddleware catches it and returns a structured JSON response.
    
    Args:
        code: Error code identifier (e.g., 'not_found', 'validation_error')
        message: Human-readable error message
        status: HTTP status code (default: 400)
        data: Additional error data (optional)
    
    Examples:
        raise ApiError("not_found", "Student not found", status=404)
        raise ApiError("validation_error", "Invalid input", status=422)
    """

    def __init__(self, code: str, message: str, status: int = 400, data: dict | None = None):
        self.code = code
        self.message = message
        self.status = status
        self.data = data
        super().__init__(message)
