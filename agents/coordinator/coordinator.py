"""Coordinator agent orchestrating the multi-agent pipeline."""
from __future__ import annotations

import logging
import time
from typing import Any, Dict, List, Optional

from agents.memory.memory_agent import MemoryAgent
from agents.reasoning.reasoning_agent import ReasoningAgent
from agents.speech.speech_agent import SpeechAgent
from agents.vision.vision_agent import VisionAgent
from agents.vision.model_loader import ModelLoader
from config import VisionAssistantConfig

logger = logging.getLogger(__name__)


class Coordinator:
    def __init__(self, config: Optional[VisionAssistantConfig] = None, model_loader: Optional[ModelLoader] = None) -> None:
        self.config = config or VisionAssistantConfig()
        self.model_loader = model_loader or ModelLoader(self.config.paths.models_dir)
        self.vision_agent = VisionAgent(model_loader=self.model_loader, config=self.config)
        self.reasoning_agent = ReasoningAgent(config=self.config)
        self.memory_agent = MemoryAgent(config=self.config)
        self.speech_agent = SpeechAgent(config=self.config)
        self.last_result: Dict[str, Any] = {}
        self.frame_count = 0

    def initialize(self) -> None:
        if not self.model_loader.detectors:
            self.vision_agent.load_models()
            logger.info("Loaded %d model(s) for inference", len(self.model_loader.detectors))
        else:
            logger.debug("Coordinator initialization skipped model reload because models are already loaded.")

    def process_frame(self, frame: Any) -> Dict[str, Any]:
        start_time = time.perf_counter()
        self.frame_count += 1

        detections = self.vision_agent.predict(frame)
        vision_time = time.perf_counter() - start_time

        messages = self.reasoning_agent.analyze_scene(detections)
        reasoning_time = time.perf_counter() - start_time - vision_time

        filtered: List[Dict[str, Any]] = []
        for message in messages:
            if self.memory_agent.should_emit(message):
                filtered.append(message)

        memory_time = time.perf_counter() - start_time - vision_time - reasoning_time

        for message in filtered:
            self.speech_agent.speak(message["message"], priority=message.get("priority", 1))

        speech_time = time.perf_counter() - start_time - vision_time - reasoning_time - memory_time
        elapsed = time.perf_counter() - start_time
        fps = 1.0 / max(elapsed, 1e-6)

        logger.info(
            "Frame %d | detections=%d | models=%d | messages=%d | ignored=%d | fps=%.2f | vision=%.3fs | reasoning=%.3fs | memory=%.3fs | speech=%.3fs",
            self.frame_count,
            len(detections),
            len(self.model_loader.detectors),
            len(filtered),
            len(messages) - len(filtered),
            fps,
            vision_time,
            reasoning_time,
            memory_time,
            speech_time,
        )

        result = {
            "detections": detections,
            "messages": filtered,
            "status": "ok",
            "frame": self.frame_count,
            "fps": fps,
        }
        self.last_result = result
        return result
