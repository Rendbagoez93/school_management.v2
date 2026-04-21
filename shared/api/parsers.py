"""Request parsing utilities for API views.

These utilities parse and validate query parameters or JSON request bodies
using Pydantic models. They raise ApiError on validation failure.
"""

import json
from typing import TypeVar

from django.http import HttpRequest
from pydantic import BaseModel, ValidationError

from .exceptions import ApiError

T = TypeVar("T", bound=BaseModel)


def parse_query(request: HttpRequest, schema: type[T]) -> T:
    """Parse and validate query parameters into a Pydantic model.
    
    Args:
        request: Django HttpRequest object
        schema: Pydantic model class to validate against
    
    Returns:
        Validated Pydantic model instance
    
    Raises:
        ApiError: If validation fails (422 status)
    
    Examples:
        params = parse_query(request, StudentFilterSchema)
        # params is now a validated StudentFilterSchema instance
    """
    try:
        return schema(**request.GET.dict())
    except ValidationError as e:
        error_messages = []
        for error in e.errors():
            field = " -> ".join(str(loc) for loc in error["loc"])
            error_messages.append(f"{field}: {error['msg']}")
        
        raise ApiError(
            "validation_error",
            "Query parameter validation failed: " + "; ".join(error_messages),
            status=422,
            data={"errors": e.errors()},
        )


def parse_body(request: HttpRequest, schema: type[T]) -> T:
    """Parse and validate JSON request body into a Pydantic model.
    
    Args:
        request: Django HttpRequest object
        schema: Pydantic model class to validate against
    
    Returns:
        Validated Pydantic model instance
    
    Raises:
        ApiError: If JSON parsing or validation fails (422 status)
    
    Examples:
        data = parse_body(request, StudentCreateSchema)
        # data is now a validated StudentCreateSchema instance
    """
    try:
        body_data = json.loads(request.body)
    except json.JSONDecodeError:
        raise ApiError(
            "invalid_json",
            "Request body must be valid JSON",
            status=422,
        )
    
    try:
        return schema(**body_data)
    except ValidationError as e:
        error_messages = []
        for error in e.errors():
            field = " -> ".join(str(loc) for loc in error["loc"])
            error_messages.append(f"{field}: {error['msg']}")
        
        raise ApiError(
            "validation_error",
            "Request body validation failed: " + "; ".join(error_messages),
            status=422,
            data={"errors": e.errors()},
        )
