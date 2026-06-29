"""Unit tests for reasoning rules."""
from agents.reasoning.reasoning_agent import ReasoningAgent


def test_reasoning_emergency_priority() -> None:
    agent = ReasoningAgent()
    payload = {"emergency": [{"label": "ambulance"}], "people": []}
    result = agent.analyze(payload)
    assert result["priority"] == 5
    assert result["danger_level"] == "critical"
    assert "ambulance" in result["message"].lower()


def test_reasoning_no_detections() -> None:
    agent = ReasoningAgent()
    result = agent.analyze({})
    assert result["priority"] == 1
    assert result["danger_level"] == "low"
    assert "no immediate hazards" in result["message"].lower()
