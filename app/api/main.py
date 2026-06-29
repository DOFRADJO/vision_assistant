"""FastAPI endpoints for Vision Assistant."""
from __future__ import annotations
import base64
import logging
from typing import Any, Dict, List, Optional

try:
    import cv2
except ImportError:  # pragma: no cover
    cv2 = None  # type: ignore[assignment]
import numpy as np
from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel

from agents.coordinator.coordinator import Coordinator
from agents.vision.model_loader import ModelLoader
from agents.vision.vision_agent import VisionAgent
from config import get_config
from core.logger import configure_logging

logger = logging.getLogger(__name__)
app = FastAPI(title="Vision Assistant API")
config = get_config()
configure_logging(config)


class PredictRequest(BaseModel):
    base64_image: str


class SpeakRequest(BaseModel):
    message: str


@app.on_event("startup")
def startup() -> None:
    model_loader = ModelLoader(config.paths.models_dir)
    vision_agent = VisionAgent(model_loader=model_loader)
    vision_agent.load_models()
    coordinator = Coordinator(config=config, model_loader=model_loader)
    coordinator.initialize()
    app.state.config = config
    app.state.model_loader = model_loader
    app.state.vision_agent = vision_agent
    app.state.coordinator = coordinator


@app.get("/status")
def status(request: Request) -> Dict[str, Any]:
    model_loader = request.app.state.model_loader
    return {
        "status": "ok",
        "models": sorted(model_loader.detectors.keys()),
        "config": {
            "camera_source": config.camera.source_type,
            "speech_backend": config.speech.backend,
        },
    }


@app.get("/models")
def models(request: Request) -> Dict[str, Any]:
    return {
        "models": [
            {
                "name": name,
                "category": model_info.category,
                "labels": model_info.labels,
            }
            for name, model_info in request.app.state.model_loader.model_info.items()
        ]
    }


@app.get("/history")
def history(request: Request) -> Dict[str, Any]:
    memory_agent = request.app.state.coordinator.memory_agent
    return {"history": memory_agent.get_history()}


@app.get("/config")
def config_endpoint(request: Request) -> Dict[str, Any]:
    config_data = request.app.state.config
    return {
        "camera": {
            "source_type": config_data.camera.source_type,
            "device_index": config_data.camera.device_index,
            "video_path": config_data.camera.video_path,
            "ip_camera_url": config_data.camera.ip_camera_url,
        },
        "speech": {
            "backend": config_data.speech.backend,
            "rate": config_data.speech.rate,
            "volume": config_data.speech.volume,
            "language": config_data.speech.language,
        },
        "memory": {
            "timeout_seconds": config_data.memory.timeout_seconds,
            "priority_bypass_threshold": config_data.memory.priority_bypass_threshold,
        },
        "model": {
            "use_onnx": config_data.model.use_onnx,
            "use_torch": config_data.model.use_torch,
            "max_workers": config_data.model.max_workers,
        },
    }


@app.post("/predict")
def predict(request: Request, payload: PredictRequest) -> Dict[str, Any]:
    if cv2 is None:
        raise HTTPException(status_code=500, detail="OpenCV is required to decode images")
    try:
        data = base64.b64decode(payload.base64_image)
        image = cv2.imdecode(np.frombuffer(data, np.uint8), cv2.IMREAD_COLOR)
        if image is None:
            raise ValueError("Unable to decode image")
    except Exception as exc:
        logger.exception("Predict request failed: %s", exc)
        raise HTTPException(status_code=400, detail="Invalid base64 image")
    predictions = request.app.state.vision_agent.predict(image)
    return {"predictions": predictions}


@app.post("/speak")
def speak(request: Request, payload: SpeakRequest) -> Dict[str, Any]:
    speech_result = request.app.state.coordinator.speech_agent.speak(payload.message)
    return {"message": payload.message, "speech": speech_result}


@app.get("/frame")
def frame(request: Request) -> Dict[str, Any]:
    last_result = request.app.state.coordinator.last_result
    if not last_result:
        raise HTTPException(status_code=404, detail="No frame processed yet")
    return last_result
