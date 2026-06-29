import json
from datetime import datetime, timezone
from pathlib import Path

import yaml
from ultralytics import YOLO

MODEL_NAME = "crosswalk_traffic_light_detector"

BEST_PT = "best.pt"
DATASET_YAML = "data.yaml"

IMG_SIZE = 640
ONNX_OPSET = 12
CONFIDENCE_THRESHOLD = 0.40
IOU_THRESHOLD = 0.45


def load_class_names() -> list[str]:
    with open(DATASET_YAML, "r") as f:
        data = yaml.safe_load(f)
    names = data["names"]
    if isinstance(names, dict):
        names = [names[i] for i in sorted(names)]
    return names


def export_onnx() -> Path:
    model = YOLO(BEST_PT)
    exported_path = model.export(
        format="onnx",
        imgsz=IMG_SIZE,
        opset=ONNX_OPSET,
        dynamic=False,
        simplify=True,
    )
    exported_path = Path(exported_path)

    dest = Path("best.onnx")
    if exported_path.resolve() != dest.resolve():
        exported_path.replace(dest)

    return dest


def write_labels_txt(class_names: list[str]) -> Path:
    path = Path("labels.txt")
    path.write_text("\n".join(class_names) + "\n")
    return path


def write_metadata_json(class_names: list[str]) -> Path:
    metadata = {
        "model": MODEL_NAME,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "task": "object_detection",
        "architecture": "YOLOv8n",
        "input": {
            "image_size": IMG_SIZE,
            "format": "RGB",
        },
        "classes": class_names,
        "thresholds": {
            "confidence": CONFIDENCE_THRESHOLD,
            "iou_nms": IOU_THRESHOLD,
        },
        "output_contract": {
            "description": (
                "Respecte le contrat d'interface commun du projet : "
                "{'model': str, 'detections': [{'label': str, 'confidence': float, "
                "'bbox': [x1, y1, x2, y2]}]}"
            ),
            "example": {
                "model": MODEL_NAME,
                "detections": [
                    {
                        "label": "pedestrian_signal_red",
                        "confidence": 0.91,
                        "bbox": [120, 85, 230, 470],
                    }
                ],
            },
        },
        "author_module_path": f"training/{MODEL_NAME}/",
    }

    path = Path("metadata.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2, ensure_ascii=False)

    return path


def main():
    if not Path(BEST_PT).exists():
        raise FileNotFoundError(
            f"{BEST_PT} introuvable. Lance d'abord : python train.py"
        )

    class_names = load_class_names()

    onnx_path = export_onnx()
    labels_path = write_labels_txt(class_names)
    metadata_path = write_metadata_json(class_names)

    print("Livrables générés :")
    print(f"  - {BEST_PT}")
    print(f"  - {onnx_path}")
    print(f"  - {labels_path}")
    print(f"  - {metadata_path}")


if __name__ == "__main__":
    main()