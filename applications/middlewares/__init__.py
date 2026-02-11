"""Middleware package for school management system.

This package contains custom middleware components that enhance
request processing and provide additional functionality.

Available middleware:
    - SchoolUserMiddleware: Attaches SchoolUser instance to request
"""

from applications.middlewares.user import SchoolUserMiddleware

__all__ = ["SchoolUserMiddleware"]
