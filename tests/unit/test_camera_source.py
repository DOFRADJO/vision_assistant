"""Unit tests for camera source resolution and configuration."""
from pathlib import Path

from config import AppConfig
from core.camera import CameraSource


def test_camera_source_resolves_laptop() -> None:
    config = AppConfig(camera=type(AppConfig().camera)(source_type="laptop", device_index=1))
    camera = CameraSource(config)
    assert camera._resolve_source() == 1


def test_camera_source_resolves_video_file(tmp_path: Path) -> None:
    video_path = str(tmp_path / "sample.mp4")
    config = AppConfig(camera=type(AppConfig().camera)(source_type="video_file", video_path=video_path))
    camera = CameraSource(config)
    assert camera._resolve_source() == video_path
