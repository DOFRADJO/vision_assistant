"""Memory agent for de-duplication, cooldowns, and history."""
from __future__ import annotations

from collections import deque
from time import time
from typing import Deque, Dict, List, Optional

from config import VisionAssistantConfig


class MemoryAgent:
    def __init__(self, config: Optional[VisionAssistantConfig] = None) -> None:
        self.config = config or VisionAssistantConfig()
        self.history: Deque[Dict[str, object]] = deque(maxlen=self.config.memory.max_history)
        self.last_emitted: Dict[str, float] = {}
        self.last_label_seen: Dict[str, float] = {}

    def should_emit(self, message: Dict[str, object]) -> bool:
        text = str(message.get("message", ""))
        priority = int(message.get("priority", 1))
        now = time()
        last_seen = self.last_emitted.get(text)
        label = str(message.get("label", ""))
        last_label_seen = self.last_label_seen.get(label)

        if priority >= self.config.memory.priority_bypass_threshold:
            self.last_emitted[text] = now
            self.last_label_seen[label] = now
            self.history.append({"message": text, "priority": priority, "timestamp": now})
            return True

        if last_seen is None:
            self.last_emitted[text] = now
            self.last_label_seen[label] = now
            self.history.append({"message": text, "priority": priority, "timestamp": now})
            return True

        cooldown = self.config.memory.timeout_seconds
        if last_label_seen is not None and (now - last_label_seen) >= cooldown:
            self.last_emitted[text] = now
            self.last_label_seen[label] = now
            self.history.append({"message": text, "priority": priority, "timestamp": now})
            return True

        if (now - last_seen) >= cooldown:
            self.last_emitted[text] = now
            self.last_label_seen[label] = now
            self.history.append({"message": text, "priority": priority, "timestamp": now})
            return True

        return False

    def get_history(self) -> List[Dict[str, object]]:
        return list(self.history)
