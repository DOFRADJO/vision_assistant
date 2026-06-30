"""Priority agent for selecting the most relevant events."""
from __future__ import annotations

from typing import Dict, List


class PriorityAgent:
    """Choose the highest-value events from a larger list."""

    def __init__(self, max_events: int = 6) -> None:
        self.max_events = max_events

    def select_top_events(self, events: List[Dict[str, object]]) -> List[Dict[str, object]]:
        sorted_events = sorted(
            events,
            key=lambda item: (-(int(item.get("priority", 1))), item.get("message", "")),
        )
        return sorted_events[: self.max_events]
