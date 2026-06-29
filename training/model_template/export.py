#!/usr/bin/env python3
"""
Template Export Script

Export trained model to PyTorch and ONNX formats for integration
into the Vision Assistant platform.

Usage:
    python export.py

Output:
    - best.pt (PyTorch model - copied to current directory)
    - best.onnx (ONNX model - created by export)

This script should be run after training completes.
"""

import logging
import shutil
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def export_models() -> None:
    """
    Export trained model to PyTorch and ONNX formats.

    For YOLOv8:
    1. Load best.pt from training runs
    2. Export to ONNX format
    3. Copy both to current directory for integration

    For other frameworks:
    1. Load trained model
    2. Export to ONNX using framework tools
    3. Ensure both PyTorch and ONNX versions are valid
    """
    try:
        from ultralytics import YOLO

        current_dir = Path(__file__).parent
        logger.info(f"Working directory: {current_dir}")

        # Path to trained model from training
        best_pt_path = current_dir / "runs" / "detect" / "train" / "weights" / "best.pt"

        if not best_pt_path.exists():
            raise FileNotFoundError(
                f"Trained model not found: {best_pt_path}\n"
                f"Run training first:\n  python train.py"
            )

        logger.info(f"Loading trained model: {best_pt_path}")
        model = YOLO(str(best_pt_path))

        # Export to ONNX
        logger.info("Exporting to ONNX format...")
        export_results = model.export(
            format="onnx",
            imgsz=640,
            opset=12,
            device=0,
        )
        logger.info(f"ONNX export complete: {export_results}")

        # ONNX file is created in runs directory
        runs_onnx = current_dir / "runs" / "detect" / "train" / "weights" / "best.onnx"

        # Check if ONNX export was successful
        # Sometimes ONNX is saved with a different name, handle that
        weights_dir = current_dir / "runs" / "detect" / "train" / "weights"
        onnx_files = list(weights_dir.glob("*.onnx"))

        if not onnx_files:
            # Try alternative export method
            logger.info("Standard export not found, trying alternative export...")
            import torch
            model.model.cpu()
            dummy_input = torch.randn(1, 3, 640, 640)
            torch.onnx.export(
                model.model,
                dummy_input,
                str(runs_onnx),
                input_names=["images"],
                output_names=["output"],
                opset_version=12,
            )
            onnx_files = [runs_onnx]

        best_onnx_src = onnx_files[0]

        # Copy models to current directory
        logger.info(f"Copying export files to {current_dir}...")

        # Copy PyTorch model
        dst_pt = current_dir / "best.pt"
        shutil.copy2(best_pt_path, dst_pt)
        logger.info(f"Copied: {best_pt_path} -> {dst_pt}")

        # Copy ONNX model
        dst_onnx = current_dir / "best.onnx"
        shutil.copy2(best_onnx_src, dst_onnx)
        logger.info(f"Copied: {best_onnx_src} -> {dst_onnx}")

        # Verify files
        if dst_pt.exists() and dst_onnx.exists():
            pt_size = dst_pt.stat().st_size / (1024 * 1024)  # MB
            onnx_size = dst_onnx.stat().st_size / (1024 * 1024)  # MB

            logger.info(f"\n✅ Export successful!")
            logger.info(f"   best.pt:   {pt_size:.2f} MB")
            logger.info(f"   best.onnx: {onnx_size:.2f} MB")
            logger.info(f"\nNext steps:")
            logger.info(f"  1. Verify labels.txt has your class names")
            logger.info(f"  2. Verify metadata.json has correct settings")
            logger.info(f"  3. Run validation: python scripts/integrate_model.py [model_name] --validate")
            logger.info(f"  4. Run integration: python scripts/integrate_model.py [model_name]")
        else:
            raise RuntimeError("Export files were not created correctly")

    except ImportError as e:
        logger.error(f"Required package not installed: {e}")
        logger.info("Install YOLOv8: pip install ultralytics")
        raise
    except Exception as e:
        logger.error(f"Export failed: {e}")
        raise


if __name__ == "__main__":
    export_models()
