"""Integrate a student-trained detector into the platform."""
from __future__ import annotations

import argparse
import shutil
from datetime import datetime
from pathlib import Path
from typing import List

from config import get_config
from core.utils import ensure_directory, serialize_json


def validate_files(model_dir: Path) -> List[str]:
    required = ["best.pt", "best.onnx", "labels.txt", "metadata.json"]
    missing = [name for name in required if not (model_dir / name).exists()]
    return missing


def integrate_model(model_path: Path, destination_dir: Path, report_path: Path) -> dict:
    destination_dir.mkdir(parents=True, exist_ok=True)
    report_path.parent.mkdir(parents=True, exist_ok=True)
    missing = validate_files(model_path)
    if missing:
        raise FileNotFoundError(f"Missing required files: {missing}")
    for file_name in ["best.pt", "best.onnx", "labels.txt", "metadata.json"]:
        shutil.copy2(model_path / file_name, destination_dir / file_name)
    report = {
        "timestamp": datetime.utcnow().isoformat(),
        "model_dir": str(model_path),
        "integrated_to": str(destination_dir),
        "files": ["best.pt", "best.onnx", "labels.txt", "metadata.json"],
    }
    report_path.write_text(serialize_json(report), encoding="utf-8")
    return report


def main() -> None:
    parser = argparse.ArgumentParser(description="Integrate a trained detector model")
    parser.add_argument("--source", required=True, help="Path to the student model directory")
    parser.add_argument("--name", required=True, help="Destination detector name")
    args = parser.parse_args()
    config = get_config()
    source_dir = Path(args.source).resolve()
    destination_dir = (config.paths.models_dir / args.name).resolve()
    report_path = (config.paths.reports_dir / f"integration_{args.name}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.md").resolve()
    report = integrate_model(source_dir, destination_dir, report_path)
    print(serialize_json(report))


if __name__ == "__main__":
    main()
