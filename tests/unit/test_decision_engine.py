"""Unit tests for DecisionEngine behavior."""
import unittest

from agents.reasoning.decision_engine import DecisionEngine, Decision
from agents.reasoning.scene_interpreter import SceneReport


class TimeMock:
    def __init__(self, start: float = 0.0):
        self._t = start

    def time(self) -> float:
        return self._t

    def advance(self, seconds: float) -> None:
        self._t += seconds


class TestDecisionEngine(unittest.TestCase):
    def setUp(self) -> None:
        self.clock = TimeMock(1000.0)
        self.engine = DecisionEngine(time_fn=self.clock.time)

    def test_empty_scene_ignored(self) -> None:
        report = SceneReport(summary="", danger_level="LOW", priority=0, events=[], recommendations=[], important_objects=[])
        decision = self.engine.decide(report)
        self.assertEqual(decision.action, "IGNORE")

    def test_single_person_speak(self) -> None:
        report = SceneReport(summary="Une personne est devant vous.", danger_level="LOW", priority=20, events=["persons_present"], recommendations=["Continuez prudemment."], important_objects=[])
        decision = self.engine.decide(report)
        self.assertEqual(decision.action, "SPEAK")
        self.assertEqual(decision.reason, "persons_present")

    def test_repetition_ignored_within_ttl(self) -> None:
        report = SceneReport(summary="Une personne est devant vous.", danger_level="LOW", priority=20, events=["persons_present"], recommendations=["Continuez prudemment."], important_objects=[])
        d1 = self.engine.decide(report)
        self.assertEqual(d1.action, "SPEAK")
        # immediate second frame
        d2 = self.engine.decide(report)
        self.assertEqual(d2.action, "IGNORE")

    def test_ttl_expiry_allows_repeat(self) -> None:
        report = SceneReport(summary="Une personne est devant vous.", danger_level="LOW", priority=20, events=["persons_present"], recommendations=["Continuez prudemment."], important_objects=[])
        d1 = self.engine.decide(report)
        self.assertEqual(d1.action, "SPEAK")
        # advance beyond TTL for persons_present (default 15s)
        self.clock.advance(16.0)
        d2 = self.engine.decide(report)
        self.assertEqual(d2.action, "SPEAK")

    def test_higher_priority_replaces(self) -> None:
        # first a person
        report_person = SceneReport(summary="Une personne.", danger_level="LOW", priority=20, events=["persons_present"], recommendations=[], important_objects=[])
        d1 = self.engine.decide(report_person)
        self.assertEqual(d1.action, "SPEAK")
        # then stairs (higher priority)
        report_stairs = SceneReport(summary="Des escaliers.", danger_level="HIGH", priority=100, events=["stairs_present"], recommendations=[], important_objects=[])
        d2 = self.engine.decide(report_stairs)
        self.assertEqual(d2.action, "SPEAK")
        self.assertEqual(d2.reason, "stairs_present")

    def test_merge_person_and_door(self) -> None:
        report = SceneReport(summary="Une personne est proche de l'entrée.", danger_level="MEDIUM", priority=70, events=["person_at_door"], recommendations=["Préparez-vous à un contact potentiel."], important_objects=[])
        decision = self.engine.decide(report)
        self.assertEqual(decision.action, "SPEAK")
        self.assertEqual(decision.reason, "person_at_door")

    def test_red_light_vs_crosswalk(self) -> None:
        report = SceneReport(summary="Le feu est rouge et il y a un passage.", danger_level="HIGH", priority=85, events=["traffic_light_red", "crosswalk_present"], recommendations=[], important_objects=[])
        decision = self.engine.decide(report)
        self.assertEqual(decision.action, "SPEAK")
        self.assertEqual(decision.reason, "traffic_light_red")


if __name__ == "__main__":
    unittest.main()
