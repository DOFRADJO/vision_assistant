"""Shared utilities for Vision Assistant."""
from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional

import cv2
import numpy as np

logger = logging.getLogger(__name__)


def ensure_directory(path: Path) -> Path:
    path.mkdir(parents=True, exist_ok=True)
    return path


def safe_read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8").strip()
    except Exception:
        return ""


def serialize_json(payload: Any) -> str:
    return json.dumps(payload, indent=2, ensure_ascii=False)


def normalize_bbox(raw_bbox: Dict[str, Any], frame_shape: Iterable[int]) -> Dict[str, int]:
    height, width = int(frame_shape[0]), int(frame_shape[1])
    x1 = int(raw_bbox.get("x1", 0))
    y1 = int(raw_bbox.get("y1", 0))
    x2 = int(raw_bbox.get("x2", width))
    y2 = int(raw_bbox.get("y2", height))
    x1 = max(0, min(x1, width - 1))
    y1 = max(0, min(y1, height - 1))
    x2 = max(0, min(x2, width - 1))
    y2 = max(0, min(y2, height - 1))
    return {"x1": x1, "y1": y1, "x2": x2, "y2": y2}


def draw_predictions(image: np.ndarray, detections: List[Dict[str, Any]]) -> np.ndarray:
    output = image.copy()
    for detection in detections:
        bbox = detection.get("bbox")
        if not bbox:
            continue
        if isinstance(bbox, dict):
            x1, y1, x2, y2 = bbox.get("x1", 0), bbox.get("y1", 0), bbox.get("x2", 0), bbox.get("y2", 0)
        else:
            x1, y1, x2, y2 = int(bbox[0]), int(bbox[1]), int(bbox[2]), int(bbox[3])
        label = detection.get("label", "unknown")
        confidence = detection.get("confidence", 0.0)
        tracking_id = detection.get("tracking_id")
        text = f"{label} {confidence:.2f}"
        if tracking_id is not None:
            text += f" ID:{tracking_id}"
        cv2.rectangle(output, (x1, y1), (x2, y2), (0, 255, 0), 2)
        cv2.putText(output, text, (x1, max(12, y1 - 8)), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)
    return output
