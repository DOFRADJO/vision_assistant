# Vision Assistant - Deployment & Setup Guide

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- pip / virtualenv
- (Optional) NVIDIA GPU + CUDA for GPU inference

### Installation

```bash
# 1. Clone the repository
cd /mnt/dtamboudisk/vision_assistant

# 2. Create virtual environment
python3 -m venv .venv
source .venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Verify models are in place
ls models/people_detector/
# Should show: best.onnx, labels.txt, metadata.json
```

### Run the System

```bash
# Desktop mode (camera + real-time display)
python run.py --mode desktop

# API server mode (headless)
uvicorn app.api.main:app --reload --host 0.0.0.0 --port 8000

# Show available options
python run.py --help
```

---

## 📦 Adding New Models (Real ONNX Only)

### 1. Prepare Your Model

You need a **YOLOv8 trained model** exported to ONNX format:

```bash
# Using YOLOv8 library
from ultralytics import YOLO

# Load your trained PyTorch model
model = YOLO("path/to/your/model.pt")

# Export to ONNX
model.export(format="onnx", half=False, imgsz=640)
# Output: your_model.onnx
```

### 2. Create Model Directory

```bash
mkdir -p models/vehicle_detector
cd models/vehicle_detector
```

### 3. Add Required Files

```bash
# Copy the ONNX model
cp /path/to/your_model.onnx best.onnx

# (Optional) Copy PyTorch model as fallback
cp /path/to/your_model.pt best.pt

# Create labels.txt (one class per line)
cat > labels.txt << 'EOF'
car
truck
motorcycle
bus
EOF

# Create metadata.json (recommended)
cat > metadata.json << 'EOF'
{
  "model_name": "vehicle_detector",
  "framework": "YOLOv8n",
  "input_size": [640, 640],
  "output_format": {
    "type": "detections",
    "num_classes": 4,
    "format": "xyxy",
    "confidence_threshold": 0.3,
    "nms_threshold": 0.45
  },
  "classes": {
    "0": "car",
    "1": "truck",
    "2": "motorcycle",
    "3": "bus"
  },
  "author": "Your Name",
  "date": "2024-06-29",
  "notes": "Trained on COCO dataset subset"
}
EOF
```

### 4. Verify Model

```bash
# Test model loading
python -c "
from agents.vision.model_loader import ModelLoader
ml = ModelLoader()
ml.load_all_models()
print(ml.registry)
"

# Output should show:
# [INFO] Loaded REAL detector: people_detector
# [INFO] Loaded REAL detector: vehicle_detector
```

### 5. Verify Predictions

```bash
python -c "
import cv2
import numpy as np
from agents.vision.model_loader import ModelLoader

ml = ModelLoader()
ml.load_all_models()

# Create test image (480x640x3)
test_frame = np.zeros((480, 640, 3), dtype=np.uint8)
test_frame[:] = (100, 150, 200)  # Light blue

# Run all detectors
results = ml.predict_all(test_frame)

for detector_name, detections in results.items():
    print(f'{detector_name}: {len(detections)} detections')
    for det in detections:
        print(f'  - {det}')
"
```

---

## 🔧 Configuration for Production

### Edit `config.py`

```python
from dataclasses import dataclass

@dataclass(frozen=True)
class ModelConfig:
    """Tune these for your deployment."""
    
    # Confidence threshold: lower = more detections, more false positives
    confidence_threshold: float = 0.3  # Try [0.2, 0.5]
    
    # ONNX vs PyTorch
    use_onnx: bool = True              # Fast, lightweight
    use_torch: bool = False             # Slower, more features
    
    # Parallel inference threads
    max_workers: int = 4                # CPUs: match num_cores
                                        # GPUs: 1-4 workers
    
    # How often to reload models (frames)
    refresh_interval_frames: int = 120  # 120 frames @ 30 FPS = 4s
```

### Environment Variables

```bash
# Use environment to override config.py values
export VISION_ASSISTANT_CONFIDENCE_THRESHOLD=0.4
export VISION_ASSISTANT_USE_ONNX=true

python run.py --mode desktop
```

### For GPU Optimization

```python
# In config.py
model = ModelConfig(
    confidence_threshold=0.25,
    use_onnx=True,              # ONNX is faster
    use_torch=False,
    max_workers=2               # Let GPU handle parallelism
)

# Also check onnxruntime version
pip show onnxruntime
# Should support GPU execution providers
```

---

## 📊 Testing Models

### Unit Test

```bash
# Test single detector
python -c "
from agents.vision.model_loader import ModelLoader
from pathlib import Path
import numpy as np

ml = ModelLoader()
ml.load_model('people_detector')

# Create dummy frame
frame = np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8)

# Predict
detections = ml.predict(frame, 'people_detector')
print(f'Found {len(detections)} people')
for det in detections:
    print(f'  Confidence: {det[\"confidence\"]:.2f}')
"
```

### Integration Test

```bash
# Full pipeline test
python -m pytest tests/integration/test_pipeline.py -v

# Should show:
# test_pipeline_runs_with_real_models PASSED
```

### Benchmark (Optional)

```bash
# Measure inference latency
python scripts/benchmark.py \
  --model people_detector \
  --iterations 100 \
  --batch_size 1
```

---

## 🐳 Docker Deployment (Optional)

### Dockerfile

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    libsm6 libxext6 libxrender-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy project
COPY . /app/

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install onnxruntime

# Expose API port
EXPOSE 8000

# Run API server
CMD ["uvicorn", "app.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Build & Run

```bash
# Build image
docker build -t vision-assistant:latest .

# Run container
docker run -it \
  -p 8000:8000 \
  -v $(pwd)/models:/app/models \
  vision-assistant:latest
```

---

## ☁️ Cloud Deployment

### AWS Lambda

1. Package models with code (size limit 500MB)
2. Use layers for ONNX Runtime
3. Trigger with S3 events or API Gateway

### AWS SageMaker

```python
# Use SageMaker inference endpoint
import sagemaker
predictor = sagemaker.predictor.Predictor("vision-assistant-endpoint")
result = predictor.predict(image_bytes)
```

### Azure Container Instances (ACI)

```bash
# Push to Azure Container Registry
az acr build --registry myregistry -t vision-assistant:latest .

# Deploy
az container create \
  --resource-group mygroup \
  --name vision-assistant \
  --image myregistry.azurecr.io/vision-assistant:latest \
  --ports 8000
```

### Google Cloud Run

```bash
gcloud run deploy vision-assistant \
  --source . \
  --platform managed \
  --region us-central1 \
  --memory 4Gi
```

---

## 🔐 Security Considerations

### 1. Model Validation

```python
# Verify model integrity
import hashlib

def validate_model(onnx_path, expected_sha256=None):
    """Verify model hasn't been tampered with."""
    with open(onnx_path, 'rb') as f:
        file_hash = hashlib.sha256(f.read()).hexdigest()
    
    if expected_sha256 and file_hash != expected_sha256:
        raise ValueError(f"Model hash mismatch: {file_hash}")
    
    return file_hash

# In production, store expected hashes:
KNOWN_MODELS = {
    "people_detector": {
        "sha256": "abc123...",
        "size_mb": 60,
        "framework": "YOLOv8n"
    }
}
```

### 2. Input Validation

```python
# Validate input before processing
def validate_frame(frame, max_dimension=4096):
    import numpy as np
    
    if not isinstance(frame, np.ndarray):
        raise TypeError("Frame must be numpy array")
    
    if frame.dtype != np.uint8:
        raise ValueError("Frame must be uint8")
    
    h, w = frame.shape[:2]
    if h > max_dimension or w > max_dimension:
        raise ValueError(f"Frame too large: {w}x{h}")
    
    return True

# Use in API endpoint:
@app.post("/predict")
async def predict(image_data: bytes):
    frame = cv2.imdecode(np.frombuffer(image_data, np.uint8), cv2.IMREAD_COLOR)
    validate_frame(frame)
    # ... continue
```

### 3. Rate Limiting

```bash
# In config.py or environment
MAX_REQUESTS_PER_MINUTE = 30
MAX_CONCURRENT_REQUESTS = 4

# Use fastapi-limiter
from slowapi import Limiter
limiter = Limiter(key_func=get_remote_address)

@app.post("/predict")
@limiter.limit("30/minute")
async def predict(...):
    pass
```

---

## 🚨 Troubleshooting

### Problem: No Models Loading

```bash
# Check models directory structure
find models/ -type f -name "best.onnx"
# Verify each detector has: best.onnx + labels.txt

# Run diagnostic
python -c "
from agents.vision.model_loader import ModelLoader
import logging
logging.basicConfig(level=logging.DEBUG)
ml = ModelLoader()
ml.load_all_models()
"
# Check logs for errors
```

### Problem: ONNX Runtime Not Found

```bash
# Install ONNX Runtime
pip install onnxruntime

# Verify
python -c "import onnxruntime; print(onnxruntime.__version__)"

# GPU support (CUDA)
pip install onnxruntime-gpu
```

### Problem: Slow Inference

```bash
# Check inference time
python -c "
from agents.vision.model_loader import ModelLoader
import numpy as np
import time

ml = ModelLoader()
ml.load_all_models()

frame = np.zeros((640, 480, 3), dtype=np.uint8)

# Warmup
ml.predict_all(frame)

# Benchmark
start = time.perf_counter()
for _ in range(10):
    ml.predict_all(frame)
elapsed = time.perf_counter() - start

print(f'Avg inference: {elapsed/10*1000:.2f} ms')
"

# If > 100ms:
# - Switch use_torch=False, use_onnx=True
# - Reduce confidence_threshold (less NMS)
# - Use GPU: pip install onnxruntime-gpu
```

### Problem: GPU Not Used

```bash
# Check ONNX providers
python -c "
import onnxruntime as rt
print(rt.get_available_providers())
# Should show: ['CUDAExecutionProvider', 'CPUExecutionProvider']
"

# If only CPU shown, install GPU version:
pip uninstall onnxruntime
pip install onnxruntime-gpu

# Verify CUDA is installed:
nvcc --version
```

---

## 📈 Monitoring & Logging

### Log Rotation

Logs are automatically rotated by size in `exports/logs/`:

```
vision_assistant.log       (current, max 10 MB)
vision_assistant.log.1     (previous rotation)
vision_assistant.log.2
...
```

### Real-time Monitoring

```bash
# Watch logs as they're written
tail -f exports/logs/vision_assistant.log | grep "PERF"

# Count detections by hour
grep "produced.*detections" exports/logs/vision_assistant.log | \
  cut -d' ' -f1 | uniq -c
```

### Metrics Export

```python
# Future: Prometheus metrics
from prometheus_client import Counter, Histogram

detection_count = Counter('vision_detections_total', 'Total detections', ['class'])
inference_time = Histogram('vision_inference_seconds', 'Inference time', ['model'])
```

---

## ✅ Production Checklist

- [ ] All models in `models/` directory
- [ ] Each model has: `best.onnx` + `labels.txt` + `metadata.json`
- [ ] ModelLoader successfully loads all detectors (test with script above)
- [ ] Inference latency tested and acceptable (< 100 ms for your hardware)
- [ ] Confidence thresholds tuned for false positive rate acceptable
- [ ] GPU enabled if using NVIDIA (onnxruntime-gpu installed)
- [ ] API endpoint tested with `curl` or Postman
- [ ] Logs being written to `exports/logs/`
- [ ] Security considerations applied (input validation, rate limiting)
- [ ] Docker image built and tested (if cloud deployment)
- [ ] Monitoring in place (tail, Prometheus, etc.)

---

## 📞 Support

For issues:

1. Check [ARCHITECTURE.md](ARCHITECTURE.md) for system design
2. Check [REAL_MODELS_ONLY.md](REAL_MODELS_ONLY.md) for v2.0 changes
3. Search logs in `exports/logs/vision_assistant.log`
4. Run diagnostic tests in `tests/integration/test_pipeline.py`

---

**Last Updated:** 29 June 2026  
**Version:** 2.0 (Real Models Only)  
**Status:** ✅ Production Ready
