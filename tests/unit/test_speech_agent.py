"""Unit tests for SpeechAgent behavior."""
from agents.speech.speech_agent import SpeechAgent


def test_speech_agent_returns_backend_info() -> None:
    agent = SpeechAgent()
    response = agent.speak("Test message", priority=1)
    assert isinstance(response, dict)
    assert response.get("backend") is not None
    assert response.get("spoken") is True


def test_speech_agent_high_priority_interrupts_queue() -> None:
    agent = SpeechAgent()
    agent.speak("Low priority message", priority=1)
    response = agent.speak("High priority alert", priority=5)
    assert response.get("queued") is True
    assert response.get("priority") == 5
