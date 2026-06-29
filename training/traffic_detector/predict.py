import json
import sys
from pathlib import Path

import numpy as np
import onnxruntime as ort
from PIL import Image

MODEL_NAME = "crosswalk_traffic_light_detector"
ONNX_PATH = "best.onnx"
LABELS_PATH = "labels.txt"

IMG_SIZE = 640
CONFIDENCE_THRESHOLD = 0.40
IOU_THRESHOLD = 0.45


def load_labels() -> list[str]:
    return Path(LABELS_PATH).read_text().strip().splitlines()


def preprocess(image: Image.Image):
    """Letterbox resize + normalisation [0,1] + NCHW. Retourne (tensor, scale, pad)."""
    original_w, original_h = image.size
    scale = min(IMG_SIZE / original_w, IMG_SIZE / original_h)
    new_w, new_h = int(original_w * scale), int(original_h * scale)

    resized = image.convert("RGB").resize((new_w, new_h))
    canvas = Image.new("RGB", (IMG_SIZE, IMG_SIZE), (114, 114, 114))
    pad_x = (IMG_SIZE - new_w) // 2
    pad_y = (IMG_SIZE - new_h) // 2
    canvas.paste(resized, (pad_x, pad_y))

    array = np.array(canvas).astype(np.float32) / 255.0
    array = array.transpose(2, 0, 1)[np.newaxis, ...]  # HWC -> NCHW

    return array, scale, (pad_x, pad_y)


def nms(boxes: np.ndarray, scores: np.ndarray, iou_threshold: float) -> list[int]:
    x1, y1, x2, y2 = boxes[:, 0], boxes[:, 1], boxes[:, 2], boxes[:, 3]
    areas = (x2 - x1) * (y2 - y1)
    order = scores.argsort()[::-1]

    keep = []
    while order.size > 0:
        i = order[0]
        keep.append(int(i))

        xx1 = np.maximum(x1[i], x1[order[1:]])
        yy1 = np.maximum(y1[i], y1[order[1:]])
        xx2 = np.minimum(x2[i], x2[order[1:]])
        yy2 = np.minimum(y2[i], y2[order[1:]])

        w = np.maximum(0.0, xx2 - xx1)
        h = np.maximum(0.0, yy2 - yy1)
        intersection = w * h
        iou = intersection / (areas[i] + areas[order[1:]] - intersection + 1e-9)

        order = order[1:][iou <= iou_threshold]

    return keep


def postprocess(raw_output: np.ndarray, scale: float, pad, labels: list[str]) -> list[dict]:
    """Décode la sortie YOLOv8 ONNX (1, 4+num_classes, n_boxes) -> liste de détections."""
    predictions = np.squeeze(raw_output).T  # -> (n_boxes, 4 + num_classes)

    boxes_xywh = predictions[:, :4]
    class_scores = predictions[:, 4:]
    class_ids = np.argmax(class_scores, axis=1)
    confidences = np.max(class_scores, axis=1)

    keep = confidences >= CONFIDENCE_THRESHOLD
    boxes_xywh, class_ids, confidences = boxes_xywh[keep], class_ids[keep], confidences[keep]

    if len(boxes_xywh) == 0:
        return []

    boxes_xyxy = np.zeros_like(boxes_xywh)
    boxes_xyxy[:, 0] = boxes_xywh[:, 0] - boxes_xywh[:, 2] / 2
    boxes_xyxy[:, 1] = boxes_xywh[:, 1] - boxes_xywh[:, 3] / 2
    boxes_xyxy[:, 2] = boxes_xywh[:, 0] + boxes_xywh[:, 2] / 2
    boxes_xyxy[:, 3] = boxes_xywh[:, 1] + boxes_xywh[:, 3] / 2

    keep_idx = nms(boxes_xyxy, confidences, IOU_THRESHOLD)

    pad_x, pad_y = pad
    detections = []
    for i in keep_idx:
        x1, y1, x2, y2 = boxes_xyxy[i]
        x1 = (x1 - pad_x) / scale
        y1 = (y1 - pad_y) / scale
        x2 = (x2 - pad_x) / scale
        y2 = (y2 - pad_y) / scale

        class_id = int(class_ids[i])
        label = labels[class_id] if class_id < len(labels) else f"unknown_{class_id}"

        detections.append(
            {
                "label": label,
                "confidence": round(float(confidences[i]), 4),
                "bbox": [round(float(v), 1) for v in (x1, y1, x2, y2)],
            }
        )

    return detections


def predict(image_path: str) -> dict:
    labels = load_labels()
    session = ort.InferenceSession(ONNX_PATH, providers=["CPUExecutionProvider"])
    input_name = session.get_inputs()[0].name

    image = Image.open(image_path)
    tensor, scale, pad = preprocess(image)

    raw_output = session.run(None, {input_name: tensor})[0]
    detections = postprocess(raw_output, scale, pad, labels)

    return {
        "model": MODEL_NAME,
        "detections": detections,
    }


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage : python predict.py chemin/vers/image.jpg")
        sys.exit(1)

    result = predict(sys.argv[1])
    print(json.dumps(result, indent=2, ensure_ascii=False))