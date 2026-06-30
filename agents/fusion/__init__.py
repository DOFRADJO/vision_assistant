"""Fusion agent package for building a unified scene from raw detections."""
from .fusion_agent import FusionAgent
from .scene import Scene, SceneObject
from .scene_builder import CATEGORY_MAP, SceneBuilder

__all__ = ["FusionAgent", "Scene", "SceneObject", "SceneBuilder", "CATEGORY_MAP"]
