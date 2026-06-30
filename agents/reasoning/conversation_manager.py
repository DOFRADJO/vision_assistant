"""Conversation Manager — stabilises vocal announcements.

The ConversationManager sits between the DecisionEngine and the SpeechPlanner
in the pipeline.  Its single responsibility (for now) is to suppress redundant
announcements caused by minor, frame-to-frame fluctuations in object counts.

Instead of tracking raw counts (which jitter constantly due to detection noise),
the manager quantises each category into one of three *buckets*:

    NONE      → 0 objects
    ONE       → exactly 1 object
    MULTIPLE  → 2 or more objects

A new announcement is authorised **only** when at least one tracked category
changes bucket — meaning the scene has changed in a way that is genuinely
useful to communicate to the user.

Additionally, high-priority (danger) events always bypass the stabilisation
gate so that safety-critical messages are never suppressed.
"""
from __future__ import annotations

import logging
import time
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Any, Dict, Optional, Tuple

from agents.reasoning.decision_engine import DecisionEngine

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Bucket enum
# ---------------------------------------------------------------------------

class CountBucket(Enum):
    """Coarse quantisation of an object count."""
    NONE = auto()
    ONE = auto()
    MULTIPLE = auto()

    @staticmethod
    def from_count(n: int) -> "CountBucket":
        if n <= 0:
            return CountBucket.NONE
        if n == 1:
            return CountBucket.ONE
        return CountBucket.MULTIPLE


# ---------------------------------------------------------------------------
# Decision result
# ---------------------------------------------------------------------------

@dataclass
class AnnouncementDecision:
    """Result of :py:meth:`ConversationManager.should_announce`."""
    allowed: bool
    reason: str
    changed_categories: list[str] = field(default_factory=list)


# ---------------------------------------------------------------------------
# Categories tracked by the manager
# ---------------------------------------------------------------------------

# Legacy fallback list of categories. When scene summary data is available,
# dynamic category detection is used instead of hard-coded lists.
TRACKED_CATEGORIES: Tuple[str, ...] = (
    "persons",
    "vehicles",
    "animals",
    "doors",
    "crosswalks",
    "traffic_signs",
    "obstacles",
    "sidewalks",
    "furniture",
    "food",
    "electronics",
    "construction",
    "weather",
)

CRITICAL_PRIORITY_THRESHOLD = 80

# ---------------------------------------------------------------------------
# ConversationManager
# ---------------------------------------------------------------------------

class ConversationManager:
    """Gate that decides whether a scene report warrants a new announcement.

    Parameters
    ----------
    min_announce_interval:
        Minimum seconds between two non-critical announcements.  Even when
        the bucket changes, the manager will not authorise a new announcement
        until this interval has elapsed.  Defaults to 3 seconds.
    """

    def __init__(self, min_announce_interval: float = 3.0) -> None:
        self.min_announce_interval = min_announce_interval

        # Last announced bucket per category.
        # Start empty and fill dynamically from incoming scene summaries.
        self._announced_buckets: Dict[str, CountBucket] = {}

        # Timestamp of the last authorised announcement.
        self._last_announce_time: float = 0.0

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def should_announce(self, scene_report: Any) -> AnnouncementDecision:
        """Decide whether *scene_report* deserves a new vocal announcement.

        Parameters
        ----------
        scene_report:
            A ``SceneReport`` produced by ``SceneInterpreter.interpret()``.
            Expected attributes: ``events`` (list of str), ``danger_level``
            (str), ``important_objects`` (list of ``SceneObject``).

        Returns
        -------
        AnnouncementDecision
            ``.allowed`` is ``True`` when the announcement should proceed.
        """
        now = time.time()
        events: list[str] = getattr(scene_report, "events", []) or []

        # ----- 1. Critical events always pass through -----
        priority_map = DecisionEngine.DEFAULT_PRIORITY
        critical_hits = [evt for evt in events if priority_map.get(evt, 0) >= CRITICAL_PRIORITY_THRESHOLD]
        if getattr(scene_report, "danger_level", "").upper() == "CRITICAL" or critical_hits:
            reason = "critical_event"
            if critical_hits:
                reason += f":{','.join(sorted(critical_hits))}"
            logger.debug("ConversationManager: critical event(s) %s — allowing.", critical_hits)
            current_buckets = self._compute_buckets(scene_report)
            self._update_announced_buckets(current_buckets)
            self._last_announce_time = now
            return AnnouncementDecision(
                allowed=True,
                reason=reason,
                changed_categories=[],
            )

        # ----- 2. Compute current buckets from the report -----
        current_buckets = self._compute_buckets(scene_report)

        # ----- 3. Detect bucket changes -----
        changed: list[str] = []
        for cat, new in current_buckets.items():
            old = self._announced_buckets.get(cat, CountBucket.NONE)
            if old != new:
                changed.append(cat)
                logger.debug(
                    "ConversationManager: bucket change %s: %s → %s",
                    cat, old.name, new.name,
                )

        if not changed:
            return AnnouncementDecision(
                allowed=False,
                reason="no_bucket_change",
                changed_categories=[],
            )

        # ----- 4. Enforce minimum interval -----
        elapsed = now - self._last_announce_time
        if elapsed < self.min_announce_interval:
            logger.debug(
                "ConversationManager: bucket changed but cooldown active (%.1fs < %.1fs).",
                elapsed, self.min_announce_interval,
            )
            return AnnouncementDecision(
                allowed=False,
                reason="cooldown_active",
                changed_categories=changed,
            )

        # ----- 5. Allow and update state -----
        self._update_announced_buckets(current_buckets)
        self._last_announce_time = now

        return AnnouncementDecision(
            allowed=True,
            reason="bucket_changed",
            changed_categories=changed,
        )

    # ------------------------------------------------------------------
    # State inspection (useful for debugging / tests)
    # ------------------------------------------------------------------

    @property
    def announced_buckets(self) -> Dict[str, CountBucket]:
        """Read-only view of the last announced bucket per category."""
        return dict(self._announced_buckets)

    @property
    def last_announce_time(self) -> float:
        return self._last_announce_time

    def reset(self) -> None:
        """Reset all internal state."""
        self._announced_buckets = {}
        self._last_announce_time = 0.0

    def _update_announced_buckets(self, current_buckets: Dict[str, CountBucket]) -> None:
        """Store the current bucket state for all observed categories."""
        self._announced_buckets = dict(current_buckets)

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _compute_buckets(scene_report: Any) -> Dict[str, CountBucket]:
        """Extract per-category counts from the scene report and quantise them.

        The method is resilient: it tries multiple attributes that might carry
        category counts depending on what the caller provides (a ``Scene``,
        a ``SceneReport``, or a plain dict).
        """
        buckets: Dict[str, CountBucket] = {}

        # Preferred path: the coordinator attaches a scene_summary dict.
        scene_summary: Optional[Dict[str, int]] = getattr(scene_report, "scene_summary", None)
        if isinstance(scene_summary, dict):
            for cat, count in scene_summary.items():
                buckets[cat] = CountBucket.from_count(int(count or 0))
            return buckets

        # Second path: count categories from the important_objects list.
        important_objects = getattr(scene_report, "important_objects", None)
        if important_objects:
            counts: Dict[str, int] = {}
            for obj in important_objects:
                cat = getattr(obj, "category", "other")
                counts[cat] = counts.get(cat, 0) + 1
            for cat, count in counts.items():
                buckets[cat] = CountBucket.from_count(count)
            return buckets

        # Third path: ask the underlying scene object for its summary.
        scene_obj = getattr(scene_report, "scene", None)
        if scene_obj is not None and hasattr(scene_obj, "summary") and callable(scene_obj.summary):
            scene_summary = scene_obj.summary()
            if isinstance(scene_summary, dict):
                for cat, count in scene_summary.items():
                    buckets[cat] = CountBucket.from_count(int(count or 0))
                return buckets

        # Last resort: use the legacy default category list.
        for cat in TRACKED_CATEGORIES:
            buckets[cat] = CountBucket.NONE
        return buckets
