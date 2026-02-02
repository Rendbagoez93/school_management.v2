"""
Pytest configuration for school management system tests.

This file configures pytest and Django integration for testing.
"""

import os
import sys
from pathlib import Path

import pytest


# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Set Django settings module
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.local")


def pytest_configure(config):
    """Configure pytest before running tests."""
    import django

    django.setup()
