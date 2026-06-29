#!/usr/bin/env python3
"""Debug the ONNX detector pipeline and save annotated output for inspection."""
from __future__ import annotations
import argparse
import json
import logging
from pathlib import Path

import cv2
from agents.vision.model_loader import ModelLoader
from core.utils import draw_bounding_boxes, ensure_directory, serialize_json


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Debug ONNX object detector predictions.")
    parser.add_argument("--image", required=True, help="Path to an input image file.")
    parser.add_argument(
        "--model",
        default=None,
        help="Detector model directory name to use (e.g. people_detector). If omitted, the first loaded model is used.",
    )
    parser.add_argument(
        "--output-dir",
        default="exports/debug",
        help="Directory where annotated image and JSON results will be saved.",
    )
    parser.add_argument("--verbose", action="store_true", help="Enable debug logging.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    log_level = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(level=log_level, format="%(asctime)s %(levelname)s %(name)s: %(message)s")

    image_path = Path(args.image)
    if not image_path.exists():
        logging.error("Image file does not exist: %s", image_path)
        return 1

    image = cv2.imread(str(image_path))
    if image is None:
        logging.error("Unable to read image: %s", image_path)
        return 1

    loader = ModelLoader()
    loader.load_all_models()
    if not loader.detectors:
        logging.error("No detector models loaded. Check models directory and ONNX files.")
        return 1

    model_name = args.model or next(iter(loader.detectors))
    if model_name not in loader.detectors:
        logging.error("Model %s not found among loaded detectors: %s", model_name, list(loader.detectors.keys()))
        return 1

    logging.info("Using detector %s", model_name)
    predictions = loader.predict(model_name, image)
    logging.info("Found %d predictions", len(predictions))

    output_dir = ensure_directory(Path(args.output_dir))
    output_image_path = output_dir / f"{image_path.stem}_{model_name}_debug.jpg"
    output_json_path = output_dir / f"{image_path.stem}_{model_name}_debug.json"

    if predictions:
        annotated = draw_bounding_boxes(image, predictions)
        cv2.imwrite(str(output_image_path), annotated)
        logging.info("Saved annotated image to %s", output_image_path)
    else:
        logging.info("No detections to draw.")

    output_payload = {
        "image": str(image_path),
        "model": model_name,
        "predictions": predictions,
    }
    output_json = serialize_json(output_payload)
    output_json_path.write_text(output_json, encoding="utf-8")
    logging.info("Saved JSON results to %s", output_json_path)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
