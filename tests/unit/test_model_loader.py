"""Unit tests for model loader behavior."""
import logging
import tempfile
import unittest
from pathlib import Path
from typing import Any

import numpy as np
from agents.vision.model_loader import ModelInfo, ModelLoader


def test_fake_model_loader_creates_detectors(tmp_path: Path) -> None:
    models_dir = tmp_path / "models"
    models_dir.mkdir(parents=True)
    loader = ModelLoader(models_dir=models_dir)
    loader.load_all_models()
    assert loader.detectors
    predictions = loader.predict_all(np.zeros((480, 640, 3), dtype=np.uint8))
    assert isinstance(predictions, dict)


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
    assert prediction["label"] == "2"
    assert prediction["confidence"] > 0.5
    assert prediction["bbox"]["x1"] == 40
    assert prediction["bbox"]["y1"] == 40
    assert prediction["bbox"]["x2"] == 60
    assert prediction["bbox"]["y2"] == 60


def _make_dummy_onnx_session(shape: Any):
    class DummyInput:
        def __init__(self, shape: Any) -> None:
            self.shape = shape
            self.name = "input"

    class DummySession:
        def __init__(self, shape: Any) -> None:
            self._input = DummyInput(shape)

        def get_inputs(self):
            return [self._input]

    return DummySession(shape)


class LogCaptureHandler(logging.Handler):
    def __init__(self):
        super().__init__()
        self.records: list[logging.LogRecord] = []

    def emit(self, record: logging.LogRecord) -> None:
        self.records.append(record)


def _capture_log_messages(logger_name: str, level: int, callback):
    logger = logging.getLogger(logger_name)
    handler = LogCaptureHandler()
    handler.setLevel(level)
    logger.addHandler(handler)
    logger.setLevel(level)
    try:
        result = callback()
        messages = "\n".join(record.getMessage() for record in handler.records)
        return messages, result
    finally:
        logger.removeHandler(handler)


class TestModelLoaderInputSize(unittest.TestCase):
    def test_resolves_fixed_onnx_input_shape(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            model_dir = Path(tmp_dir) / "models"
            model_dir.mkdir(parents=True, exist_ok=True)
            loader = ModelLoader(models_dir=model_dir)
            model_info = ModelInfo(
                name="fixed_shape",
                category="test",
                directory=model_dir,
                metadata={},
                onnx_session=_make_dummy_onnx_session([1, 3, 480, 640]),
            )

            messages, size = _capture_log_messages(
                "agents.vision.model_loader",
                logging.INFO,
                lambda: loader._resolve_onnx_input_size(model_info),
            )

            self.assertEqual(size, (640, 480))
            self.assertIn("Using ONNX input shape", messages)

    def test_resolves_dynamic_onnx_input_shape_with_metadata(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            model_dir = Path(tmp_dir) / "models"
            model_dir.mkdir(parents=True, exist_ok=True)
            loader = ModelLoader(models_dir=model_dir)
            model_info = ModelInfo(
                name="dynamic_with_metadata",
                category="test",
                directory=model_dir,
                metadata={"input_size": [320, 240]},
                onnx_session=_make_dummy_onnx_session([1, 3, None, None]),
            )

            messages, size = _capture_log_messages(
                "agents.vision.model_loader",
                logging.INFO,
                lambda: loader._resolve_onnx_input_size(model_info),
            )

            self.assertEqual(size, (320, 240))
            self.assertIn("falling back to metadata.input_size", messages)

    def test_resolves_dynamic_onnx_input_shape_without_metadata_uses_camera_config(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            model_dir = Path(tmp_dir) / "models"
            model_dir.mkdir(parents=True, exist_ok=True)
            loader = ModelLoader(models_dir=model_dir)
            loader.config.camera.resize_width = 800
            loader.config.camera.resize_height = 600
            model_info = ModelInfo(
                name="dynamic_with_config",
                category="test",
                directory=model_dir,
                metadata={},
                onnx_session=_make_dummy_onnx_session([1, 3, None, None]),
            )

            messages, size = _capture_log_messages(
                "agents.vision.model_loader",
                logging.INFO,
                lambda: loader._resolve_onnx_input_size(model_info),
            )

            self.assertEqual(size, (800, 600))
            self.assertIn("falling back to config.camera resize", messages)


def test_parse_yolo_channel_first_output(tmp_path: Path) -> None:
    loader = ModelLoader(models_dir=tmp_path / "models")
    # Emulate a channel-first ONNX output of shape (1, 5, 2)
    raw_output = np.array(
        [
            [
                [50.0, 100.0],
                [50.0, 100.0],
                [20.0, 25.0],
                [30.0, 40.0],
                [0.9, 0.8],
            ]
        ],
        dtype=np.float32,
    )
    predictions = loader._parse_raw_predictions(raw_output, (200, 200, 3), model_shape=(100, 100))
    assert len(predictions) == 2
    assert predictions[0]["label"] == "0"
    assert predictions[0]["confidence"] == 0.9
    assert predictions[0]["bbox"]["x1"] == 40
    assert predictions[0]["bbox"]["y1"] == 35
    assert predictions[0]["bbox"]["x2"] == 60
    assert predictions[0]["bbox"]["y2"] == 65
    assert predictions[1]["confidence"] == 0.8
