"""
Environment-specific common settings loaded from environment variables.

This module uses pydantic-settings to load configuration from .env files
and environment variables, providing type validation and defaults.
"""

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class CommonEnvSettings(BaseSettings):
    """Common environment settings for all deployment environments."""

    # Security
    SECRET_KEY: str = Field(
        default="django-insecure-change-this-in-production",
        description="Django secret key for cryptographic signing",
    )

    # Debug and Environment
    DEBUG: bool = Field(default=False, description="Enable debug mode")
    ENVIRONMENT: str = Field(default="local", description="Current environment (local, dev, staging, prod)")

    # Allowed Hosts
    ALLOWED_HOSTS: list[str] = Field(
        default=["localhost", "127.0.0.1"],
        description="List of allowed host/domain names",
    )

    # Internationalization
    LANGUAGE_CODE: str = Field(default="en-us", description="Language code for the application")
    TIME_ZONE: str = Field(default="UTC", description="Time zone for the application")

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )
