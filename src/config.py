from functools import lru_cache
from pathlib import Path
from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict

root_dir = Path(__file__).parent.parent


class Settings(BaseSettings):
    """Application settings."""

    service_name: str = "Invoice Generator Service"
    env: Literal["development", "production"] = "development"
    output_dir: str = str(root_dir / "outputs")
    template_dir: str = str(root_dir / "templates")
    data_file: str = str(root_dir / "data/billing.toml")

    model_config = SettingsConfigDict(
        env_file=".env",
        env_prefix="APP_",
    )


@lru_cache()
def get_settings() -> Settings:
    """Get the application settings."""
    return Settings()
