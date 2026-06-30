"""Tests for stable IDs and temporal approach estimation."""

from core.tracker import Tracker


def _person(bbox):
    return {"label": "person", "confidence": 0.9, "bbox": bbox}


def test_tracker_keeps_id_and_updates_motion() -> None:
    tracker = Tracker(iou_threshold=0.2, min_hits=2)
    first = tracker.update([_person([20, 20, 80, 120])])[0]
    second = tracker.update([_person([18, 18, 84, 128])])[0]

    assert first["tracking_id"] == second["tracking_id"]
    assert second["track_hits"] == 2
    assert second["movement_direction"] in {"left", "right", "up", "down", "stationary"}


def test_approach_requires_several_consistent_frames() -> None:
    tracker = Tracker(iou_threshold=0.2, min_hits=2)
    first = tracker.update([_person([30, 30, 70, 90])])[0]
    second = tracker.update([_person([27, 27, 73, 96])])[0]
    third = tracker.update([_person([23, 23, 77, 103])])[0]

    assert first.get("approaching") is None
    assert second["approaching"] is False
    assert third["approaching"] is True


def test_tracker_never_matches_different_labels() -> None:
    tracker = Tracker(iou_threshold=0.2)
    person = tracker.update([_person([20, 20, 80, 120])])[0]
    vehicle = tracker.update([{"label": "car", "confidence": 0.9, "bbox": [20, 20, 80, 120]}])[0]

    assert person["tracking_id"] != vehicle["tracking_id"]
