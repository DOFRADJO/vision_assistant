import numpy as np

from agents.coordinator.coordinator import Coordinator
from config import get_config


def test_coordinator_process_frame() -> None:
    frame = np.zeros((240, 320, 3), dtype=np.uint8)
    coordinator = Coordinator(config=get_config())
    coordinator.initialize()
    result = coordinator.process_frame(frame)
    assert "status" in result
