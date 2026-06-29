"""Real model loader for ONNX and PyTorch detectors."""
from __future__ import annotations

import json
import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

try:
    import cv2
except ImportError:  # pragma: no cover
    cv2 = None  # type: ignore[assignment]

import numpy as np

from config import get_config
from core.utils import normalize_bbox, safe_read_text

logger = logging.getLogger(__name__)


def normalize_category(name: str) -> str:
    """Normalize a detector directory name to a consistent category key."""
    normalized = name.lower().replace("_detector", "").replace("detector", "").strip("_")
    if normalized == "vehicle":
        return "vehicles"
    if normalized == "people":
        return "people"
    if normalized == "traffic":
        return "traffic"
    if normalized == "animal":
        return "animals"
    if normalized == "emergency":
        return "emergency"
    if normalized == "obstacle":
        return "obstacles"
    if normalized == "furniture":
        return "furniture"
    if normalized == "food":
        return "food"
    return normalized


@dataclass
class ModelInfo:
    """Model metadata and runtime artifacts."""

    name: str
    category: str
    directory: Path
    labels: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    onnx_path: Optional[Path] = None
    pt_path: Optional[Path] = None
    onnx_session: Optional[Any] = None
    torch_model: Optional[Any] = None


class ModelLoader:
    """Load and manage multiple detector models for VisionAgent."""

    def __init__(self, models_dir: Optional[Path] = None) -> None:
        self.config = get_config()
        self.models_dir = Path(models_dir) if models_dir is not None else self.config.paths.models_dir
        self.detectors: Dict[str, Any] = {}
        self.model_info: Dict[str, ModelInfo] = {}
        self._snapshot: Dict[str, Dict[str, int]] = {}
        self._torch_available = self._detect_torch()

    def _detect_torch(self) -> bool:
        try:
            import torch  # noqa: F401
            return True
        except ImportError:
            logger.debug("PyTorch is not installed; skipping PyTorch model support.")
            return False

    def load_all_models(self) -> None:
        """Discover and load all available real detectors from the models directory."""
        self.detectors = {}
        self.model_info = {}
        discovered_names = self._discover_model_names()
        model_names = sorted(set(discovered_names))

        if not discovered_names:
            logger.info("No model directories found in %s", self.models_dir)

        for name in model_names:
            try:
                self.load_model(name)
            except Exception as exc:
                logger.exception("Failed to initialize detector %s: %s", name, exc)
        self._snapshot = self._build_snapshot()

    def refresh_models(self) -> None:
        """Reload the detector configuration if the model files have changed."""
        try:
            current_snapshot = self._build_snapshot()
            if current_snapshot != self._snapshot:
                logger.info("Model directory change detected, reloading detectors.")
                self.load_all_models()
        except Exception as exc:
            logger.exception("Failed to refresh models: %s", exc)

    def _discover_model_names(self) -> List[str]:
        if not self.models_dir.exists():
            return []
        return [child.name for child in self.models_dir.iterdir() if child.is_dir()]

    def _build_snapshot(self) -> Dict[str, Dict[str, int]]:
        snapshot: Dict[str, Dict[str, int]] = {}
        if not self.models_dir.exists():
            return snapshot
        for model_dir in self.models_dir.iterdir():
            if not model_dir.is_dir():
                continue
            snapshot[model_dir.name] = {}
            for filename in ["best.onnx", "best.pt", "labels.txt", "metadata.json"]:
                path = model_dir / filename
                snapshot[model_dir.name][filename] = int(path.stat().st_mtime) if path.exists() else 0
        return snapshot

    def _read_labels(self, folder: Path) -> List[str]:
        labels_path = folder / "labels.txt"
        text = safe_read_text(labels_path)
        if not text:
            return []
        return [line.strip() for line in text.splitlines() if line.strip()]

    def _read_metadata(self, folder: Path) -> Dict[str, Any]:
        metadata_path = folder / "metadata.json"
        if not metadata_path.exists():
            return {}
        try:
            raw = safe_read_text(metadata_path)
            if not raw:
                return {}
            return json.loads(raw)
        except json.JSONDecodeError:
            logger.warning("Invalid metadata for model %s", folder.name)
            return {}

    def _is_real_model(self, folder: Path) -> bool:
        onnx_path = folder / "best.onnx"
        pt_path = folder / "best.pt"
        return any(p.exists() and p.stat().st_size > 0 for p in (onnx_path, pt_path))

    def load_model(self, name: str) -> None:
        """Load a single real model by directory name."""
        folder = self.models_dir / name
        category = normalize_category(name)
        labels: List[str] = []
        metadata: Dict[str, Any] = {}
        if folder.exists() and folder.is_dir():
            labels = self._read_labels(folder)
            metadata = self._read_metadata(folder)
        if folder.exists() and folder.is_dir() and self._is_real_model(folder):
            onnx_path = folder / "best.onnx"
            pt_path = folder / "best.pt"
            model_info = ModelInfo(
                name=name,
                category=category,
                directory=folder,
                labels=labels,
                metadata=metadata,
                onnx_path=onnx_path if onnx_path.exists() and onnx_path.stat().st_size > 0 else None,
                pt_path=pt_path if pt_path.exists() and pt_path.stat().st_size > 0 else None,
            )
            self._initialize_real_detector(model_info)
        else:
            logger.debug("Skipping %s: no real model files found (best.onnx or best.pt).", name)

    def _initialize_real_detector(self, model_info: ModelInfo) -> None:
        if model_info.onnx_path and self.config.model.use_onnx:
            model_info.onnx_session = self._load_onnx_session(model_info.onnx_path)
        if model_info.torch_model is None and model_info.pt_path and self._torch_available and self.config.model.use_torch:
            model_info.torch_model = self._load_torch_model(model_info.pt_path)
        if model_info.onnx_session or model_info.torch_model:
            self.model_info[model_info.name] = model_info
            self.detectors[model_info.name] = model_info
            logger.info("Loaded REAL detector: %s", model_info.name)
            return
        logger.error(
            "Real model directory exists for %s but could not be initialized. The model will remain unavailable.",
            model_info.name,
        )

    def _load_onnx_session(self, path: Path) -> Optional[Any]:
        try:
            import onnxruntime as ort
            return ort.InferenceSession(str(path), providers=["CPUExecutionProvider"])
        except Exception as exc:
            logger.warning("Failed to load ONNX model %s: %s", path, exc)
            return None

    def _load_torch_model(self, path: Path) -> Optional[Any]:
        try:
            import torch
            model = torch.jit.load(str(path)) if path.suffix == ".pt" else torch.load(str(path), map_location="cpu")
            model.eval()
            return model
        except Exception as exc:
            logger.warning("Failed to load PyTorch model %s: %s", path, exc)
            return None

    def _prepare_image(self, image: Any, target_shape: Tuple[int, int]) -> np.ndarray:
        if cv2 is None:
            raise RuntimeError("OpenCV is required for image preprocessing")
        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        resized = cv2.resize(image_rgb, target_shape, interpolation=cv2.INTER_AREA)
        tensor = resized.astype(np.float32) / 255.0
        return np.transpose(tensor, (2, 0, 1))[None, ...]

    def _decode_label(self, label: Any, labels: Optional[List[str]] = None) -> str:
        if labels and isinstance(label, (int, np.integer)) and 0 <= int(label) < len(labels):
            return labels[int(label)]
        if isinstance(label, str):
            return label
        return str(label or "object")

    def _parse_raw_predictions(self, raw: Any, image_shape: Tuple[int, int, int]) -> List[Dict[str, Any]]:
        if raw is None:
            return []
        if isinstance(raw, (list, tuple)) and len(raw) == 1:
            raw = raw[0]
        array = np.asarray(raw)
        if array.ndim == 0:
            return []
        if array.ndim == 3 and array.shape[0] == 1:
            array = array[0]
        if array.ndim == 2 and array.shape[1] >= 5:
            predictions: List[Dict[str, Any]] = []
            for row in array:
                if len(row) < 5:
                    continue
                x1, y1, x2, y2, conf = [float(value) for value in row[:5]]
                predictions.append(
                    {
                        "bbox": {
                            "x1": x1,
                            "y1": y1,
                            "x2": x2,
                            "y2": y2,
                        },
                        "confidence": conf,
                        "label": 0,
                    }
                )
            return predictions
        return []

    def _predict_onnx(self, model_info: ModelInfo, image: Any) -> List[Dict[str, Any]]:
        if model_info.onnx_session is None:
            return []
        try:
            prepared = self._prepare_image(image, (640, 640))
            outputs = model_info.onnx_session.run(None, {model_info.onnx_session.get_inputs()[0].name: prepared})
            return self._parse_raw_predictions(outputs, image.shape[:2])
        except Exception as exc:
            logger.warning("ONNX inference failed for %s: %s", model_info.name, exc)
            return []

    def _predict_torch(self, model_info: ModelInfo, image: Any) -> List[Dict[str, Any]]:
        if model_info.torch_model is None:
            return []
        try:
            import torch

            prepared = self._prepare_image(image, (640, 640))
            with torch.no_grad():
                outputs = model_info.torch_model(torch.from_numpy(prepared))
            return self._parse_raw_predictions(outputs, image.shape[:2])
        except Exception as exc:
            logger.warning("Torch inference failed for %s: %s", model_info.name, exc)
            return []

    def predict(self, name: str, image: Any) -> Dict[str, Any]:
        """Predict with a named detector and return normalized detections."""
        if name not in self.detectors:
            raise KeyError(f"Model {name} is not registered")

        model_info = self.model_info[name]
        if model_info.onnx_session is not None:
            logger.info("Running detector: %s Backend: ONNX", name)
            predictions = self._predict_onnx(model_info, image)
        elif model_info.torch_model is not None:
            logger.info("Running detector: %s Backend: TORCH", name)
            predictions = self._predict_torch(model_info, image)
        else:
            logger.warning("Detector %s has no valid backend and will return no predictions.", name)
            return {"model": name, "detections": []}

        normalized = [self._normalize_prediction(item, model_info) for item in predictions]
        logger.info("Detector %s finished with %d predictions", name, len(normalized))
        return {"model": name, "detections": normalized}

    def predict_all(self, image: Any) -> Dict[str, List[Dict[str, Any]]]:
        """Run prediction on every loaded detector and return categorized results."""
        results: Dict[str, List[Dict[str, Any]]] = {}
        for name in sorted(self.detectors):
            try:
                raw_predictions = self.predict(name, image)
            except Exception as exc:
                logger.exception("Prediction failed for %s: %s", name, exc)
                raw_predictions = {"model": name, "detections": []}
            category = normalize_category(name)
            normalized_predictions: List[Dict[str, Any]] = []
            for item in raw_predictions.get("detections", []):
                bbox = item.get("bbox")
                if bbox:
                    item["bbox"] = normalize_bbox({"x1": bbox[0], "y1": bbox[1], "x2": bbox[2], "y2": bbox[3]}, image.shape)
                item.setdefault("source", category)
                item.setdefault("confidence", 0.0)
                normalized_predictions.append(item)
            results.setdefault(category, []).extend(normalized_predictions)
        for category in [normalize_category(name) for name in self.model_info]:
            results.setdefault(category, [])
        return results

    def _normalize_prediction(self, item: Dict[str, Any], model_info: ModelInfo) -> Dict[str, Any]:
        label = item.get("label")
        item["label"] = self._decode_label(label, model_info.labels)
        item.setdefault("confidence", 0.0)
        item.setdefault("source", model_info.category)
        bbox = item.get("bbox")
        if isinstance(bbox, dict):
            item["bbox"] = [
                float(bbox.get("x1", 0)),
                float(bbox.get("y1", 0)),
                float(bbox.get("x2", 0)),
                float(bbox.get("y2", 0)),
            ]
        elif isinstance(bbox, (list, tuple)) and len(bbox) == 4:
            item["bbox"] = [float(v) for v in bbox]
        return item
