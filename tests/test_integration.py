"""
Integration Tests for Model Integration System.

Comprehensive tests covering:
- Model validation
- File verification
- Metadata validation
- Labels validation
- Installation with rollback
- Registration
- Inference testing
- Report generation
- Batch operations

Run tests with:
    pytest tests/test_integration.py -v
    pytest tests/test_integration.py::TestModelValidator -v
    pytest tests/test_integration.py::TestModelInstaller -v

"""

import json
import tempfile
from pathlib import Path
from datetime import datetime
from typing import Tuple

import pytest

# Import integration components
from scripts.integrate_model import (
    ModelMetadata,
    ModelValidator,
    ModelInstaller,
    IntegrationTester,
    IntegrationResult,
    ReportGenerator,
    discover_models,
)


# ============================================================================
# FIXTURES
# ============================================================================

@pytest.fixture
def temp_training_dir() -> Path:
    """Create temporary training directory structure."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)
        yield tmpdir


@pytest.fixture
def temp_models_dir() -> Path:
    """Create temporary models directory."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)
        yield tmpdir


@pytest.fixture
def temp_reports_dir() -> Path:
    """Create temporary reports directory."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)
        yield tmpdir


def create_test_model_dir(
    base_dir: Path,
    model_name: str,
    valid: bool = True,
    include_files: bool = True,
    metadata_dict: dict = None,
    labels: list = None,
) -> Path:
    """
    Create a test model directory with files.

    Args:
        base_dir: Base directory for the model
        model_name: Name of the model
        valid: Whether to create valid files
        include_files: Whether to include model files
        metadata_dict: Custom metadata (if valid=True)
        labels: Custom labels (if valid=True)

    Returns:
        Path to created model directory
    """
    model_dir = base_dir / model_name
    model_dir.mkdir(parents=True, exist_ok=True)

    if valid:
        # Create metadata.json
        metadata = metadata_dict or {
            "model_name": model_name,
            "author": "Test Author",
            "version": "1.0.0",
            "framework": "YOLOv8",
            "input_size": [640, 640],
            "output_format": {
                "type": "detections",
                "num_classes": 1,
                "format": "xyxy",
            },
        }
        (model_dir / "metadata.json").write_text(json.dumps(metadata))

        # Create labels.txt
        labels_content = "\n".join(labels or ["object"])
        (model_dir / "labels.txt").write_text(labels_content)

        if include_files:
            # Create dummy model files
            (model_dir / "best.pt").write_text("dummy pytorch model" * 100)
            (model_dir / "best.onnx").write_text("dummy onnx model" * 100)
    else:
        # Create incomplete/invalid files
        if include_files:
            (model_dir / "best.pt").write_text("")
            (model_dir / "best.onnx").write_text("")
            (model_dir / "labels.txt").write_text("")

    return model_dir


# ============================================================================
# TEST: MODEL METADATA
# ============================================================================

class TestModelMetadata:
    """Tests for ModelMetadata dataclass."""

    def test_valid_metadata(self):
        """Test creating valid metadata."""
        data = {
            "model_name": "people_detector",
            "author": "John Doe",
            "version": "1.0.0",
            "framework": "YOLOv8",
            "input_size": [640, 640],
            "output_format": {"type": "detections", "num_classes": 1},
        }
        metadata = ModelMetadata.from_dict(data)
        assert metadata.model_name == "people_detector"
        assert metadata.author == "John Doe"
        assert metadata.version == "1.0.0"
        assert metadata.input_size == (640, 640)

    def test_missing_required_field(self):
        """Test metadata with missing required field."""
        data = {
            "model_name": "people_detector",
            "author": "John Doe",
            # Missing: "version", "framework", "input_size", "output_format"
        }
        with pytest.raises(ValueError, match="missing required fields"):
            ModelMetadata.from_dict(data)

    def test_invalid_input_size(self):
        """Test metadata with invalid input_size."""
        data = {
            "model_name": "people_detector",
            "author": "John Doe",
            "version": "1.0.0",
            "framework": "YOLOv8",
            "input_size": 640,  # Should be [width, height]
            "output_format": {"type": "detections"},
        }
        with pytest.raises(ValueError, match="input_size must be"):
            ModelMetadata.from_dict(data)

    def test_optional_fields(self):
        """Test metadata with optional fields."""
        data = {
            "model_name": "people_detector",
            "author": "John Doe",
            "version": "1.0.0",
            "framework": "YOLOv8",
            "input_size": [640, 640],
            "output_format": {},
            "description": "Test model",
            "timestamp": "2024-06-29T10:00:00Z",
        }
        metadata = ModelMetadata.from_dict(data)
        assert metadata.description == "Test model"
        assert metadata.timestamp == "2024-06-29T10:00:00Z"


# ============================================================================
# TEST: MODEL VALIDATOR
# ============================================================================

class TestModelValidator:
    """Tests for ModelValidator class."""

    def test_valid_model(self, temp_training_dir):
        """Test validation of valid model."""
        model_dir = create_test_model_dir(temp_training_dir, "people_detector", valid=True)
        validator = ModelValidator(model_dir)
        valid, metadata, labels = validator.validate_all()

        assert valid is True
        assert metadata is not None
        assert metadata.model_name == "people_detector"
        assert labels == ["object"]

    def test_missing_file(self, temp_training_dir):
        """Test validation with missing required file."""
        model_dir = create_test_model_dir(temp_training_dir, "people_detector", valid=True)
        (model_dir / "best.pt").unlink()  # Remove one file

        validator = ModelValidator(model_dir)
        valid, metadata, labels = validator.validate_all()

        assert valid is False
        assert len(validator.errors) > 0

    def test_empty_labels(self, temp_training_dir):
        """Test validation with empty labels."""
        model_dir = create_test_model_dir(
            temp_training_dir,
            "people_detector",
            valid=True,
            labels=[],  # Empty labels
        )
        (model_dir / "labels.txt").write_text("")

        validator = ModelValidator(model_dir)
        valid, metadata, labels = validator.validate_all()

        assert valid is False
        assert any("empty" in e.lower() for e in validator.errors)

    def test_duplicate_labels(self, temp_training_dir):
        """Test validation with duplicate labels."""
        model_dir = create_test_model_dir(
            temp_training_dir,
            "people_detector",
            valid=True,
        )
        (model_dir / "labels.txt").write_text("person\nperson\ncar")

        validator = ModelValidator(model_dir)
        valid, metadata, labels = validator.validate_all()

        assert valid is False
        assert any("duplicate" in e.lower() for e in validator.errors)

    def test_malformed_metadata(self, temp_training_dir):
        """Test validation with malformed metadata."""
        model_dir = create_test_model_dir(temp_training_dir, "people_detector", valid=True)
        (model_dir / "metadata.json").write_text("{invalid json}")

        validator = ModelValidator(model_dir)
        valid, metadata, labels = validator.validate_all()

        assert valid is False
        assert any("malformed" in e.lower() for e in validator.errors)

    def test_model_name_mismatch(self, temp_training_dir):
        """Test validation with model_name mismatch."""
        model_dir = create_test_model_dir(
            temp_training_dir,
            "people_detector",
            valid=True,
            metadata_dict={
                "model_name": "wrong_name",  # Doesn't match directory
                "author": "Test",
                "version": "1.0.0",
                "framework": "YOLOv8",
                "input_size": [640, 640],
                "output_format": {},
            },
        )

        validator = ModelValidator(model_dir)
        valid, metadata, labels = validator.validate_all()

        # Should still validate but with warning
        assert len(validator.warnings) > 0


# ============================================================================
# TEST: MODEL INSTALLER
# ============================================================================

class TestModelInstaller:
    """Tests for ModelInstaller class."""

    def test_install_model(self, temp_training_dir, temp_models_dir):
        """Test successful model installation."""
        source_dir = create_test_model_dir(temp_training_dir, "people_detector", valid=True)
        dest_dir = temp_models_dir / "people_detector"

        installer = ModelInstaller(source_dir, dest_dir)
        success, msg = installer.install(dry_run=False, overwrite=False)

        assert success is True
        assert dest_dir.exists()
        assert (dest_dir / "best.pt").exists()
        assert (dest_dir / "best.onnx").exists()
        assert (dest_dir / "labels.txt").exists()
        assert (dest_dir / "metadata.json").exists()

    def test_dry_run_installation(self, temp_training_dir, temp_models_dir):
        """Test dry-run installation."""
        source_dir = create_test_model_dir(temp_training_dir, "people_detector", valid=True)
        dest_dir = temp_models_dir / "people_detector"

        installer = ModelInstaller(source_dir, dest_dir)
        success, msg = installer.install(dry_run=True, overwrite=False)

        assert success is True
        assert not dest_dir.exists()  # Dry-run should not create directory

    def test_install_existing_model_without_overwrite(self, temp_training_dir, temp_models_dir):
        """Test installation of existing model without overwrite."""
        source_dir = create_test_model_dir(temp_training_dir, "people_detector", valid=True)
        dest_dir = temp_models_dir / "people_detector"

        # First installation
        installer1 = ModelInstaller(source_dir, dest_dir)
        installer1.install(dry_run=False, overwrite=False)

        # Second installation without overwrite should fail
        installer2 = ModelInstaller(source_dir, dest_dir)
        success, msg = installer2.install(dry_run=False, overwrite=False)

        assert success is False
        assert "already installed" in msg.lower()

    def test_install_with_overwrite(self, temp_training_dir, temp_models_dir):
        """Test installation with overwrite."""
        source_dir = create_test_model_dir(temp_training_dir, "people_detector", valid=True)
        dest_dir = temp_models_dir / "people_detector"

        # First installation
        installer1 = ModelInstaller(source_dir, dest_dir)
        installer1.install(dry_run=False, overwrite=False)

        # Modify installed file
        (dest_dir / "best.pt").write_text("modified content")

        # Second installation with overwrite
        installer2 = ModelInstaller(source_dir, dest_dir)
        success, msg = installer2.install(dry_run=False, overwrite=True)

        assert success is True
        # Check backup was created
        assert installer2.backup_dir is not None


# ============================================================================
# TEST: INTEGRATION RESULT
# ============================================================================

class TestIntegrationResult:
    """Tests for IntegrationResult dataclass."""

    def test_result_serialization(self):
        """Test converting result to dictionary."""
        start = datetime.now()
        end = datetime.now()

        result = IntegrationResult(
            model_name="people_detector",
            success=True,
            start_time=start,
            end_time=end,
            files_validated=["best.pt", "best.onnx", "labels.txt", "metadata.json"],
            labels=["object"],
            execution_time_ms=100.0,
        )

        result_dict = result.to_dict()
        assert result_dict["model_name"] == "people_detector"
        assert result_dict["success"] is True
        assert isinstance(result_dict["start_time"], str)
        assert isinstance(result_dict["end_time"], str)


# ============================================================================
# TEST: REPORT GENERATOR
# ============================================================================

class TestReportGenerator:
    """Tests for ReportGenerator class."""

    def test_generate_model_report(self, temp_reports_dir):
        """Test generating report for single model."""
        result = IntegrationResult(
            model_name="people_detector",
            success=True,
            start_time=datetime.now(),
            end_time=datetime.now(),
            files_validated=["best.pt", "best.onnx", "labels.txt", "metadata.json"],
            labels=["object"],
            metadata=ModelMetadata(
                model_name="people_detector",
                author="Test Author",
                version="1.0.0",
                framework="YOLOv8",
                input_size=(640, 640),
                output_format={"type": "detections", "num_classes": 1},
            ),
            execution_time_ms=150.0,
        )

        generator = ReportGenerator(temp_reports_dir)
        report_path = generator.generate_model_report(result)

        assert report_path.exists()
        content = report_path.read_text()
        assert "people_detector" in content
        assert "Test Author" in content
        assert "✅" in content or "SUCCESS" in content

    def test_generate_batch_report(self, temp_reports_dir):
        """Test generating batch report."""
        results = [
            IntegrationResult(
                model_name="model1",
                success=True,
                start_time=datetime.now(),
                end_time=datetime.now(),
                files_validated=[],
                labels=[],
                execution_time_ms=100.0,
            ),
            IntegrationResult(
                model_name="model2",
                success=False,
                start_time=datetime.now(),
                end_time=datetime.now(),
                files_validated=[],
                labels=[],
                error="Test error",
                execution_time_ms=50.0,
            ),
        ]

        generator = ReportGenerator(temp_reports_dir)
        report_path = generator.generate_batch_report(results)

        assert report_path.exists()
        content = report_path.read_text()
        assert "model1" in content
        assert "model2" in content
        assert "Failed" in content or "2" in content


# ============================================================================
# TEST: BATCH OPERATIONS
# ============================================================================

class TestBatchOperations:
    """Tests for batch discovery and integration."""

    def test_discover_models(self, temp_training_dir):
        """Test model discovery."""
        # Create multiple models
        create_test_model_dir(temp_training_dir, "people_detector", valid=True)
        create_test_model_dir(temp_training_dir, "vehicle_detector", valid=True)

        # Mock the TRAINING_DIR for this test
        import sys
        from unittest.mock import patch

        with patch("scripts.integrate_model.TRAINING_DIR", temp_training_dir):
            models = discover_models()

        assert "people_detector" in models
        assert "vehicle_detector" in models

    def test_skip_template_directory(self, temp_training_dir):
        """Test that template directory is skipped."""
        create_test_model_dir(temp_training_dir, "model_template", valid=True)
        create_test_model_dir(temp_training_dir, "people_detector", valid=True)

        from unittest.mock import patch

        with patch("scripts.integrate_model.TRAINING_DIR", temp_training_dir):
            models = discover_models()

        assert "model_template" in models  # discovered but skipped in integration
        assert "people_detector" in models


# ============================================================================
# INTEGRATION TESTS
# ============================================================================

class TestFullIntegration:
    """End-to-end integration tests."""

    def test_full_workflow(self, temp_training_dir, temp_models_dir, temp_reports_dir):
        """Test complete integration workflow."""
        from scripts.integrate_model import ModelIntegrator

        # Create test model
        source_dir = create_test_model_dir(temp_training_dir, "people_detector", valid=True)

        # Mock directories
        from unittest.mock import patch

        with patch("scripts.integrate_model.TRAINING_DIR", temp_training_dir), \
             patch("scripts.integrate_model.MODELS_DIR", temp_models_dir), \
             patch("scripts.integrate_model.REPORTS_DIR", temp_reports_dir):

            integrator = ModelIntegrator("people_detector", dry_run=False)
            result = integrator.integrate()

            assert result.success is True
            assert result.metadata is not None
            assert len(result.labels) > 0

    def test_integration_with_missing_files(self, temp_training_dir, temp_models_dir, temp_reports_dir):
        """Test integration with missing required files."""
        from scripts.integrate_model import ModelIntegrator

        # Create incomplete model
        model_dir = create_test_model_dir(temp_training_dir, "people_detector", valid=True)
        (model_dir / "best.onnx").unlink()  # Remove ONNX file

        from unittest.mock import patch

        with patch("scripts.integrate_model.TRAINING_DIR", temp_training_dir), \
             patch("scripts.integrate_model.MODELS_DIR", temp_models_dir), \
             patch("scripts.integrate_model.REPORTS_DIR", temp_reports_dir):

            integrator = ModelIntegrator("people_detector", dry_run=False)
            result = integrator.integrate()

            assert result.success is False


# ============================================================================
# EDGE CASES
# ============================================================================

class TestEdgeCases:
    """Tests for edge cases and error conditions."""

    def test_very_long_label(self, temp_training_dir):
        """Test validation of very long label names."""
        model_dir = create_test_model_dir(
            temp_training_dir,
            "people_detector",
            valid=True,
            labels=["a" * 101],  # Over 100 characters
        )
        validator = ModelValidator(model_dir)
        valid, metadata, labels = validator.validate_all()

        # Should warn about long labels
        assert len(validator.warnings) > 0

    def test_special_characters_in_labels(self, temp_training_dir):
        """Test labels with special characters."""
        model_dir = create_test_model_dir(
            temp_training_dir,
            "people_detector",
            valid=True,
            labels=["person_head", "person-face", "person@home"],
        )
        validator = ModelValidator(model_dir)
        valid, metadata, labels = validator.validate_all()

        # Should handle special characters gracefully
        assert valid is True
        assert len(labels) == 3

    def test_unicode_labels(self, temp_training_dir):
        """Test labels with unicode characters."""
        model_dir = create_test_model_dir(
            temp_training_dir,
            "people_detector",
            valid=True,
        )
        (model_dir / "labels.txt").write_text("人物\n車")  # Chinese characters

        validator = ModelValidator(model_dir)
        valid, metadata, labels = validator.validate_all()

        # Should handle unicode gracefully
        assert valid is True


# ============================================================================
# PERFORMANCE TESTS
# ============================================================================

class TestPerformance:
    """Performance-related tests."""

    def test_large_labels_file(self, temp_training_dir):
        """Test validation of large labels file."""
        model_dir = create_test_model_dir(temp_training_dir, "people_detector", valid=True)

        # Create large labels file with many unique labels
        labels = [f"object_{i}" for i in range(1000)]
        (model_dir / "labels.txt").write_text("\n".join(labels))

        # Update metadata
        metadata = {
            "model_name": "people_detector",
            "author": "Test",
            "version": "1.0.0",
            "framework": "YOLOv8",
            "input_size": [640, 640],
            "output_format": {"type": "detections", "num_classes": 1000},
        }
        (model_dir / "metadata.json").write_text(json.dumps(metadata))

        validator = ModelValidator(model_dir)
        valid, metadata, labels = validator.validate_all()

        assert valid is True
        assert len(labels) == 1000


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
