"""Unit tests for ConversationManager."""
from __future__ import annotations

import sys
import time
from dataclasses import dataclass, field
from typing import Any, Dict, List
from unittest.mock import patch

sys.path.insert(0, "/mnt/dtamboudisk/vision_assistant")

from agents.reasoning.conversation_manager import (
    AnnouncementDecision,
    ConversationManager,
    CountBucket,
    TRACKED_CATEGORIES,
)


# ---------------------------------------------------------------------------
# Helpers — lightweight stand-ins for SceneReport
# ---------------------------------------------------------------------------

@dataclass
class FakeReport:
    summary: str = ""
    danger_level: str = "LOW"
    priority: int = 1
    events: List[str] = field(default_factory=list)
    important_objects: List[Any] = field(default_factory=list)
    scene_summary: Dict[str, int] = field(default_factory=dict)


def make_report(persons: int = 0, vehicles: int = 0, obstacles: int = 0,
                food: int = 0, sidewalks: int = 0,
                events: List[str] | None = None) -> FakeReport:
    """Build a minimal fake report with controllable category counts."""
    summary = {}
    for cat in TRACKED_CATEGORIES:
        summary[cat] = 0
    summary["persons"] = persons
    summary["vehicles"] = vehicles
    summary["obstacles"] = obstacles
    summary["food"] = food
    summary["sidewalks"] = sidewalks
    return FakeReport(
        summary=f"{persons}p {vehicles}v",
        events=events or [],
        scene_summary=summary,
    )


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

class TestCountBucket:
    def test_from_count_zero(self):
        assert CountBucket.from_count(0) == CountBucket.NONE

    def test_from_count_one(self):
        assert CountBucket.from_count(1) == CountBucket.ONE

    def test_from_count_many(self):
        assert CountBucket.from_count(5) == CountBucket.MULTIPLE
        assert CountBucket.from_count(2) == CountBucket.MULTIPLE
        assert CountBucket.from_count(100) == CountBucket.MULTIPLE

    def test_from_count_negative(self):
        assert CountBucket.from_count(-1) == CountBucket.NONE


class TestStabilisation:
    """Core test suite: minor count fluctuations must NOT trigger announcements."""

    def test_no_change_means_no_announce(self):
        """Empty scene stays empty → no announcement."""
        mgr = ConversationManager(min_announce_interval=0)
        report = make_report(persons=0)
        decision = mgr.should_announce(report)
        assert not decision.allowed
        assert decision.reason == "no_bucket_change"

    def test_none_to_one_triggers(self):
        """0 persons → 1 person = bucket change NONE→ONE."""
        mgr = ConversationManager(min_announce_interval=0)
        report = make_report(persons=1)
        decision = mgr.should_announce(report)
        assert decision.allowed
        assert "persons" in decision.changed_categories

    def test_one_to_multiple_triggers(self):
        """1 person → 3 persons = bucket change ONE→MULTIPLE."""
        mgr = ConversationManager(min_announce_interval=0)
        # First: go from NONE → ONE
        mgr.should_announce(make_report(persons=1))
        # Now: ONE → MULTIPLE
        decision = mgr.should_announce(make_report(persons=3))
        assert decision.allowed
        assert "persons" in decision.changed_categories

    def test_multiple_to_none_triggers(self):
        """5 persons → 0 = MULTIPLE→NONE."""
        mgr = ConversationManager(min_announce_interval=0)
        mgr.should_announce(make_report(persons=5))
        decision = mgr.should_announce(make_report(persons=0))
        assert decision.allowed
        assert "persons" in decision.changed_categories

    def test_jitter_within_multiple_is_suppressed(self):
        """4→5→4→6→5 persons all stay in MULTIPLE — no new announcement."""
        mgr = ConversationManager(min_announce_interval=0)
        # Establish MULTIPLE bucket
        mgr.should_announce(make_report(persons=4))
        # All subsequent frames stay in MULTIPLE
        for count in [5, 4, 6, 5, 3, 7, 2]:
            decision = mgr.should_announce(make_report(persons=count))
            assert not decision.allowed, f"Should NOT announce for {count} persons (still MULTIPLE)"
            assert decision.reason == "no_bucket_change"

    def test_jitter_within_one_is_suppressed(self):
        """1→1→1 stays ONE — only the first transition is announced."""
        mgr = ConversationManager(min_announce_interval=0)
        first = mgr.should_announce(make_report(persons=1))
        assert first.allowed  # NONE→ONE
        second = mgr.should_announce(make_report(persons=1))
        assert not second.allowed  # ONE→ONE, no change


class TestCriticalBypass:
    """Critical events must always be allowed through, regardless of bucket state."""

    def test_vehicle_approaching_always_passes(self):
        mgr = ConversationManager(min_announce_interval=0)
        # Even with no bucket change, critical events pass.
        report = make_report(events=["vehicle_approaching"])
        decision = mgr.should_announce(report)
        assert decision.allowed
        assert "critical_event" in decision.reason

    def test_person_approaching_always_passes(self):
        mgr = ConversationManager(min_announce_interval=0)
        report = make_report(persons=3, events=["person_approaching"])
        mgr.should_announce(report)  # establish bucket
        # Same bucket, but critical event → still allowed
        decision = mgr.should_announce(make_report(persons=3, events=["person_approaching"]))
        assert decision.allowed


class TestCooldown:
    """The minimum announcement interval must be respected for non-critical events."""

    def test_cooldown_blocks_rapid_changes(self):
        mgr = ConversationManager(min_announce_interval=5.0)
        # First announcement goes through (NONE→ONE)
        first = mgr.should_announce(make_report(persons=1))
        assert first.allowed
        # Immediate bucket change (ONE→MULTIPLE) but cooldown blocks it
        second = mgr.should_announce(make_report(persons=3))
        assert not second.allowed
        assert second.reason == "cooldown_active"

    def test_cooldown_expires(self):
        mgr = ConversationManager(min_announce_interval=0.1)
        mgr.should_announce(make_report(persons=1))
        time.sleep(0.15)
        decision = mgr.should_announce(make_report(persons=3))
        assert decision.allowed


class TestReset:
    def test_reset_clears_state(self):
        mgr = ConversationManager(min_announce_interval=0)
        mgr.should_announce(make_report(persons=5))
        mgr.reset()
        # After reset, all buckets are NONE again
        assert all(b == CountBucket.NONE for b in mgr.announced_buckets.values())
        assert mgr.last_announce_time == 0.0


class TestMultipleCategories:
    """Changes in different categories are tracked independently."""

    def test_persons_and_vehicles_independent(self):
        mgr = ConversationManager(min_announce_interval=0)
        # Establish: 2 persons, 0 vehicles
        mgr.should_announce(make_report(persons=2, vehicles=0))
        # Now: persons stay MULTIPLE (no change), but vehicles appear
        decision = mgr.should_announce(make_report(persons=3, vehicles=1))
        assert decision.allowed
        assert "vehicles" in decision.changed_categories
        assert "persons" not in decision.changed_categories


# ---------------------------------------------------------------------------
# Run
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import unittest

    # Convert test classes to unittest.TestCase dynamically
    test_classes = [
        TestCountBucket, TestStabilisation, TestCriticalBypass,
        TestCooldown, TestReset, TestMultipleCategories,
    ]
    
    suite = unittest.TestSuite()
    for cls in test_classes:
        for method_name in dir(cls):
            if method_name.startswith("test_"):
                # Wrap in a proper TestCase
                method = getattr(cls, method_name)
                tc = type(cls.__name__, (unittest.TestCase,), {method_name: lambda self, m=method, c=cls: m(c())})
                suite.addTest(tc(method_name))
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    raise SystemExit(0 if result.wasSuccessful() else 1)
