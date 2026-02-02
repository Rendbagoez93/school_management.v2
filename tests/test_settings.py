"""
Tests for Django settings configuration.

This module tests the settings configuration including base settings,
environment settings, and school configuration.
"""

import pytest
from pathlib import Path


class TestBaseSettings:
    """Test base settings configuration."""

    def test_base_dir_exists(self):
        """Test that BASE_DIR is correctly configured."""
        from config.settings.base import BASE_DIR

        assert BASE_DIR.exists()
        assert BASE_DIR.is_dir()
        assert (BASE_DIR / "manage.py").exists()

    def test_secret_key_configured(self):
        """Test that SECRET_KEY is set."""
        from config.settings.base import SECRET_KEY

        assert SECRET_KEY
        assert isinstance(SECRET_KEY, str)
        assert len(SECRET_KEY) > 0

    def test_debug_mode(self):
        """Test DEBUG setting."""
        from config.settings.base import DEBUG

        assert isinstance(DEBUG, bool)

    def test_allowed_hosts_configured(self):
        """Test ALLOWED_HOSTS configuration."""
        from config.settings.base import ALLOWED_HOSTS

        assert isinstance(ALLOWED_HOSTS, list)

    def test_installed_apps_configured(self):
        """Test INSTALLED_APPS configuration."""
        from config.settings.base import INSTALLED_APPS

        required_apps = [
            "django.contrib.admin",
            "django.contrib.auth",
            "django.contrib.contenttypes",
            "django.contrib.sessions",
            "django.contrib.messages",
            "django.contrib.staticfiles",
        ]

        for app in required_apps:
            assert app in INSTALLED_APPS

    def test_middleware_configured(self):
        """Test MIDDLEWARE configuration."""
        from config.settings.base import MIDDLEWARE

        required_middleware = [
            "django.middleware.security.SecurityMiddleware",
            "django.contrib.sessions.middleware.SessionMiddleware",
            "django.middleware.common.CommonMiddleware",
            "django.middleware.csrf.CsrfViewMiddleware",
            "django.contrib.auth.middleware.AuthenticationMiddleware",
            "django.contrib.messages.middleware.MessageMiddleware",
            "django.middleware.clickjacking.XFrameOptionsMiddleware",
        ]

        for mw in required_middleware:
            assert mw in MIDDLEWARE

    def test_templates_configured(self):
        """Test TEMPLATES configuration."""
        from config.settings.base import TEMPLATES

        assert len(TEMPLATES) > 0
        assert TEMPLATES[0]["BACKEND"] == "django.template.backends.django.DjangoTemplates"
        assert TEMPLATES[0]["APP_DIRS"] is True

    def test_database_configured(self):
        """Test DATABASES configuration."""
        from config.settings.base import DATABASES

        assert "default" in DATABASES
        assert "ENGINE" in DATABASES["default"]
        assert "NAME" in DATABASES["default"]

    def test_static_files_configured(self):
        """Test static files configuration."""
        from config.settings.base import STATIC_URL, STATIC_ROOT, STATICFILES_DIRS

        assert STATIC_URL == "static/"
        assert isinstance(STATIC_ROOT, Path)
        assert isinstance(STATICFILES_DIRS, list)

    def test_media_files_configured(self):
        """Test media files configuration."""
        from config.settings.base import MEDIA_URL, MEDIA_ROOT

        assert MEDIA_URL == "media/"
        assert isinstance(MEDIA_ROOT, Path)

    def test_internationalization_configured(self):
        """Test internationalization settings."""
        from config.settings.base import LANGUAGE_CODE, TIME_ZONE, USE_I18N, USE_TZ

        assert isinstance(LANGUAGE_CODE, str)
        assert isinstance(TIME_ZONE, str)
        assert USE_I18N is True
        assert USE_TZ is True


class TestSchoolConfiguration:
    """Test school configuration settings."""

    def test_school_name_configured(self):
        """Test that school name is loaded."""
        from config.settings.base import SCHOOL_NAME

        assert SCHOOL_NAME
        assert isinstance(SCHOOL_NAME, str)
        assert SCHOOL_NAME == "SMA Islam Malang"

    def test_school_address_configured(self):
        """Test that school address is loaded."""
        from config.settings.base import SCHOOL_ADDRESS

        assert SCHOOL_ADDRESS
        assert isinstance(SCHOOL_ADDRESS, str)

    def test_school_contact_configured(self):
        """Test that school contact information is loaded."""
        from config.settings.base import SCHOOL_PHONE, SCHOOL_EMAIL

        assert SCHOOL_PHONE
        assert SCHOOL_EMAIL
        assert isinstance(SCHOOL_PHONE, str)
        assert isinstance(SCHOOL_EMAIL, str)

    def test_school_description_configured(self):
        """Test that school description is loaded."""
        from config.settings.base import SCHOOL_DESCRIPTION

        assert SCHOOL_DESCRIPTION
        assert isinstance(SCHOOL_DESCRIPTION, str)

    def test_school_attributes_configured(self):
        """Test that school attributes are loaded."""
        from config.settings.base import SCHOOL_ATTRIBUTES

        assert SCHOOL_ATTRIBUTES is not None
        if SCHOOL_ATTRIBUTES:
            assert isinstance(SCHOOL_ATTRIBUTES, list)
            assert len(SCHOOL_ATTRIBUTES) > 0
            # Check first attribute structure
            first_attr = SCHOOL_ATTRIBUTES[0]
            assert hasattr(first_attr, "key")
            assert hasattr(first_attr, "value")


class TestEnvironmentSettings:
    """Test environment settings configuration."""

    def test_env_settings_imports(self):
        """Test that environment settings can be imported."""
        from config.settings.envcommon import CommonEnvSettings

        env = CommonEnvSettings()
        assert env is not None

    def test_env_defaults(self):
        """Test environment settings defaults."""
        from config.settings.envcommon import CommonEnvSettings

        env = CommonEnvSettings()
        assert isinstance(env.DEBUG, bool)
        assert isinstance(env.LANGUAGE_CODE, str)
        assert isinstance(env.TIME_ZONE, str)
        assert isinstance(env.ALLOWED_HOSTS, list)

    def test_secret_key_has_default(self):
        """Test that SECRET_KEY has a default value."""
        from config.settings.envcommon import CommonEnvSettings

        env = CommonEnvSettings()
        assert env.SECRET_KEY
        assert len(env.SECRET_KEY) > 0
