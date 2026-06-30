"""Scene interpreter for producing a high-level scene report."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List

from agents.fusion.scene import Scene, SceneObject
from agents.reasoning.scene_rules import choose_important_objects, select_applicable_rules
from agents.reasoning.decision_engine import DecisionEngine
from agents.fusion.labels import LabelsRegistry

def get_spatial_context(obj: SceneObject, frame_width: float = 640.0, frame_height: float = 640.0) -> str:
    """Computes a natural language description of the object's position and distance using invariable adverbs."""
    # 1. Position
    cx = obj.center[0]
    if cx < frame_width / 3.0:
        pos_str = "à votre gauche"
    elif cx > 2.0 * frame_width / 3.0:
        pos_str = "à votre droite"
    else:
        pos_str = "au centre"

    # 2. Distance (using area ratio)
    obj_area = obj.width * obj.height
    total_area = frame_width * frame_height
    ratio = obj_area / total_area if total_area > 0 else 0

    if ratio > 0.4:
        dist_str = "très près"
    elif ratio > 0.1:
        dist_str = "à moyenne distance"
    else:
        dist_str = "au loin"

    return f"{dist_str}, {pos_str}"


def build_natural_summary(scene: Scene, matched_rules: List[Any]) -> str:
    if not scene.all_objects:
        return "Aucune détection disponible."

    num_persons = len(scene.get("persons") or [])
    num_vehicles = len(scene.get("vehicles") or [])
    rule_names = [r.name for r in matched_rules]
    
    # 1. Critical Approaching Threats
    if "vehicle_approaching" in rule_names:
        vehicles = scene.get("vehicles") or []
        approaching = [v for v in vehicles if v.metadata.get("approaching")]
        target = approaching[0] if approaching else vehicles[0]
        pos = get_spatial_context(target)
        prefix = "Un véhicule" if num_vehicles <= 1 else f"Attention, parmi {num_vehicles} véhicules, l'un d'eux"
        return f"{prefix} s'approche de vous {pos}."
        
    if "person_approaching" in rule_names:
        persons = scene.get("persons") or []
        approaching = [p for p in persons if p.metadata.get("approaching")]
        target = approaching[0] if approaching else persons[0]
        pos = get_spatial_context(target)
        prefix = "Une personne" if num_persons <= 1 else f"Parmi {num_persons} personnes autour de vous, l'une d'elles"
        return f"{prefix} s'approche de vous {pos}."

    # 2. High-Priority Static Warnings
    if "vehicle_at_crosswalk" in rule_names:
        return "Un véhicule approche d'un passage piéton devant vous."
    if "traffic_light_red" in rule_names:
        return "Le feu est rouge devant vous, attendez."
    if "stairs_present" in rule_names:
        return "Des escaliers se trouvent devant vous, prudence."

    # 3. Dynamic Enumeration of Scene
    sentences = []
    
    if num_persons > 0:
        target = (scene.get("persons") or [])[0]
        pos = get_spatial_context(target)
        if num_persons == 1:
            sentences.append(f"une personne {pos}")
        else:
            sentences.append(f"{num_persons} personnes {pos}")
            
    if num_vehicles > 0:
        target = (scene.get("vehicles") or [])[0]
        pos = get_spatial_context(target)
        if num_vehicles == 1:
            sentences.append(f"un véhicule {pos}")
        else:
            sentences.append(f"{num_vehicles} véhicules {pos}")

    # Add contexts from minor rules
    if "wet_floor" in rule_names:
        sentences.append("un sol glissant")
    if "dog_with_person" in rule_names:
        sentences.append("un chien accompagné")
    if "crosswalk_present" in rule_names:
        sentences.append("un passage piéton")
    if "sidewalk_present" in rule_names:
        sentences.append("un trottoir")
    if "food_present" in rule_names:
        sentences.append("de la nourriture")
        
    if sentences:
        if len(sentences) > 1:
            joined = ", ".join(sentences[:-1]) + " et " + sentences[-1]
        else:
            joined = sentences[0]
        return f"Je perçois {joined}."
        
    # Ultimate Fallback
    obj_descriptions = []
    for obj in scene.all_objects[:2]:
        pos = get_spatial_context(obj)
        obj_descriptions.append(f"{obj.label} ({pos})")
    
    joined = ", ".join(obj_descriptions)
    return f"J'ai détecté : {joined}."

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
        summary = build_natural_summary(scene, matched_rules)
        
        if matched_rules:
            sorted_rules = sorted(matched_rules, key=lambda rule: (-rule.priority, rule.name))
            danger_level = self._highest_danger_level(sorted_rules)
            recommendations = self._merge_unique(
                [recommendation for rule in sorted_rules for recommendation in rule.recommendations]
            )
            important_objects = choose_important_objects(scene, matched_rules)
        else:
            danger_level = "LOW"
            recommendations = ["Continuez prudemment."]
            important_objects = scene.all_objects[:3]


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

        # Important objects are already extracted above

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
