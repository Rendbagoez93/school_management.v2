"""API middleware for School Management System."""

from django.http import JsonResponse

from .exceptions import ApiError
from .response import api_error


class ApiErrorMiddleware:
    """Middleware to catch ApiError exceptions and return structured JSON responses.
    
    This middleware catches ApiError exceptions raised anywhere in the request
    processing chain and converts them to standard JSON error responses.
    
    Register in settings.MIDDLEWARE:
        "shared.api.middleware.ApiErrorMiddleware"
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        return self.get_response(request)

    def process_exception(self, request, exception):
        """Process ApiError exceptions and return JSON error response."""
        if isinstance(exception, ApiError):
            return api_error(
                code=exception.code,
                msg=exception.message,
                status=exception.status,
                data=exception.data,
            )
        
        # Let other exceptions propagate
        return None
