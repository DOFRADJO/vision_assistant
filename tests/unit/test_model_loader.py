from pathlib import Path

import numpy as np

from agents.vision.model_loader import ModelLoader


def test_parse_yolo_matrix_output(tmp_path: Path) -> None:
    loader = ModelLoader(models_dir=tmp_path / "models")
    raw_output = np.array([[[50.0, 50.0, 20.0, 20.0, 0.9, 0.1, 0.2, 0.9]]], dtype=np.float32)
    predictions = loader._parse_raw_predictions(raw_output, (100, 100, 3))
    assert len(predictions) == 1
    assert predictions[0]["bbox"]["x1"] == 40


def test_parse_channel_first_output(tmp_path: Path) -> None:
    loader = ModelLoader(models_dir=tmp_path / "models")
    raw_output = np.zeros((5, 8400), dtype=np.float32)
    raw_output[:, 0] = [50.0, 50.0, 20.0, 20.0, 0.9]
    predictions = loader._parse_raw_predictions(raw_output, (200, 200, 3), model_shape=(100, 100))
    assert len(predictions) == 1
