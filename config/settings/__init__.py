"""
Settings package initialization.

This imports local settings by default for development.
For production, use DJANGO_SETTINGS_MODULE=config.settings.production
"""

from .local import *  # noqa: F403, F401
