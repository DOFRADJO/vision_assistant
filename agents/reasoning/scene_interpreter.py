"""Scene interpreter for producing a high-level scene report."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List

from agents.fusion.scene import Scene, SceneObject
from agents.reasoning.scene_rules import choose_important_objects, select_applicable_rules
from agents.reasoning.decision_engine import DecisionEngine
from agents.fusion.labels import LabelsRegistry


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
        # Keep high-level rule-based summary + recommendations
        matched_rules = select_applicable_rules(scene)
        if matched_rules:
            sorted_rules = sorted(matched_rules, key=lambda rule: (-rule.priority, rule.name))
            summary = sorted_rules[0].summary
            danger_level = self._highest_danger_level(sorted_rules)
            recommendations = self._merge_unique(
                [recommendation for rule in sorted_rules for recommendation in rule.recommendations]
            )
        else:
            summary = "Aucune situation critique détectée." if scene.all_objects else "Aucune détection disponible."
            danger_level = "LOW"
            recommendations = ["Continuez prudemment."]

        # Generate events by iterating all detected objects
        events_set: set[str] = set()
        categories: set[str] = set()

        def _norm(value: str) -> str:
            return str(value or "").strip().lower()

        for obj in scene.all_objects:
            label = _norm(obj.label)
            category = _norm(obj.category) if getattr(obj, "category", None) else ""
            source_model = _norm(getattr(obj, "source_model", ""))
            confidence = float(getattr(obj, "confidence", 0.0))

            # prefer labels from registry; otherwise keep reported label
            registry = LabelsRegistry.get_instance()
            if label and not registry.has_label(label) and source_model:
                # try to map using model's labels
                model_labels = registry.labels_for_model(source_model)
                # if the reported label is similar to any model label, prefer that normalized label
                for ml in model_labels:
                    if ml in label or label in ml:
                        label = ml
                        break

            # basic detected event per object (raw object-level reporting)
            if label:
                events_set.add(f"{label}_detected")

            # category-level presence events are generated automatically as well
            if category:
                categories.add(category)
                events_set.add(f"{category}_detected")

        # Ensure raw object events are generated automatically without manual fusion rules.
        # Business-level composite events are still produced by scene_rules via matched_rules.

        # Add business event names from matching rules so composite events are included too.
        for rule in matched_rules:
            events_set.update(rule.events)

        # Ensure events are unique and sorted by DecisionEngine priority
        priority_map = DecisionEngine.DEFAULT_PRIORITY
        def event_priority(ev: str) -> int:
            return priority_map.get(ev, 0)

        events_list = sorted(list(events_set), key=lambda e: -event_priority(e))

        # Determine overall priority
        overall_priority = max((event_priority(e) for e in events_list), default=1)

        # Choose important objects (reuse existing helper rules when present)
        important_objects = choose_important_objects(scene, matched_rules) if matched_rules else scene.all_objects[:3]

        return SceneReport(
            summary=summary,
            danger_level=danger_level,
            priority=overall_priority,
            events=events_list,
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
