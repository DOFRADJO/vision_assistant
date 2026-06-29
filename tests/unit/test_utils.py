"""Unit tests for core utility functions."""
from pathlib import Path

from core.utils import ensure_directory, normalize_bbox


def test_ensure_directory(tmp_path: Path) -> None:
    folder = tmp_path / "nested" / "path"
    result = ensure_directory(folder)
    assert result.exists()
    assert result.is_dir()


def test_normalize_bbox(tmp_path: Path) -> None:
    shape = (480, 640, 3)
    bbox = {"x1": -10, "y1": 0, "x2": 700, "y2": 500}
    normalized = normalize_bbox(bbox, shape)
    assert normalized["x1"] == 0
    assert normalized["y1"] == 0
    assert normalized["x2"] == 639
    assert normalized["y2"] == 479
