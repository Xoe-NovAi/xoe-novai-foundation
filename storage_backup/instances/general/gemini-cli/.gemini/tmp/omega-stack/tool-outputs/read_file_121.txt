"""
Simple local model registry (skeleton).

Allows registering local GGUF/ONNX/ggml models for agent use. Registry is a JSON file under models/registry.json.
"""

import json
import os
from typing import Optional

REGISTRY_PATH = os.getenv("MODEL_REGISTRY_PATH", "models/registry.json")


class ModelRegistry:
    def __init__(self, registry_path: str = REGISTRY_PATH):
        self.registry_path = registry_path
        os.makedirs(os.path.dirname(self.registry_path), exist_ok=True)
        if not os.path.exists(self.registry_path):
            with open(self.registry_path, "w") as f:
                json.dump({}, f)

    def _load(self) -> dict:
        with open(self.registry_path, "r") as f:
            return json.load(f)

    def _save(self, data: dict):
        with open(self.registry_path, "w") as f:
            json.dump(data, f, indent=2)

    def register_model(self, name: str, path: str, metadata: Optional[dict] = None):
        data = self._load()
        data[name] = {"path": path, "metadata": metadata or {}}
        self._save(data)

    def get_model(self, name: str) -> Optional[dict]:
        data = self._load()
        return data.get(name)

    def list_models(self) -> list:
        data = self._load()
        return list(data.keys())
