#!/usr/bin/env python3
"""
Model Integration System for Vision Assistant.

This script provides a complete pipeline for integrating student-developed
detectors into the Vision Assistant platform. Handles validation, installation,
testing, and reporting with comprehensive error handling and rollback capability.

Usage:
    python scripts/integrate_model.py people_detector
    python scripts/integrate_model.py vehicle_detector --verbose
    python scripts/integrate_model.py --all
    python scripts/integrate_model.py --report
    python scripts/integrate_model.py --list
    python scripts/integrate_model.py --validate
    python scripts/integrate_model.py people_detector --dry-run

Author: AI Platform Architecture Team
Version: 1.0.0
"""

from __future__ import annotations
import argparse
import json
import logging
import shutil
import sys
import time
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
import numpy as np

# ============================================================================
# CONFIGURATION & PATHS
# ============================================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent
TRAINING_DIR = PROJECT_ROOT / "training"
MODELS_DIR = PROJECT_ROOT / "models"
REPORTS_DIR = PROJECT_ROOT / "exports" / "reports"
LOGS_DIR = PROJECT_ROOT / "exports" / "logs"
TEMPLATE_DIR = TRAINING_DIR / "model_template"

# Ensure directories exist
REPORTS_DIR.mkdir(parents=True, exist_ok=True)
LOGS_DIR.mkdir(parents=True, exist_ok=True)

# Setup logging
INTEGRATION_LOG = LOGS_DIR / "integration.log"
logger = logging.getLogger("integration")
logger.setLevel(logging.DEBUG)

# File handler
fh = logging.FileHandler(INTEGRATION_LOG)
fh.setLevel(logging.DEBUG)
fh.setFormatter(
    logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
)
logger.addHandler(fh)

# Console handler
ch = logging.StreamHandler()
ch.setLevel(logging.INFO)
ch.setFormatter(
    logging.Formatter("[%(levelname)s] %(message)s")
)
logger.addHandler(ch)


# ============================================================================
# DATA STRUCTURES
# ============================================================================

@dataclass
class ModelMetadata:
    """Model metadata from metadata.json."""
    model_name: str
    author: str
    version: str
    framework: str
    input_size: Tuple[int, int]
    output_format: Dict[str, Any]
    description: Optional[str] = None
    timestamp: Optional[str] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> ModelMetadata:
        """Parse metadata from dictionary with validation."""
        required = {"model_name", "author", "version", "framework", "input_size", "output_format"}
        missing = required - set(data.keys())
        if missing:
            raise ValueError(f"Metadata missing required fields: {missing}")

        input_size = data.get("input_size")
        if not isinstance(input_size, (list, tuple)) or len(input_size) != 2:
            raise ValueError("input_size must be [width, height]")

        return cls(
            model_name=str(data["model_name"]),
            author=str(data["author"]),
            version=str(data["version"]),
            framework=str(data["framework"]),
            input_size=tuple(int(x) for x in input_size),
            output_format=dict(data.get("output_format", {})),
            description=data.get("description"),
            timestamp=data.get("timestamp"),
        )


@dataclass
class IntegrationResult:
    """Complete integration operation result."""
    model_name: str
    success: bool
    start_time: datetime
    end_time: datetime
    files_validated: List[str]
    labels: List[str]
    metadata: Optional[ModelMetadata] = None
    inference_result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    warning: Optional[str] = None
    execution_time_ms: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        result = asdict(self)
        result["start_time"] = self.start_time.isoformat()
        result["end_time"] = self.end_time.isoformat()
        if self.metadata:
            result["metadata"] = asdict(self.metadata)
        return result


# ============================================================================
# VALIDATION FUNCTIONS
# ============================================================================

class ModelValidator:
    """Comprehensive model validation before integration."""

    REQUIRED_FILES = {"best.pt", "best.onnx", "labels.txt", "metadata.json"}

    def __init__(self, model_dir: Path):
        """Initialize validator with model directory."""
        self.model_dir = model_dir
        self.model_name = model_dir.name
        self.errors: List[str] = []
        self.warnings: List[str] = []

    def validate_all(self) -> Tuple[bool, ModelMetadata, List[str]]:
        """Run all validations and return success status, metadata, and labels."""
        logger.info(f"Starting validation for model: {self.model_name}")

        # Step 1: Verify required files
        if not self._verify_required_files():
            return False, None, []

        # Step 2: Validate metadata.json
        metadata = self._validate_metadata()
        if metadata is None:
            return False, None, []

        # Step 3: Validate labels.txt
        labels = self._validate_labels()
        if labels is None:
            return False, metadata, []

        # Step 4: Cross-validation
        self._validate_metadata_consistency(metadata, labels)

        if self.errors:
            logger.error(f"Validation failed for {self.model_name}")
            return False, metadata, labels

        logger.info(f"Validation passed for {self.model_name}")
        return True, metadata, labels

    def _verify_required_files(self) -> bool:
        """Verify all required files exist and are non-empty."""
        missing = []
        for filename in self.REQUIRED_FILES:
            filepath = self.model_dir / filename
            if not filepath.exists():
                missing.append(filename)
                self.errors.append(f"Missing required file: {filename}")
            elif filepath.stat().st_size == 0:
                self.errors.append(f"Empty file: {filename}")

        return len(missing) == 0 and len(self.errors) == 0

    def _validate_metadata(self) -> Optional[ModelMetadata]:
        """Validate metadata.json structure and content."""
        metadata_path = self.model_dir / "metadata.json"
        try:
            with open(metadata_path, "r") as f:
                data = json.load(f)
        except json.JSONDecodeError as e:
            self.errors.append(f"metadata.json is malformed JSON: {e}")
            return None
        except Exception as e:
            self.errors.append(f"Failed to read metadata.json: {e}")
            return None

        try:
            metadata = ModelMetadata.from_dict(data)
            logger.debug(f"Metadata validated: {metadata.model_name} v{metadata.version}")
            return metadata
        except ValueError as e:
            self.errors.append(f"Invalid metadata: {e}")
            return None

    def _validate_labels(self) -> Optional[List[str]]:
        """Validate labels.txt format and content."""
        labels_path = self.model_dir / "labels.txt"
        try:
            with open(labels_path, "r") as f:
                lines = [line.strip() for line in f if line.strip()]
        except Exception as e:
            self.errors.append(f"Failed to read labels.txt: {e}")
            return None

        if not lines:
            self.errors.append("labels.txt is empty")
            return None

        # Check for duplicates
        if len(lines) != len(set(lines)):
            duplicates = [label for label in set(lines) if lines.count(label) > 1]
            self.errors.append(f"Duplicate labels found: {duplicates}")
            return None

        # Check for invalid characters
        invalid = [label for label in lines if not label or len(label) > 100]
        if invalid:
            self.warnings.append(f"Some labels may be invalid: {invalid[:5]}")

        logger.debug(f"Labels validated: {len(lines)} unique labels")
        return lines

    def _validate_metadata_consistency(self, metadata: ModelMetadata, labels: List[str]) -> None:
        """Cross-validate metadata and labels."""
        if metadata.model_name != self.model_name:
            self.warnings.append(
                f"Model name mismatch: folder={self.model_name}, "
                f"metadata={metadata.model_name}"
            )

        output_format = metadata.output_format
        if isinstance(output_format, dict):
            if "num_classes" in output_format:
                num_classes = output_format["num_classes"]
                if num_classes != len(labels):
                    self.warnings.append(
                        f"Label count mismatch: metadata says {num_classes}, "
                        f"but found {len(labels)} labels"
                    )

    def report(self) -> str:
        """Generate validation report."""
        report = f"\n--- Validation Report for {self.model_name} ---\n"
        if self.errors:
            report += f"ERRORS ({len(self.errors)}):\n"
            for error in self.errors:
                report += f"  ❌ {error}\n"
        if self.warnings:
            report += f"WARNINGS ({len(self.warnings)}):\n"
            for warning in self.warnings:
                report += f"  ⚠️  {warning}\n"
        if not self.errors and not self.warnings:
            report += "✅ All validations passed\n"
        return report


# ============================================================================
# INSTALLATION & FILE MANAGEMENT
# ============================================================================

class ModelInstaller:
    """Handle model file installation with safety checks."""

    def __init__(self, source_dir: Path, dest_dir: Path):
        """Initialize installer."""
        self.source_dir = source_dir
        self.dest_dir = dest_dir
        self.model_name = source_dir.name
        self.backup_dir: Optional[Path] = None

    def install(self, dry_run: bool = False, overwrite: bool = False) -> Tuple[bool, str]:
        """
        Install model files from source to destination.

        Args:
            dry_run: If True, don't actually copy files
            overwrite: If True, overwrite existing model without backup

        Returns:
            (success, message)
        """
        logger.info(f"Installing model: {self.model_name}")

        # Check if model already installed (skip for dry-run)
        if not dry_run and self.dest_dir.exists():
            if not overwrite:
                msg = f"Model {self.model_name} already installed. Use --overwrite to replace."
                logger.warning(msg)
                return False, msg

            # Create backup
            if not self._create_backup():
                return False, "Failed to create backup of existing model"

        if dry_run:
            logger.info(f"[DRY-RUN] Would install to {self.dest_dir}")
            return True, "Dry-run OK (no files copied)"

        # Create destination directory
        self.dest_dir.mkdir(parents=True, exist_ok=True)

        # Copy files
        try:
            for filename in ModelValidator.REQUIRED_FILES:
                src = self.source_dir / filename
                dst = self.dest_dir / filename
                if src.exists():
                    shutil.copy2(src, dst)
                    logger.debug(f"Copied {filename} to {self.dest_dir}")

            logger.info(f"Successfully installed model: {self.model_name}")
            return True, f"Model installed to {self.dest_dir}"
        except Exception as e:
            logger.error(f"Installation failed: {e}")
            self._restore_backup()
            return False, f"Installation failed: {e}"

    def _create_backup(self) -> bool:
        """Create backup of existing model."""
        try:
            backup_name = f"{self.model_name}_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            self.backup_dir = self.dest_dir.parent / backup_name
            if self.dest_dir.exists():
                shutil.copytree(self.dest_dir, self.backup_dir)
                logger.info(f"Created backup at {self.backup_dir}")
            return True
        except Exception as e:
            logger.error(f"Backup creation failed: {e}")
            return False

    def _restore_backup(self) -> None:
        """Restore model from backup if available."""
        if self.backup_dir and self.backup_dir.exists():
            try:
                if self.dest_dir.exists():
                    shutil.rmtree(self.dest_dir)
                shutil.copytree(self.backup_dir, self.dest_dir)
                logger.info(f"Restored model from backup")
            except Exception as e:
                logger.error(f"Backup restore failed: {e}")


# ============================================================================
# INTEGRATION TESTING
# ============================================================================

class IntegrationTester:
    """Test integrated model with inference."""

    def __init__(self, model_name: str, metadata: ModelMetadata):
        """Initialize tester."""
        self.model_name = model_name
        self.metadata = metadata

    def run_inference_test(self) -> Tuple[bool, Optional[Dict[str, Any]], str]:
        """
        Run inference test with random test image.

        Returns:
            (success, inference_result, message)
        """
        logger.info(f"Starting inference test for {self.model_name}")

        try:
            # Import here to avoid circular imports
            from agents.vision.model_loader import ModelLoader
            import numpy as np

            # Create a test image with realistic size
            width, height = self.metadata.input_size
            test_image = np.random.randint(0, 256, (height, width, 3), dtype=np.uint8)
            logger.debug(f"Created test image: {width}x{height}")

            # Initialize loader
            loader = ModelLoader()
            start_time = time.time()

            # Run inference
            predictions = loader.predict(self.model_name, test_image)
            elapsed_ms = (time.time() - start_time) * 1000

            # Format result
            result = {
                "model": self.model_name,
                "detections": predictions,
                "execution_time_ms": elapsed_ms,
                "num_detections": len(predictions),
            }

            logger.info(
                f"Inference test passed: {len(predictions)} detections in {elapsed_ms:.1f}ms"
            )
            return True, result, f"Inference OK: {len(predictions)} detections"

        except Exception as e:
            logger.error(f"Inference test failed: {e}")
            return False, None, f"Inference test failed: {e}"


# ============================================================================
# REPORT GENERATION
# ============================================================================

class ReportGenerator:
    """Generate integration reports."""

    def __init__(self, reports_dir: Path = REPORTS_DIR):
        """Initialize generator."""
        self.reports_dir = reports_dir
        self.reports_dir.mkdir(parents=True, exist_ok=True)

    def generate_model_report(self, result: IntegrationResult) -> Path:
        """Generate report for single model."""
        filename = f"integration_report_{result.model_name}.md"
        filepath = self.reports_dir / filename

        lines = [
            f"# Integration Report: {result.model_name}",
            "",
            f"**Generated:** {result.end_time.isoformat()}",
            f"**Status:** {'✅ SUCCESS' if result.success else '❌ FAILED'}",
            "",
            "## Model Information",
            "",
        ]

        if result.metadata:
            m = result.metadata
            lines.extend([
                f"- **Model Name:** {m.model_name}",
                f"- **Author:** {m.author}",
                f"- **Version:** {m.version}",
                f"- **Framework:** {m.framework}",
                f"- **Input Size:** {m.input_size}",
                f"- **Description:** {m.description or 'N/A'}",
                "",
            ])

        lines.extend([
            "## Files",
            "",
        ])

        for filename in result.files_validated:
            lines.append(f"- ✅ {filename}")

        if result.labels:
            lines.extend([
                "",
                "## Labels",
                "",
                f"**Count:** {len(result.labels)}",
                "",
                "```",
            ])
            lines.extend(result.labels)
            lines.append("```")

        if result.inference_result:
            lines.extend([
                "",
                "## Inference Test Result",
                "",
                "```json",
                json.dumps(result.inference_result, indent=2),
                "```",
            ])

        lines.extend([
            "",
            "## Execution Summary",
            "",
            f"- **Start Time:** {result.start_time.isoformat()}",
            f"- **End Time:** {result.end_time.isoformat()}",
            f"- **Duration:** {result.execution_time_ms:.1f}ms",
            "",
        ])

        if result.error:
            lines.extend([
                "## Error",
                "",
                f"```\n{result.error}\n```",
                "",
            ])

        if result.warning:
            lines.extend([
                "## Warnings",
                "",
                f"```\n{result.warning}\n```",
                "",
            ])

        with open(filepath, "w") as f:
            f.write("\n".join(lines))

        logger.info(f"Report generated: {filepath}")
        return filepath

    def generate_batch_report(self, results: List[IntegrationResult]) -> Path:
        """Generate summary report for batch integration."""
        filename = f"integration_batch_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        filepath = self.reports_dir / filename

        successful = [r for r in results if r.success]
        failed = [r for r in results if not r.success]

        lines = [
            "# Batch Integration Report",
            "",
            f"**Generated:** {datetime.now().isoformat()}",
            f"**Total Models:** {len(results)}",
            f"**Successful:** {len(successful)}",
            f"**Failed:** {len(failed)}",
            "",
            "## Summary",
            "",
        ]

        if successful:
            lines.extend([
                "### ✅ Successfully Integrated",
                "",
            ])
            for r in successful:
                lines.append(f"- {r.model_name} (v{r.metadata.version if r.metadata else 'N/A'})")

        if failed:
            lines.extend([
                "",
                "### ❌ Failed Integration",
                "",
            ])
            for r in failed:
                error = r.error or "Unknown error"
                lines.append(f"- {r.model_name}: {error}")

        lines.extend([
            "",
            "## Statistics",
            "",
            f"- **Total Duration:** {sum(r.execution_time_ms for r in results):.1f}ms",
            f"- **Average Duration:** {sum(r.execution_time_ms for r in results) / len(results):.1f}ms",
            "",
        ])

        with open(filepath, "w") as f:
            f.write("\n".join(lines))

        logger.info(f"Batch report generated: {filepath}")
        return filepath


# ============================================================================
# MAIN INTEGRATION ORCHESTRATOR
# ============================================================================

class ModelIntegrator:
    """Orchestrate complete model integration workflow."""

    def __init__(self, model_name: str, dry_run: bool = False, overwrite: bool = False, verbose: bool = False):
        """Initialize integrator."""
        self.model_name = model_name
        self.dry_run = dry_run
        self.overwrite = overwrite
        self.verbose = verbose
        self.source_dir = TRAINING_DIR / model_name
        self.dest_dir = MODELS_DIR / model_name

    def integrate(self) -> IntegrationResult:
        """Execute complete integration workflow."""
        start_time = datetime.now()
        result = IntegrationResult(
            model_name=self.model_name,
            success=False,
            start_time=start_time,
            end_time=start_time,
            files_validated=[],
            labels=[],
        )

        try:
            # Step 1: Check source directory
            if not self.source_dir.exists():
                result.error = f"Model directory not found: {self.source_dir}"
                logger.error(result.error)
                result.end_time = datetime.now()
                result.execution_time_ms = (result.end_time - start_time).total_seconds() * 1000
                return result

            logger.info(f"=== Integrating {self.model_name} ===")

            # Step 2: Validate model
            validator = ModelValidator(self.source_dir)
            valid, metadata, labels = validator.validate_all()

            result.metadata = metadata
            result.labels = labels
            result.files_validated = list(ModelValidator.REQUIRED_FILES)

            if not valid:
                result.error = "Validation failed"
                for error in validator.errors:
                    logger.error(error)
                logger.warning(validator.report())
                result.end_time = datetime.now()
                result.execution_time_ms = (result.end_time - start_time).total_seconds() * 1000
                return result

            # Step 3: Install model
            installer = ModelInstaller(self.source_dir, self.dest_dir)
            install_ok, install_msg = installer.install(
                dry_run=self.dry_run,
                overwrite=self.overwrite,
            )

            if not install_ok:
                result.error = install_msg
                result.end_time = datetime.now()
                result.execution_time_ms = (result.end_time - start_time).total_seconds() * 1000
                return result

            logger.info(install_msg)

            # Step 4: Register model
            if not self.dry_run:
                try:
                    from agents.vision.model_loader import ModelLoader
                    loader = ModelLoader()
                    loader.refresh_models()
                    logger.info(f"Model registered and loaded: {self.model_name}")
                except Exception as e:
                    result.warning = f"Registration partial: {e}"
                    logger.warning(result.warning)

            # Step 5: Run inference test
            if not self.dry_run:
                tester = IntegrationTester(self.model_name, metadata)
                test_ok, test_result, test_msg = tester.run_inference_test()
                result.inference_result = test_result
                if not test_ok:
                    result.warning = test_msg
                    logger.warning(test_msg)

            # Step 6: Generate report
            reporter = ReportGenerator()
            reporter.generate_model_report(result)

            result.success = True
            result.end_time = datetime.now()
            result.execution_time_ms = (result.end_time - start_time).total_seconds() * 1000

            logger.info(f"✅ Successfully integrated {self.model_name} in {result.execution_time_ms:.1f}ms")
            return result

        except Exception as e:
            logger.exception(f"Integration failed with exception: {e}")
            result.error = str(e)
            result.end_time = datetime.now()
            result.execution_time_ms = (result.end_time - start_time).total_seconds() * 1000
            return result


# ============================================================================
# BATCH OPERATIONS
# ============================================================================

def discover_models() -> List[str]:
    """Discover all available models in training directory."""
    if not TRAINING_DIR.exists():
        return []

    models = []
    for item in TRAINING_DIR.iterdir():
        if item.is_dir() and (item / "metadata.json").exists():
            models.append(item.name)

    return sorted(models)


def integrate_all(dry_run: bool = False, verbose: bool = False) -> List[IntegrationResult]:
    """Integrate all available models."""
    models = discover_models()
    results = []

    logger.info(f"Discovered {len(models)} models: {models}")

    for model_name in models:
        if model_name == "model_template":
            logger.debug(f"Skipping template directory: {model_name}")
            continue

        try:
            integrator = ModelIntegrator(
                model_name,
                dry_run=dry_run,
                verbose=verbose,
            )
            result = integrator.integrate()
            results.append(result)
        except Exception as e:
            logger.error(f"Failed to integrate {model_name}: {e}")
            result = IntegrationResult(
                model_name=model_name,
                success=False,
                start_time=datetime.now(),
                end_time=datetime.now(),
                error=str(e),
                files_validated=[],
                labels=[],
            )
            results.append(result)

    return results


def list_models() -> None:
    """List all available models."""
    models = discover_models()
    installed = [d.name for d in MODELS_DIR.iterdir() if d.is_dir()] if MODELS_DIR.exists() else []

    print("\n📦 Available Models in training/:")
    for model in models:
        status = "✅ Installed" if model in installed else "⏳ Not installed"
        print(f"  - {model:<30} {status}")

    if not models:
        print("  (No models found)")


# ============================================================================
# CLI
# ============================================================================

def main() -> int:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Vision Assistant Model Integration System",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python scripts/integrate_model.py people_detector
  python scripts/integrate_model.py --all
  python scripts/integrate_model.py --list
  python scripts/integrate_model.py people_detector --validate
  python scripts/integrate_model.py people_detector --dry-run
        """,
    )

    parser.add_argument(
        "model",
        nargs="?",
        default=None,
        help="Model name to integrate (e.g., people_detector)",
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="Integrate all discovered models",
    )
    parser.add_argument(
        "--list",
        action="store_true",
        help="List available models",
    )
    parser.add_argument(
        "--validate",
        action="store_true",
        help="Validate model without installation",
    )
    parser.add_argument(
        "--report",
        action="store_true",
        help="Display integration reports",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Run without actually copying files",
    )
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Overwrite existing model",
    )
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Verbose output",
    )

    args = parser.parse_args()

    # Handle --list
    if args.list:
        list_models()
        return 0

    # Handle --all
    if args.all:
        logger.info("Starting batch integration of all models")
        results = integrate_all(dry_run=args.dry_run, verbose=args.verbose)

        # Generate batch report
        reporter = ReportGenerator()
        reporter.generate_batch_report(results)

        # Summary
        successful = sum(1 for r in results if r.success)
        print(f"\n{'=' * 60}")
        print(f"Batch Integration Complete")
        print(f"{'=' * 60}")
        print(f"Total models:    {len(results)}")
        print(f"Successful:      {successful}")
        print(f"Failed:          {len(results) - successful}")
        print(f"Reports:         {REPORTS_DIR}")
        print(f"Logs:            {INTEGRATION_LOG}")
        print(f"{'=' * 60}\n")

        return 0 if successful == len(results) else 1

    # Handle single model
    if not args.model:
        parser.print_help()
        return 1

    # Validation only
    if args.validate:
        source_dir = TRAINING_DIR / args.model
        if not source_dir.exists():
            logger.error(f"Model not found: {source_dir}")
            return 1

        validator = ModelValidator(source_dir)
        valid, metadata, labels = validator.validate_all()
        print(validator.report())
        return 0 if valid else 1

    # Full integration
    logger.info(f"Starting integration of {args.model}")
    integrator = ModelIntegrator(
        args.model,
        dry_run=args.dry_run,
        overwrite=args.overwrite,
        verbose=args.verbose,
    )
    result = integrator.integrate()

    print(f"\n{'=' * 60}")
    print(f"Integration Result: {args.model}")
    print(f"{'=' * 60}")
    print(f"Status:           {'✅ SUCCESS' if result.success else '❌ FAILED'}")
    print(f"Duration:         {result.execution_time_ms:.1f}ms")
    if result.metadata:
        print(f"Version:          {result.metadata.version}")
        print(f"Framework:        {result.metadata.framework}")
    if result.inference_result:
        print(f"Detections:       {result.inference_result.get('num_detections', 0)}")
    if result.error:
        print(f"Error:            {result.error}")
    if result.warning:
        print(f"Warning:          {result.warning}")
    print(f"Report:           {REPORTS_DIR / f'integration_report_{args.model}.md'}")
    print(f"{'=' * 60}\n")

    return 0 if result.success else 1


if __name__ == "__main__":
    sys.exit(main())
