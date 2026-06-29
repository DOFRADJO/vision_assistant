"""Scene analysis rules for the reasoning agent."""
from __future__ import annotations

from typing import Dict, List, Tuple


def build_risk_profile(label: str, confidence: float, bbox: List[float]) -> Tuple[str, int]:
    label_lower = label.lower()
    if label_lower in {"person", "people", "personnel"}:
        return "A person is nearby.", 2
    if label_lower in {"vehicle", "car", "truck", "bus"}:
        return "A vehicle is nearby.", 3
    if label_lower in {"obstacle", "door", "stair", "stairs", "chair"}:
        return "An obstacle is in front of you.", 4
    if label_lower in {"animal", "dog", "cat"}:
        return "An animal is nearby.", 2
    if label_lower in {"food", "plate"}:
        return "Food is visible.", 1
    return f"{label} detected.", 1
