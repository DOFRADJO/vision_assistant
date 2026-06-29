"""Unit tests for VisionAgent behavior."""
from pathlib import Path

import numpy as np
from agents.vision.model_loader import ModelLoader
from agents.vision.vision_agent import VisionAgent


def test_vision_agent_returns_category_keys(tmp_path: Path) -> None:
    models_dir = tmp_path / "models"
    models_dir.mkdir(parents=True)
    loader = ModelLoader(models_dir=models_dir)
    agent = VisionAgent(model_loader=loader)
    agent.load_models()
    frame = np.zeros((480, 640, 3), dtype=np.uint8)
    result = agent.predict(frame, frame_id=42)
    assert isinstance(result, dict)
    assert result["frame_id"] == 42
    assert "timestamp" in result
    assert "people" in result
    assert "vehicles" in result
    assert isinstance(result["people"], list)
