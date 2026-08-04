"""
SentinelAI - AI Service Integration
Bridges the ai_engine PredictionService with the FastAPI backend.

Provides:
  - a lazily-initialized singleton PredictionService
  - cached predictions for performance
  - helper methods mirroring the API endpoints
  - WebSocket-driven alert broadcast hooks

Metadata only: never inspects file contents.
"""

import os
import sys
import threading
from typing import Any, Dict, List, Optional

import pandas as pd

# Ensure parent dir is on path so `ai_engine` is importable
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ai_engine.prediction_service import create_prediction_service, PredictionService

# Resolve dataset directory relative to repo root
REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATASET_DIR = os.path.join(REPO_ROOT, 'dataset')


class AIService:
    """
    Thread-safe wrapper around PredictionService with result caching.
    Lazily loads the dataset and trains/loads the model on first use.
    """

    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._service: Optional[PredictionService] = None
        self._ready = False
        self._cache: Dict[str, Dict[str, Any]] = {}
        self._cache_ttl = 300  # seconds

    # === Lifecycle ===

    def _ensure_ready(self) -> PredictionService:
        """Initialize the service if not already done (thread-safe)."""
        if self._ready and self._service is not None:
            return self._service
        with self._lock:
            if self._ready and self._service is not None:
                return self._service
            self._service = create_prediction_service()
            try:
                self._service.load_dataset(DATASET_DIR)
                # Light-weight: don't force full SHAP training on boot.
                # Train in background or on demand.
                self._service.train()
            except Exception as e:
                print(f"⚠️ AI service init warning: {e}")
            self._ready = True
            return self._service

    def force_train(self) -> Dict[str, Any]:
        """Force a full retrain (used by /api/ai/train)."""
        self._ensure_ready()
        self._cache.clear()
        return self._service.train()

# === Prediction helpers ===

    def predict(self, employee_id: str) -> Dict[str, Any]:
        """Predict risk for a single employee with explainability."""
        svc = self._ensure_ready()
        return svc.predict_employee(employee_id)

    def predict_all(self) -> List[Dict[str, Any]]:
        """Predict risk for all employees (compact, used for live alerts)."""
        svc = self._ensure_ready()
        return svc.predict_all()

    def predict_employee_cached(self, employee_id: str) -> Dict[str, Any]:
        """Cached prediction for an employee."""
        cached = self._cache.get(employee_id)
        if cached:
            return cached
        result = self.predict(employee_id)
        self._cache[employee_id] = result
        return result

    def get_employee_risk(self, employee_id: str) -> Dict[str, Any]:
        """Return a compact risk payload for an employee (for dashboards)."""
        try:
            result = self.predict_employee_cached(employee_id)
            return {
                'employee_id': employee_id,
                'risk_score': result.get('risk_score', 0),
                'threat_level': result.get('threat_level', 'Safe'),
                'confidence': result.get('confidence', 0),
                'model_version': result.get('model_version', 'SentinelAI v1.0'),
                'timestamp': result.get('timestamp', '')
            }
        except Exception as e:
            return {
                'employee_id': employee_id,
                'risk_score': 0,
                'threat_level': 'Safe',
                'confidence': 0,
                'error': str(e)
            }

    def get_risk_history(self, employee_id: str, days: int = 30) -> List[Dict[str, Any]]:
        """Return risk history for an employee."""
        svc = self._ensure_ready()
        return svc.get_risk_history(employee_id, days)

    def get_high_risk(self, threshold: float = 60.0, limit: int = 10) -> List[Dict[str, Any]]:
        """Return high-risk employees (compact)."""
        svc = self._ensure_ready()
        results = svc.predict_all()
        high = [r for r in results if r['risk_score'] > threshold]
        high.sort(key=lambda x: x['risk_score'], reverse=True)
        return [
            {
                'employee_id': r['employee_id'],
                'risk_score': r['risk_score'],
                'threat_level': r['threat_level'],
                'confidence': r['confidence'],
                'reasons': r['reasons'][:3]
            }
            for r in high[:limit]
        ]

    def get_baseline(self, employee_id: str) -> Dict[str, Any]:
        """Return behavioural baseline for an employee."""
        svc = self._ensure_ready()
        return svc.get_employee_baseline(employee_id)

    def get_model_info(self) -> Dict[str, Any]:
        """Return active model version + registry info."""
        svc = self._ensure_ready()
        active = svc.registry.get_active_model()
        return {
            'active_model': active,
            'versions': svc.registry.get_all_versions()
        }

    def get_risk_distribution(self) -> Dict[str, int]:
        """Return risk distribution across all employees."""
        svc = self._ensure_ready()
        return svc._risk_distribution()

    def get_dashboard_stats(self) -> Dict[str, Any]:
        """Return combined dashboard stats from the AI engine."""
        svc = self._ensure_ready()
        dist = svc._risk_distribution()
        results = svc.predict_all()
        total = len(results)
        avg = sum(r['risk_score'] for r in results) / max(total, 1)
        return {
            'total_employees': total,
            'high_risk_employees': dist.get('high', 0) + dist.get('critical', 0),
            'critical_risk_employees': dist.get('critical', 0),
            'average_risk_score': round(avg, 2),
            'risk_distribution': dist
        }


# Global singleton
ai_service = AIService()


def get_ai_service() -> AIService:
    """Dependency-injection getter for the AI service."""
    return ai_service
