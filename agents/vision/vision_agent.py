"""Vision agent responsible for loading models and producing detections."""
from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

import numpy as np

from agents.vision.model_loader import ModelLoader
from config import VisionAssistantConfig
from core.tracker import Tracker

logger = logging.getLogger(__name__)


class VisionAgent:
    def __init__(self, model_loader: Optional[ModelLoader] = None, config: Optional[VisionAssistantConfig] = None) -> None:
        self.config = config or VisionAssistantConfig()
        self.model_loader = model_loader or ModelLoader(self.config.paths.models_dir)
        self.tracker = Tracker(
            tracker_type=self.config.tracking.tracker_type,
            iou_threshold=self.config.tracking.iou_threshold,
            max_age=self.config.tracking.max_age,
        )
        self.last_results: List[Dict[str, Any]] = []

    def load_models(self) -> None:
        self.model_loader.load_all_models()

    def predict(self, image: np.ndarray) -> List[Dict[str, Any]]:
        if image is None:
            return []

        standardized: List[Dict[str, Any]] = []
        for model_name in sorted(self.model_loader.detectors):
            try:
                payload = self.model_loader.predict(model_name, image)
            except Exception as exc:  # pragma: no cover
                logger.exception("Vision prediction failed for %s: %s", model_name, exc)
                continue

            for prediction in payload.get("detections", []):
                bbox = prediction.get("bbox", [])
                if isinstance(bbox, dict):
                    bbox_values = [float(bbox.get("x1", 0)), float(bbox.get("y1", 0)), float(bbox.get("x2", 0)), float(bbox.get("y2", 0))]
                else:
                    bbox_values = [float(value) for value in bbox[:4]]

                if float(prediction.get("confidence", 0.0)) < self.config.model.confidence_threshold:
                    continue

                standardized.append(
                    {
                        "model": payload.get("model", model_name),
                        "label": prediction.get("label", "object"),
                        "confidence": float(prediction.get("confidence", 0.0)),
                        "bbox": bbox_values,
                        "backend": prediction.get("backend", "unknown"),
                    }
                )

        tracked = self.tracker.update(standardized)
        self.last_results = tracked
        return tracked
