"""Unit tests for model loader behavior."""
from pathlib import Path

import numpy as np
from agents.vision.model_loader import ModelLoader


def test_registers_model_directory(tmp_path: Path) -> None:
    models_dir = tmp_path / "models"
    folder = models_dir / "people_detector"
    folder.mkdir(parents=True)
    (folder / "labels.txt").write_text("person\n")
    loader = ModelLoader(models_dir=models_dir)
    loader.load_all_models()
    assert "people_detector" in loader.detectors


def test_model_loader_refreshes_when_model_appears(tmp_path: Path) -> None:
    models_dir = tmp_path / "models"
    models_dir.mkdir(parents=True)
    loader = ModelLoader(models_dir=models_dir)
    loader.load_all_models()
    assert loader.detectors
    folder = models_dir / "vehicle_detector"
    folder.mkdir(parents=True)
    (folder / "labels.txt").write_text("car\nbus\n")
    loader.refresh_models()
    assert "vehicle_detector" in loader.detectors


def test_parse_yolo_matrix_output(tmp_path: Path) -> None:
    loader = ModelLoader(models_dir=tmp_path / "models")
    raw_output = np.array([[[50.0, 50.0, 20.0, 20.0, 0.9, 0.1, 0.2, 0.9]]], dtype=np.float32)
    predictions = loader._parse_raw_predictions(raw_output, (100, 100, 3))
    assert len(predictions) == 1
    prediction = predictions[0]
    assert prediction["label"] == "0"
    assert prediction["confidence"] > 0.5
    assert prediction["bbox"]["x1"] == 40
    assert prediction["bbox"]["y1"] == 40
    assert prediction["bbox"]["x2"] == 60
    assert prediction["bbox"]["y2"] == 60
