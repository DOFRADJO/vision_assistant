"""Scene and object models for unified detection fusion."""
from __future__ import annotations

import time
from dataclasses import asdict, dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class SceneObject:
    """A single detected object enriched for scene understanding."""
    source: str
    source_model: str
    category: str
    label: str
    confidence: float
    bbox: List[float]
    backend: str
    timestamp: float = field(default_factory=time.time)
    metadata: Dict[str, Any] = field(default_factory=dict)
    tracking_id: Optional[int] = None
    width: float = field(init=False)
    height: float = field(init=False)
    center: List[float] = field(init=False)
    model: str = field(init=False)

    def __post_init__(self) -> None:
        self.width = float(self.bbox[2] - self.bbox[0]) if len(self.bbox) >= 4 else 0.0
        self.height = float(self.bbox[3] - self.bbox[1]) if len(self.bbox) >= 4 else 0.0
        self.center = [
            float(self.bbox[0] + self.width / 2.0),
            float(self.bbox[1] + self.height / 2.0),
        ]
        self.model = self.source_model


@dataclass
class Scene:
    """A unified scene representation consumed by reasoning and speech planning."""
    persons: List[SceneObject] = field(default_factory=list)
    vehicles: List[SceneObject] = field(default_factory=list)
    animals: List[SceneObject] = field(default_factory=list)
    doors: List[SceneObject] = field(default_factory=list)
    crosswalks: List[SceneObject] = field(default_factory=list)
    traffic_signs: List[SceneObject] = field(default_factory=list)
    obstacles: List[SceneObject] = field(default_factory=list)
    sidewalks: List[SceneObject] = field(default_factory=list)
    weather: List[SceneObject] = field(default_factory=list)
    furniture: List[SceneObject] = field(default_factory=list)
    electronics: List[SceneObject] = field(default_factory=list)
    construction: List[SceneObject] = field(default_factory=list)
    food: List[SceneObject] = field(default_factory=list)
    other_objects: Dict[str, List[SceneObject]] = field(default_factory=dict)
    all_objects: List[SceneObject] = field(default_factory=list)

    def add(self, bucket: str, obj: SceneObject) -> None:
        if bucket == "other_objects" or not hasattr(self, bucket):
            self.other_objects.setdefault(bucket, []).append(obj)
        else:
            getattr(self, bucket).append(obj)
        self.all_objects.append(obj)

    def remove(self, obj: SceneObject, bucket: Optional[str] = None) -> None:
        if bucket is None:
            bucket = self._find_bucket_for(obj)

        if bucket and hasattr(self, bucket):
            bucket_list = getattr(self, bucket)
        else:
            bucket_list = self.other_objects.get(bucket, [])

        if obj in bucket_list:
            bucket_list.remove(obj)

        if obj in self.all_objects:
            self.all_objects.remove(obj)

    def get(self, bucket: str) -> List[SceneObject]:
        if hasattr(self, bucket):
            return getattr(self, bucket)
        return self.other_objects.get(bucket, [])

    def count(self, bucket: Optional[str] = None) -> int:
        if bucket is None:
            return len(self.all_objects)
        return len(self.get(bucket))

    def summary(self) -> Dict[str, int]:
        counts = {
            "persons": len(self.persons),
            "vehicles": len(self.vehicles),
            "animals": len(self.animals),
            "doors": len(self.doors),
            "crosswalks": len(self.crosswalks),
            "traffic_signs": len(self.traffic_signs),
            "obstacles": len(self.obstacles),
            "sidewalks": len(self.sidewalks),
            "weather": len(self.weather),
            "furniture": len(self.furniture),
            "electronics": len(self.electronics),
            "construction": len(self.construction),
            "food": len(self.food),
        }
        counts.update({key: len(value) for key, value in self.other_objects.items()})
        return counts

    def to_dict(self) -> Dict[str, Any]:
        serialized = {
            "summary": self.summary(),
            "objects": {
                "persons": [asdict(obj) for obj in self.persons],
                "vehicles": [asdict(obj) for obj in self.vehicles],
                "animals": [asdict(obj) for obj in self.animals],
                "doors": [asdict(obj) for obj in self.doors],
                "crosswalks": [asdict(obj) for obj in self.crosswalks],
                "traffic_signs": [asdict(obj) for obj in self.traffic_signs],
                "obstacles": [asdict(obj) for obj in self.obstacles],
                "sidewalks": [asdict(obj) for obj in self.sidewalks],
                "weather": [asdict(obj) for obj in self.weather],
                "furniture": [asdict(obj) for obj in self.furniture],
                "electronics": [asdict(obj) for obj in self.electronics],
                "construction": [asdict(obj) for obj in self.construction],
                "food": [asdict(obj) for obj in self.food],
                **{key: [asdict(item) for item in value] for key, value in self.other_objects.items()},
            },
            "all_objects": [asdict(obj) for obj in self.all_objects],
        }
        return serialized

    def _find_bucket_for(self, obj: SceneObject) -> Optional[str]:
        for bucket in self.summary():
            if hasattr(self, bucket) and obj in getattr(self, bucket):
                return bucket
        for bucket, objects in self.other_objects.items():
            if obj in objects:
                return bucket
        return None
