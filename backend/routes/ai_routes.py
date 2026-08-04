"""
SentinelAI - AI Prediction Routes
Exposes AI engine endpoints wired to the PredictionService.

Endpoints:
  POST /api/ai/predict            -> predict risk for an employee
  GET  /api/ai/employee-risk      -> compact risk for an employee
  GET  /api/ai/risk-history       -> risk history for an employee
  GET  /api/ai/alerts/live        -> live AI-generated alerts
  GET  /api/ai/timeline           -> incident timeline for an employee
  GET  /api/ai/high-risk          -> high-risk employees
  GET  /api/ai/model-info         -> active model version
  POST /api/ai/train              -> force retrain
"""

import asyncio
import random
from datetime import datetime, timedelta
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel

import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from auth import get_current_active_user, require_role
from database import get_session, User
from ai_service import get_ai_service
from websocket_manager import manager

router = APIRouter(prefix="/api/ai", tags=["AI Engine"])


# === Request/Response Schemas ===

class PredictRequest(BaseModel):
    employee_id: str


class PredictResponse(BaseModel):
    employee_id: str
    risk_score: float
    threat_level: str
    confidence: float
    reasons: List[str]
    recommended_actions: List[str]
    evidence: List[dict]
    model_version: str
    timestamp: str


# === Helper to build live alerts from predictions ===

def _build_alerts_from_predictions(predictions: List[dict], limit: int = 20) -> List[dict]:
    """Convert AI predictions into live alert objects."""
    alerts = []
    for p in predictions:
        if p['risk_score'] < 50:
            continue
        severity = 'critical' if p['risk_score'] > 80 else 'high' if p['risk_score'] > 60 else 'medium'
        alerts.append({
            'id': f"ALT-{random.randint(10000, 99999)}",
            'employee_id': p['employee_id'],
            'type': 'ai_risk_alert',
            'title': f"AI Risk Alert: {p.get('threat_level', 'Risk')} level",
            'description': p.get('reasons', ['AI detected elevated risk'])[0],
            'severity': severity,
            'risk_score': p['risk_score'],
            'confidence': p['confidence'],
            'status': 'new',
            'is_read': False,
            'created_at': p.get('timestamp', datetime.now().isoformat()),
            'metadata': {
                'source': 'AI Engine',
                'model_version': p.get('model_version', 'SentinelAI v1.0'),
                'reasons': p.get('reasons', [])[:5],
                'recommended_actions': p.get('recommended_actions', [])
            }
        })
    alerts.sort(key=lambda a: a['risk_score'], reverse=True)
    return alerts[:limit]


def _build_timeline(employee_id: str, prediction: dict) -> List[dict]:
    """Build a chronological incident timeline from a prediction's evidence."""
    events = []
    now = datetime.now()
    for i, ev in enumerate(prediction.get('evidence', [])):
        events.append({
            'time': (now - timedelta(minutes=(len(events) + 1) * 8)).isoformat(),
            'event': ev.get('detail', ''),
            'type': ev.get('signal', 'signal'),
            'severity': ev.get('severity', 'medium')
        })
    # Add detection event
    events.append({
        'time': now.isoformat(),
        'event': f"AI Engine detected risk {prediction.get('risk_score', 0):.0f}/100 ({prediction.get('threat_level', '')})",
        'type': 'detection',
        'severity': 'critical' if prediction.get('risk_score', 0) > 80 else 'high'
    })
    return sorted(events, key=lambda x: x['time'])


# === Endpoints ===

@router.post("/predict", response_model=PredictResponse)
async def predict(
    request: PredictRequest,
    current_user: User = Depends(get_current_active_user)
):
    """Predict risk for an employee with full explainability."""
    try:
        result = get_ai_service().predict(request.employee_id)
        return PredictResponse(
            employee_id=result['employee_id'],
            risk_score=result['risk_score'],
            threat_level=result['threat_level'],
            confidence=result['confidence'],
            reasons=result.get('reasons', []),
            recommended_actions=result.get('recommended_actions', []),
            evidence=result.get('evidence', []),
            model_version=result.get('model_version', 'SentinelAI v1.0'),
            timestamp=result.get('timestamp', datetime.now().isoformat())
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prediction failed: {e}")


@router.get("/employee-risk")
async def get_employee_risk(
    employee_id: str = Query(...),
    current_user: User = Depends(get_current_active_user)
):
    """Get compact risk information for an employee."""
    return get_ai_service().get_employee_risk(employee_id)


@router.get("/risk-history")
async def get_risk_history(
    employee_id: str = Query(...),
    days: int = Query(30, ge=1, le=365),
    current_user: User = Depends(get_current_active_user)
):
    """Get risk history for an employee."""
    return get_ai_service().get_risk_history(employee_id, days)


@router.get("/alerts/live")
async def get_live_alerts(
    limit: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_active_user)
):
    """Get live AI-generated alerts."""
    try:
        predictions = get_ai_service().predict_all()
        return {
            "alerts": _build_alerts_from_predictions(predictions, limit),
            "total": len(predictions),
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        # Fallback: return empty alerts if engine not ready
        return {"alerts": [], "total": 0, "error": str(e), "timestamp": datetime.now().isoformat()}


@router.get("/timeline")
async def get_timeline(
    employee_id: str = Query(...),
    current_user: User = Depends(get_current_active_user)
):
    """Get a chronological incident timeline for an employee."""
    try:
        prediction = get_ai_service().predict(employee_id)
        return {
            "employee_id": employee_id,
            "timeline": _build_timeline(employee_id, prediction),
            "risk_score": prediction.get('risk_score', 0),
            "threat_level": prediction.get('threat_level', 'Safe')
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Timeline failed: {e}")


@router.get("/high-risk")
async def get_high_risk(
    threshold: float = Query(60.0, ge=0, le=100),
    limit: int = Query(10, ge=1, le=50),
    current_user: User = Depends(require_role(["admin", "analyst"]))
):
    """Get high-risk employees."""
    return get_ai_service().get_high_risk(threshold, limit)


@router.get("/model-info")
async def get_model_info(current_user: User = Depends(get_current_active_user)):
    """Get active model version and registry info."""
    return get_ai_service().get_model_info()


@router.get("/baseline/{employee_id}")
async def get_employee_baseline(
    employee_id: str,
    current_user: User = Depends(get_current_active_user)
):
    """Get behavioural baseline for an employee."""
    return get_ai_service().get_baseline(employee_id)


@router.post("/train")
async def retrain(
    current_user: User = Depends(require_role(["admin"]))
):
    """Force a full retrain of the AI model (admin only)."""
    try:
        summary = get_ai_service().force_train()
        # Broadcast to websocket clients
        await manager.broadcast({
            "type": "model_retrained",
            "data": summary,
            "timestamp": datetime.now().isoformat()
        })
        return {"message": "Retraining complete", "summary": summary}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Retrain failed: {e}")
