"""Registry for model labels found under the workspace `models/` directory.

Loads `labels.txt` from each model subfolder and provides helpers
to check available labels and mappings model->labels.
"""
from __future__ import annotations

import os
from typing import Dict, List, Set


class LabelsRegistry:
    _instance: "LabelsRegistry" | None = None

    def __init__(self, models_dir: str = "models") -> None:
        self.models_dir = models_dir
        self.model_to_labels: Dict[str, List[str]] = {}
        self.label_set: Set[str] = set()
        self._load()

    @classmethod
    def get_instance(cls, models_dir: str | None = None) -> "LabelsRegistry":
        if cls._instance is None:
            cls._instance = LabelsRegistry(models_dir or "models")
        return cls._instance

    def _load(self) -> None:
        if not os.path.isdir(self.models_dir):
            return

        for entry in os.listdir(self.models_dir):
            model_path = os.path.join(self.models_dir, entry)
            if not os.path.isdir(model_path):
                continue
            labels_file = os.path.join(model_path, "labels.txt")
            if not os.path.isfile(labels_file):
                continue
            try:
                with open(labels_file, "r", encoding="utf-8") as fh:
                    labels = [line.strip() for line in fh.readlines() if line.strip()]
                normalized = [lbl.lower() for lbl in labels]
                self.model_to_labels[entry] = normalized
                for lbl in normalized:
                    self.label_set.add(lbl)
            except Exception:
                # best-effort load; skip models we can't read
                continue

    def has_label(self, label: str) -> bool:
        return label.lower() in self.label_set

    def labels_for_model(self, model_name: str) -> List[str]:
        return self.model_to_labels.get(model_name, [])
