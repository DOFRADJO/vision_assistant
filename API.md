# Vision Assistant - API Reference

## 📡 REST API Endpoints (FastAPI)

### Server Setup

```bash
# Start the API server
uvicorn app.api.main:app --host 0.0.0.0 --port 8000 --reload

# Production (Gunicorn)
gunicorn -w 4 -k uvicorn.workers.UvicornWorker app.api.main:app --bind 0.0.0.0:8000
```

---

## Endpoints

### 1. GET `/`

**Health check / Welcome**

```bash
curl http://localhost:8000/
```

**Response (200):**
```json
{
  "message": "Vision Assistant API",
  "version": "2.0",
  "status": "running"
}
```

---

### 2. GET `/status`

**System status and loaded models**

```bash
curl http://localhost:8000/status
```

**Response (200):**
```json
{
  "service_healthy": true,
  "models_loaded": 1,
  "loaded_detectors": ["people_detector"],
  "memory_usage_mb": 256.5,
  "uptime_seconds": 3600,
  "last_frame_id": 2,
  "timestamp": "2024-06-29T14:30:45.123456"
}
```

---

### 3. GET `/models`

**List all loaded detectors with metadata**

```bash
curl http://localhost:8000/models
```

**Response (200):**
```json
{
  "people_detector": {
    "model_path": "/mnt/dtamboudisk/vision_assistant/models/people_detector/best.onnx",
    "framework": "YOLOv8n",
    "backend": "ONNX",
    "labels": ["person"],
    "num_classes": 1,
    "input_size": [640, 640],
    "output_shape": [1, 5, 8400],
    "confidence_threshold": 0.3,
    "loaded_at": "2024-06-29T14:00:00.000000",
    "inference_time_ms": 42.15
  }
}
```

---

### 4. GET `/config`

**Current configuration**

```bash
curl http://localhost:8000/config
```

**Response (200):**
```json
{
  "model": {
    "confidence_threshold": 0.3,
    "use_onnx": true,
    "use_torch": true,
    "max_workers": 4,
    "refresh_interval_frames": 120
  },
  "memory": {
    "timeout_seconds": 30,
    "max_history": 50
  },
  "speech": {
    "backend": "console",
    "tts_engine": "pyttsx3"
  },
  "reasoning": {
    "danger_rules": "enabled"
  }
}
```

---

### 5. GET `/history`

**Message history (last N messages)**

```bash
curl "http://localhost:8000/history?limit=10"
```

**Response (200):**
```json
{
  "messages": [
    {
      "timestamp": "2024-06-29T14:30:45.123456",
      "message": "Person ahead",
      "category": "people",
      "priority": 2,
      "danger_level": "medium",
      "announced": true
    },
    {
      "timestamp": "2024-06-29T14:30:15.654321",
      "message": "Vehicle detected",
      "category": "vehicles",
      "priority": 1,
      "danger_level": "low",
      "announced": true
    }
  ],
  "total": 2
}
```

---

### 6. POST `/predict`

**Run inference on image**

**Request (multipart/form-data):**
```bash
curl -X POST \
  -F "image=@/path/to/image.jpg" \
  "http://localhost:8000/predict"
```

**Request (base64):**
```bash
# Encode image to base64
base64_image=$(base64 -w 0 < image.jpg)

curl -X POST \
  -H "Content-Type: application/json" \
  -d "{\"image_base64\": \"$base64_image\"}" \
  "http://localhost:8000/predict"
```

**Response (200):**
```json
{
  "detections": {
    "people": [
      {
        "x1": 100,
        "y1": 150,
        "x2": 300,
        "y2": 450,
        "confidence": 0.94,
        "class_name": "person",
        "class_id": 0
      }
    ]
  },
  "inference_time_ms": 42.15,
  "frame_width": 640,
  "frame_height": 480,
  "detectors_run": ["people_detector"],
  "timestamp": "2024-06-29T14:30:45.123456"
}
```

**Error Response (400):**
```json
{
  "error": "Invalid image format or missing field",
  "details": "image field is required"
}
```

---

### 7. POST `/execute`

**Full pipeline: detect → reason → remember → speak**

**Request (JSON):**
```bash
curl -X POST \
  -H "Content-Type: application/json" \
  -d '{
    "image_base64": "iVBORw0KGgoAAAANS...",
    "frame_id": 1,
    "enable_speech": true
  }' \
  "http://localhost:8000/execute"
```

**Response (200):**
```json
{
  "frame_id": 1,
  "models_ran": ["people_detector"],
  "detections": {
    "people": [
      {
        "x1": 100,
        "y1": 150,
        "x2": 300,
        "y2": 450,
        "confidence": 0.94
      }
    ]
  },
  "reasoning": {
    "message": "Person ahead",
    "category": "people",
    "priority": 2,
    "danger_level": "medium"
  },
  "memory": {
    "should_announce": true,
    "message_repeated": false,
    "time_since_last_ms": 30000
  },
  "speech": {
    "announced": true,
    "backend": "console",
    "text": "Person ahead"
  },
  "total_time_ms": 45.67,
  "timestamp": "2024-06-29T14:30:45.123456"
}
```

---

### 8. POST `/speak`

**Speak a message**

**Request (JSON):**
```bash
curl -X POST \
  -H "Content-Type: application/json" \
  -d '{"message": "Obstacle ahead"}' \
  "http://localhost:8000/speak"
```

**Response (200):**
```json
{
  "success": true,
  "message": "Obstacle ahead",
  "backend": "console",
  "timestamp": "2024-06-29T14:30:45.123456"
}
```

---

### 9. GET `/frame`

**Get last processed frame info**

```bash
curl http://localhost:8000/frame
```

**Response (200):**
```json
{
  "frame_id": 2,
  "width": 640,
  "height": 480,
  "detections_count": 1,
  "last_message": "Person ahead",
  "timestamp": "2024-06-29T14:30:45.123456"
}
```

---

## Python Client Example

### Installation

```bash
pip install requests Pillow
```

### Basic Usage

```python
import requests
import json
from pathlib import Path
import base64

class VisionAssistantClient:
    """Client for Vision Assistant API."""
    
    def __init__(self, base_url="http://localhost:8000"):
        self.base_url = base_url
    
    def status(self):
        """Get system status."""
        resp = requests.get(f"{self.base_url}/status")
        return resp.json()
    
    def models(self):
        """Get loaded detectors."""
        resp = requests.get(f"{self.base_url}/models")
        return resp.json()
    
    def predict(self, image_path):
        """Run inference on image."""
        with open(image_path, 'rb') as f:
            files = {'image': f}
            resp = requests.post(f"{self.base_url}/predict", files=files)
        return resp.json()
    
    def execute_full_pipeline(self, image_path, frame_id=1, enable_speech=True):
        """Full pipeline: detect → reason → remember → speak."""
        
        # Read and encode image
        with open(image_path, 'rb') as f:
            image_bytes = f.read()
        image_base64 = base64.b64encode(image_bytes).decode()
        
        # Send request
        payload = {
            "image_base64": image_base64,
            "frame_id": frame_id,
            "enable_speech": enable_speech
        }
        resp = requests.post(
            f"{self.base_url}/execute",
            json=payload
        )
        return resp.json()
    
    def speak(self, message):
        """Speak a message."""
        resp = requests.post(
            f"{self.base_url}/speak",
            json={"message": message}
        )
        return resp.json()
    
    def history(self, limit=10):
        """Get message history."""
        resp = requests.get(
            f"{self.base_url}/history",
            params={"limit": limit}
        )
        return resp.json()

# Usage
if __name__ == "__main__":
    client = VisionAssistantClient()
    
    # Check status
    status = client.status()
    print(f"Service healthy: {status['service_healthy']}")
    print(f"Loaded detectors: {status['loaded_detectors']}")
    
    # Get models
    models = client.models()
    for model_name, model_info in models.items():
        print(f"\n{model_name}:")
        print(f"  Backend: {model_info['backend']}")
        print(f"  Latency: {model_info['inference_time_ms']} ms")
    
    # Run inference
    result = client.predict("test_image.jpg")
    for category, detections in result['detections'].items():
        print(f"\n{category}: {len(detections)} found")
        for det in detections:
            print(f"  Confidence: {det['confidence']:.2f}")
    
    # Full pipeline with speech
    result = client.execute_full_pipeline(
        "test_image.jpg",
        frame_id=1,
        enable_speech=True
    )
    print(f"\nAnnounced: {result['speech']['text']}")
    
    # Get history
    history = client.history(limit=5)
    print("\nRecent announcements:")
    for msg in history['messages']:
        print(f"  {msg['timestamp']}: {msg['message']}")
```

---

## cURL Examples

### Count detections from API

```bash
# Get detections and pretty-print
curl -s http://localhost:8000/status | jq '.models_loaded'

# Loop inference and track frame IDs
for i in {1..10}; do
  curl -s -X POST \
    -F "image=@frame_$i.jpg" \
    http://localhost:8000/predict | jq '.detections'
done
```

### Stream predictions

```bash
# Send frames continuously
while true; do
  curl -X POST \
    -F "image=@camera.jpg" \
    http://localhost:8000/predict \
    | jq '.detections.people | length'
  sleep 0.1
done
```

---

## WebSocket Support (Future)

```python
import asyncio
import websockets
import json

async def stream_frames():
    """Stream predictions over WebSocket."""
    uri = "ws://localhost:8000/ws/predictions"
    
    async with websockets.connect(uri) as websocket:
        # Send frame
        await websocket.send(json.dumps({
            "frame_id": 1,
            "image_base64": "..."
        }))
        
        # Receive prediction
        response = await websocket.recv()
        print(json.loads(response))

# Run
asyncio.run(stream_frames())
```

---

## Error Handling

### Common HTTP Status Codes

| Code | Meaning | Example |
|------|---------|---------|
| 200 | Success | All predictions returned |
| 400 | Bad Request | Image format invalid |
| 422 | Validation Error | Missing required field |
| 500 | Server Error | ONNX session crash |
| 503 | Service Unavailable | No detectors loaded |

### Error Response Format

```json
{
  "error": "Model not found",
  "details": "people_detector folder exists but no best.onnx",
  "code": "MODEL_NOT_FOUND",
  "timestamp": "2024-06-29T14:30:45.123456"
}
```

### Handle Errors in Python

```python
try:
    result = client.predict("image.jpg")
except requests.exceptions.HTTPError as e:
    if e.response.status_code == 400:
        print("Invalid image format")
    elif e.response.status_code == 500:
        print("Server error - detectors may have crashed")
except requests.exceptions.ConnectionError:
    print("API server not running")
```

---

## Rate Limiting

### Headers

```bash
curl -i http://localhost:8000/status

# Headers in response:
# X-RateLimit-Limit: 30
# X-RateLimit-Remaining: 29
# X-RateLimit-Reset: 1719667845
```

### Default Limits

```
- 30 requests per minute per client IP
- 4 concurrent requests maximum
- 100 MB max image size
```

---

## Performance Tips

### 1. Reuse Connections

```python
# Don't create new session for every request
session = requests.Session()

for image in images:
    result = session.post(f"{base_url}/predict", files={"image": open(image, 'rb')})
    print(result.json())
```

### 2. Batch Processing

```bash
# Instead of one request per frame:
# 1. Send frames with --parallel
for image in *.jpg; do
  curl -X POST -F "image=@$image" http://localhost:8000/predict
done

# Better: Use ThreadPoolExecutor
```

### 3. Monitor Latency

```python
import time

start = time.perf_counter()
result = client.predict("image.jpg")
latency = (time.perf_counter() - start) * 1000

print(f"API latency: {latency:.2f} ms")
print(f"Inference latency: {result['inference_time_ms']:.2f} ms")
print(f"Network overhead: {latency - result['inference_time_ms']:.2f} ms")
```

---

## Security

### API Key (Optional)

```bash
# In config.py, add:
# api_key = "your-secret-key-here"

# When calling API:
curl -H "Authorization: Bearer your-secret-key-here" \
  http://localhost:8000/models
```

### HTTPS

```bash
# Use with reverse proxy (nginx, HAProxy)
# or behind load balancer (AWS ALB, etc.)
nginx config:
  server {
    listen 443 ssl;
    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;
    
    location / {
      proxy_pass http://localhost:8000;
    }
  }
```

---

## Monitoring & Logging

### Check Server Logs

```bash
# See API requests
tail -f exports/logs/vision_assistant.log | grep "POST /predict"

# See inference times
tail -f exports/logs/vision_assistant.log | grep "inference_time"

# See errors
tail -f exports/logs/vision_assistant.log | grep "ERROR\|CRITICAL"
```

### Prometheus Metrics (Future)

```bash
# GET /metrics in Prometheus format
curl http://localhost:8000/metrics

# Metrics include:
#   vision_predictions_total
#   vision_inference_seconds
#   vision_api_requests_total
#   vision_api_request_duration_seconds
```

---

**Last Updated:** 29 June 2026  
**Version:** 2.0 (Real Models Only)  
**Status:** ✅ Complete
