"""Middleware for attaching SchoolUser to request object.

This middleware enhances the request object with a school_user attribute
that provides access to the SchoolUser proxy model with its custom manager
and methods.
"""

from collections.abc import Callable

from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpRequest, HttpResponse

from applications.user_management.models import SchoolUser


class SchoolUserMiddleware:
    """Middleware that attaches SchoolUser instance to request.
    
    This middleware:
    - Converts the default User instance to SchoolUser proxy model
    - Prefetches related groups for role checking efficiency
    - Handles unauthenticated users gracefully
    - Caches the result to avoid multiple database queries
    
    """

    def __init__(self, get_response: Callable[[HttpRequest], HttpResponse]):
        self.get_response = get_response

    def __call__(self, request: HttpRequest) -> HttpResponse:
        # Skip if already set (prevents duplicate queries)
        if hasattr(request, "school_user") and request.school_user:
            return self.get_response(request)

        # Attach SchoolUser if authenticated, None otherwise
        if hasattr(request, "user") and request.user.is_authenticated:
            try:
                # Use prefetch_related to optimize role checking
                request.school_user = (
                    SchoolUser.objects.prefetch_related("groups")
                    .get(id=request.user.id)
                )
            except ObjectDoesNotExist:
                # User exists in auth but not as SchoolUser (shouldn't happen in normal flow)
                request.school_user = None
        else:
            request.school_user = None

        response = self.get_response(request)
        return response

