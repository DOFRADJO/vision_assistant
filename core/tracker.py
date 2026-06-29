"""Tracking utilities with IoU fallback and optional ByteTrack support."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple

import numpy as np


@dataclass
class Track:
    track_id: int
    label: str
    confidence: float
    bbox: Tuple[float, float, float, float]
    metadata: Dict[str, Any] = field(default_factory=dict)


class Tracker:
    def __init__(self, tracker_type: str = "iou", iou_threshold: float = 0.35, max_age: int = 10) -> None:
        self.tracker_type = tracker_type
        self.iou_threshold = iou_threshold
        self.max_age = max_age
        self.tracks: List[Track] = []
        self._next_id = 1
        self._active_ids: Dict[int, int] = {}

    def _compute_iou(self, box_a: Tuple[float, float, float, float], box_b: Tuple[float, float, float, float]) -> float:
        x1 = max(box_a[0], box_b[0])
        y1 = max(box_a[1], box_b[1])
        x2 = min(box_a[2], box_b[2])
        y2 = min(box_a[3], box_b[3])
        inter = max(0.0, x2 - x1) * max(0.0, y2 - y1)
        area_a = max(0.0, box_a[2] - box_a[0]) * max(0.0, box_a[3] - box_a[1])
        area_b = max(0.0, box_b[2] - box_b[0]) * max(0.0, box_b[3] - box_b[1])
        union = area_a + area_b - inter
        if union <= 0:
            return 0.0
        return inter / union

    def update(self, detections: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        if self.tracker_type == "bytetrack":
            try:
                import ultralytics.trackers.byte_tracker  # noqa: F401
            except Exception:
                self.tracker_type = "iou"
        tracked: List[Dict[str, Any]] = []
        if self.tracker_type != "iou":
            for detection in detections:
                detection = dict(detection)
                detection["tracking_id"] = self._next_id
                self._next_id += 1
                tracked.append(detection)
            return tracked

        if not detections:
            self.tracks = [track for track in self.tracks if getattr(track, "metadata", {}).get("age", 0) < self.max_age]
            return []

        matched: List[int] = []
        for detection in detections:
            bbox = tuple(float(v) for v in detection.get("bbox", [0, 0, 0, 0]))
            best_track: Optional[Track] = None
            best_score = 0.0
            for track in self.tracks:
                if track.track_id in matched:
                    continue
                score = self._compute_iou(bbox, track.bbox)
                if score > best_score and score >= self.iou_threshold:
                    best_score = score
                    best_track = track
            if best_track is None:
                track_id = self._next_id
                self._next_id += 1
                best_track = Track(track_id=track_id, label=detection.get("label", "object"), confidence=detection.get("confidence", 0.0), bbox=bbox)
                self.tracks.append(best_track)
            else:
                matched.append(best_track.track_id)
            result = dict(detection)
            result["tracking_id"] = best_track.track_id
            tracked.append(result)
        self.tracks = [track for track in self.tracks if getattr(track, "metadata", {}).get("age", 0) < self.max_age]
        return tracked
