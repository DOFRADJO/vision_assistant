#!/usr/bin/env python3
"""
Template Prediction Script

Test inference with trained model on images.

Usage:
    python predict.py image.jpg
    python predict.py --image path/to/image.jpg
    python predict.py --video path/to/video.mp4

This script demonstrates how to use your trained model
for inference during development and testing.
"""

import argparse
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def predict_image(image_path: str, model_path: str = None) -> None:
    """
    Run inference on a single image.

    Args:
        image_path: Path to image file
        model_path: Path to model file (default: best.pt)
    """
    try:
        from ultralytics import YOLO
        import cv2

        if model_path is None:
            model_path = Path(__file__).parent / "best.pt"
        else:
            model_path = Path(model_path)

        if not model_path.exists():
            raise FileNotFoundError(f"Model not found: {model_path}")

        image_path = Path(image_path)
        if not image_path.exists():
            raise FileNotFoundError(f"Image not found: {image_path}")

        logger.info(f"Loading model: {model_path}")
        model = YOLO(str(model_path))

        logger.info(f"Running inference on: {image_path}")
        results = model.predict(str(image_path), conf=0.3)

        for result in results:
            logger.info(f"Detections: {len(result.boxes)}")
            for box in result.boxes:
                cls = int(box.cls[0])
                conf = float(box.conf[0])
                coords = box.xyxy[0].cpu().numpy()
                x1, y1, x2, y2 = coords
                label = model.names[cls]
                logger.info(f"  {label}: conf={conf:.3f} bbox=[{x1:.0f},{y1:.0f},{x2:.0f},{y2:.0f}]")

    except ImportError:
        logger.error("YOLOv8 not installed: pip install ultralytics")
        raise
    except Exception as e:
        logger.error(f"Prediction failed: {e}")
        raise


def predict_video(video_path: str, model_path: str = None) -> None:
    """
    Run inference on video file.

    Args:
        video_path: Path to video file
        model_path: Path to model file (default: best.pt)
    """
    try:
        from ultralytics import YOLO

        if model_path is None:
            model_path = Path(__file__).parent / "best.pt"
        else:
            model_path = Path(model_path)

        if not model_path.exists():
            raise FileNotFoundError(f"Model not found: {model_path}")

        video_path = Path(video_path)
        if not video_path.exists():
            raise FileNotFoundError(f"Video not found: {video_path}")

        logger.info(f"Loading model: {model_path}")
        model = YOLO(str(model_path))

        logger.info(f"Running inference on: {video_path}")
        logger.info(f"Processing video (this may take a while)...")

        results = model.predict(str(video_path), conf=0.3, save=True)

        logger.info(f"✅ Video processing complete!")
        logger.info(f"Results saved to: runs/detect/predict/")

    except ImportError:
        logger.error("YOLOv8 not installed: pip install ultralytics")
        raise
    except Exception as e:
        logger.error(f"Video prediction failed: {e}")
        raise


def main() -> None:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Predict with trained detector model",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python predict.py image.jpg
  python predict.py --image test.png
  python predict.py --video video.mp4
  python predict.py --image test.jpg --model best.pt
        """,
    )

    parser.add_argument(
        "input",
        nargs="?",
        default=None,
        help="Image or video file to predict on",
    )
    parser.add_argument(
        "--image",
        type=str,
        default=None,
        help="Image file path",
    )
    parser.add_argument(
        "--video",
        type=str,
        default=None,
        help="Video file path",
    )
    parser.add_argument(
        "--model",
        type=str,
        default=None,
        help="Model file path (default: best.pt)",
    )

    args = parser.parse_args()

    # Determine input file
    if args.image:
        predict_image(args.image, args.model)
    elif args.video:
        predict_video(args.video, args.model)
    elif args.input:
        # Auto-detect based on extension
        if args.input.lower().endswith((".mp4", ".avi", ".mov")):
            predict_video(args.input, args.model)
        else:
            predict_image(args.input, args.model)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
