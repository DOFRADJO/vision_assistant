"""Scene interpreter for producing a high-level scene report."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List

from agents.fusion.scene import Scene, SceneObject
from agents.reasoning.scene_rules import choose_important_objects, select_applicable_rules


@dataclass
class SceneReport:
    summary: str
    danger_level: str
    priority: int
    events: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
    important_objects: List[SceneObject] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "summary": self.summary,
            "danger_level": self.danger_level,
            "priority": self.priority,
            "events": list(self.events),
            "recommendations": list(self.recommendations),
            "important_objects": [obj.__dict__ for obj in self.important_objects],
        }


class SceneInterpreter:
    """Convert a fused scene into a structured scene report."""

    def interpret(self, scene: Scene) -> SceneReport:
        matched_rules = select_applicable_rules(scene)
        if not matched_rules:
            return self._default_report(scene)

        sorted_rules = sorted(matched_rules, key=lambda rule: (-rule.priority, rule.name))
        summary = sorted_rules[0].summary
        danger_level = self._highest_danger_level(sorted_rules)
        priority = max(rule.priority for rule in sorted_rules)
        events = self._merge_unique([event for rule in sorted_rules for event in rule.events])
        recommendations = self._merge_unique(
            [recommendation for rule in sorted_rules for recommendation in rule.recommendations]
        )
        important_objects = choose_important_objects(scene, sorted_rules)

        if not recommendations:
            recommendations = ["Continuez prudemment."]

        return SceneReport(
            summary=summary,
            danger_level=danger_level,
            priority=priority,
            events=events,
            recommendations=recommendations,
            important_objects=important_objects,
        )

    def _default_report(self, scene: Scene) -> SceneReport:
        summary = "Aucune situation critique détectée." if scene.all_objects else "Aucune détection disponible."
        return SceneReport(
            summary=summary,
            danger_level="LOW",
            priority=1,
            events=["scene_clear"],
            recommendations=["Continuez normalement."],
            important_objects=scene.all_objects[:3],
        )

    def _highest_danger_level(self, rules: List[Any]) -> str:
        levels = [rule.danger_level.upper() for rule in rules]
        if "CRITICAL" in levels:
            return "CRITICAL"
        if "HIGH" in levels:
            return "HIGH"
        if "MEDIUM" in levels:
            return "MEDIUM"
        return "LOW"

    @staticmethod
    def _merge_unique(items: List[str]) -> List[str]:
        seen: set[str] = set()
        result: List[str] = []
        for item in items:
            if item not in seen:
                seen.add(item)
                result.append(item)
        return result
