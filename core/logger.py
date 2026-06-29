"""Logging helpers for the Vision Assistant application."""
from __future__ import annotations
import logging
import sys
from logging.handlers import RotatingFileHandler, TimedRotatingFileHandler
from pathlib import Path
from typing import Iterable

from config import AppConfig
from core.utils import ensure_directory

LOG_COLORS = {
    "DEBUG": "\x1b[36m",
    "INFO": "\x1b[32m",
    "WARNING": "\x1b[33m",
    "ERROR": "\x1b[31m",
    "CRITICAL": "\x1b[35m",
}


class ColorFormatter(logging.Formatter):
    """Formatter that adds ANSI colors to console log output."""

    def __init__(self, fmt: str, use_colors: bool = True) -> None:
        super().__init__(fmt)
        self.use_colors = use_colors and sys.stdout.isatty()

    def format(self, record: logging.LogRecord) -> str:
        message = super().format(record)
        if self.use_colors:
            color = LOG_COLORS.get(record.levelname, "")
            reset = "\x1b[0m"
            return f"{color}{message}{reset}"
        return message


class DomainFilter(logging.Filter):
    """Filter log records by logger name domain prefixes."""

    def __init__(self, domains: Iterable[str]) -> None:
        super().__init__()
        self.domains = tuple(domains)

    def filter(self, record: logging.LogRecord) -> bool:
        return any(record.name.startswith(domain) for domain in self.domains)


class PerformanceFilter(logging.Filter):
    """Filter that includes only performance-related records."""

    def filter(self, record: logging.LogRecord) -> bool:
        return record.name.startswith("vision_assistant.performance")


def configure_logging(config: AppConfig) -> None:
    """Configure root logging with console, rotating files, and performance logs."""
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)

    while root_logger.handlers:
        root_logger.handlers.pop()

    ensure_directory(config.paths.logs_dir)

    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(config.logging.console_level)
    console_handler.setFormatter(ColorFormatter(config.logging.log_format, use_colors=config.logging.enable_console_colors))
    root_logger.addHandler(console_handler)

    general_file_handler = TimedRotatingFileHandler(
        config.paths.logs_dir / config.logging.log_file_name,
        when="midnight",
        backupCount=config.logging.backup_count,
        encoding="utf-8",
    )
    general_file_handler.setLevel(config.logging.file_level)
    general_file_handler.setFormatter(logging.Formatter(config.logging.log_format))
    root_logger.addHandler(general_file_handler)

    vision_file_handler = RotatingFileHandler(
        config.paths.logs_dir / config.logging.vision_log_name,
        maxBytes=config.logging.max_bytes,
        backupCount=config.logging.backup_count,
        encoding="utf-8",
    )
    vision_file_handler.setLevel(config.logging.file_level)
    vision_file_handler.addFilter(DomainFilter(["agents.vision", "vision_assistant.vision"]))
    vision_file_handler.setFormatter(logging.Formatter(config.logging.log_format))
    root_logger.addHandler(vision_file_handler)

    reasoning_file_handler = RotatingFileHandler(
        config.paths.logs_dir / config.logging.reasoning_log_name,
        maxBytes=config.logging.max_bytes,
        backupCount=config.logging.backup_count,
        encoding="utf-8",
    )
    reasoning_file_handler.setLevel(config.logging.file_level)
    reasoning_file_handler.addFilter(DomainFilter(["agents.reasoning", "vision_assistant.reasoning"]))
    reasoning_file_handler.setFormatter(logging.Formatter(config.logging.log_format))
    root_logger.addHandler(reasoning_file_handler)

    speech_file_handler = RotatingFileHandler(
        config.paths.logs_dir / config.logging.speech_log_name,
        maxBytes=config.logging.max_bytes,
        backupCount=config.logging.backup_count,
        encoding="utf-8",
    )
    speech_file_handler.setLevel(config.logging.file_level)
    speech_file_handler.addFilter(DomainFilter(["agents.speech", "vision_assistant.speech"]))
    speech_file_handler.setFormatter(logging.Formatter(config.logging.log_format))
    root_logger.addHandler(speech_file_handler)

    error_file_handler = RotatingFileHandler(
        config.paths.logs_dir / config.logging.error_log_name,
        maxBytes=config.logging.max_bytes,
        backupCount=config.logging.backup_count,
        encoding="utf-8",
    )
    error_file_handler.setLevel(logging.ERROR)
    error_file_handler.setFormatter(logging.Formatter(config.logging.log_format))
    root_logger.addHandler(error_file_handler)

    performance_file_handler = RotatingFileHandler(
        config.paths.logs_dir / config.logging.performance_log_name,
        maxBytes=config.logging.max_bytes,
        backupCount=config.logging.backup_count,
        encoding="utf-8",
    )
    performance_file_handler.setLevel(logging.INFO)
    performance_file_handler.addFilter(PerformanceFilter())
    performance_file_handler.setFormatter(logging.Formatter(config.logging.log_format))
    root_logger.addHandler(performance_file_handler)
