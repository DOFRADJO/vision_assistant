"""Speech agent with prioritized queue and non-blocking output."""
from __future__ import annotations

import logging
import queue
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
        self._queue: queue.PriorityQueue[tuple[int, int, str]] = queue.PriorityQueue()
        self._counter = 0
        self._stop_event = threading.Event()
        self._worker = threading.Thread(target=self._run, daemon=True)
        self._initialize_engine()
        self._worker.start()

    def _initialize_engine(self) -> None:
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

    def _run(self) -> None:
        while not self._stop_event.is_set():
            try:
                priority, sequence, message = self._queue.get(timeout=0.2)
            except queue.Empty:
                continue
            try:
                self._speak(message)
            finally:
                self._queue.task_done()

    def _speak(self, message: str) -> None:
        if self._engine is not None:
            with self._lock:
                self._engine.say(message)
                self._engine.runAndWait()
        else:
            logger.info("Speech output: %s", message)

    def speak(self, message: str, priority: int = 1) -> Dict[str, object]:
        if not message:
            return {"spoken": False, "message": message}

        if self._queue.qsize() >= self.config.speech.queue_size:
            logger.warning("Speech queue full: dropping message: %s", message)
            return {"spoken": False, "message": message, "backend": "dropped"}

        self._counter += 1
        self._queue.put((-priority, self._counter, message))
        return {
            "spoken": True,
            "queued": True,
            "enqueued": True,
            "message": message,
            "priority": priority,
            "backend": "pyttsx3" if self._engine is not None else "log",
        }

    def stop(self) -> None:
        self._stop_event.set()
        self._worker.join(timeout=1.0)
