"""Professional logging setup for Vision Assistant."""
from __future__ import annotations

import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import Optional

from config import VisionAssistantConfig


def configure_logging(config: Optional[VisionAssistantConfig] = None) -> logging.Logger:
    config = config or VisionAssistantConfig()
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, config.logging.level.upper(), logging.INFO))
    root_logger.handlers.clear()

    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)
    root_logger.addHandler(stream_handler)

    log_dir = Path(config.paths.logs_dir)
    log_dir.mkdir(parents=True, exist_ok=True)
    file_handler = RotatingFileHandler(
        log_dir / "vision_assistant.log",
        maxBytes=config.logging.max_bytes,
        backupCount=config.logging.backup_count,
    )
    file_handler.setFormatter(formatter)
    root_logger.addHandler(file_handler)
    return root_logger
