"""Vision agent responsible for loading models and producing raw detections."""
from __future__ import annotations

import logging
import time
from typing import Any, Dict, List, Optional

import numpy as np

from agents.vision.model_loader import ModelLoader
from config import VisionAssistantConfig

logger = logging.getLogger(__name__)


class VisionAgent:
    def __init__(self, model_loader: Optional[ModelLoader] = None, config: Optional[VisionAssistantConfig] = None) -> None:
        self.config = config or VisionAssistantConfig()
        self.model_loader = model_loader or ModelLoader(self.config.paths.models_dir)
        self.last_results: Dict[str, Any] = {}

    def load_models(self) -> None:
        self.model_loader.load_all_models()

    def predict(self, image: np.ndarray, frame_id: int = 0) -> Dict[str, Any]:
        if image is None:
            return {
                "frame_id": frame_id,
                "timestamp": time.time(),
                "detections": [],
                "raw_predictions": {},
                "people": [],
                "vehicles": [],
                "model_count": len(self.model_loader.detectors),
            }

        raw_predictions = self.model_loader.predict_all(image)
        all_detections: List[Dict[str, Any]] = []

        for category, predictions in raw_predictions.items():
            for prediction in predictions:
                prediction["source"] = category
                prediction.setdefault("model", category)
                all_detections.append(prediction)

        self.last_results = {
            "frame_id": frame_id,
            "timestamp": time.time(),
            "detections": all_detections,
            "raw_predictions": raw_predictions,
            "people": raw_predictions.get("people", []) + raw_predictions.get("persons", []),
            "vehicles": raw_predictions.get("vehicles", []),
            "model_count": len(self.model_loader.detectors),
        }
        return self.last_results
