"""
SentinelAI - Alert Routes
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Optional
from datetime import datetime, timedelta
import random

import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from auth import get_current_active_user, require_role
from database import get_session, User

router = APIRouter(prefix="/api/alerts", tags=["Alerts"])


def generate_alerts(count: int = 20):
    """Generate realistic alerts"""
    alert_types = [
        'data_exfiltration', 'unauthorized_access', 'anomaly_detected',
        'policy_violation', 'suspicious_login', 'high_risk_activity',
        'bulk_operation', 'usb_activity', 'cloud_upload', 'email_anomaly'
    ]
    
    severity_levels = ['low', 'medium', 'high', 'critical']
    
    titles = {
        'data_exfiltration': 'Potential Data Exfiltration Detected',
        'unauthorized_access': 'Unauthorized Access Attempt',
        'anomaly_detected': 'Behavioral Anomaly Detected',
        'policy_violation': 'Security Policy Violation',
        'suspicious_login': 'Suspicious Login Activity',
        'high_risk_activity': 'High Risk Activity Pattern',
        'bulk_operation': 'Bulk File Operation Alert',
        'usb_activity': 'Unauthorized USB Device',
        'cloud_upload': 'Suspicious Cloud Upload',
        'email_anomaly': 'Email Anomaly Detected'
    }
    
    descriptions = {
        'data_exfiltration': 'Employee downloaded 600+ files and connected USB device simultaneously',
        'unauthorized_access': 'Failed login attempts from unrecognized IP address',
        'anomaly_detected': 'Unusual activity pattern detected outside normal working hours',
        'policy_violation': 'Violation of data access policy - sensitive directory accessed',
        'suspicious_login': 'Login from unusual geographic location with new device',
        'high_risk_activity': 'Multiple high-risk behaviors detected in short time window',
        'bulk_operation': 'Bulk file copy operation exceeding normal threshold',
        'usb_activity': 'Unknown USB mass storage device connected to workstation',
        'cloud_upload': 'Large data upload to personal cloud storage account',
        'email_anomaly': 'Multiple emails with large attachments to external recipients'
    }
    
    alerts = []
    for i in range(count):
        alert_type = random.choice(alert_types)
        severity = random.choices(severity_levels, weights=[0.2, 0.3, 0.35, 0.15])[0]
        
        alert = {
            "id": f"ALT-{random.randint(10000, 99999)}",
            "employee_id": f"EMP{random.randint(1, 1000):05d}",
            "employee_name": random.choice([
                "Alice Johnson", "Bob Smith", "Charlie Brown", "Diana Ross",
                "Edward Chen", "Fiona White", "George Kim", "Hannah Lee"
            ]),
            "department": random.choice(['Engineering', 'Sales', 'Marketing', 'HR', 'Finance', 'IT']),
            "type": alert_type,
            "title": titles[alert_type],
            "description": descriptions[alert_type],
            "severity": severity,
            "risk_score": round(random.uniform(20, 98), 1),
            "status": random.choice(['new', 'acknowledged', 'investigating', 'resolved']),
            "is_read": random.random() < 0.3,
            "is_acknowledged": random.random() < 0.4,
            "created_at": (datetime.now() - timedelta(hours=random.randint(1, 168))).isoformat(),
            "acknowledged_by": None,
            "resolved_at": None,
            "metadata": {
                "source": random.choice(['AI Engine', 'Behavioral Analysis', 'Rule Engine', 'Network Monitor']),
                "confidence": round(random.uniform(0.7, 0.99), 2),
                "affected_devices": random.randint(1, 3),
                "related_events": random.randint(1, 20)
            }
        }
        alerts.append(alert)
    
    return sorted(alerts, key=lambda x: x['created_at'], reverse=True)


@router.get("/")
async def get_all_alerts(
    status: Optional[str] = None,
    severity: Optional[str] = None,
    alert_type: Optional[str] = None,
    employee_id: Optional[str] = None,
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_active_user)
):
    """Get all alerts with filtering"""
    alerts = generate_alerts(50)
    
    # Apply filters
    if status:
        alerts = [a for a in alerts if a['status'] == status]
    if severity:
        alerts = [a for a in alerts if a['severity'] == severity]
    if alert_type:
        alerts = [a for a in alerts if a['type'] == alert_type]
    if employee_id:
        alerts = [a for a in alerts if a['employee_id'] == employee_id]
    
    # Pagination
    start = (page - 1) * limit
    end = start + limit
    paginated = alerts[start:end]
    
    return {
        "alerts": paginated,
        "total": len(alerts),
        "page": page,
        "limit": limit,
        "total_pages": max(1, (len(alerts) + limit - 1) // limit)
    }


@router.get("/stats")
async def get_alert_stats(current_user: User = Depends(get_current_active_user)):
    """Get alert statistics"""
    return {
        "total_alerts": random.randint(100, 500),
        "new_alerts": random.randint(5, 30),
        "critical_alerts": random.randint(1, 8),
        "high_alerts": random.randint(5, 20),
        "medium_alerts": random.randint(10, 40),
        "low_alerts": random.randint(15, 50),
        "avg_response_time": f"{random.randint(5, 60)}m",
        "alerts_by_type": {
            "data_exfiltration": random.randint(5, 30),
            "unauthorized_access": random.randint(10, 40),
            "anomaly_detected": random.randint(20, 60),
            "policy_violation": random.randint(15, 45),
            "suspicious_login": random.randint(25, 70),
            "usb_activity": random.randint(5, 20),
            "cloud_upload": random.randint(10, 35),
            "email_anomaly": random.randint(8, 25)
        }
    }


@router.get("/{alert_id}")
async def get_alert(alert_id: str, current_user: User = Depends(get_current_active_user)):
    """Get specific alert details"""
    alerts = generate_alerts(1)
    alert = alerts[0]
    alert['id'] = alert_id
    alert['related_activities'] = [
        {"id": f"ACT-{random.randint(10000, 99999)}", "type": "login", "timestamp": (datetime.now() - timedelta(minutes=random.randint(5, 60))).isoformat()},
        {"id": f"ACT-{random.randint(10000, 99999)}", "type": "file_download", "timestamp": (datetime.now() - timedelta(minutes=random.randint(5, 60))).isoformat()},
        {"id": f"ACT-{random.randint(10000, 99999)}", "type": "usb_insert", "timestamp": (datetime.now() - timedelta(minutes=random.randint(5, 60))).isoformat()},
    ]
    return alert


@router.put("/{alert_id}/acknowledge")
async def acknowledge_alert(
    alert_id: str,
    current_user: User = Depends(require_role(["admin", "analyst"]))
):
    """Acknowledge an alert"""
    return {
        "message": "Alert acknowledged",
        "alert_id": alert_id,
        "acknowledged_by": current_user.username,
        "timestamp": datetime.now().isoformat()
    }


@router.put("/{alert_id}/status")
async def update_alert_status(
    alert_id: str,
    status: str,
    current_user: User = Depends(require_role(["admin", "analyst"]))
):
    """Update alert status"""
    return {
        "message": f"Alert status updated to {status}",
        "alert_id": alert_id,
        "status": status,
        "updated_by": current_user.username,
        "timestamp": datetime.now().isoformat()
    }

