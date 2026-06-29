"""Unit tests for memory agent deduplication."""
from agents.memory.memory_agent import MemoryAgent


def test_memory_prevents_duplicate_messages() -> None:
    memory = MemoryAgent()
    message = "Test message"
    first = memory.filter_message(message, priority=1)
    second = memory.filter_message(message, priority=1)
    assert first["should_speak"] is True
    assert second["should_speak"] is False


def test_memory_allows_high_priority_repeat() -> None:
    memory = MemoryAgent()
    message = "Warning: obstacle ahead"
    first = memory.filter_message(message, priority=5)
    second = memory.filter_message(message, priority=5)
    assert first["should_speak"] is True
    assert second["should_speak"] is True
