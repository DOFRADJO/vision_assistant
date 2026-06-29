"""Registry for registering detector models and runtime state."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List


@dataclass(slots=True)
class RegisteredModel:
    name: str
    category: str
    labels: List[str] = field(default_factory=list)


class ModelRegistry:
    def __init__(self) -> None:
        self._models: Dict[str, RegisteredModel] = {}

    def register(self, model: RegisteredModel) -> None:
        self._models[model.name] = model

    def list_models(self) -> List[RegisteredModel]:
        return list(self._models.values())

    def get(self, name: str) -> RegisteredModel | None:
        return self._models.get(name)
