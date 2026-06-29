# Vision Assistant - Model Format Specification

## 📚 Table of Contents

1. [Overview](#overview)
2. [Directory Structure](#directory-structure)
3. [ONNX Model Format](#onnx-model-format)
4. [PyTorch Model Format](#pytorch-model-format)
5. [Labels File](#labels-file)
6. [Metadata JSON](#metadata-json)
7. [Input Format](#input-format)
8. [Output Format](#output-format)
9. [NMS (Non-Maximum Suppression)](#nms-non-maximum-suppression)
10. [Examples](#examples)

---

## Overview

Vision Assistant expects **YOLOv8 models** exported in ONNX format. These models:

- Input: RGB image (640×640×3)
- Output: Detections in format [1, 5, 8400]
- Classes: Variable (1+ classes per detector)
- Framework: YOLOv8n, YOLOv8s, YOLOv8m, etc.

### Supported Backends

| Format | Size | Speed | Accuracy | Hardware | Recommended |
|--------|------|-------|----------|----------|-------------|
| ONNX | 60 MB | Fast | ✅ | CPU/GPU | ✅ YES |
| PyTorch | 120 MB | Medium | ✅ | CPU/GPU | Fallback only |
| TensorRT | 30 MB | Fastest | ✅ | NVIDIA GPU | Future |
| CoreML | 60 MB | Medium | ✅ | Apple | Future |

---

## Directory Structure

### Valid Model Directories

```
models/
├── people_detector/
│   ├── best.onnx           ← REQUIRED OR best.pt
│   ├── labels.txt          ← REQUIRED
│   └── metadata.json       ← OPTIONAL (recommended)
│
├── vehicle_detector/
│   ├── best.onnx
│   ├── best.pt             ← Fallback if ONNX fails
│   ├── labels.txt
│   └── metadata.json
│
└── traffic_detector/
    ├── best.onnx
    └── labels.txt
```

### Invalid Directories (Skipped)

```
models/
├── old_model_v1/           ← No .onnx or .pt file → SKIPPED ❌
├── incomplete_detector/    ← Missing labels.txt → SKIPPED ❌
└── documentation/          ← Not a model folder → SKIPPED ❌
```

---

## ONNX Model Format

### Export from YOLOv8

```python
from ultralytics import YOLO

# Load trained model
model = YOLO("runs/detect/train/weights/best.pt")

# Export to ONNX
model.export(
    format="onnx",           # Export format
    imgsz=640,              # Input size (640x640)
    half=False,             # FP32 (not FP16)
    opset=12,               # ONNX opset version
    simplify=True           # Simplify model graph
)
# Output: best.onnx
```

### Model Inspection

```bash
# View ONNX model structure
python -c "
import onnx

model = onnx.load('models/people_detector/best.onnx')

# Print input details
print('=== INPUTS ===')
for input in model.graph.input:
    print(f'  Name: {input.name}')
    print(f'  Shape: {input.type.tensor_type.shape.dim}')
    print(f'  Type: {input.type.tensor_type.data_type}')

# Print output details
print('=== OUTPUTS ===')
for output in model.graph.output:
    print(f'  Name: {output.name}')
    print(f'  Shape: {output.type.tensor_type.shape.dim}')
    print(f'  Type: {output.type.tensor_type.data_type}')
"
```

### Expected ONNX Properties

| Property | Value | Notes |
|----------|-------|-------|
| **Input name** | `images` | Standard YOLOv8 |
| **Input shape** | `[1, 3, 640, 640]` | [batch, channels, height, width] |
| **Input dtype** | Float32 | Range: [0.0, 1.0] after normalization |
| **Output name** | `output0` | Standard YOLOv8 |
| **Output shape** | `[1, 5, 8400]` | [batch, features, detections] |
| **Output dtype** | Float32 | Raw logits (before sigmoid) |

### Session Creation

```python
import onnxruntime as rt

onnx_path = "models/people_detector/best.onnx"

# CPU
session = rt.InferenceSession(
    onnx_path,
    providers=['CPUExecutionProvider']
)

# GPU (NVIDIA)
session = rt.InferenceSession(
    onnx_path,
    providers=['CUDAExecutionProvider', 'CPUExecutionProvider']
)

# Get model info
inputs = session.get_inputs()
outputs = session.get_outputs()

print(f"Input: {inputs[0].name}, shape: {inputs[0].shape}")
print(f"Output: {outputs[0].name}, shape: {outputs[0].shape}")
```

---

## PyTorch Model Format

### Export from YOLOv8

```python
from ultralytics import YOLO

model = YOLO("runs/detect/train/weights/best.pt")
# .pt file represents standard PyTorch checkpoint

# Optional: Convert to TorchScript for faster inference
scripted = torch.jit.script(model)
scripted.save("models/people_detector/best.jit")
```

### Loading

```python
import torch
from ultralytics import YOLO

# Load via ultralytics (recommended)
model = YOLO("models/people_detector/best.pt")

# Or direct PyTorch
model = torch.load("models/people_detector/best.pt")
model.eval()
model.to("cuda:0")  # or "cpu"
```

### Inference

```python
import torch
import numpy as np

model = YOLO("models/people_detector/best.pt")

# Input: numpy array (H, W, 3) uint8
frame = np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8)

# Predict
with torch.no_grad():
    results = model(frame, conf=0.3)

# Output: ultralytics Results object
for result in results:
    boxes = result.boxes  # Tensor [N, 6] = [x1, y1, x2, y2, conf, cls]
    
    for box in boxes:
        x1, y1, x2, y2, conf, cls = box.cpu().numpy()
        print(f"Class: {int(cls)}, Confidence: {conf:.2f}")
```

---

## Labels File

### Format: `labels.txt`

One class name per line, ordered by class index (0-indexed):

```
person
bicycle
car
motorcycle
bus
truck
```

### Grammar Rules

- **One label per line**, no extra spaces
- **No blank lines** at end of file
- **Index = line number - 1**
  - Line 1 → class 0 (person)
  - Line 2 → class 1 (bicycle)
  - ...
  - Line 6 → class 5 (truck)

### Verify

```bash
# Count classes
wc -l models/people_detector/labels.txt
# Output: 1 (one class = "person")

wc -l models/vehicle_detector/labels.txt
# Output: 6 (six classes = car, truck, motorcycle, ...)
```

---

## Metadata JSON

### Format: `metadata.json`

```json
{
  "model_name": "people_detector",
  "framework": "YOLOv8n",
  "training_date": "2024-06-15",
  "author": "Your Team Name",
  "description": "Detects people in images using YOLOv8n",
  
  "model_architecture": {
    "backbone": "CSPDarknet",
    "depth_multiple": 0.33,
    "width_multiple": 0.25,
    "max_stride": 32
  },
  
  "input_format": {
    "height": 640,
    "width": 640,
    "channels": 3,
    "color_space": "RGB",
    "normalization": "divide by 255.0",
    "data_type": "float32",
    "range": "[0.0, 1.0]"
  },
  
  "output_format": {
    "type": "detections",
    "tensor_shape": [1, 5, 8400],
    "tensor_format": [
      "batch_size",
      "features (x_center, y_center, width, height, confidence)",
      "grid_detections (80x80 + 40x40 + 20x20 grids, 1 anchor each)"
    ],
    "num_classes": 1,
    "classes": {
      "0": "person"
    },
    "coordinate_format": "xyxy",
    "confidence_threshold": 0.3,
    "nms_threshold": 0.45
  },
  
  "performance": {
    "latency_ms": 42.5,
    "throughput_fps": 23.5,
    "gpu": "NVIDIA RTX 3080"
  },
  
  "training": {
    "dataset": "COCO128",
    "num_classes": 1,
    "num_epochs": 100,
    "batch_size": 16,
    "learning_rate": 0.01,
    "augmentation": "enabled"
  },
  
  "evaluation": {
    "mAP50": 0.72,
    "mAP95": 0.48,
    "precision": 0.85,
    "recall": 0.68
  },
  
  "notes": "Optimized for real-time inference on CPU with minimal false positives"
}
```

### Minimal Required Fields

```json
{
  "model_name": "people_detector",
  "framework": "YOLOv8n",
  "num_classes": 1,
  "classes": { "0": "person" }
}
```

---

## Input Format

### Image Preprocessing

```
Raw frame from camera
    ↓
Shape: (H, W, 3), dtype=uint8, range [0, 255]
    ↓
Resize to [640, 640]
    ↓
Convert to float32
    ↓
Normalize: divide by 255.0 → range [0.0, 1.0]
    ↓
Transpose: (H, W, 3) → (3, H, W)
    ↓
Batch: (3, 640, 640) → (1, 3, 640, 640)
    ↓
ONNX Input: shape [1, 3, 640, 640], dtype float32
```

### Python Code

```python
import cv2
import numpy as np
import onnxruntime as rt

def preprocess(frame, target_size=(640, 640)):
    """Prepare frame for ONNX inference."""
    
    # Resize
    resized = cv2.resize(frame, target_size)  # (640, 640, 3)
    
    # BGR→RGB (if from OpenCV)
    rgb = cv2.cvtColor(resized, cv2.COLOR_BGR2RGB)  # (640, 640, 3)
    
    # uint8→float32
    float_frame = rgb.astype(np.float32)  # (640, 640, 3)
    
    # Normalize [0, 255] → [0.0, 1.0]
    normalized = float_frame / 255.0  # (640, 640, 3)
    
    # Transpose (H, W, C) → (C, H, W)
    transposed = np.transpose(normalized, (2, 0, 1))  # (3, 640, 640)
    
    # Batch: add batch dimension
    batched = np.expand_dims(transposed, 0)  # (1, 3, 640, 640)
    
    return batched

# Usage
frame = cv2.imread("image.jpg")
input_tensor = preprocess(frame)

session = rt.InferenceSession("models/people_detector/best.onnx")
input_name = session.get_inputs()[0].name
output_tensor = session.run(None, {input_name: input_tensor})

print(output_tensor[0].shape)  # [1, 5, 8400]
```

---

## Output Format

### Raw ONNX Output

```
Tensor shape: [1, 5, 8400]
    └─ [1]: batch size (always 1 in inference)
    └─ [5]: [x_center, y_center, width, height, confidence + class_logits]
    └─ [8400]: grid cells
       ├─ 80×80 grid (stride 8) = 6400 cells
       ├─ 40×40 grid (stride 16) = 1600 cells
       └─ 20×20 grid (stride 32) = 400 cells
```

### Post-Processing Steps

```
Raw Output [1, 5, 8400]
    ↓
1. Transpose to [1, 8400, 5]
    ↓
2. Squeeze batch → [8400, 5]
    ↓
3. Extract confidence column [8400]
    ↓
4. Filter by threshold (e.g., 0.3)
    │  → Only keep rows where confidence > 0.3
    │  → [N, 5] where N < 8400
    ↓
5. Convert center+size → xyxy bbox
    │  x_center, y_center, width, height
    │      ↓
    │  x1 = x_center - width/2
    │  y1 = y_center - height/2
    │  x2 = x_center + width/2
    │  y2 = y_center + height/2
    ↓
6. Scale to image coordinates
    │  [0.0, 1.0] → [0, 640]
    ↓
7. Apply NMS (remove overlapping boxes)
    │  IoU threshold: 0.45
    ↓
8. Normalize output
    │  Add class names from labels.txt
    │  Format: {"x1": ..., "y1": ..., "x2": ..., "y2": ..., "confidence": ..., "class_name": "person"}
```

### Python Implementation

```python
import numpy as np
import cv2

def postprocess(raw_output, labels, confidence_threshold=0.3, nms_threshold=0.45):
    """Convert raw ONNX output to detection list."""
    
    # raw_output shape: [1, 5, 8400]
    output = raw_output[0]  # [5, 8400]
    
    # Transpose to [8400, 5]
    output = output.transpose(1, 0)  # [8400, 5]
    
    # Extract predictions
    detections = []
    for pred in output:
        x_center, y_center, width, height, confidence = pred[:5]
        
        # Filter by confidence
        if confidence < confidence_threshold:
            continue
        
        # Convert center+size to xyxy
        x1 = x_center - width / 2
        y1 = y_center - height / 2
        x2 = x_center + width / 2
        y2 = y_center + height / 2
        
        # Scale to image coordinates (640x640)
        x1 = max(0, min(640, x1))
        y1 = max(0, min(640, y1))
        x2 = max(0, min(640, x2))
        y2 = max(0, min(640, y2))
        
        detection = {
            'x1': int(x1),
            'y1': int(y1),
            'x2': int(x2),
            'y2': int(y2),
            'confidence': float(confidence),
            'class_name': labels[0] if labels else 'unknown',
            'class_id': 0
        }
        detections.append(detection)
    
    # Apply NMS
    if detections:
        detections = apply_nms(detections, nms_threshold)
    
    return detections

def apply_nms(detections, iou_threshold=0.45):
    """Remove overlapping bounding boxes."""
    
    if not detections:
        return []
    
    # Sort by confidence descending
    sorted_dets = sorted(detections, key=lambda x: x['confidence'], reverse=True)
    
    keep = []
    while sorted_dets:
        # Keep highest confidence
        current = sorted_dets.pop(0)
        keep.append(current)
        
        # Remove overlapping boxes
        remaining = []
        for det in sorted_dets:
            iou = compute_iou(current, det)
            if iou < iou_threshold:
                remaining.append(det)
        sorted_dets = remaining
    
    return keep

def compute_iou(box1, box2):
    """Intersection over Union."""
    
    x1_min, y1_min, x1_max, y1_max = box1['x1'], box1['y1'], box1['x2'], box1['y2']
    x2_min, y2_min, x2_max, y2_max = box2['x1'], box2['y1'], box2['x2'], box2['y2']
    
    # Intersection
    xi_min = max(x1_min, x2_min)
    yi_min = max(y1_min, y2_min)
    xi_max = min(x1_max, x2_max)
    yi_max = min(y1_max, y2_max)
    
    if xi_max <= xi_min or yi_max <= yi_min:
        return 0.0
    
    intersection = (xi_max - xi_min) * (yi_max - yi_min)
    
    # Union
    area1 = (x1_max - x1_min) * (y1_max - y1_min)
    area2 = (x2_max - x2_min) * (y2_max - y2_min)
    union = area1 + area2 - intersection
    
    return intersection / union if union > 0 else 0.0
```

---

## NMS (Non-Maximum Suppression)

### Why NMS?

YOLO produces multiple bounding boxes for the same object at different grid scales. NMS removes duplicates.

### Algorithm

```
Input: Detections with [x1, y1, x2, y2, confidence]
IoU threshold: 0.45

1. Sort by confidence (highest first)
2. For each detection in sorted order:
   a. Add to final list (keep)
   b. Remove all remaining detections with IoU > threshold
3. Return final list
```

### Example

```
3 detections of same person:
  Box A: confidence=0.94, IoU(A,B)=0.75 > 0.45 → Remove B
  Box B: confidence=0.87, IoU(A,C)=0.52 > 0.45 → Remove C
  Box C: confidence=0.81

Result: Only Box A kept (highest confidence)
```

### Parameters

| Parameter | Value | Notes |
|-----------|-------|-------|
| **NMS threshold** | 0.45 | IoU > 0.45 → box removed |
| **Confidence threshold** | 0.3 | confidence < 0.3 → box removed |

---

## Examples

### Example 1: People Detector

**Input:** Camera frame (480×640×3)

**Model Output (raw):**
```
[1, 5, 8400]
  → [0.52, 0.45, 0.15, 0.25, 0.91, 0.05, 0.02, ...]
     └─ x_ctr=0.52, y_ctr=0.45, w=0.15, h=0.25, conf=0.91
```

**After Post-processing:**
```python
[
  {
    'x1': 332,
    'y1': 224,
    'x2': 428,
    'y2': 416,
    'confidence': 0.91,
    'class_name': 'person',
    'class_id': 0
  }
]
```

### Example 2: Vehicle Detector

**labels.txt:**
```
car
truck
motorcycle
```

**Model Output (raw):**
```
[1, 5, 8400]
Detections at different grid cells:
  - Grid cell 1: car, confidence=0.87
  - Grid cell 2: truck, confidence=0.75
  - Grid cell 3: car, confidence=0.65 (overlaps with cell 1, removed by NMS)
```

**After Post-processing:**
```python
[
  {
    'x1': 50,
    'y1': 100,
    'x2': 300,
    'y2': 450,
    'confidence': 0.87,
    'class_name': 'car',
    'class_id': 0
  },
  {
    'x1': 320,
    'y1': 150,
    'x2': 640,
    'y2': 640,
    'confidence': 0.75,
    'class_name': 'truck',
    'class_id': 1
  }
]
```

---

## Validation Checklist

- [ ] Model exports to ONNX successfully
- [ ] ONNX session loads without errors
- [ ] Input shape is [1, 3, 640, 640]
- [ ] Output shape is [1, 5, 8400]
- [ ] `labels.txt` has correct number of lines
- [ ] Each label is on its own line
- [ ] `metadata.json` is valid JSON
- [ ] ONNX inference latency acceptable (<100ms)
- [ ] NMS removes overlapping boxes correctly
- [ ] Post-processed detections have correct format

---

**Last Updated:** 29 June 2026  
**Version:** 2.0 (Real Models Only)  
**Status:** ✅ Complete
