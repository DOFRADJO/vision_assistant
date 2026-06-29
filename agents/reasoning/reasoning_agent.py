"""Reasoning agent converting detections into prioritized spoken messages."""
from __future__ import annotations

import logging
from typing import Any, Dict, List

from agents.reasoning.danger_rules import build_risk_profile
from agents.reasoning.priority_manager import sort_messages
from config import VisionAssistantConfig

logger = logging.getLogger(__name__)


class ReasoningAgent:
    def __init__(self, config: VisionAssistantConfig | None = None) -> None:
        self.config = config or VisionAssistantConfig()

    def analyze_scene(self, detections: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        messages: List[Dict[str, Any]] = []
        for detection in detections:
            label = str(detection.get("label", "object"))
            confidence = float(detection.get("confidence", 0.0))
            bbox = detection.get("bbox", [0, 0, 0, 0])
            content, priority = build_risk_profile(label, confidence, list(bbox))
            if confidence < self.config.model.confidence_threshold:
                continue
            messages.append({"message": content, "priority": priority, "label": label})
        return sort_messages(messages)
