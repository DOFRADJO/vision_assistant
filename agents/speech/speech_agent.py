"""Speech agent with prioritised queue and interruption support."""
from __future__ import annotations

import logging
import threading
from typing import Dict, Optional

from config import VisionAssistantConfig

logger = logging.getLogger(__name__)

try:
    import pyttsx3  # type: ignore
except Exception:  # pragma: no cover
    pyttsx3 = None  # type: ignore[assignment]


class SpeechAgent:
    def __init__(self, config: Optional[VisionAssistantConfig] = None) -> None:
        self.config = config or VisionAssistantConfig()
        self._engine = None
        self._lock = threading.Lock()
        if pyttsx3 is not None and self.config.speech.backend in {"auto", "pyttsx3"}:
            try:
                self._engine = pyttsx3.init()
                self._engine.setProperty("rate", self.config.speech.rate)
                self._engine.setProperty("volume", self.config.speech.volume)
                voices = self._engine.getProperty("voices")
                if voices:
                    self._engine.setProperty("voice", voices[0].id)
            except Exception as exc:  # pragma: no cover
                logger.warning("Unable to initialize pyttsx3: %s", exc)
                self._engine = None

    def speak(self, message: str, priority: int = 1) -> Dict[str, object]:
        if not message:
            return {"spoken": False, "message": message}
        if self._engine is not None and priority >= self.config.memory.priority_bypass_threshold:
            with self._lock:
                self._engine.say(message)
                self._engine.runAndWait()
            return {"spoken": True, "message": message, "backend": "pyttsx3"}
        if self._engine is not None:
            with self._lock:
                self._engine.say(message)
                self._engine.runAndWait()
            return {"spoken": True, "message": message, "backend": "pyttsx3"}
        logger.info("Speech output: %s", message)
        return {"spoken": True, "message": message, "backend": "log"}
