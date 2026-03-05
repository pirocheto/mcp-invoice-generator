"""Load billing data from the configured TOML file."""

from pathlib import Path

from dynaconf import Dynaconf

from src.config import get_settings

settings = get_settings()


def load_default_data() -> dict:
    """Load billing data from the configured TOML file."""

    data_path = Path(settings.data_file)
    raw_data = Dynaconf(
        root_path=str(data_path.parent),
        settings_files=[str(data_path)],
    )
    return raw_data.as_dict()


_data = load_default_data()


def get_default_data() -> dict:
    """Utility function for dependency injection."""

    return _data
