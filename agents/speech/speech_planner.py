"""Speech planner for translating events into natural spoken phrases."""
from __future__ import annotations

from typing import Any, Dict, List


class SpeechPlanner:
    """Prepare natural language phrases from a scene report."""

    def plan(self, report: Any) -> List[Dict[str, object]]:
        planned: List[Dict[str, object]] = []
        if hasattr(report, "summary"):
            summary = str(getattr(report, "summary", "")).strip()
            priority = int(getattr(report, "priority", 1))
            planned.append(
                {
                    "message": summary or "Aucune information de scène disponible.",
                    "priority": priority,
                    "label": "scene_summary",
                }
            )
            return planned

        for event in report:
            message = self._format_message(event)
            planned.append(
                {
                    "message": message,
                    "priority": int(event.get("priority", 1)),
                    "label": event.get("type", str(event.get("message", ""))),
                }
            )
        return planned

    def _format_message(self, event: Dict[str, Any]) -> str:
        event_type = str(event.get("type", "")).lower()
        base = str(event.get("message", "")).strip()

        if event_type == "collision":
            return "Warning: a vehicle is approaching nearby."
        if event_type == "crosswalk":
            return "Crosswalk ahead. Stay close to the edge."
        if event_type == "door":
            return "A door is ahead."
        if event_type == "animal":
            return "An animal is nearby."
        if event_type == "obstacle":
            return "Obstacle ahead. Be careful."
        if event_type == "weather":
            return "Weather alert: " + base
        if event_type == "indoor":
            return "It looks like an indoor area."
        if event_type == "construction":
            return "Construction area ahead."
        if event_type == "food":
            return "Food is visible nearby."
        if event_type == "traffic_sign":
            return "Traffic sign detected."
        if event_type == "person":
            return "A person is nearby."

        if base:
            return base
        return "Attention required."
