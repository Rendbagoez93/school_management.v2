from typing import Literal

from pydantic import BaseModel
from pydantic_settings import SettingsConfigDict
from pydantic_settings_yaml import YamlBaseSettings


class SchoolAttribute(BaseModel):
    key: str
    value: str | int | float | bool | list | dict
    type: Literal["string", "number", "boolean", "array", "object"] = "string"


class SchoolConfig(YamlBaseSettings):
    """Common school config with dynamic attributes."""

    name: str
    address: str | None = None
    phone: str | None = None
    email: str | None = None
    description: str | None = None
    attributes: list[SchoolAttribute] | None = None

    model_config = SettingsConfigDict(
        extra="ignore",
        secrets_dir=".",
        yaml_file="school_config.yaml",
        yaml_file_encoding="utf-8",
    )
