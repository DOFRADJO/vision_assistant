# Vision Assistant - Architecture (Real Models Only)

## 📋 Table of Contents

1. [System Overview](#system-overview)
2. [Component Hierarchy](#component-hierarchy)
3. [Data Flow](#data-flow)
4. [Model Loading & Inference](#model-loading--inference)
5. [Agent Communication](#agent-communication)
6. [Configuration](#configuration)
7. [Logging & Diagnostics](#logging--diagnostics)

---

## System Overview

**Vision Assistant** is a modular, multi-agent system for vision-based assistance. It captures video frames, runs multiple object detectors in parallel, reasons about the detections, maintains memory of past events, and produces voice output.

### Key Principles

1. **Real Models Only**: No fake detectors or fallbacks. Pure production-grade inference.
2. **Multi-Detector**: Runs multiple YOLO-based detectors in parallel (people, vehicles, traffic, etc.)
3. **Agent-Based**: Decoupled components communicate via structured messages
4. **Backend Agnostic**: Supports ONNX Runtime (CPU/GPU) and PyTorch
5. **Extensible**: Easy to add new detectors or reasoning rules

### Design Philosophy

```
┌─────────────────────────────────────────────────────┐
│  Vision Assistant = Detective Squad                 │
├─────────────────────────────────────────────────────┤
│ Coordinator (Detective Chief) orchestrates          │
│   ├─ VisionAgent (Lookout) - spots objects         │
│   ├─ ReasoningAgent (Analyst) - interprets events  │
│   ├─ MemoryAgent (Scribe) - avoids repetition      │
│   └─ SpeechAgent (Messenger) - communicates        │
│                                                     │
│ All decisions are collaborative, logged, and clear.│
└─────────────────────────────────────────────────────┘
```

---

## Component Hierarchy

### Layer 1: Configuration & Bootstrapping

```
config.py
    ├── PathConfig: Filesystem paths (models/, logs/, datasets/)
    ├── CameraConfig: Camera source, resolution, FPS
    ├── ModelConfig: ONNX/PyTorch backend toggle, confidence threshold
    ├── ReasoningConfig: Priority rules, danger thresholds
    ├── MemoryConfig: Message deduplication timeout
    ├── SpeechConfig: Backend (console/desktop), TTS settings
    └── AppConfig: Integrates all above
```

### Layer 2: Core Infrastructure

```
agents/coordinator/coordinator.py
    ├── Registry: Maintains list of loaded models and agents
    ├── Coordinator.execute(): Main pipeline
    │   ├─ Takes frame + frame_id
    │   ├─ Distributes to agents
    │   ├─ Collects results
    │   └─ Returns JSON response
    └── Coordinator.status(): System health check

agents/coordinator/registry.py
    └── Tracks loaded detectors and their metadata
```

### Layer 3: Vision Processing

```
agents/vision/model_loader.py
    ├── ModelInfo: Container for loaded detector metadata
    ├── ModelLoader.load_all_models(): Discovers & loads all detectors
    ├── ModelLoader.load_model(detector_name): Loads single detector
    ├── ModelLoader.predict(frame, detector_name): Runs inference
    ├── ModelLoader.predict_all(frame): Runs all detectors in parallel
    ├── normalize_category(): Standardizes class names (person → people)
    └── ONNX parsing: Handles tensor->detection conversion

agents/vision/vision_agent.py
    ├── VisionAgent.predict(frame): Orchestrates all detectors
    ├── Parallel execution with ThreadPoolExecutor
    └── Returns: {"people": [...detections], "vehicles": [...], ...}
```

### Layer 4: Reasoning & Decision Making

```
agents/reasoning/reasoning_agent.py
    ├── ReasoningAgent.analyze(predictions): Turns detections into events
    ├── apply_danger_rules(): Categorizes threat level
    ├── apply_priority_rules(): Sets urgency
    └── Returns: {"message": "...", "priority": 1, "danger_level": "high"}

agents/reasoning/danger_rules.py
    ├── DANGER_RULES: Defines what's dangerous
    │   ├── "People ahead" → danger_level=medium
    │   ├── "Traffic light red" → danger_level=high
    │   └── "Obstacle ahead" → danger_level=critical
    └── apply_danger_rules(category, prediction): Lookup & return level

agents/reasoning/priority_manager.py
    ├── PRIORITY_MATRIX: Maps (category, danger) → priority (1-5)
    └── get_priority(category, danger_level): Returns 1=low...5=critical
```

### Layer 5: Memory & Deduplication

```
agents/memory/memory_agent.py
    ├── MemoryAgent.filter_message(current_msg): Dedup logic
    ├── history: List of recent messages with timestamps
    ├── Remember message only if:
    │   ├─ New message (never seen before), OR
    │   ├─ Old message (timeout_seconds since last announcement)
    └── Returns: bool (should_announce)

agents/memory/history.py
    ├── MessageRecord: {text, timestamp, category}
    └── History: List of MessageRecord
```

### Layer 6: Speech Output

```
agents/speech/speech_agent.py
    ├── SpeechAgent.speak(message): Outputs detected content
    ├── Backend selection:
    │   ├── "console" → Print to stdout (headless)
    │   ├── "desktop" → TTS library (pyttsx3)
    │   └── "android" → Android text-to-speech (future)
    └── Returns: bool (success)

agents/speech/tts.py
    ├── TTSBackend (abstract base)
    ├── ConsoleBackend: print() implementation
    ├── DesktopBackend: pyttsx3 implementation
    └── factory_tts(): Create appropriate backend
```

### Layer 7: Application Layer

```
app/desktop/desktop_app.py
    ├── Opens webcam
    ├── Frame capture loop
    ├── Calls Coordinator.execute(frame, frame_id)
    ├── Draws bounding boxes with OpenCV
    └── Displays priority text on screen

app/api/main.py
    ├── FastAPI server
    ├── GET /status: Model listing
    ├── GET /models: Detector details
    ├── POST /predict: Image → detections
    ├── GET /history: Previous messages
    └── GET /config: Current settings
```

---

## Data Flow

### 1. Startup Flow

```
run.py
  ↓
load config.py (ALL settings loaded)
  ↓
ModelLoader.__init__()
  ├─ Read models/ directory
  ├─ For each folder with best.onnx/best.pt:
  │  ├─ Read labels.txt
  │  ├─ Parse metadata.json
  │  └─ Preload session (ONNX/PyTorch)
  └─ Register in Registry
  ↓
Create agents
  ├─ VisionAgent
  ├─ ReasoningAgent
  ├─ MemoryAgent
  ├─ SpeechAgent
  └─ Coordinator (ties all together)
  ↓
Ready for inference
```

### 2. Frame Processing Pipeline

```
┌─────────────────────────────────────────────────────────────┐
│                    Coordinator.execute()                    │
│                   (input: frame, frame_id)                  │
└─────────────────────────────────────────────────────────────┘
         ↓
         │ (frame passes to VisionAgent)
         ↓
┌─────────────────────────────────────────────────────────────┐
│              VisionAgent.predict(frame)                     │
├─────────────────────────────────────────────────────────────┤
│ ThreadPoolExecutor.map( detector.predict, [...models] )    │
│                                                             │
│ Parallel:                                                   │
│   people_detector.predict(frame)                           │
│   vehicle_detector.predict(frame)                          │
│   traffic_detector.predict(frame)                          │
│   ...                                                      │
└─────────────────────────────────────────────────────────────┘
         ↓
         │ Result: {"people": [...], "vehicles": [...], ...}
         ↓
┌─────────────────────────────────────────────────────────────┐
│           ReasoningAgent.analyze(predictions)              │
├─────────────────────────────────────────────────────────────┤
│ For each detected category:                                │
│   ├─ Check danger_rules.py for threat level               │
│   ├─ Get priority from priority_manager.py                │
│   └─ Generate human-readable message                       │
│                                                             │
│ Output example: "Person ahead; priority=2; danger=medium" │
└─────────────────────────────────────────────────────────────┘
         ↓
         │ (message → MemoryAgent)
         ↓
┌─────────────────────────────────────────────────────────────┐
│          MemoryAgent.filter_message(message)               │
├─────────────────────────────────────────────────────────────┤
│ Should announce?                                           │
│   IF (message is new OR timeout_seconds passed)           │
│       THEN should_announce = True                         │
│       ELSE should_announce = False                        │
│                                                             │
│ Output: bool (should_announce)                            │
└─────────────────────────────────────────────────────────────┘
         ↓
         │ if should_announce:
         ↓
┌─────────────────────────────────────────────────────────────┐
│              SpeechAgent.speak(message)                    │
├─────────────────────────────────────────────────────────────┤
│ Backend selection:                                         │
│   IF backend == "console":                                │
│       print(message)                                       │
│   ELIF backend == "desktop":                              │
│       use pyttsx3.Engine.say(message)                     │
│                                                             │
│ Returns: True (success)                                   │
└─────────────────────────────────────────────────────────────┘
         ↓
    Return to caller
    {
      "frame_id": 2,
      "models_ran": ["people_detector", "vehicle_detector"],
      "detections": {...},
      "message": "Person ahead",
      "priority": 2,
      "announced": true
    }
```

---

## Model Loading & Inference

### 3a. Model Discovery

```python
# models/
#   people_detector/
#     ├─ best.onnx        ✅ Loaded
#     ├─ best.pt          (Fallback if ONNX fails)
#     ├─ labels.txt       ✅ Read
#     └─ metadata.json    ✅ Parsed
#   vehicle_detector/
#     ├─ best.onnx
#     ├─ labels.txt
#     └─ metadata.json
```

**Code Path:**
```python
ModelLoader.load_all_models()
    for folder in models/ directory:
        if "best.onnx" OR "best.pt" exists:
            load_model(folder)
        else:
            skip with debug log
```

### 3b. ONNX Model Inference

```
Input: np.ndarray, shape (H, W, 3), dtype=uint8, range [0, 255]
    ↓
Preprocessing:
    ├─ Resize to [640, 640] (model input size)
    ├─ Convert BGR→RGB if needed
    ├─ Normalize: (img / 255.0).astype(float32)
    ├─ Transpose to [3, 640, 640]
    └─ Reshape to [1, 3, 640, 640] (batch)
    ↓
ONNX Session.run():
    Input: onnx_input = [[1, 3, 640, 640]] tensor
    Output: onnx_output = [[1, 5, 8400]] tensor
            └─ 1: batch size
            └─ 5: [x_center, y_center, width, height, confidence]
            └─ 8400: 80×80 + 40×40 + 20×20 grid cells × 1 anchor
    ↓
Parsing (in _parse_raw_predictions()):
    ├─ Transpose [1, 5, 8400] → [1, 8400, 5]
    ├─ Reshape → [8400, 5]
    ├─ Filter by confidence_threshold (0.3)
    ├─ Convert center+size → xyxy bounding box
    ├─ Sort by confidence (descending)
    └─ Apply NMS if available
    ↓
Normalization:
    ├─ Convert bbox values to image coordinates
    ├─ Add class_id and class_name
    └─ Return: [{x1, y1, x2, y2, confidence, class_name}, ...]
    ↓
Output: List[Detection]
```

### 3c. Label Mapping

```
labels.txt (one label per line):
    0  person
    1  bicycle
    2  car
    ...

metadata.json (optional):
    {
      "model_name": "people_detector",
      "framework": "YOLOv8n",
      "input_size": [640, 640],
      "output_format": "xyxy",
      "confidence_threshold": 0.3,
      "classes": {
        "0": "person",
        "1": "bicycle"
      }
    }
```

**Class Name Normalization:**
```python
normalize_category("person") → "people"
normalize_category("car") → "vehicles"
normalize_category("traffic light") → "traffic"
```

---

## Agent Communication

### 4a. Message Protocol

All agents communicate via structured JSON/dict:

**Vision Output:**
```python
{
    "people": [
        {"x1": 100, "y1": 150, "x2": 300, "y2": 450, "confidence": 0.94},
        {"x1": 50,  "y1": 200, "x2": 150, "y2": 350, "confidence": 0.87}
    ],
    "vehicles": [
        {"x1": 0,   "y1": 0,   "x2": 640, "y2": 480, "confidence": 0.92}
    ]
}
```

**Reasoning Output:**
```python
{
    "message": "Person ahead",
    "category": "people",
    "priority": 2,
    "danger_level": "medium",
    "confidence": 0.94
}
```

**Memory Output:**
```python
should_announce = True  # or False if duplicate within timeout
```

**Speech Output:**
```python
success = True  # or False if audio backend failed
```

### 4b. Thread Safety

```
Coordinator.execute(frame, frame_id)
    ├─ ThreadPoolExecutor
    │  ├─ Thread 1: people_detector.predict(frame)
    │  ├─ Thread 2: vehicle_detector.predict(frame)
    │  └─ Thread 3: traffic_detector.predict(frame)
    │  All return their results concurrently
    │
    ├─ Collect results (blocking wait)
    └─ Pass to next agent (sequential)
```

**No race conditions because:**
- Frame is read-only (detectors don't modify input)
- ONNX sessions are thread-safe (separate per detector)
- Results are merged in main thread

---

## Configuration

### 5a. Hierarchy

```
config.py (file)
    ↓
AppConfig dataclass
    ├─ path: PathConfig
    │   ├─ models_dir = "./models"
    │   ├─ logs_dir = "./exports/logs"
    │   └─ datasets_dir = "./datasets"
    │
    ├─ camera: CameraConfig
    │   ├─ source = 0  (webcam)
    │   ├─ width = 1280
    │   ├─ height = 720
    │   └─ fps = 30
    │
    ├─ model: ModelConfig (REAL MODELS ONLY)
    │   ├─ confidence_threshold = 0.3
    │   ├─ use_onnx = True
    │   ├─ use_torch = True
    │   ├─ max_workers = 4
    │   └─ refresh_interval_frames = 120
    │
    ├─ reasoning: ReasoningConfig
    │   └─ (rules defined in danger_rules.py)
    │
    ├─ memory: MemoryConfig
    │   ├─ timeout_seconds = 30
    │   └─ max_history = 50
    │
    └─ speech: SpeechConfig
        ├─ backend = "console"  (or "desktop", "android")
        └─ tts_engine = "pyttsx3"
```

### 5b. Loading Priority

```
1. Default values in dataclass definitions
   ↓ (can be overridden by)
2. Environment variables (prefix: VISION_ASSISTANT_)
   ↓ (can be overridden by)
3. .env file
   ↓ (can be overridden by)
4. Programmatic config.py edits
```

### 5c. No Fake Detector Flags

**Removed from v2.0:**
- ❌ `enable_fake_detectors: bool = False`
- ❌ `real_models_only: bool = True`

**Why:** Now all detectors are real by design. No configuration choice needed.

---

## Logging & Diagnostics

### 6a. Log Levels

```
DEBUG
    - Frame capture details
    - Model loading debug
    - Tensor shape/dtype info
    ├─> Log file: exports/logs/vision_assistant.log

INFO
    - Detector loaded
    - Inference time measurements
    - Detections found
    ├─> Console (colored) + Log file

WARNING
    - Model file missing but folder found
    - Low confidence detections filtered
    ├─> Console (yellow) + Log file

ERROR
    - ONNX session creation failed
    - Model inference exception
    ├─> Console (red) + Log file

CRITICAL
    - All detectors failed to load
    - Camera initialization failed
    ├─> Console (red bold) + Log file
```

### 6b. Example Log Output

```
[INFO] Loading model: people_detector
[DEBUG] Model path: /mnt/dtamboudisk/vision_assistant/models/people_detector/best.onnx
[DEBUG] Labels: ['person', 'bicycle']
[DEBUG] Metadata: {...}
[INFO] people_detector ONNX session created
[INFO] VisionAgent started with 1 detector loaded

[INFO] Frame 1 captured, dims=1280x720
[DEBUG] Preprocessing frame...
[INFO] Running detector: people_detector Backend: ONNX
[INFO] people_detector ONNX inference time: 42.15 ms
[DEBUG] people_detector tensor[0] dtype=float32 shape=(1, 5, 8400) first_values=[2.41, 15.00, 23.99]
[INFO] people_detector ONNX returned 1 tensors
[INFO] people_detector ONNX parsed 2 predictions
[INFO] Detector people_detector returned 2 normalized predictions

[INFO] VisionAgent frame 1 detector people_detector (people) produced 2 detections
[INFO] People detector output: person confidence=0.94 bbox={x1: 100, y1: 150, x2: 300, y2: 450}
[INFO] People detector output: person confidence=0.87 bbox={x1: 50, y1: 200, x2: 150, y2: 350}

[INFO] Reasoning input categories=['people']
[INFO] Reasoning generated message=Person ahead priority=2 danger_level=medium

[INFO] Memory previous messages=[...last 5...] current_message=Person ahead
[INFO] Memory remembering message: Person ahead

[INFO] Speech backend=console
[INFO] Announcing: "Person ahead"
```

### 6c. Performance Metrics

Logged in every inference cycle:

```
- Frame capture time (ms)
- Preprocessing time (ms)
- ONNX inference time per detector (ms)
- JSON parsing time (ms)
- Reasoning time (ms)
- Memory lookup time (ms)
- Speech time (ms)
- Total pipeline latency (ms)
```

Example:
```
[PERF] Cycle 123: capture=5.2ms, preprocess=2.1ms, 
       people_detector=42.15ms, vehicle_detector=48.3ms,
       reasoning=1.2ms, memory=0.3ms, speech=0.1ms,
       TOTAL=99.35ms (10.1 FPS)
```

---

## File Organization

```
vision_assistant/
├── config.py                  # ← Modify settings here
├── run.py                     # ← Entrypoint
│
├── agents/
│   ├── coordinator/
│   │   ├── coordinator.py     # Main orchestrator
│   │   └── registry.py        # Model tracking
│   │
│   ├── vision/
│   │   ├── model_loader.py    # ← Load & run detectors
│   │   ├── vision_agent.py    # Parallel inference
│   │   ├── fake_models.py     # ❌ DELETED in v2.0
│   │   └── fake_models will never return
│   │
│   ├── reasoning/
│   │   ├── reasoning_agent.py # Decision making
│   │   ├── danger_rules.py    # Threat definitions
│   │   └── priority_manager.py# Priority matrix
│   │
│   ├── memory/
│   │   ├── memory_agent.py    # Deduplication
│   │   └── history.py         # Message history
│   │
│   └── speech/
│       ├── speech_agent.py    # Speech output
│       └── tts.py            # TTS backends
│
├── app/
│   ├── api/
│   │   └── main.py            # FastAPI server
│   └── desktop/
│       └── desktop_app.py     # GUI demo
│
├── models/
│   ├── people_detector/
│   │   ├── best.onnx         # ← Real model
│   │   ├── labels.txt
│   │   └── metadata.json
│   └── vehicle_detector/
│       └── ...
│
├── exports/
│   └── logs/
│       └── vision_assistant.log
│
├── docs/
├── tests/
└── ARCHITECTURE.md  ← You are here
```

---

## Summary: Real Models Only

This architecture is **production-ready**:

- ✅ **Zero fake detectors fallback**: If a model is missing, that detector is simply skipped
- ✅ **Parallel inference**: All detectors run concurrently
- ✅ **Flexible backends**: ONNX or PyTorch, CPU or GPU
- ✅ **Configurable**: Thresholds, prioritization, memory timeout
- ✅ **Diagnostic**: Extensive logging at DEBUG/INFO levels
- ✅ **Testable**: Each agent can be tested independently
- ✅ **Extensible**: Add new detectors by creating `models/detector_name/best.onnx`

---

**Architecture Version:** 2.0 (Real Models Only)  
**Last Updated:** 29 June 2026  
**Status:** ✅ Production Ready
