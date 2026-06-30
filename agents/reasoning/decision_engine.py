"""Decision engine that chooses a single action from a SceneReport.

The engine receives a SceneReport and returns a single Decision.
It applies a configurable priority table, respects TTLs, and avoids
repeating announcements while a decision is still valid.
"""
from __future__ import annotations

import time
from dataclasses import dataclass
from typing import Any, Callable, Dict, Optional


@dataclass
class Decision:
    priority: int
    action: str
    message: str
    reason: str
    danger_level: str


class DecisionEngine:
    """Choose a single Decision from a SceneReport.

    Behavior:
    - Use a priority table (modifiable) to map event reasons to priority.
    - Respect per-reason TTLs to avoid repeating the same announcement.
    - If a new higher-priority reason appears before TTL expiry, replace and speak.
    - If nothing to announce or TTL still active for the top reason, return Decision(action="IGNORE").
    """

    # Default priority map (can be replaced by setting instance attribute)
    DEFAULT_PRIORITY: Dict[str, int] = {
        "vehicle_approaching": 110,
        "person_approaching": 80,
        "stairs_present": 100,
        "wet_floor": 95,
        "obstacle": 90,
        "vehicle_at_crosswalk": 88,
        "traffic_light_red": 85,
        "green_light_crosswalk": 75,
        "dog_with_person": 60,
        "person_at_door": 70,
        "persons_present": 40,
        "multiple_persons": 30,
        "vehicle_present": 40,
        "crosswalk_present": 25,
        "door": 20,
        "persons_present_verbose": 40,
    }

    # TTLs in seconds for announcements by reason
    DEFAULT_TTL: Dict[str, float] = {
        "vehicle_approaching": 3.0,
        "person_approaching": 5.0,
        "stairs_present": 5.0,
        "wet_floor": 10.0,
        "obstacle": 10.0,
        "vehicle_at_crosswalk": 8.0,
        "traffic_light_red": 8.0,
        "person_at_door": 15.0,
        "persons_present": 15.0,
        "multiple_persons": 15.0,
        "door": 20.0,
    }

    def __init__(self, priority_map: Optional[Dict[str, int]] = None, ttl_map: Optional[Dict[str, float]] = None, time_fn: Optional[Callable[[], float]] = None) -> None:
        self.priority_map = dict(self.DEFAULT_PRIORITY)
        if priority_map:
            self.priority_map.update(priority_map)
        self.ttl_map = dict(self.DEFAULT_TTL)
        if ttl_map:
            self.ttl_map.update(ttl_map)
        self._time = time_fn or time.time

        # Last spoken decision state
        self._last_reason: Optional[str] = None
        self._last_priority: int = 0
        self._last_spoken_at: float = 0.0

    def decide(self, report: Any) -> Decision:
        now = self._time()

        # No events -> ignore
        if not report or not getattr(report, "events", None):
            return Decision(priority=0, action="IGNORE", message="", reason="none", danger_level="LOW")

        # Determine the top reason among report.events using priority_map
        best_reason = None
        best_priority = -1
        for evt in report.events:
            prio = self.priority_map.get(evt, report.priority or 0)
            if prio > best_priority:
                best_priority = prio
                best_reason = evt

        # Fallback
        if not best_reason:
            return Decision(priority=0, action="IGNORE", message="", reason="none", danger_level="LOW")

        # TTL handling: determine TTL for this reason
        ttl = self.ttl_map.get(best_reason, 10.0)
        expired = (now - self._last_spoken_at) >= ttl
        message = report.summary or "Information sur la scène."

        # If same reason and not expired AND the message is the exact same -> ignore
        if self._last_reason == best_reason and not expired:
            if getattr(self, "_last_message", "") == message:
                return Decision(priority=0, action="IGNORE", message="", reason=best_reason, danger_level=report.danger_level)

        # If a previous decision exists and has higher priority and is not expired AND message is the same -> ignore
        if self._last_reason and not expired and self._last_priority > best_priority:
            if getattr(self, "_last_message", "") == message:
                return Decision(priority=0, action="IGNORE", message="", reason=best_reason, danger_level=report.danger_level)

        # Otherwise, produce a SPEAK decision
        decision = Decision(
            priority=best_priority,
            action="SPEAK",
            message=message,
            reason=best_reason,
            danger_level=report.danger_level,
        )

        # Update last spoken state
        self._last_reason = best_reason
        self._last_priority = best_priority
        self._last_spoken_at = now
        self._last_message = message

        return decision

    def reset(self) -> None:
        """Reset the internal state (useful for tests)."""
        self._last_reason = None
        self._last_priority = 0
        self._last_spoken_at = 0.0
