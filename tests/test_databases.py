"""
Tests for database configuration.

This module tests the database settings, factory pattern, and
database configuration validation.
"""

import pytest
from pathlib import Path
from unittest.mock import patch
from pydantic import ValidationError


class TestDatabaseEnums:
    """Test database engine enumerations."""

    def test_db_engine_enum_values(self):
        """Test DBEngineEnum has correct values."""
        from config.settings.databases import DBEngineEnum

        assert DBEngineEnum.SQLITE == "django.db.backends.sqlite3"
        assert DBEngineEnum.POSTGRES == "django.db.backends.postgresql"

    def test_db_engine_enum_members(self):
        """Test DBEngineEnum members."""
        from config.settings.databases import DBEngineEnum

        assert "SQLITE" in DBEngineEnum.__members__
        assert "POSTGRES" in DBEngineEnum.__members__


class TestBaseDatabaseSettings:
    """Test base database settings."""

    def test_validate_engine_with_enum_name(self):
        """Test engine validation with enum name."""
        from config.settings.databases import BaseDatabaseSettings, DBEngineEnum

        with patch.dict("os.environ", {"DATABASE_ENGINE": "SQLITE"}):
            settings = BaseDatabaseSettings()
            assert settings.engine == DBEngineEnum.SQLITE

    def test_validate_engine_with_enum_value(self):
        """Test engine validation with enum value."""
        from config.settings.databases import BaseDatabaseSettings, DBEngineEnum

        with patch.dict("os.environ", {"DATABASE_ENGINE": "django.db.backends.postgresql"}):
            settings = BaseDatabaseSettings()
            assert settings.engine == DBEngineEnum.POSTGRES

    def test_validate_engine_case_insensitive(self):
        """Test engine validation is case insensitive for names."""
        from config.settings.databases import BaseDatabaseSettings, DBEngineEnum

        with patch.dict("os.environ", {"DATABASE_ENGINE": "sqlite"}):
            settings = BaseDatabaseSettings()
            assert settings.engine == DBEngineEnum.SQLITE

    def test_validate_engine_invalid_value(self):
        """Test engine validation with invalid value."""
        from config.settings.databases import BaseDatabaseSettings

        with patch.dict("os.environ", {"DATABASE_ENGINE": "invalid_engine"}):
            with pytest.raises(ValidationError) as exc_info:
                BaseDatabaseSettings()
            assert "enum" in str(exc_info.value).lower()

    def test_settings_immutable(self):
        """Test that database settings are frozen/immutable."""
        from config.settings.databases import BaseDatabaseSettings

        with patch.dict("os.environ", {"DATABASE_ENGINE": "SQLITE"}):
            settings = BaseDatabaseSettings()
            with pytest.raises((ValidationError, AttributeError)):
                settings.engine = "POSTGRES"


class TestSqliteDatabaseSettings:
    """Test SQLite database settings."""

    def test_sqlite_default_name(self):
        """Test SQLite default database name."""
        from config.settings.databases import SqliteDatabaseSettings

        with patch.dict("os.environ", {"DATABASE_ENGINE": "SQLITE"}):
            settings = SqliteDatabaseSettings()
            assert "db.sqlite3" in settings.name
            assert settings.name.endswith("db.sqlite3")

    def test_sqlite_engine_type(self):
        """Test SQLite engine type."""
        from config.settings.databases import SqliteDatabaseSettings, DBEngineEnum

        with patch.dict("os.environ", {"DATABASE_ENGINE": "SQLITE"}):
            settings = SqliteDatabaseSettings()
            assert settings.engine == DBEngineEnum.SQLITE

    def test_sqlite_custom_name(self):
        """Test SQLite with custom database name."""
        from config.settings.databases import SqliteDatabaseSettings

        with patch.dict("os.environ", {"DATABASE_ENGINE": "SQLITE", "DATABASE_NAME": "/custom/path/db.sqlite3"}):
            settings = SqliteDatabaseSettings()
            assert settings.name == "/custom/path/db.sqlite3"


class TestPostgresDatabaseSettings:
    """Test PostgreSQL database settings."""

    def test_postgres_defaults(self):
        """Test PostgreSQL default settings."""
        from config.settings.databases import PostgresDatabaseSettings, DBEngineEnum

        with patch.dict("os.environ", {"DATABASE_ENGINE": "POSTGRES"}):
            settings = PostgresDatabaseSettings()
            assert settings.engine == DBEngineEnum.POSTGRES
            assert settings.port == 5432
            assert settings.host == "localhost"
            assert settings.user == "postgres"
            assert settings.password == "postgres"
            assert settings.name == "school_management"

    def test_postgres_custom_values(self):
        """Test PostgreSQL with custom values."""
        from config.settings.databases import PostgresDatabaseSettings

        with patch.dict(
            "os.environ",
            {
                "DATABASE_ENGINE": "POSTGRES",
                "DATABASE_HOST": "db.example.com",
                "DATABASE_PORT": "5433",
                "DATABASE_USER": "admin",
                "DATABASE_PASSWORD": "secret123",
                "DATABASE_NAME": "test_db",
            },
        ):
            settings = PostgresDatabaseSettings()
            assert settings.host == "db.example.com"
            assert settings.port == 5433
            assert settings.user == "admin"
            assert settings.password == "secret123"
            assert settings.name == "test_db"

    def test_postgres_port_type_validation(self):
        """Test PostgreSQL port type validation."""
        from config.settings.databases import PostgresDatabaseSettings

        with patch.dict("os.environ", {"DATABASE_ENGINE": "POSTGRES", "DATABASE_PORT": "invalid"}):
            with pytest.raises(ValidationError):
                PostgresDatabaseSettings()


class TestDjangoDatabases:
    """Test Django databases container."""

    def test_django_databases_with_sqlite(self):
        """Test DjangoDatabases with SQLite."""
        from config.settings.databases import DjangoDatabases, SqliteDatabaseSettings

        with patch.dict("os.environ", {"DATABASE_ENGINE": "SQLITE"}):
            sqlite_settings = SqliteDatabaseSettings()
            db = DjangoDatabases(default=sqlite_settings)
            assert db.default == sqlite_settings

    def test_django_databases_with_postgres(self):
        """Test DjangoDatabases with PostgreSQL."""
        from config.settings.databases import DjangoDatabases, PostgresDatabaseSettings

        with patch.dict("os.environ", {"DATABASE_ENGINE": "POSTGRES"}):
            postgres_settings = PostgresDatabaseSettings()
            db = DjangoDatabases(default=postgres_settings)
            assert db.default == postgres_settings

    def test_django_databases_model_dump(self):
        """Test DjangoDatabases serialization."""
        from config.settings.databases import DjangoDatabases, SqliteDatabaseSettings

        with patch.dict("os.environ", {"DATABASE_ENGINE": "SQLITE"}):
            sqlite_settings = SqliteDatabaseSettings()
            db = DjangoDatabases(default=sqlite_settings)
            dumped = db.model_dump(mode="json", by_alias=True)

            assert "default" in dumped
            assert "ENGINE" in dumped["default"]
            assert "NAME" in dumped["default"]


class TestDatabaseFactory:
    """Test database factory functions."""

    def test_get_django_dbs_sqlite(self):
        """Test get_django_dbs with SQLite."""
        from config.settings.factory import get_django_dbs

        with patch.dict("os.environ", {"DATABASE_ENGINE": "SQLITE"}):
            dbs = get_django_dbs()
            assert dbs is not None
            assert dbs.default is not None

    def test_get_django_dbs_postgres(self):
        """Test get_django_dbs with PostgreSQL."""
        from config.settings.factory import get_django_dbs

        with patch.dict("os.environ", {"DATABASE_ENGINE": "POSTGRES"}):
            dbs = get_django_dbs()
            assert dbs is not None
            assert dbs.default is not None

    def test_get_django_db_dict_structure(self):
        """Test get_django_db_dict returns proper dict structure."""
        from config.settings.factory import get_django_db_dict

        with patch.dict("os.environ", {"DATABASE_ENGINE": "SQLITE"}):
            db_dict = get_django_db_dict()

            assert isinstance(db_dict, dict)
            assert "default" in db_dict
            assert isinstance(db_dict["default"], dict)
            assert "ENGINE" in db_dict["default"]
            assert "NAME" in db_dict["default"]

    def test_get_django_db_dict_sqlite(self):
        """Test get_django_db_dict for SQLite."""
        from config.settings.factory import get_django_db_dict

        with patch.dict("os.environ", {"DATABASE_ENGINE": "SQLITE"}):
            db_dict = get_django_db_dict()

            assert db_dict["default"]["ENGINE"] == "django.db.backends.sqlite3"
            assert "db.sqlite3" in db_dict["default"]["NAME"]

    def test_get_django_db_dict_postgres(self):
        """Test get_django_db_dict for PostgreSQL."""
        from config.settings.factory import get_django_db_dict

        with patch.dict(
            "os.environ",
            {
                "DATABASE_ENGINE": "POSTGRES",
                "DATABASE_HOST": "localhost",
                "DATABASE_PORT": "5432",
                "DATABASE_NAME": "school_management",
            },
        ):
            db_dict = get_django_db_dict()

            assert db_dict["default"]["ENGINE"] == "django.db.backends.postgresql"
            assert db_dict["default"]["HOST"] == "localhost"
            assert db_dict["default"]["PORT"] == 5432
            assert db_dict["default"]["NAME"] == "school_management"


class TestDatabaseIntegration:
    """Integration tests for database configuration."""

    def test_database_settings_in_django_settings(self):
        """Test that database settings are properly integrated into Django settings."""
        from config.settings.base import DATABASES

        assert DATABASES is not None
        assert "default" in DATABASES
        assert isinstance(DATABASES["default"], dict)

    def test_database_connection_settings(self):
        """Test database connection settings are valid."""
        from config.settings.base import DATABASES

        default_db = DATABASES["default"]
        assert "ENGINE" in default_db
        assert "NAME" in default_db

        # Verify engine is one of supported backends
        valid_engines = ["django.db.backends.sqlite3", "django.db.backends.postgresql"]
        assert default_db["ENGINE"] in valid_engines

    @pytest.mark.django_db
    def test_database_connection(self):
        """Test actual database connection."""
        from django.db import connection

        # This will fail if database is not properly configured
        with connection.cursor() as cursor:
            # Simple query to test connection
            cursor.execute("SELECT 1")
            result = cursor.fetchone()
            assert result == (1,)
