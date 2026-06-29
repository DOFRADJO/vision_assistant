"""Integration test for the Vision Assistant pipeline."""
import numpy as np
from agents.coordinator.coordinator import Coordinator


def test_pipeline_runs_with_real_models() -> None:
    """Integration test for the Vision Assistant pipeline with real models."""
    coordinator = Coordinator()
    coordinator.initialize()
    frame = np.zeros((480, 640, 3), dtype=np.uint8)
    output = coordinator.execute(frame, frame_id=1)
    assert "vision" in output
    assert "reasoning" in output
    assert "memory" in output
    assert "speech" in output
    assert output["vision"].get("frame_id") == 1
    assert output["metrics"]["processing_time"] >= 0
    assert output["status"] == "ok"
