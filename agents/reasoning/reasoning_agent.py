"""Reasoning agent converting a fused scene into prioritized events."""
from __future__ import annotations

import logging
from typing import Any, Dict, List

from agents.fusion.scene import Scene
from agents.reasoning.danger_rules import build_risk_profile
from agents.reasoning.priority_agent import PriorityAgent
from config import VisionAssistantConfig

logger = logging.getLogger(__name__)


class ReasoningAgent:
    def __init__(self, config: VisionAssistantConfig | None = None) -> None:
        self.config = config or VisionAssistantConfig()
        self.priority_agent = PriorityAgent()

    def analyze_scene(self, scene: Scene | List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        events = build_risk_profile(scene)
        return events
