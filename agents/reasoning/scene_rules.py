"""Business rules for interpreting a visual scene."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable, Dict, List

from agents.fusion.scene import Scene, SceneObject

RuleCondition = Callable[[Scene], bool]


@dataclass(frozen=True)
class SceneRule:
    name: str
    condition: RuleCondition
    summary: str
    danger_level: str
    priority: int
    events: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
    important_labels: List[str] = field(default_factory=list)
    important_categories: List[str] = field(default_factory=list)


def _normalize_label(value: str) -> str:
    return str(value or "").strip().lower()


def has_label(scene: Scene, label: str) -> bool:
    normalized = _normalize_label(label)
    return any(normalized == _normalize_label(obj.label) or normalized in _normalize_label(obj.label) for obj in scene.all_objects)


def has_any_label(scene: Scene, labels: List[str]) -> bool:
    return any(has_label(scene, label) for label in labels)


def count_category(scene: Scene, category: str) -> int:
    if hasattr(scene, category):
        return len(getattr(scene, category))
    return 0


def category_is_approaching(scene: Scene, category: str) -> bool:
    return any(bool(obj.metadata.get("approaching")) for obj in scene.get(category))


def important_objects(scene: Scene, labels: List[str], categories: List[str]) -> List[SceneObject]:
    selected: List[SceneObject] = []
    lowercase_labels = {_normalize_label(label) for label in labels}
    lowercase_categories = {category for category in categories}

    for obj in scene.all_objects:
        if _normalize_label(obj.label) in lowercase_labels:
            selected.append(obj)
            continue
        if obj.category in lowercase_categories:
            selected.append(obj)

    return selected


RULES: List[SceneRule] = [
    SceneRule(
        name="vehicle_approaching",
        condition=lambda scene: category_is_approaching(scene, "vehicles"),
        summary="Attention, un véhicule s'approche.",
        danger_level="CRITICAL",
        priority=100,
        events=["vehicle_approaching"],
        recommendations=["Arrêtez-vous et éloignez-vous de sa trajectoire."],
        important_categories=["vehicles"],
    ),
    SceneRule(
        name="person_approaching",
        condition=lambda scene: category_is_approaching(scene, "persons"),
        summary="Une personne s'approche de vous.",
        danger_level="MEDIUM",
        priority=70,
        events=["person_approaching"],
        recommendations=["Restez attentif à son déplacement."],
        important_categories=["persons"],
    ),
    SceneRule(
        name="wet_floor",
        condition=lambda scene: has_label(scene, "wet_floor") or has_label(scene, "wet floor"),
        summary="Attention, le sol semble mouillé.",
        danger_level="HIGH",
        priority=90,
        events=["wet_floor"],
        recommendations=["Marchez lentement et évitez les surfaces glissantes."],
        important_labels=["wet_floor", "wet floor"],
    ),
    SceneRule(
        name="traffic_light_red",
        condition=lambda scene: any(
            (has_label(scene, "traffic_light") and (has_label(scene, "red") or _normalize_label(obj.metadata.get("color", "")) == "red"))
            for obj in scene.traffic_signs
        ),
        summary="Le feu est rouge.",
        danger_level="HIGH",
        priority=85,
        events=["traffic_light_red"],
        recommendations=["Attendez jusqu'à ce que le feu passe au vert."],
        important_categories=["traffic_signs"],
    ),
    SceneRule(
        name="green_light_crosswalk",
        condition=lambda scene: has_label(scene, "green_light") and count_category(scene, "crosswalks") > 0,
        summary="Le passage est autorisé.",
        danger_level="LOW",
        priority=75,
        events=["green_light_crosswalk"],
        recommendations=["Traversez prudemment."],
        important_labels=["green_light"],
        important_categories=["crosswalks"],
    ),
    SceneRule(
        name="dog_with_person",
        condition=lambda scene: count_category(scene, "persons") > 0 and count_category(scene, "animals") > 0 and has_any_label(scene, ["dog"]),
        summary="Une personne est accompagnée d'un chien.",
        danger_level="LOW",
        priority=60,
        events=["dog_with_person"],
        recommendations=["Restez attentif à la présence d'un animal."],
        important_labels=["dog"],
        important_categories=["persons"],
    ),
    SceneRule(
        name="person_at_door",
        condition=lambda scene: count_category(scene, "persons") > 0 and count_category(scene, "doors") > 0,
        summary="Une personne est proche de l'entrée.",
        danger_level="MEDIUM",
        priority=70,
        events=["person_at_door"],
        recommendations=["Préparez-vous à un contact potentiel."],
        important_categories=["persons", "doors"],
    ),
    SceneRule(
        name="vehicle_at_crosswalk",
        condition=lambda scene: count_category(scene, "vehicles") > 0 and count_category(scene, "crosswalks") > 0,
        summary="Un véhicule approche d'un passage piéton.",
        danger_level="HIGH",
        priority=80,
        events=["vehicle_at_crosswalk"],
        recommendations=["Restez sur le côté et attendez."],
        important_categories=["vehicles", "crosswalks"],
    ),
    SceneRule(
        name="stairs_present",
        condition=lambda scene: has_any_label(scene, ["stairs", "stair"]),
        summary="Des escaliers sont devant vous.",
        danger_level="HIGH",
        priority=80,
        events=["stairs_present"],
        recommendations=["Descendez ou montez avec précaution."],
        important_labels=["stairs", "stair"],
    ),
    SceneRule(
        name="single_person",
        condition=lambda scene: count_category(scene, "persons") == 1,
        summary="Une personne est devant vous.",
        danger_level="LOW",
        priority=20,
        events=["persons_present"],
        recommendations=["Continuez prudemment."],
        important_categories=["persons"],
    ),
    SceneRule(
        name="multiple_persons",
        condition=lambda scene: count_category(scene, "persons") > 1,
        summary="Plusieurs personnes se trouvent devant vous.",
        danger_level="LOW",
        priority=30,
        events=["persons_present"],
        recommendations=["Soyez vigilant dans la foule."],
        important_categories=["persons"],
    ),
    SceneRule(
        name="vehicle_present",
        condition=lambda scene: count_category(scene, "vehicles") > 0,
        summary="Un véhicule est à proximité.",
        danger_level="MEDIUM",
        priority=40,
        events=["vehicle_present"],
        recommendations=["Gardez vos distances."],
        important_categories=["vehicles"],
    ),
    SceneRule(
        name="crosswalk_present",
        condition=lambda scene: count_category(scene, "crosswalks") > 0,
        summary="Un passage piéton est visible.",
        danger_level="LOW",
        priority=25,
        events=["crosswalk_present"],
        recommendations=["Soyez attentif à la circulation."],
        important_categories=["crosswalks"],
    ),
    SceneRule(
        name="sidewalk_present",
        condition=lambda scene: count_category(scene, "sidewalks") > 0,
        summary="Un trottoir est détecté.",
        danger_level="LOW",
        priority=10,
        events=["sidewalk_detected"],
        recommendations=["Vous pouvez y marcher en sécurité."],
        important_categories=["sidewalks"],
    ),
    SceneRule(
        name="food_present",
        condition=lambda scene: count_category(scene, "food") > 0,
        summary="De la nourriture est visible.",
        danger_level="LOW",
        priority=5,
        events=["food_detected"],
        recommendations=["Information contextuelle."],
        important_categories=["food"],
    ),
]


def select_applicable_rules(scene: Scene) -> List[SceneRule]:
    return [rule for rule in RULES if rule.condition(scene)]


def choose_important_objects(scene: Scene, rules: List[SceneRule], limit: int = 3) -> List[SceneObject]:
    if not rules:
        return []

    selected: List[SceneObject] = []
    for rule in rules:
        selected.extend(important_objects(scene, rule.important_labels, rule.important_categories))
        if len(selected) >= limit:
            break

    if not selected:
        selected = scene.all_objects[:limit]

    unique: Dict[str, SceneObject] = {}
    for obj in selected:
        key = f"{obj.label}:{obj.source}:{obj.bbox}"
        unique[key] = obj
    return list(unique.values())[:limit]
