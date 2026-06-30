"""Tracking agent for assigning stable IDs to scene objects."""
from __future__ import annotations

import logging
from typing import Dict, List

from agents.fusion.scene import Scene, SceneObject
from core.tracker import Tracker

logger = logging.getLogger(__name__)


class TrackingAgent:
    """Assign tracking identifiers to fused scene objects."""

    def __init__(
        self,
        tracker_type: str = "iou",
        iou_threshold: float = 0.35,
        max_age: int = 10,
        min_hits: int = 2,
    ) -> None:
        self.tracker = Tracker(
            tracker_type=tracker_type,
            iou_threshold=iou_threshold,
            max_age=max_age,
            min_hits=min_hits,
        )

    def track(self, scene: Scene) -> Scene:
        if not scene.all_objects:
            return scene

        detections = [
            {
                "label": obj.label,
                "confidence": obj.confidence,
                "bbox": obj.bbox,
            }
            for obj in scene.all_objects
        ]
        tracked = self.tracker.update(detections)
        for obj, tracked_item in zip(scene.all_objects, tracked):
            obj.tracking_id = tracked_item.get("tracking_id")
            for key in ("track_hits", "movement_direction", "approaching", "area_change_ratio", "motion_vector"):
                if key in tracked_item:
                    obj.metadata[key] = tracked_item[key]
        logger.debug("Tracked %d scene objects", len(scene.all_objects))
        return scene
