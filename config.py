"""Central configuration for Vision Assistant."""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional


@dataclass(slots=True)
class CameraConfig:
    source_type: str = "webcam"
    device_index: int = 0
    video_path: str = ""
    ip_camera_url: str = ""
    resize_width: int = 640
    resize_height: int = 480
    fps: int = 20


@dataclass(slots=True)
class SpeechConfig:
    backend: str = "auto"
    rate: int = 150
    volume: float = 1.0
    language: str = "en"
    queue_size: int = 8
    priority_interrupt: bool = True


@dataclass(slots=True)
class MemoryConfig:
    timeout_seconds: float = 3.0
    priority_bypass_threshold: int = 3
    max_history: int = 100


@dataclass(slots=True)
class TrackingConfig:
    enabled: bool = True
    tracker_type: str = "iou"
    max_age: int = 10
    min_hits: int = 2
    iou_threshold: float = 0.35


@dataclass(slots=True)
class ModelConfig:
    use_onnx: bool = True
    use_torch: bool = False
    confidence_threshold: float = 0.25
    max_workers: int = 4
    supported_formats: List[str] = field(default_factory=lambda: [".onnx", ".pt"])


@dataclass(slots=True)
class ApiConfig:
    host: str = "0.0.0.0"
    port: int = 8000
    reload: bool = False


@dataclass(slots=True)
class PathsConfig:
    root: Path = field(default_factory=lambda: Path(__file__).resolve().parent)
    models_dir: Path = field(default_factory=lambda: Path(__file__).resolve().parent / "models")
    datasets_dir: Path = field(default_factory=lambda: Path(__file__).resolve().parent / "datasets")
    exports_dir: Path = field(default_factory=lambda: Path(__file__).resolve().parent / "exports")
    logs_dir: Path = field(default_factory=lambda: Path(__file__).resolve().parent / "exports" / "logs")
    reports_dir: Path = field(default_factory=lambda: Path(__file__).resolve().parent / "exports" / "reports")
    training_dir: Path = field(default_factory=lambda: Path(__file__).resolve().parent / "training")


@dataclass(slots=True)
class LoggingConfig:
    level: str = "INFO"
    max_bytes: int = 5_000_000
    backup_count: int = 5


@dataclass(slots=True)
class VisionAssistantConfig:
    camera: CameraConfig = field(default_factory=CameraConfig)
    speech: SpeechConfig = field(default_factory=SpeechConfig)
    memory: MemoryConfig = field(default_factory=MemoryConfig)
    tracking: TrackingConfig = field(default_factory=TrackingConfig)
    model: ModelConfig = field(default_factory=ModelConfig)
    api: ApiConfig = field(default_factory=ApiConfig)
    paths: PathsConfig = field(default_factory=PathsConfig)
    logging: LoggingConfig = field(default_factory=LoggingConfig)
    debug: bool = False


_CONFIG: Optional[VisionAssistantConfig] = None


def get_config() -> VisionAssistantConfig:
    global _CONFIG
    if _CONFIG is None:
        _CONFIG = VisionAssistantConfig()
    return _CONFIG
