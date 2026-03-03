"""Load billing data from the configured TOML file."""

from pathlib import Path

from dynaconf import Dynaconf

from src.config import get_settings
from src.schemas import DataModel

settings = get_settings()


def load_data() -> dict:
    """Load billing data from the configured TOML file."""

    data_path = Path(settings.data_file)
    if not data_path.is_absolute():
        data_path = Path(__file__).resolve().parent.parent / data_path

    raw_data = Dynaconf(
        root_path=str(data_path.parent),
        settings_files=[str(data_path)],
    )

    data = DataModel.model_validate(raw_data.as_dict())
    data_dict: dict = data.model_dump()
    data_dict["templates"] = [f.stem for f in Path("templates").glob("*.html")]
    return data_dict


_data = load_data()


def get_data() -> dict:
    """Utility function for dependency injection."""

    return _data
