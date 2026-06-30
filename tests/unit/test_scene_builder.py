"""Unit tests for the scene builder and scene model."""
import unittest

from agents.fusion.scene_builder import SceneBuilder


class TestSceneBuilder(unittest.TestCase):
    def test_constructs_scene_from_raw_predictions(self) -> None:
        raw_predictions = {
            "people_detector": [
                {
                    "label": "person",
                    "confidence": 0.95,
                    "bbox": [10, 20, 50, 100],
                    "backend": "onnx",
                    "model": "people_detector",
                }
            ],
            "vehicle_detector": [
                {
                    "label": "car",
                    "confidence": 0.85,
                    "bbox": [100, 50, 220, 130],
                    "backend": "onnx",
                    "model": "vehicle_detector",
                }
            ],
        }

        scene = SceneBuilder().build_scene(raw_predictions)

        self.assertEqual(scene.count("persons"), 1)
        self.assertEqual(scene.count("vehicles"), 1)
        self.assertEqual(scene.count(), 2)

        persons = scene.get("persons")
        self.assertEqual(len(persons), 1)
        self.assertEqual(persons[0].source, "people_detector")
        self.assertEqual(persons[0].source_model, "people_detector")
        self.assertEqual(persons[0].label, "person")
        self.assertEqual(persons[0].category, "persons")
        self.assertAlmostEqual(persons[0].width, 40.0)
        self.assertAlmostEqual(persons[0].height, 80.0)
        self.assertEqual(len(scene.all_objects), 2)

        summary = scene.summary()
        self.assertEqual(summary["persons"], 1)
        self.assertEqual(summary["vehicles"], 1)

        data = scene.to_dict()
        self.assertEqual(data["summary"]["persons"], 1)
        self.assertEqual(data["summary"]["vehicles"], 1)
        self.assertIsInstance(data["objects"]["persons"][0]["bbox"], list)
