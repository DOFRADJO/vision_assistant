# Vision Assistant

Vision Assistant is a production-ready multi-agent computer vision platform for assisting visually impaired users.

## Features
- Multi-agent orchestration with Coordinator, Vision, Reasoning, Memory, and Speech agents
- Real ONNX/PyTorch model loading from `models/`
- Tracking with IoU fallback and optional ByteTrack support
- FastAPI endpoints for image and video inference
- OpenCV desktop UI
- Model integration tooling and logs

## Architecture
- `agents/` contains the agent implementations
- `core/` contains camera, tracking, and utility services
- `app/api/` contains the FastAPI app
- `app/desktop/` contains the OpenCV desktop app
- `models/` stores student-trained detector artifacts
- `training/` stores training recipes and exported artifacts

## Quick start
```bash
python -m pip install -r requirements.txt
python run.py --mode api
```

## Model integration
```bash
python scripts/integrate_model.py --source /path/to/student_model --name people_detector
```

## Testing
```bash
pytest -q
```
