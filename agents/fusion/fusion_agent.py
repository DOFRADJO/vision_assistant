"""Fusion agent for merging raw detector outputs into a single scene."""
from __future__ import annotations

import logging
from typing import Any, Dict, List, Tuple

from agents.fusion.scene import Scene, SceneObject

logger = logging.getLogger(__name__)

CATEGORY_BUCKETS: Dict[str, str] = {
    "person": "persons",
    "people": "persons",
    "people_tracking": "persons",
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
    "sidewalk": "sidewalks",
    "weather": "weather",
    "furniture": "furniture",
    "chair": "furniture",
    "table": "furniture",
    "electronics": "electronics",
    "electronic": "electronics",
    "phone": "electronics",
    "construction": "construction",
    "food": "food",
    "animal": "animals",
    "dog": "animals",
    "cat": "animals",
    "dangerous_animal": "animals",
}

LABEL_BUCKETS: Dict[str, str] = {
    "person": "persons",
    "people": "persons",
    "man": "persons",
    "woman": "persons",
    "child": "persons",
    "vehicle": "vehicles",
    "car": "vehicles",
    "bus": "vehicles",
    "truck": "vehicles",
    "crosswalk": "crosswalks",
    "traffic light": "traffic_signs",
    "traffic sign": "traffic_signs",
    "door": "doors",
    "stair": "obstacles",
    "stairs": "obstacles",
    "obstacle": "obstacles",
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
    "phone": "electronics",
    "computer": "electronics",
    "construction": "construction",
    "work zone": "construction",
    "food": "food",
    "plate": "food",
    "animal": "animals",
    "dog": "animals",
    "cat": "animals",
}

DEFAULT_BUCKET = "other_objects"


def _normalize_text(value: Any) -> str:
    return str(value or "").strip().lower()


def _bucket_for(source: str, label: str) -> str:
    normalized_source = _normalize_text(source)
    normalized_label = _normalize_text(label)

    for token, bucket in CATEGORY_BUCKETS.items():
        if token in normalized_source:
            return bucket

    for token, bucket in LABEL_BUCKETS.items():
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
        return [float(value), float(value), float(value), float(value)]
    except Exception:
        return [0.0, 0.0, 0.0, 0.0]


class FusionAgent:
    """Combine raw detector outputs into a single scene representation."""

    def fuse(self, raw_predictions: Dict[str, List[Dict[str, Any]]]) -> Scene:
        scene = Scene()
        for source, predictions in raw_predictions.items():
            for prediction in predictions:
                bucket = _bucket_for(source, prediction.get("label", ""))
                metadata = dict(prediction.get("metadata", {})) if isinstance(prediction.get("metadata", {}), dict) else {}
                metadata.setdefault("name", prediction.get("label"))
                metadata.setdefault("model", prediction.get("model", source))
                obj = SceneObject(
                    source=source,
                    label=str(prediction.get("label", "object")),
                    confidence=float(prediction.get("confidence", 0.0)),
                    bbox=_normalize_bbox(prediction.get("bbox", [0.0, 0.0, 0.0, 0.0])),
                    backend=str(prediction.get("backend", "unknown")),
                    model=str(prediction.get("model", source)),
                    category=source,
                    metadata=metadata,
                )
                scene.add(bucket, obj)
                scene.all_objects.append(obj)
        logger.debug("Fused %d sources into scene with %d objects", len(raw_predictions), len(scene.all_objects))
        return scene
