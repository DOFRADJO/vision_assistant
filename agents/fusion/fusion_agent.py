"""Fusion agent for merging raw detector outputs into a single scene."""
from __future__ import annotations

import logging
from typing import Any, Dict, List

from agents.fusion.scene import Scene
from agents.fusion.scene_builder import SceneBuilder

logger = logging.getLogger(__name__)


class FusionAgent:
    """Combine raw detector outputs into a single scene representation."""

    def __init__(self, scene_builder: SceneBuilder | None = None) -> None:
        self.scene_builder = scene_builder or SceneBuilder()

    def fuse(self, raw_predictions: Dict[str, List[Dict[str, Any]]]) -> Scene:
        return self.scene_builder.build_scene(raw_predictions)
