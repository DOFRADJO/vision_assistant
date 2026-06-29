from agents.reasoning.reasoning_agent import ReasoningAgent
from config import get_config


def test_reasoning_agent_returns_messages() -> None:
    agent = ReasoningAgent(config=get_config())
    detections = [{"label": "person", "confidence": 0.95, "bbox": [0, 0, 100, 100]}]
    messages = agent.analyze_scene(detections)
    assert messages
