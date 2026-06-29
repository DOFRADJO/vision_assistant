#!/usr/bin/env python3
"""
Template Training Script

This is a reference implementation showing how to train a detector
for the Vision Assistant platform using YOLOv8.

Usage:
    python train.py

The training process should produce:
    - runs/detect/train/weights/best.pt (PyTorch model)
    - runs/detect/train/weights/best.onnx (ONNX model)

Students should customize this script for their specific model
and training strategy.
"""

import logging
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def train_model() -> None:
    """
    Train a YOLOv8 detector model.

    This is a template implementation. Students should:
    1. Prepare their dataset in YOLO format
    2. Update paths and hyperparameters
    3. Configure data.yaml with dataset path
    4. Run training
    """
    try:
        from ultralytics import YOLO

        logger.info("Starting model training...")

        # Initialize YOLOv8 model
        # Use: nano, small, medium, large, or xlarge
        model = YOLO("yolov8m.pt")

        # Dataset should be in YOLO format with dataset/data.yaml
        # See: https://docs.ultralytics.com/datasets/detect/
        dataset_yaml = Path(__file__).parent / "dataset" / "data.yaml"

        if not dataset_yaml.exists():
            raise FileNotFoundError(
                f"Dataset configuration not found: {dataset_yaml}\n"
                f"Create dataset/data.yaml with your dataset configuration."
            )

        # Train the model
        results = model.train(
            data=str(dataset_yaml),
            epochs=100,
            imgsz=640,
            patience=20,
            batch=16,
            device=0,  # GPU device (0=first GPU, or CPU if no GPU)
            project="runs/detect",
            name="train",
            exist_ok=True,
            verbose=True,
            save_json=True,
        )

        logger.info(f"Training complete!")
        logger.info(f"Results: {results}")

        # Best model is automatically saved to:
        # runs/detect/train/weights/best.pt

    except ImportError:
        logger.error(
            "YOLOv8 not installed. Install with:\n"
            "  pip install ultralytics"
        )
        raise
    except FileNotFoundError as e:
        logger.error(f"Training setup error: {e}")
        raise
    except Exception as e:
        logger.error(f"Training failed: {e}")
        raise


if __name__ == "__main__":
    train_model()
