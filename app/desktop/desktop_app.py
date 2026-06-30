"""Desktop OpenCV application for live vision assistant output."""
from __future__ import annotations

import logging
from typing import Optional

import cv2
import numpy as np

from agents.coordinator.coordinator import Coordinator
from config import get_config
from core.camera import CameraManager
from core.logger import configure_logging
from core.utils import draw_predictions

logger = logging.getLogger(__name__)


class DesktopApp:
    def __init__(self, config=None) -> None:
        self.config = config or get_config()
        configure_logging(self.config)
        logger.info("Starting desktop pipeline")
        logger.info("Configuration | camera=%s backend=%s", self.config.camera.source_type, self.config.speech.backend)
        self.camera = CameraManager(
            source_type=self.config.camera.source_type,
            device_index=self.config.camera.device_index,
            video_path=self.config.camera.video_path,
            ip_camera_url=self.config.camera.ip_camera_url,
        )
        self.coordinator = Coordinator(config=self.config)
        self.coordinator.initialize()
        logger.info("Loaded models: %s", sorted(self.coordinator.model_loader.detectors.keys()))

    def run(self) -> None:
        if not self.camera.open():
            raise RuntimeError("Unable to open camera")
        logger.info("Camera opened successfully")
        while True:
            ok, frame = self.camera.read()
            if not ok or frame is None:
                break
            result = self.coordinator.process_frame(frame)
            annotated = draw_predictions(frame, result.get("detections", []))
            cv2.putText(annotated, f"FPS: {result.get('fps', 0.0):.2f}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
            cv2.imshow("Vision Assistant", annotated)
            if cv2.waitKey(1) & 0xFF == ord("q"):
                break
        self.camera.release()
        cv2.destroyAllWindows()
        logger.info("Desktop pipeline stopped")
