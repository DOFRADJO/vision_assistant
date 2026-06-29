# Model Template

This directory contains a template structure for developing a detector model for the Vision Assistant platform.

## Quick Start

1. **Copy this template to create your model:**
   ```bash
   cd training/
   cp -r model_template/ your_detector_name/
   cd your_detector_name/
   ```

2. **Rename files to match your model name:**
   ```bash
   # The folder name becomes your model identifier
   # training/your_detector_name/ → model_name = "your_detector_name"

   # Edit metadata.json.example
   # Edit labels.txt.example
   ```

3. **Remove the .example extension:**
   ```bash
   mv metadata.json.example metadata.json
   mv labels.txt.example labels.txt
   ```

4. **Add your model files (after training):**
   ```bash
   # Copy your trained models here:
   cp /path/to/your/best.pt .
   cp /path/to/your/best.onnx .
   ```

5. **Validate before submission:**
   ```bash
   cd ../../  # Back to project root
   python scripts/integrate_model.py your_detector_name --validate
   ```

## File Structure

```
model_template/
├── README.md                    # This file
├── metadata.json.example        # Template metadata (rename to metadata.json)
├── labels.txt.example           # Template labels (rename to labels.txt)
├── train.py                     # Example training script
├── export.py                    # Example export script
├── predict.py                   # Example prediction script
└── dataset/                     # Training data directory (optional)
    └── .gitkeep
```

## Files You Will Add (After Training)

- `best.pt` - PyTorch model (REQUIRED)
- `best.onnx` - ONNX model (REQUIRED)

## Step-by-Step Guide

### Step 1: Copy Template

```bash
cd training/
cp -r model_template/ people_detector/
cd people_detector/
```

Your folder structure now looks like:

```
training/people_detector/
├── README.md
├── metadata.json.example
├── labels.txt.example
├── train.py
├── export.py
├── predict.py
└── dataset/
```

### Step 2: Edit metadata.json

Rename and edit the metadata file:

```bash
cp metadata.json.example metadata.json
nano metadata.json
```

Update these fields with YOUR model details:

```json
{
  "model_name": "people_detector",
  "author": "Your Name or Team",
  "version": "1.0.0",
  "framework": "YOLOv8",
  "input_size": [640, 640],
  "output_format": {
    "type": "detections",
    "num_classes": 1,
    "format": "xyxy"
  },
  "description": "Detects people in images and videos"
}
```

**Important Fields:**
- `model_name` - Must match your folder name
- `author` - Your name (will be in final report)
- `version` - Your model version (e.g., 1.0.0)
- `framework` - Model framework used (YOLOv8, etc.)
- `input_size` - [width, height] your model expects

### Step 3: Edit labels.txt

Rename and edit the labels file:

```bash
cp labels.txt.example labels.txt
nano labels.txt
```

Add your class names, one per line:

```
person
```

For multi-class detector:

```
person
face
hand
```

**Important Rules:**
- One label per line
- No duplicates
- No empty lines
- No extra spaces or commas

### Step 4: Organize Training Files

Place your training scripts and data in the directory:

```bash
# Example structure
training/people_detector/
├── train.py              # Your training script
├── export.py             # Your export script
├── dataset/              # Training data
│   ├── train/
│   ├── val/
│   └── test/
├── runs/                 # Will contain training outputs
└── weights/              # Will contain checkpoints
```

### Step 5: Train Your Model

Develop and train your detector using your preferred framework:

```bash
python train.py
```

This should produce:
- Trained model weights
- Best performing checkpoint

### Step 6: Export Models

Export your trained model to PyTorch and ONNX formats:

**Using YOLOv8:**

```python
from ultralytics import YOLO

# Load model
model = YOLO("runs/detect/train/weights/best.pt")

# Export to ONNX
model.export(format="onnx")

# Copy to current directory
cp runs/detect/train/weights/best.pt .
cp runs/detect/train/weights/best.onnx .
```

**Using PyTorch directly:**

```python
import torch

# Load state dict
model = create_model()
model.load_state_dict(torch.load("checkpoint.pt"))
model.eval()

# Save PyTorch model
torch.save(model, "best.pt")

# Export to ONNX
dummy_input = torch.randn(1, 3, 640, 640)
torch.onnx.export(
    model,
    dummy_input,
    "best.onnx",
    input_names=["input"],
    output_names=["output"],
    opset_version=12
)
```

### Step 7: Verify Files

Check all required files are present:

```bash
ls -lh training/people_detector/
```

You should see:

```
best.pt          (>100 KB)
best.onnx        (>100 KB)
labels.txt       (>0 bytes)
metadata.json    (>100 bytes)
```

### Step 8: Run Validation

Test your model before committing:

```bash
cd ../../  # Back to project root
python scripts/integrate_model.py people_detector --validate
```

Expected output:

```
--- Validation Report for people_detector ---
✅ All validations passed
```

### Step 9: Run Integration Test

Do a dry-run integration (no files copied to models/):

```bash
python scripts/integrate_model.py people_detector --dry-run
```

### Step 10: Commit and Push

When everything is working:

```bash
git add training/people_detector/
git commit -m "Add people_detector model

- Trained YOLOv8 on custom dataset
- Achieves 95% mAP on validation set
- Exported to PyTorch and ONNX
- All validation checks passed"

git push origin feature/people_detector
```

## Example Workflow

Complete example for a people detector:

```bash
# 1. Copy template
cd training/
cp -r model_template/ people_detector/
cd people_detector/

# 2. Edit configuration
cp metadata.json.example metadata.json
cp labels.txt.example labels.txt

# Edit files with your data
echo "person" > labels.txt

# 3. Train model (your implementation)
python train.py

# 4. Export model
python export.py

# 5. Validate
cd ../../
python scripts/integrate_model.py people_detector --validate

# 6. Test integration
python scripts/integrate_model.py people_detector --dry-run

# 7. Commit
git add training/people_detector/
git commit -m "Add people_detector model"

# 8. Push
git push origin feature/people_detector
```

## Common Issues

### "Model directory not found"

**Problem:** Folder name doesn't match model_name in metadata.json

**Solution:**
```
Folder:    training/people_detector/
Metadata:  model_name = "people_detector"  ✅

Folder:    training/people_detector/
Metadata:  model_name = "person_detector"  ❌ WRONG
```

### "metadata.json is malformed JSON"

**Problem:** JSON syntax error in metadata.json

**Solution:**
```bash
# Validate JSON
python -m json.tool training/people_detector/metadata.json

# Copy template and re-edit
cp metadata.json.example metadata.json
```

### "Duplicate labels found"

**Problem:** Same label appears multiple times in labels.txt

**Solution:**
```
person     ✅ OK
face       ✅ OK

person     ❌ DUPLICATE
person     ❌ DUPLICATE
```

### "Empty file: labels.txt"

**Problem:** labels.txt is empty

**Solution:**
```bash
# Add labels
echo "person" > labels.txt
```

### "Missing required file: best.onnx"

**Problem:** ONNX model not exported

**Solution:**
```bash
# Export to ONNX using training script
python export.py

# Or manually:
python -c "import torch; torch.onnx.export(...)"
```

## Pre-Integration Checklist

Before running `python scripts/integrate_model.py people_detector`:

- ✅ `best.pt` exists and size > 100 KB
- ✅ `best.onnx` exists and size > 100 KB
- ✅ `labels.txt` contains class names (no duplicates)
- ✅ `metadata.json` is valid JSON
- ✅ `model_name` in metadata matches folder name
- ✅ Validation passes: `--validate`
- ✅ Dry-run works: `--dry-run`

## Integration Commands

```bash
# Validate your model
python scripts/integrate_model.py people_detector --validate

# Test integration without copying files
python scripts/integrate_model.py people_detector --dry-run

# Full integration (copies to models/, runs tests)
python scripts/integrate_model.py people_detector

# List all available models
python scripts/integrate_model.py --list

# Integrate all discovered models
python scripts/integrate_model.py --all
```

## Output After Integration

After successful integration:

```
models/people_detector/
├── best.pt
├── best.onnx
├── labels.txt
└── metadata.json

exports/reports/
└── integration_report_people_detector.md

exports/logs/
└── integration.log
```

## Next Steps

1. **Study the MODEL_CONTRACT:** `docs/MODEL_CONTRACT.md`
2. **Review training examples:** `training/*/train.py`
3. **Develop your model:** Use your preferred framework
4. **Export to PyTorch and ONNX:** Follow export guidelines
5. **Validate:** Use `--validate` command
6. **Integrate:** Use integration script
7. **Submit:** Create pull request

## Resources

- **Contract:** `docs/MODEL_CONTRACT.md`
- **Integration Script:** `scripts/integrate_model.py --help`
- **Examples:** See other model folders in `training/`
- **Logs:** `exports/logs/integration.log`
- **Reports:** `exports/reports/integration_report_*.md`

## Support

Questions? Check:
1. `docs/MODEL_CONTRACT.md` - Full specification
2. `exports/logs/integration.log` - Integration errors
3. `exports/reports/integration_report_*.md` - Detailed results
4. `--validate` output - Validation errors

Good luck with your model! 🚀
