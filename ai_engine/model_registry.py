"""
SentinelAI - Model Registry
Stores trained models + metadata for versioning.

Each model version records:
  - model_version
  - training_date
  - accuracy / metrics
  - feature list
  - path to model artifacts
"""

import json
import os
import shutil
from datetime import datetime
from typing import Any, Dict, List, Optional


class ModelRegistry:
    """Registry for managing versioned AI model artifacts."""

    def __init__(self, registry_dir: str = 'output/models') -> None:
        self.registry_dir = registry_dir
        self.metadata_file = os.path.join(registry_dir, 'registry.json')
        os.makedirs(registry_dir, exist_ok=True)
        self._registry: Dict[str, Any] = self._load_registry()

    def _load_registry(self) -> Dict[str, Any]:
        """Load registry metadata from disk."""
        if os.path.exists(self.metadata_file):
            try:
                with open(self.metadata_file, 'r') as f:
                    return json.load(f)
            except Exception:
                return {'versions': []}
        return {'versions': []}

    def _save_registry(self) -> None:
        """Persist registry metadata."""
        with open(self.metadata_file, 'w') as f:
            json.dump(self._registry, f, indent=2)

    def register_model(
        self,
        version: str,
        model_path: str,
        metrics: Dict[str, Any],
        features: List[str],
        model_type: str = 'isolation_forest+xgboost'
    ) -> Dict[str, Any]:
        """
        Register a trained model version.

        Args:
            version: Semantic model version (e.g. 'v1.0.0')
            model_path: Directory containing model artifacts
            metrics: Dict of performance metrics (accuracy, precision, etc.)
            features: List of feature names used
            model_type: Description of the model architecture
        """
        entry = {
            'model_version': version,
            'training_date': datetime.now().isoformat(),
            'model_type': model_type,
            'metrics': metrics,
            'features': features,
            'model_path': model_path,
            'status': 'active'
        }

        # Promote previous active to 'archived'
        for existing in self._registry.get('versions', []):
            if existing.get('status') == 'active':
                existing['status'] = 'archived'

        self._registry.setdefault('versions', []).append(entry)
        self._save_registry()
        print(f"📦 Model {version} registered and set active")
        return entry

    def get_active_model(self) -> Optional[Dict[str, Any]]:
        """Get the currently active model version."""
        for v in self._registry.get('versions', []):
            if v.get('status') == 'active':
                return v
        return None

    def get_all_versions(self) -> List[Dict[str, Any]]:
        """List all registered model versions."""
        return self._registry.get('versions', [])

    def get_version(self, version: str) -> Optional[Dict[str, Any]]:
        """Get a specific model version by name."""
        for v in self._registry.get('versions', []):
            if v.get('model_version') == version:
                return v
        return None

    def export_metadata(self, path: Optional[str] = None) -> Dict[str, Any]:
        """Export registry metadata (optionally to a file)."""
        data = self._registry
        if path:
            with open(path, 'w') as f:
                json.dump(data, f, indent=2)
        return data

    def copy_artifacts(self, source_dir: str, version: str) -> str:
        """Copy model artifacts into a versioned directory."""
        dest = os.path.join(self.registry_dir, version)
        os.makedirs(dest, exist_ok=True)
        for fname in os.listdir(source_dir):
            src = os.path.join(source_dir, fname)
            if os.path.isfile(src):
                shutil.copy2(src, os.path.join(dest, fname))
        return dest
