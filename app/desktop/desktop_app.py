"""Simple desktop application to display live detections and reasoning output."""
from __future__ import annotations
import logging
from typing import Any

try:
    import cv2
except ImportError:  # pragma: no cover
    cv2 = None  # type: ignore[assignment]
from config import AppConfig, get_config
from core.utils import draw_bounding_boxes
from agents.coordinator.coordinator import Coordinator

logger = logging.getLogger(__name__)


class DesktopApp:
    """A desktop demo application for Vision Assistant."""

    def __init__(self, config: AppConfig | None = None) -> None:
        self.config = config or get_config()
        self.coordinator = Coordinator(self.config)
        self.window_name = "Vision Assistant"

    def run(self) -> None:
        if cv2 is None:
            raise RuntimeError("OpenCV is required for desktop mode")
        self.coordinator.initialize()
        if not self.coordinator.camera.open():
            raise RuntimeError("Unable to open camera for desktop mode")
        try:
            while True:
                for frame_id, frame in self.coordinator.camera.frames():
                    output = self.coordinator.execute(frame, frame_id=frame_id)
                    annotations = []
                    for category, predictions in output["vision"].items():
                        if category in {"timestamp", "frame_id"}:
                            continue
                        annotations.extend(predictions)
                    overlay = draw_bounding_boxes(frame, annotations)
                    self._render_overlay(overlay, output)
                    if cv2.waitKey(1) in {27, ord("q")}:
                        return
        finally:
            self.coordinator.camera.close()
            cv2.destroyAllWindows()

    def _render_overlay(self, frame: Any, output: dict) -> None:
        status = f"Priority: {output['reasoning'].get('priority', 1)} | {output['reasoning'].get('danger_level', 'low')}"
        lines = [
            f"Status: {output.get('status', 'ok')}",
            f"Models: {len(self.coordinator.model_loader.detectors)} loaded",
            f"FPS: {output['metrics'].get('fps', 0):.1f}",
            f"Latency: {output['metrics'].get('processing_time', 0):.3f}s",
            f"Priority: {output['reasoning'].get('priority', 1)}",
            f"Danger: {output['reasoning'].get('danger_level', 'low')}",
            f"Message: {output['reasoning'].get('message', '')}",
        ]
        y = 24
        for line in lines:
            cv2.putText(frame, line, (8, y), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (230, 230, 230), 1)
            y += 22
        detected = [f"{len(items)} {category}" for category, items in output['vision'].items() if category not in {"timestamp", "frame_id"} and items]
        if detected:
            cv2.putText(frame, f"Detected: {', '.join(detected)}", (8, y), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (180, 180, 255), 1)
        cv2.imshow(self.window_name, frame)
