"""Camera manager for live video, files, and IP streams."""
from __future__ import annotations

from typing import Optional, Tuple

import cv2
import numpy as np


class CameraManager:
    def __init__(self, source_type: str = "webcam", device_index: int = 0, video_path: str = "", ip_camera_url: str = "") -> None:
        self.source_type = source_type
        self.device_index = device_index
        self.video_path = video_path
        self.ip_camera_url = ip_camera_url
        self.capture: Optional[cv2.VideoCapture] = None

    def open(self) -> bool:
        if self.capture is not None and self.capture.isOpened():
            return True
        self.capture = cv2.VideoCapture(self.resolve_source())
        return bool(self.capture and self.capture.isOpened())

    def resolve_source(self):
        if self.source_type in {"webcam", "camera", "device", "laptop"}:
            return self.device_index
        if self.source_type in {"video", "video_file"}:
            return self.video_path
        elif self.source_type in {"rtsp", "ip", "ipwebcam"}:
            return self.ip_camera_url or self.video_path
        return self.device_index

    def read(self) -> Tuple[bool, Optional[np.ndarray]]:
        if self.capture is None:
            self.open()
        if self.capture is None:
            return False, None
        ok, frame = self.capture.read()
        if not ok or frame is None:
            return False, None
        return True, frame

    def release(self) -> None:
        if self.capture is not None:
            self.capture.release()
            self.capture = None


class CameraSource(CameraManager):
    """Backward-compatible camera wrapper used by older clients and tests."""

    def __init__(self, config) -> None:
        camera = config.camera
        super().__init__(
            source_type=camera.source_type,
            device_index=camera.device_index,
            video_path=camera.video_path,
            ip_camera_url=camera.ip_camera_url,
        )

    def _resolve_source(self):
        return self.resolve_source()
