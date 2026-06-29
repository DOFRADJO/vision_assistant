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
        if self.source_type in {"webcam", "camera", "device"}:
            self.capture = cv2.VideoCapture(self.device_index)
        elif self.source_type == "video":
            self.capture = cv2.VideoCapture(self.video_path)
        elif self.source_type in {"rtsp", "ip", "ipwebcam"}:
            self.capture = cv2.VideoCapture(self.ip_camera_url or self.video_path)
        else:
            self.capture = cv2.VideoCapture(self.device_index)
        return bool(self.capture and self.capture.isOpened())

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
