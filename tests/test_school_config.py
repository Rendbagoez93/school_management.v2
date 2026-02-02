"""
Tests for school configuration.

This module tests the school configuration loading from YAML file
and schema validation.
"""

import pytest
from pathlib import Path


class TestSchoolConfigModel:
    """Test SchoolConfig model."""

    def test_school_config_imports(self):
        """Test that SchoolConfig can be imported."""
        from config.settings.schoolconf import SchoolConfig

        assert SchoolConfig is not None

    def test_school_config_loads_from_yaml(self):
        """Test that school config loads from YAML file."""
        from config.settings.schoolconf import SchoolConfig

        config = SchoolConfig()
        assert config is not None
        assert config.name is not None

    def test_school_config_required_fields(self):
        """Test that required fields are present."""
        from config.settings.schoolconf import SchoolConfig

        config = SchoolConfig()
        assert config.name
        assert isinstance(config.name, str)

    def test_school_config_optional_fields(self):
        """Test that optional fields can be None."""
        from config.settings.schoolconf import SchoolConfig

        config = SchoolConfig()
        # These fields should exist but can be None
        assert hasattr(config, "address")
        assert hasattr(config, "phone")
        assert hasattr(config, "email")
        assert hasattr(config, "description")
        assert hasattr(config, "attributes")

    def test_school_config_values_from_yaml(self):
        """Test that values match YAML file."""
        from config.settings.schoolconf import SchoolConfig

        config = SchoolConfig()
        assert config.name == "SMA Islam Malang"
        assert config.address == "Jln R.A kartini, Malang, Indonesia"
        assert config.phone == "+62 341 123456"
        assert config.email == "info@smaislammalang.sch.id"


class TestSchoolAttribute:
    """Test SchoolAttribute model."""

    def test_school_attribute_imports(self):
        """Test that SchoolAttribute can be imported."""
        from config.settings.schoolconf import SchoolAttribute

        assert SchoolAttribute is not None

    def test_school_attribute_creation(self):
        """Test SchoolAttribute creation."""
        from config.settings.schoolconf import SchoolAttribute

        attr = SchoolAttribute(key="test", value="value")
        assert attr.key == "test"
        assert attr.value == "value"
        assert attr.type == "string"

    def test_school_attribute_types(self):
        """Test SchoolAttribute with different types."""
        from config.settings.schoolconf import SchoolAttribute

        # String type
        str_attr = SchoolAttribute(key="name", value="Test", type="string")
        assert str_attr.type == "string"
        assert isinstance(str_attr.value, str)

        # Number type
        num_attr = SchoolAttribute(key="year", value=2024, type="number")
        assert num_attr.type == "number"
        assert isinstance(num_attr.value, int)

        # Boolean type
        bool_attr = SchoolAttribute(key="active", value=True, type="boolean")
        assert bool_attr.type == "boolean"
        assert isinstance(bool_attr.value, bool)

        # Array type
        arr_attr = SchoolAttribute(key="colors", value=["red", "blue"], type="array")
        assert arr_attr.type == "array"
        assert isinstance(arr_attr.value, list)

        # Object type
        obj_attr = SchoolAttribute(key="metadata", value={"key": "value"}, type="object")
        assert obj_attr.type == "object"
        assert isinstance(obj_attr.value, dict)


class TestSchoolConfigAttributes:
    """Test school config attributes from YAML."""

    def test_attributes_loaded(self):
        """Test that attributes are loaded from YAML."""
        from config.settings.schoolconf import SchoolConfig

        config = SchoolConfig()
        assert config.attributes is not None
        assert isinstance(config.attributes, list)
        assert len(config.attributes) > 0

    def test_attributes_structure(self):
        """Test attributes have correct structure."""
        from config.settings.schoolconf import SchoolConfig

        config = SchoolConfig()
        for attr in config.attributes:
            assert hasattr(attr, "key")
            assert hasattr(attr, "value")
            assert attr.key is not None

    def test_specific_attributes(self):
        """Test specific attributes from YAML."""
        from config.settings.schoolconf import SchoolConfig

        config = SchoolConfig()
        attr_dict = {attr.key: attr.value for attr in config.attributes}

        assert "Established Year" in attr_dict
        assert attr_dict["Established Year"] == 1995

        assert "Principal" in attr_dict
        assert attr_dict["Principal"] == "Dr. Jane Smith"

        assert "Motto" in attr_dict
        assert attr_dict["Motto"] == "Empowering Future Leaders"

        assert "Number of Students" in attr_dict
        assert attr_dict["Number of Students"] == 1200

        assert "Number of Teachers" in attr_dict
        assert attr_dict["Number of Teachers"] == 75

    def test_array_attributes(self):
        """Test array type attributes."""
        from config.settings.schoolconf import SchoolConfig

        config = SchoolConfig()
        attr_dict = {attr.key: attr for attr in config.attributes}

        assert "School Colors" in attr_dict
        colors = attr_dict["School Colors"]
        assert isinstance(colors.value, list)
        assert "Green" in colors.value
        assert "White" in colors.value


class TestSchoolConfigYAMLFile:
    """Test YAML file configuration."""

    def test_yaml_file_exists(self):
        """Test that school_config.yaml exists."""
        from config.settings.schoolconf import SchoolConfig

        yaml_path = Path(__file__).parent.parent / "school_config.yaml"
        assert yaml_path.exists()

    def test_yaml_file_readable(self):
        """Test that YAML file is readable."""
        yaml_path = Path(__file__).parent.parent / "school_config.yaml"
        with open(yaml_path, "r", encoding="utf-8") as f:
            content = f.read()
            assert len(content) > 0
            assert "name:" in content

    def test_yaml_schema_file_exists(self):
        """Test that schema file exists."""
        schema_path = Path(__file__).parent.parent / "school_config.schema.json"
        assert schema_path.exists()

    def test_yaml_schema_readable(self):
        """Test that schema file is readable."""
        import json

        schema_path = Path(__file__).parent.parent / "school_config.schema.json"
        with open(schema_path, "r", encoding="utf-8") as f:
            schema = json.load(f)
            assert "properties" in schema
            assert "name" in schema["properties"]


class TestSchoolConfigIntegration:
    """Integration tests for school configuration."""

    def test_school_config_in_django_settings(self):
        """Test that school config is loaded in Django settings."""
        from config.settings.base import (
            SCHOOL_NAME,
            SCHOOL_ADDRESS,
            SCHOOL_PHONE,
            SCHOOL_EMAIL,
            SCHOOL_DESCRIPTION,
        )

        assert SCHOOL_NAME == "SMA Islam Malang"
        assert SCHOOL_ADDRESS is not None
        assert SCHOOL_PHONE is not None
        assert SCHOOL_EMAIL is not None
        assert SCHOOL_DESCRIPTION is not None

    def test_school_attributes_in_django_settings(self):
        """Test that school attributes are available in Django settings."""
        from config.settings.base import SCHOOL_ATTRIBUTES

        assert SCHOOL_ATTRIBUTES is not None
        assert isinstance(SCHOOL_ATTRIBUTES, list)
        assert len(SCHOOL_ATTRIBUTES) > 0

    def test_school_config_accessible(self):
        """Test that school config is accessible from settings."""
        from django.conf import settings

        assert hasattr(settings, "SCHOOL_NAME")
        assert hasattr(settings, "SCHOOL_ADDRESS")
        assert hasattr(settings, "SCHOOL_PHONE")
        assert hasattr(settings, "SCHOOL_EMAIL")
