from typing import Literal

from pydantic import BaseModel
from pydantic_settings import BaseSettings, PydanticBaseSettingsSource, SettingsConfigDict, YamlConfigSettingsSource


class SchoolAttribute(BaseModel):
    key: str
    value: str | int | float | bool | list | dict
    type: Literal["string", "number", "boolean", "array", "object"] = "string"


class SchoolConfig(BaseSettings):
    """Common school config with dynamic attributes."""

    name: str
    address: str | None = None
    phone: str | None = None
    email: str | None = None
    description: str | None = None
    attributes: list[SchoolAttribute] | None = None

    @classmethod
    def settings_customise_sources(
        cls,
        settings_cls: type[BaseSettings],
        init_settings: PydanticBaseSettingsSource,
        env_settings: PydanticBaseSettingsSource,
        dotenv_settings: PydanticBaseSettingsSource,
        file_secret_settings: PydanticBaseSettingsSource,
    ) -> tuple[PydanticBaseSettingsSource, ...]:
        return (
            init_settings,
            YamlConfigSettingsSource(settings_cls),
            env_settings,
            dotenv_settings,
            file_secret_settings,
        )

    model_config = SettingsConfigDict(
        extra="ignore",
        secrets_dir=".",
        yaml_file="school_config.yaml",
        yaml_file_encoding="utf-8",
    )
