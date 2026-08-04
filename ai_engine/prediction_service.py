"""
SentinelAI - Prediction Service
Orchestrates the full AI pipeline exposed as a service layer.

Exposes:
  - PredictionService (high-level API)
  - RiskEngine (from models)
  - FeatureService (FeatureEngineer)
  - BehaviourBaseline

Metadata only: never inspects file contents.
"""

import os
import sys
from typing import Any, Dict, List, Optional

import pandas as pd

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ai_engine.behaviour_baseline import BehaviourBaseline
from ai_engine.feature_engineering import FeatureEngineer
from ai_engine.models import RiskEngine
from ai_engine.rule_correlation import RuleCorrelationEngine
from ai_engine.explainability import ExplainabilityEngine
from ai_engine.model_registry import ModelRegistry

# Vector file names
VECTOR_FILES = {
    'login_events': 'login_events.csv',
    'usb_events': 'usb_events.csv',
    'cloud_events': 'cloud_events.csv',
    'network_events': 'network_events.csv',
    'browser_events': 'browser_events.csv',
    'email_events': 'email_events.csv',
    'application_events': 'application_events.csv'
}


class PredictionService:
    """
    High-level service that ties together feature engineering, baseline,
    models, correlation, and explainability.

    Dependency injection: components are injected so they can be swapped.
    """

    def __init__(
        self,
        feature_engineer: Optional[FeatureEngineer] = None,
        baseline: Optional[BehaviourBaseline] = None,
        risk_engine: Optional[RiskEngine] = None,
        correlation: Optional[RuleCorrelationEngine] = None,
        explainability: Optional[ExplainabilityEngine] = None,
        registry: Optional[ModelRegistry] = None
    ) -> None:
        self.feature_engineer = feature_engineer or FeatureEngineer()
        self.baseline = baseline or BehaviourBaseline()
        self.risk_engine = risk_engine or RiskEngine()
        self.correlation = correlation or RuleCorrelationEngine()
        self.explainability = explainability or ExplainabilityEngine()
        self.registry = registry or ModelRegistry()

        self.employees: Optional[pd.DataFrame] = None
        self.events: Dict[str, pd.DataFrame] = {}
        self.features: Optional[pd.DataFrame] = None
        self.results: Optional[pd.DataFrame] = None
        self._loaded = False

    # === Loaders ===

    def load_dataset(self, dataset_dir: str = 'dataset') -> None:
        """Load employees and per-vector event CSVs from disk."""
        self.employees = pd.read_csv(os.path.join(dataset_dir, 'employees.csv'))
        for key, fname in VECTOR_FILES.items():
            path = os.path.join(dataset_dir, fname)
            if os.path.exists(path):
                self.events[key] = pd.read_csv(path)
            else:
                self.events[key] = pd.DataFrame()
        self._loaded = True
        print(f"📥 Loaded {len(self.employees)} employees and {len(self.events)} vector files")

    def set_data(self, employees: pd.DataFrame, events: Dict[str, pd.DataFrame]) -> None:
        """Inject pre-loaded data (useful for tests)."""
        self.employees = employees
        self.events = events
        self._loaded = True

    # === Full pipeline ===

    def train(self, train_ratio: float = 0.8) -> Dict[str, Any]:
        """
        Run the full training pipeline: baseline + features + models.
        Returns a summary dict.
        """
        if not self._loaded:
            raise RuntimeError("Dataset not loaded. Call load_dataset() or set_data() first.")

        # 1. Build behaviour baselines
        self.baseline.attach_events(self.events)
        self.baseline.fit(self.employees, self.events)

        # 2. Engineer features
        self.features = self.feature_engineer.create_feature_matrix(self.employees, self.events)

        # 3. Train AI models
        self.risk_engine.train(self.features)

        # 4. Evaluate all employees
        print("📊 Evaluating all employees...")
        results = self.risk_engine.evaluate_all(self.features)
        self.results = pd.DataFrame(results)

        # 5. Register model
        version = f"v1.{self._next_patch()}"
        metrics = self._compute_metrics()
        registry_entry = self.registry.register_model(
            version=version,
            model_path='output/models/',
            metrics=metrics,
            features=self.feature_engineer.get_all_feature_names()
        )

        summary = {
            'model_version': version,
            'trained_at': registry_entry['training_date'],
            'metrics': metrics,
            'employees_evaluated': len(self.results),
            'risk_distribution': self._risk_distribution()
        }
        print(f"✅ Training complete. Model {version} registered.")
        return summary

    def _next_patch(self) -> int:
        """Increment patch version based on existing versions."""
        versions = self.registry.get_all_versions()
        return len(versions) + 1

    def _compute_metrics(self) -> Dict[str, Any]:
        """Compute basic metrics from results (accuracy proxy)."""
        if self.results is None or self.features is None:
            return {'note': 'no results'}
        # Map risk score to predicted class vs risk_profile
        try:
            pred = (self.results['risk_score'] > 50).astype(int)
            actual = self.features['risk_profile'].values[:len(pred)]
            accuracy = float((pred.values == actual).mean())
            return {
                'accuracy': round(accuracy, 3),
                'mean_risk': round(float(self.results['risk_score'].mean()), 2),
                'critical_count': int((self.results['risk_score'] > 80).sum())
            }
        except Exception:
            return {'note': 'metrics unavailable'}

    def _risk_distribution(self) -> Dict[str, int]:
        """Compute risk distribution from results."""
        if self.results is None:
            return {}
        return {
            'safe': int((self.results['risk_score'] <= 20).sum()),
            'low': int(((self.results['risk_score'] > 20) & (self.results['risk_score'] <= 40)).sum()),
            'medium': int(((self.results['risk_score'] > 40) & (self.results['risk_score'] <= 60)).sum()),
            'high': int(((self.results['risk_score'] > 60) & (self.results['risk_score'] <= 80)).sum()),
            'critical': int((self.results['risk_score'] > 80).sum())
        }

    # === Prediction ===

    def predict_employee(self, employee_id: str) -> Dict[str, Any]:
        """
        Predict risk for a single employee with full explainability.
        Combines Isolation Forest score + baseline deviation + correlation.
        """
        if not self._loaded:
            raise RuntimeError("Dataset not loaded.")

        # Base risk from AI model
        base_assessment = self.risk_engine.evaluate_employee(self.features, employee_id)

        # Behaviour baseline deviation
        current = self.baseline.build_recent_features(employee_id)
        deviation = self.baseline.score_deviation(employee_id, current)

        # Correlation
        correlation = self.correlation.correlate(deviation.get('deviations', {}), employee_id)

        # Aggregate final risk score
        ml_score = base_assessment.get('risk_score', 50)
        anomaly_score = deviation.get('total_anomaly_score', 0) * 100
        correlation_score = correlation.get('correlation_score', 0) * 100

        final_score = 0.5 * ml_score + 0.3 * anomaly_score + 0.2 * correlation_score
        final_score = min(final_score, 100.0)

        # Confidence: blend model confidence + correlation
        base_confidence = base_assessment.get('confidence', 0.7)
        confidence = min(0.5 * base_confidence + 0.3 * correlation.get('correlation_score', 0.5) + 0.2, 0.99)

        # Explainability
        explanation = self.explainability.explain(
            risk_score=final_score,
            confidence=confidence,
            deviations=deviation.get('deviations', {}),
            correlation=correlation,
            shap_values=base_assessment.get('shap_values', []),
            employee_id=employee_id
        )

        return {
            **explanation,
            'ml_risk_score': round(float(ml_score), 2),
            'anomaly_score': round(float(anomaly_score), 2),
            'correlation_score': round(float(correlation_score), 2),
            'is_anomaly': final_score > 60,
            'model_version': base_assessment.get('model_version', 'SentinelAI v1.0')
        }

    def predict_all(self) -> List[Dict[str, Any]]:
        """Predict risk for all employees."""
        if self.employees is None:
            return []
        return [self.predict_employee(eid) for eid in self.employees['employee_id']]

    def get_risk_history(self, employee_id: str, days: int = 30) -> List[Dict[str, Any]]:
        """Return mock risk history for an employee (used by API)."""
        import random
        from datetime import datetime, timedelta
        history = []
        for i in range(days):
            date = datetime.now() - timedelta(days=days - i - 1)
            score = self._history_score(employee_id, i)
            history.append({
                'date': date.strftime('%Y-%m-%d'),
                'risk_score': round(score, 1),
                'threat_level': self._level(score)
            })
        return history

    def _history_score(self, employee_id: str, index: int) -> float:
        """Deterministic pseudo-history score for an employee."""
        base = 20 + (hash(employee_id) % 20)
        return min(base + index * 0.5, 95)

    def _level(self, score: float) -> str:
        if score <= 20:
            return 'Safe'
        if score <= 40:
            return 'Low'
        if score <= 60:
            return 'Medium'
        if score <= 80:
            return 'High'
        return 'Critical'

    def get_employee_baseline(self, employee_id: str) -> Dict[str, Any]:
        """Return the behaviour baseline for an employee."""
        return self.baseline.get_baseline(employee_id)

    def get_high_risk_employees(self, threshold: float = 60.0) -> List[Dict[str, Any]]:
        """Return employees above a risk threshold."""
        if self.results is None:
            return []
        high = self.results[self.results['risk_score'] > threshold]
        return high.to_dict('records')

    # === Compatibility aliases ===

    @property
    def risk_engine_instance(self) -> RiskEngine:
        """Alias for external access to RiskEngine."""
        return self.risk_engine

    @property
    def baseline_engine(self) -> BehaviourBaseline:
        """Alias for external access to BehaviourBaseline."""
        return self.baseline

    @property
    def feature_service(self) -> FeatureEngineer:
        """Alias for external access to FeatureEngineer."""
        return self.feature_engineer


def create_prediction_service() -> PredictionService:
    """Factory to build a PredictionService with injected dependencies."""
    return PredictionService(
        feature_engineer=FeatureEngineer(),
        baseline=BehaviourBaseline(),
        risk_engine=RiskEngine(),
        correlation=RuleCorrelationEngine(),
        explainability=ExplainabilityEngine(),
        registry=ModelRegistry()
    )


if __name__ == '__main__':
    svc = create_prediction_service()
    svc.load_dataset('dataset')
    summary = svc.train()
    print(summary)
    # Demo prediction
    top = svc.get_high_risk_employees(80)
    if top:
        emp_id = top[0]['employee_id']
        print(f"\n🔍 Prediction for {emp_id}:")
        print(svc.predict_employee(emp_id))
