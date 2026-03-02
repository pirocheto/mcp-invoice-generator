from functools import lru_cache
from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings."""

    service_name: str = "Invoice Generator Service"
    env: Literal["development", "production"] = "development"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_prefix="APP_",
    )


@lru_cache()
def get_settings() -> Settings:
    """Get the application settings."""
    return Settings()
