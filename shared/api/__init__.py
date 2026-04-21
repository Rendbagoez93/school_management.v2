"""Shared API utilities for School Management System."""

from .exceptions import ApiError
from .parsers import parse_body, parse_query
from .response import api_error, api_list_response, api_paginated_response, api_response

__all__ = [
    "ApiError",
    "parse_body",
    "parse_query",
    "api_error",
    "api_response",
    "api_list_response",
    "api_paginated_response",
]
