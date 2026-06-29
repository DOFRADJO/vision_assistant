"""Unit tests for Vision Assistant configuration."""
from config import get_config


def test_get_config_paths() -> None:
    config = get_config()
    assert config.paths.models_dir.name == "models"
    assert config.paths.logs_dir.name == "logs"
