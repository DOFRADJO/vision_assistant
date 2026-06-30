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
    age: int = 0
    hits: int = 1


class Tracker:
    def __init__(
        self,
        tracker_type: str = "iou",
        iou_threshold: float = 0.35,
        max_age: int = 10,
        min_hits: int = 2,
    ) -> None:
        self.tracker_type = tracker_type
        self.iou_threshold = iou_threshold
        self.max_age = max_age
        self.min_hits = min_hits
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
            for track in self.tracks:
                track.age += 1
            self.tracks = [track for track in self.tracks if track.age <= self.max_age]
            return []

        matched: set[int] = set()
        for detection in detections:
            bbox = tuple(float(v) for v in detection.get("bbox", [0, 0, 0, 0]))
            label = str(detection.get("label", "object")).strip().lower()
            best_track: Optional[Track] = None
            best_score = 0.0
            for track in self.tracks:
                if track.track_id in matched:
                    continue
                if track.label.strip().lower() != label:
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
                previous_bbox = best_track.bbox
                motion = self._motion_metadata(previous_bbox, bbox)
                previous_streak = int(best_track.metadata.get("approach_streak", 0))
                approach_streak = previous_streak + 1 if motion.pop("approach_candidate") else 0
                motion["approach_streak"] = approach_streak
                motion["approaching"] = approach_streak >= 2 and best_track.hits + 1 >= self.min_hits
                best_track.metadata = motion
                best_track.bbox = bbox
                best_track.confidence = float(detection.get("confidence", 0.0))
                best_track.age = 0
                best_track.hits += 1
            matched.add(best_track.track_id)
            result = dict(detection)
            result["tracking_id"] = best_track.track_id
            result["track_hits"] = best_track.hits
            result.update(best_track.metadata)
            tracked.append(result)

        for track in self.tracks:
            if track.track_id not in matched:
                track.age += 1
        self.tracks = [track for track in self.tracks if track.age <= self.max_age]
        return tracked

    @staticmethod
    def _motion_metadata(
        previous: Tuple[float, float, float, float],
        current: Tuple[float, float, float, float],
    ) -> Dict[str, Any]:
        previous_center = ((previous[0] + previous[2]) / 2.0, (previous[1] + previous[3]) / 2.0)
        current_center = ((current[0] + current[2]) / 2.0, (current[1] + current[3]) / 2.0)
        dx = current_center[0] - previous_center[0]
        dy = current_center[1] - previous_center[1]
        previous_area = max(1.0, (previous[2] - previous[0]) * (previous[3] - previous[1]))
        current_area = max(1.0, (current[2] - current[0]) * (current[3] - current[1]))
        area_ratio = current_area / previous_area

        if abs(dx) < 3.0 and abs(dy) < 3.0:
            direction = "stationary"
        elif abs(dx) >= abs(dy):
            direction = "right" if dx > 0 else "left"
        else:
            direction = "down" if dy > 0 else "up"

        return {
            "movement_direction": direction,
            "approach_candidate": area_ratio >= 1.12,
            "area_change_ratio": round(area_ratio, 3),
            "motion_vector": [round(dx, 2), round(dy, 2)],
        }
