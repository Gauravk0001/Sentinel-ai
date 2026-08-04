"""
SentinelAI - Celery Background Tasks
Asynchronous jobs for AI model retraining, alert generation, and dashboard refresh.

These tasks are consumed by the Celery worker and run in the background,
offloading expensive operations from the synchronous FastAPI request path.
"""

import sys
import os
from datetime import datetime
from typing import Any, Dict, List

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from celery_app import celery_app
from ai_service import get_ai_service


@celery_app.task(name="tasks.retrain_model")
def retrain_model_task() -> Dict[str, Any]:
    """
    Retrain the AI model in the background.

    Returns:
        Dictionary with training summary and model version.
    """
    service = get_ai_service()
    summary = service.force_train()
    summary["task"] = "retrain_model"
    summary["completed_at"] = datetime.now().isoformat()
    return summary


@celery_app.task(name="tasks.generate_live_alerts")
def generate_live_alerts_task(limit: int = 20) -> Dict[str, Any]:
    """
    Generate live AI alerts from current predictions.

    Args:
        limit: Maximum number of alerts to generate.

    Returns:
        Dictionary with alert list and count.
    """
    service = get_ai_service()
    try:
        predictions = service.predict_all()
        alerts = []
        for p in predictions:
            if p.get("risk_score", 0) < 50:
                continue
            severity = (
                "critical"
                if p["risk_score"] > 80
                else "high"
                if p["risk_score"] > 60
                else "medium"
            )
            alerts.append(
                {
                    "id": f"ALT-{abs(hash(p['employee_id'])) % 100000}",
                    "employee_id": p["employee_id"],
                    "type": "ai_risk_alert",
                    "title": f"AI Risk Alert: {p.get('threat_level', 'Risk')} level",
                    "description": p.get("reasons", ["AI detected elevated risk"])[0],
                    "severity": severity,
                    "risk_score": p["risk_score"],
                    "confidence": p.get("confidence", 0),
                    "status": "new",
                    "created_at": datetime.now().isoformat(),
                }
            )
        alerts.sort(key=lambda a: a["risk_score"], reverse=True)
        return {"alerts": alerts[:limit], "total": len(alerts), "task": "generate_live_alerts"}
    except Exception as e:
        return {"alerts": [], "total": 0, "error": str(e), "task": "generate_live_alerts"}


@celery_app.task(name="tasks.refresh_dashboard_stats")
def refresh_dashboard_stats_task() -> Dict[str, Any]:
    """
    Refresh cached dashboard statistics from the AI engine.

    Returns:
        Dictionary with dashboard statistics.
    """
    service = get_ai_service()
    try:
        stats = service.get_dashboard_stats()
        stats["task"] = "refresh_dashboard_stats"
        stats["refreshed_at"] = datetime.now().isoformat()
        return stats
    except Exception as e:
        return {"error": str(e), "task": "refresh_dashboard_stats"}


@celery_app.task(name="tasks.health_check")
def health_check_task() -> Dict[str, Any]:
    """
    Perform a health check of the AI service.

    Returns:
        Dictionary with health status.
    """
    try:
        service = get_ai_service()
        model_info = service.get_model_info()
        return {
            "status": "healthy",
            "service": "ai-engine",
            "model": model_info.get("active_model", {}).get("model_version", "unknown"),
            "timestamp": datetime.now().isoformat(),
        }
    except Exception as e:
        return {"status": "unhealthy", "error": str(e), "timestamp": datetime.now().isoformat()}
