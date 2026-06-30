"""Unit tests for scene interpretation and report generation."""
import unittest

from agents.fusion.scene import SceneObject
from agents.reasoning.scene_interpreter import SceneInterpreter, SceneReport


class TestSceneInterpreter(unittest.TestCase):
    def setUp(self) -> None:
        self.interpreter = SceneInterpreter()

    def test_single_person_summary(self) -> None:
        scene = self._build_scene([
            {"label": "person", "category": "persons", "confidence": 0.95, "bbox": [10, 10, 50, 120], "backend": "onnx", "model": "people_detector", "source": "people_detector"}
        ])

        report = self.interpreter.interpret(scene)

        self.assertEqual(report.summary, "Une personne est devant vous.")
        self.assertEqual(report.danger_level, "LOW")
        self.assertIn("persons_present", report.events)
        self.assertIn("Continuez prudemment.", report.recommendations)

    def test_vehicle_crosswalk_summary(self) -> None:
        scene = self._build_scene([
            {"label": "car", "category": "vehicles", "confidence": 0.85, "bbox": [10, 20, 100, 80], "backend": "onnx", "model": "vehicle_detector", "source": "vehicle_detector"},
            {"label": "crosswalk", "category": "crosswalks", "confidence": 0.9, "bbox": [120, 10, 220, 100], "backend": "onnx", "model": "crosswalk_detector", "source": "crosswalk_detector"},
        ])

        report = self.interpreter.interpret(scene)

        self.assertEqual(report.summary, "Un véhicule approche d'un passage piéton.")
        self.assertEqual(report.danger_level, "HIGH")
        self.assertEqual(report.priority, 80)
        self.assertIn("vehicle_at_crosswalk", report.events)

    def test_wet_floor_summary(self) -> None:
        scene = self._build_scene([
            {"label": "wet_floor", "category": "other_objects", "confidence": 0.8, "bbox": [0, 0, 200, 200], "backend": "onnx", "model": "hazard_detector", "source": "hazard_detector"}
        ])

        report = self.interpreter.interpret(scene)

        self.assertEqual(report.summary, "Attention, le sol semble mouillé.")
        self.assertEqual(report.danger_level, "HIGH")
        self.assertIn("wet_floor", report.events)

    def _build_scene(self, predictions: list[dict]) -> "agents.fusion.scene.Scene":
        from agents.fusion.scene import Scene

        scene = Scene()
        for prediction in predictions:
            scene_object = SceneObject(
                source=prediction["source"],
                source_model=prediction["model"],
                category=prediction["label"],
                label=prediction["label"],
                confidence=float(prediction["confidence"]),
                bbox=prediction["bbox"],
                backend=prediction["backend"],
                metadata={"model": prediction["model"]},
            )
            scene.add(prediction.get("category", prediction["label"]), scene_object)
        return scene


class TestSceneReport(unittest.TestCase):
    def test_scene_report_to_dict(self) -> None:
        report = SceneReport(
            summary="Test summary",
            danger_level="LOW",
            priority=10,
            events=["test"],
            recommendations=["Continuez."],
            important_objects=[],
        )

        data = report.to_dict()
        self.assertEqual(data["summary"], "Test summary")
        self.assertEqual(data["danger_level"], "LOW")
        self.assertEqual(data["priority"], 10)
        self.assertEqual(data["events"], ["test"])
        self.assertEqual(data["recommendations"], ["Continuez."])
