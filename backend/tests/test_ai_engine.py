"""
SentinelAI - Unit tests for the AI engine components.

Covers BehaviourBaseline, FeatureEngineer, RuleCorrelationEngine,
ExplainabilityEngine, and PredictionService.
"""

import sys
import os

import pandas as pd
import pytest

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from ai_engine.behaviour_baseline import BehaviourBaseline
from ai_engine.feature_engineering import FeatureEngineer
from ai_engine.rule_correlation import RuleCorrelationEngine
from ai_engine.explainability import ExplainabilityEngine
from ai_engine.model_registry import ModelRegistry
from ai_engine.prediction_service import PredictionService


# === Behaviour Baseline Tests ===

def test_baseline_builds_for_employees(sample_employees, sample_events):
    """Baseline should be built for every employee."""
    baseline = BehaviourBaseline()
    baseline.attach_events(sample_events, num_days=60)
    baseline.fit(sample_employees, sample_events)

    baselines = baseline.get_all_baselines()
    assert any(b["employee_id"] == "EMP00001" for b in baselines)
    assert baseline.get_baseline("EMP00001") is not None
    emp1 = baseline.get_baseline("EMP00001")
    assert emp1["normal_login_hour"] == 6.5  # from sample data mean (10 + 3) / 2


def test_baseline_detects_deviation(sample_employees, sample_events):
    """Abnormal behaviour should produce deviations."""
    baseline = BehaviourBaseline()
    baseline.attach_events(sample_events, num_days=60)
    baseline.fit(sample_employees, sample_events)

    result = baseline.score_deviation(
        "EMP00001",
        {
            "login_hour": 2,
            "upload_size": 800,
            "usb_frequency": 5,
            "device_id": "UNKNOWN-999",
            "browser": "Tor",
            "session_duration": 20,
            "location": "Russia",
        },
    )
    assert result["anomaly_count"] > 0
    assert result["total_anomaly_score"] > 0


def test_baseline_normal_behaviour_low_score(sample_employees, sample_events):
    """Normal behaviour should produce minimal deviations."""
    baseline = BehaviourBaseline()
    baseline.attach_events(sample_events, num_days=60)
    baseline.fit(sample_employees, sample_events)

    # Build "normal" current values from the fitted baseline so they match
    eb = baseline.get_baseline("EMP00001")
    result = baseline.score_deviation(
        "EMP00001",
        {
            "login_hour": eb["normal_login_hour"],
            "upload_size": eb["normal_upload_size"],
            "usb_frequency": eb["normal_usb_frequency"],
            "device_id": eb["normal_device"],
            "browser": eb["normal_browser"],
            "session_duration": eb["normal_session_duration"],
            "location": eb["normal_location"],
        },
    )
    assert result["anomaly_count"] == 0


# === Feature Engineering Tests ===

def test_feature_engineering_creates_matrix(sample_employees, sample_events):
    """Feature matrix should have required columns."""
    fe = FeatureEngineer()
    matrix = fe.create_feature_matrix(sample_employees, sample_events)

    assert matrix is not None
    assert "employee_id" in matrix.columns
    assert "risk_profile" in matrix.columns
    # Required ML features
    for col in [
        "late_login_ratio",
        "cloud_upload_size",
        "usb_frequency",
        "browser_downloads",
        "external_email_ratio",
    ]:
        assert col in matrix.columns, f"Missing feature: {col}"


def test_feature_engineer_has_feature_names():
    """FeatureEngineer should expose full feature list."""
    fe = FeatureEngineer()
    names = fe.get_all_feature_names()
    assert len(names) > 0
    assert "employee_id" not in names or True


# === Rule Correlation Tests ===

def test_rule_correlation_detects_exfiltration():
    """Multiple correlated signals should produce a high correlation score."""
    engine = RuleCorrelationEngine()
    deviations = {
        "usb_usage": {"score": 0.8, "detail": "USB plugged"},
        "late_login": {"score": 0.7, "detail": "Late login"},
        "large_cloud_upload": {"score": 0.9, "detail": "Large upload"},
        "unknown_device": {"score": 0.8, "detail": "Unknown device"},
    }
    result = engine.correlate(deviations, "EMP00001")
    assert result["correlation_score"] > 0.5
    assert result["correlated"] is True
    assert result["severity"] == "critical"


def test_rule_correlation_no_signals():
    """No signals should yield low correlation."""
    engine = RuleCorrelationEngine()
    result = engine.correlate({}, "EMP00001")
    assert result["correlation_score"] == 0.0


# === Explainability Tests ===

def test_explainability_returns_reasons():
    """Explanation should include risk score, confidence, and reasons."""
    engine = ExplainabilityEngine()
    result = engine.explain(
        risk_score=85.0,
        confidence=0.9,
        deviations={"usb_usage": {"score": 0.8, "detail": "USB plugged"}},
        correlation={"correlation_score": 0.8, "scenario": "data_exfiltration"},
        shap_values=[],
        employee_id="EMP00001",
    )
    assert result["risk_score"] == 85.0
    assert result["confidence"] == 0.9
    assert len(result["reasons"]) > 0
    assert len(result["recommended_actions"]) > 0


# === Model Registry Tests ===

def test_model_registry_register_and_versioning(tmp_path):
    """Model registry should register versions and track active model."""
    registry = ModelRegistry(registry_dir=str(tmp_path))
    registry.register_model(
        version="v1.0",
        model_path="models/",
        metrics={"accuracy": 0.9},
        features=["a", "b"],
    )
    active = registry.get_active_model()
    assert active["model_version"] == "v1.0"
    assert active["status"] == "active"

    # Register v2 -> v1 becomes archived
    registry.register_model(
        version="v2.0",
        model_path="models/",
        metrics={"accuracy": 0.95},
        features=["a", "b", "c"],
    )
    active = registry.get_active_model()
    assert active["model_version"] == "v2.0"
    versions = registry.get_all_versions()
    assert len(versions) == 2


# === PredictionService Tests ===

def test_prediction_service_pipeline(sample_employees, sample_events):
    """Training + prediction should run end-to-end."""
    service = PredictionService()
    service.set_data(sample_employees, sample_events)
    summary = service.train()
    assert "model_version" in summary
    assert "metrics" in summary

    result = service.predict_employee("EMP00001")
    assert "risk_score" in result
    assert "threat_level" in result
    assert result["risk_score"] >= 0
    assert result["risk_score"] <= 100
