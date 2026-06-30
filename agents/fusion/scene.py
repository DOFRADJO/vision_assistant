"""Scene and object models for unified detection fusion."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class SceneObject:
    """A single detected object enriched for scene understanding."""
    source: str
    label: str
    confidence: float
    bbox: List[float]
    backend: str
    model: str
    category: str
    metadata: Dict[str, Any] = field(default_factory=dict)
    tracking_id: Optional[int] = None


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
        if not hasattr(self, bucket):
            self.other_objects.setdefault(bucket, []).append(obj)
            return
        getattr(self, bucket).append(obj)

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
