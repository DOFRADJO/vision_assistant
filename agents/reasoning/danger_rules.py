"""Scene analysis rules for the reasoning agent."""
from __future__ import annotations

from typing import Any, Dict, List, Tuple, Union

from agents.fusion.scene import Scene


def _make_event(event_type: str, message: str, priority: int, details: Dict[str, Any] | None = None) -> Dict[str, object]:
    return {
        "type": event_type,
        "message": message,
        "priority": priority,
        "details": details or {},
        "label": event_type,
    }


def _add_event(events: List[Dict[str, object]], event_type: str, message: str, priority: int, details: Dict[str, Any] | None = None) -> None:
    if any(existing.get("type") == event_type for existing in events):
        return
    events.append(_make_event(event_type, message, priority, details))


def build_risk_profile(target: Scene | List[Dict[str, Any]], confidence: float = 0.0, bbox: List[float] | None = None) -> List[Dict[str, object]]:
    if isinstance(target, list):
        return _build_risk_profile_from_detections(target, confidence, bbox or [0, 0, 0, 0])
    return _build_risk_profile_from_scene(target)


def _build_risk_profile_from_detections(detections: List[Dict[str, Any]], confidence: float, bbox: List[float]) -> List[Dict[str, object]]:
    events: List[Dict[str, object]] = []
    for detection in detections:
        label = str(detection.get("label", "object")).lower()
        if label in {"person", "people", "personnel"}:
            _add_event(events, "person", "A person is nearby.", 2)
        elif label in {"vehicle", "car", "truck", "bus"}:
            _add_event(events, "vehicle", "A vehicle is nearby.", 3)
        elif label in {"obstacle", "door", "stair", "stairs", "chair"}:
            _add_event(events, "obstacle", "An obstacle is ahead.", 4)
        elif label in {"animal", "dog", "cat"}:
            _add_event(events, "animal", "An animal is nearby.", 2)
        elif label in {"food", "plate"}:
            _add_event(events, "food", "Food is visible.", 1)
        else:
            _add_event(events, label, f"{label} detected.", 1)
    return events


def _build_risk_profile_from_scene(scene: Scene) -> List[Dict[str, object]]:
    events: List[Dict[str, object]] = []
    if scene.vehicles and scene.persons:
        _add_event(
            events,
            "collision",
            "A vehicle is near a person. Stay alert.",
            10,
            {"vehicles": len(scene.vehicles), "persons": len(scene.persons)},
        )
    if scene.vehicles and scene.crosswalks:
        _add_event(
            events,
            "crosswalk",
            "Vehicle approaching a crosswalk.",
            9,
            {"vehicles": len(scene.vehicles), "crosswalks": len(scene.crosswalks)},
        )
    if scene.persons and scene.doors:
        _add_event(
            events,
            "door",
            "A door is ahead.",
            6,
            {"doors": len(scene.doors), "persons": len(scene.persons)},
        )
    if scene.obstacles:
        _add_event(events, "obstacle", "Obstacle ahead.", 8, {"obstacles": len(scene.obstacles)})
    if scene.weather:
        weather_names = {obj.label for obj in scene.weather}
        _add_event(events, "weather", "Weather condition detected.", 6, {"weather": list(weather_names)})
    if scene.animals:
        _add_event(events, "animal", "An animal is nearby.", 4, {"animals": len(scene.animals)})
    if scene.construction:
        _add_event(events, "construction", "Construction area ahead.", 6, {"construction": len(scene.construction)})
    if scene.furniture and scene.doors:
        _add_event(events, "indoor", "An indoor area may be ahead.", 4, {"furniture": len(scene.furniture), "doors": len(scene.doors)})
    if scene.food:
        _add_event(events, "food", "Food is visible nearby.", 1, {"food": len(scene.food)})
    if (scene.persons or scene.vehicles) and not scene.sidewalks:
        _add_event(events, "no_sidewalk", "No sidewalk detected. Use care.", 5, {"persons": len(scene.persons), "vehicles": len(scene.vehicles)})

    if scene.vehicles and not any(event["type"] == "collision" for event in events):
        _add_event(events, "vehicle", "A vehicle is nearby.", 3, {"vehicles": len(scene.vehicles)})
    if scene.persons and not any(event["type"] == "person" for event in events):
        _add_event(events, "person", "A person is nearby.", 2, {"persons": len(scene.persons)})
    if scene.crosswalks and not any(event["type"] == "crosswalk" for event in events):
        _add_event(events, "crosswalk", "Crosswalk ahead.", 8, {"crosswalks": len(scene.crosswalks)})
    if scene.doors and not any(event["type"] == "door" for event in events):
        _add_event(events, "door", "A door is ahead.", 5, {"doors": len(scene.doors)})
    if scene.animals and not any(event["type"] == "animal" for event in events):
        _add_event(events, "animal", "An animal is nearby.", 4, {"animals": len(scene.animals)})

    return events
