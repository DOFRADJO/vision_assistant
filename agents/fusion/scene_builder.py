"""Scene Builder for turning raw model outputs into a unified Scene."""
from __future__ import annotations

import logging
import time
from typing import Any, Dict, List

from agents.fusion.scene import Scene, SceneObject

logger = logging.getLogger(__name__)

DEFAULT_BUCKET = "other_objects"

CATEGORY_MAP: Dict[str, str] = {
    "person": "persons",
    "people": "persons",
    "people_tracking": "persons",
    "man": "persons",
    "woman": "persons",
    "child": "persons",
    "vehicle": "vehicles",
    "car": "vehicles",
    "truck": "vehicles",
    "bus": "vehicles",
    "traffic": "traffic_signs",
    "traffic_light": "traffic_signs",
    "traffic_sign": "traffic_signs",
    "crosswalk": "crosswalks",
    "door": "doors",
    "obstacle": "obstacles",
    "stair": "obstacles",
    "stairs": "obstacles",
    "sidewalk": "sidewalks",
    "weather": "weather",
    "rain": "weather",
    "snow": "weather",
    "sunny": "weather",
    "furniture": "furniture",
    "chair": "furniture",
    "sofa": "furniture",
    "table": "furniture",
    "electronics": "electronics",
    "electronic": "electronics",
    "phone": "electronics",
    "computer": "electronics",
    "construction": "construction",
    "work zone": "construction",
    "food": "food",
    "plate": "food",
    "animal": "animals",
    "dog": "animals",
    "cat": "animals",
    "dangerous_animal": "animals",
}


def _normalize_text(value: Any) -> str:
    return str(value or "").strip().lower()


def _bucket_for(source: str, label: str, category_map: Dict[str, str]) -> str:
    normalized_source = _normalize_text(source)
    normalized_label = _normalize_text(label)

    for token, bucket in category_map.items():
        if token in normalized_source:
            return bucket

    for token, bucket in category_map.items():
        if token in normalized_label:
            return bucket

    if normalized_source.endswith("s"):
        return normalized_source

    if normalized_label.endswith("s"):
        return normalized_label

    return DEFAULT_BUCKET


def _normalize_bbox(value: Any) -> List[float]:
    if isinstance(value, dict):
        keys = ["x1", "y1", "x2", "y2"]
        if all(key in value for key in keys):
            return [
                float(value["x1"]),
                float(value["y1"]),
                float(value["x2"]),
                float(value["y2"]),
            ]
        values = [value.get(key) for key in keys]
        return [float(v) if v is not None else 0.0 for v in values]

    if isinstance(value, (list, tuple)) and len(value) >= 4:
        return [float(value[0]), float(value[1]), float(value[2]), float(value[3])]

    try:
        number = float(value)
        return [number, number, number, number]
    except Exception:
        return [0.0, 0.0, 0.0, 0.0]


class SceneBuilder:
    """Build a unified scene from raw model outputs."""

    def __init__(self, category_map: Dict[str, str] | None = None) -> None:
        self.category_map = category_map or CATEGORY_MAP

    def build_scene(self, raw_predictions: Dict[str, List[Dict[str, Any]]]) -> Scene:
        scene = Scene()
        for source, predictions in raw_predictions.items():
            for prediction in predictions:
                bucket = _bucket_for(source, prediction.get("label", ""), self.category_map)
                metadata = dict(prediction.get("metadata", {})) if isinstance(prediction.get("metadata", {}), dict) else {}
                metadata.setdefault("name", prediction.get("label"))
                metadata.setdefault("model", prediction.get("model", source))

                timestamp = prediction.get("timestamp")
                scene_object = SceneObject(
                    source=source,
                    source_model=str(prediction.get("model", source)),
                    category=bucket,
                    label=str(prediction.get("label", "object")),
                    confidence=float(prediction.get("confidence", 0.0)),
                    bbox=_normalize_bbox(prediction.get("bbox", [0.0, 0.0, 0.0, 0.0])),
                    backend=str(prediction.get("backend", "unknown")),
                    timestamp=float(timestamp) if timestamp is not None else time.time(),
                    metadata=metadata,
                )
                scene.add(bucket, scene_object)
        logger.debug("Built scene with %d objects from %d sources", len(scene.all_objects), len(raw_predictions))
        return scene

    def summarize(self, raw_predictions: Dict[str, List[Dict[str, Any]]]) -> Dict[str, int]:
        return self.build_scene(raw_predictions).summary()
