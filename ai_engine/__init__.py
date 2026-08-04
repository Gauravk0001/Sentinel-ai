"""
SentinelAI - AI Engine Package.

Exposes the public API for the AI engine:
  - PredictionService (orchestrator)
  - RiskEngine (models + scoring)
  - FeatureEngineer (feature engineering)
  - BehaviourBaseline (baseline engine)
  - RuleCorrelationEngine (alert correlation)
  - ExplainabilityEngine (explainable risk)
  - ModelRegistry (model versioning)
"""

from ai_engine.prediction_service import PredictionService, create_prediction_service
from ai_engine.models import RiskEngine, AnomalyDetector, XGBoostRiskScorer, SHAPExplainer
from ai_engine.feature_engineering import FeatureEngineer
from ai_engine.behaviour_baseline import BehaviourBaseline
from ai_engine.rule_correlation import RuleCorrelationEngine
from ai_engine.explainability import ExplainabilityEngine
from ai_engine.model_registry import ModelRegistry

__all__ = [
    'PredictionService',
    'create_prediction_service',
    'RiskEngine',
    'AnomalyDetector',
    'XGBoostRiskScorer',
    'SHAPExplainer',
    'FeatureEngineer',
    'BehaviourBaseline',
    'RuleCorrelationEngine',
    'ExplainabilityEngine',
    'ModelRegistry',
]
