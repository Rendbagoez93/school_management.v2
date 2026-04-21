"""API response wrappers for School Management System.

All API responses follow a standard format:
{
    "code": "ok" | "error_code",
    "msg": "Human-readable message",
    "data": { ... } | null
}
"""

from typing import Any

from django.http import JsonResponse
from pydantic import BaseModel


def api_response(
    data: BaseModel | dict | list | None,
    code: str = "ok",
    msg: str = "success",
    status: int = 200,
) -> JsonResponse:
    """Return a standard API response for a single object.
    
    Args:
        data: Response data (Pydantic model, dict, list, or None)
        code: Response code (default: "ok")
        msg: Human-readable message (default: "success")
        status: HTTP status code (default: 200)
    
    Returns:
        JsonResponse with standard format
    
    Examples:
        return api_response(student)
        return api_response(student_dict)
        return api_response(None, code="created", msg="Student created", status=201)
    """
    if isinstance(data, BaseModel):
        data = data.model_dump(mode="json")
    
    return JsonResponse(
        {
            "code": code,
            "msg": msg,
            "data": data,
        },
        status=status,
    )


def api_list_response(
    results: list[BaseModel | dict],
    code: str = "ok",
    msg: str = "success",
    status: int = 200,
) -> JsonResponse:
    """Return a standard API response for a list of objects.
    
    Args:
        results: List of objects (Pydantic models or dicts)
        code: Response code (default: "ok")
        msg: Human-readable message (default: "success")
        status: HTTP status code (default: 200)
    
    Returns:
        JsonResponse with standard format and results array
    
    Examples:
        return api_list_response(students)
        return api_list_response([s.model_dump() for s in students])
    """
    results_data = []
    for item in results:
        if isinstance(item, BaseModel):
            results_data.append(item.model_dump(mode="json"))
        else:
            results_data.append(item)
    
    return JsonResponse(
        {
            "code": code,
            "msg": msg,
            "data": {
                "results": results_data,
            },
        },
        status=status,
    )


def api_paginated_response(
    results: list[BaseModel | dict],
    total_items: int,
    current_page: int,
    per_page: int,
    code: str = "ok",
    msg: str = "success",
    status: int = 200,
) -> JsonResponse:
    """Return a standard API response for paginated data.
    
    Args:
        results: List of objects for current page
        total_items: Total number of items across all pages
        current_page: Current page number (1-indexed)
        per_page: Items per page
        code: Response code (default: "ok")
        msg: Human-readable message (default: "success")
        status: HTTP status code (default: 200)
    
    Returns:
        JsonResponse with standard format, results array, and pagination metadata
    
    Examples:
        return api_paginated_response(
            students,
            total_items=100,
            current_page=1,
            per_page=20
        )
    """
    results_data = []
    for item in results:
        if isinstance(item, BaseModel):
            results_data.append(item.model_dump(mode="json"))
        else:
            results_data.append(item)
    
    total_pages = (total_items + per_page - 1) // per_page  # Ceiling division
    
    return JsonResponse(
        {
            "code": code,
            "msg": msg,
            "data": {
                "results": results_data,
                "pagination": {
                    "totalItems": total_items,
                    "totalPages": total_pages,
                    "currentPage": current_page,
                    "perPage": per_page,
                },
            },
        },
        status=status,
    )


def api_error(
    code: str,
    msg: str,
    status: int = 400,
    data: Any | None = None,
) -> JsonResponse:
    """Return a standard API error response.
    
    Args:
        code: Error code identifier
        msg: Human-readable error message
        status: HTTP status code (default: 400)
        data: Additional error data (optional)
    
    Returns:
        JsonResponse with standard error format
    
    Examples:
        return api_error("not_found", "Student not found", status=404)
        return api_error("validation_error", "Invalid input", status=422)
    """
    return JsonResponse(
        {
            "code": code,
            "msg": msg,
            "data": data,
        },
        status=status,
    )
