"""
SentinelAI - Incident Management Routes
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Optional
from datetime import datetime, timedelta
import random
import uuid

import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from auth import get_current_active_user, require_role
from database import get_session, User

router = APIRouter(prefix="/api/incidents", tags=["Incidents"])


def generate_incidents(count: int = 15):
    """Generate realistic incidents"""
    incident_types = [
        'data_exfiltration', 'insider_threat', 'policy_violation',
        'unauthorized_access', 'suspicious_behavior', 'data_leak'
    ]
    
    statuses = ['open', 'investigating', 'contained', 'resolved', 'false_positive']
    severities = ['low', 'medium', 'high', 'critical']
    
    descriptions = [
        "Employee connected USB device and uploaded 2GB to Google Drive at 2 AM",
        "Multiple failed login attempts from unrecognized IP addresses across 3 days",
        "Bulk download of 500+ files from sensitive directory followed by cloud upload",
        "Abnormal working hours with access to confidential financial records",
        "Employee emailed 50+ external recipients with attached sensitive documents",
        "Unauthorized access attempt to the source code repository from personal device",
        "Large data transfer to personal cloud storage during off-hours"
    ]
    
    incidents = []
    for i in range(count):
        created_at = datetime.now() - timedelta(hours=random.randint(1, 720))
        status = random.choice(statuses)
        
        incident = {
            "incident_id": f"INC-{datetime.now().strftime('%Y%m')}-{random.randint(1000, 9999)}",
            "employee_id": f"EMP{random.randint(1, 1000):05d}",
            "employee_name": random.choice([
                "Alice Johnson", "Bob Smith", "Charlie Brown", "Diana Ross",
                "Edward Chen", "Fiona White", "George Kim", "Hannah Lee"
            ]),
            "department": random.choice(['Engineering', 'Sales', 'Marketing', 'HR', 'Finance', 'IT']),
            "title": random.choice([
                "Suspected Data Exfiltration via USB",
                "Unauthorized Cloud Data Transfer",
                "Anomalous Login Pattern Detected",
                "Policy Violation - Sensitive Data Access",
                "Insider Threat - Bulk File Download",
                "Email Data Leak Attempt",
                "Suspicious Network Activity"
            ]),
            "description": random.choice(descriptions),
            "type": random.choice(incident_types),
            "severity": random.choice(severities),
            "status": status,
            "risk_score": round(random.uniform(40, 98), 1),
            "confidence": round(random.uniform(0.75, 0.99), 2),
            "assigned_to": random.choice([None, 'Sarah Chen', 'Mike Johnson', 'Alex Rivera']),
            "related_activities": random.randint(5, 50),
            "evidence_count": random.randint(2, 15),
            "created_at": created_at.isoformat(),
            "detected_at": (created_at + timedelta(minutes=random.randint(5, 120))).isoformat(),
            "updated_at": datetime.now().isoformat(),
            "resolved_at": (datetime.now() - timedelta(hours=random.randint(1, 48))).isoformat() if status in ['resolved', 'false_positive'] else None,
            "remediation_steps": [
                "Review and revoke unnecessary data access permissions",
                "Enable multi-factor authentication",
                "Audit all recent file access logs",
                "Conduct user security awareness training"
            ] if status == 'resolved' else []
        }
        incidents.append(incident)
    
    return sorted(incidents, key=lambda x: x['created_at'], reverse=True)


@router.get("/")
async def get_all_incidents(
    status: Optional[str] = None,
    severity: Optional[str] = None,
    incident_type: Optional[str] = None,
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_active_user)
):
    """Get all incidents with filtering"""
    incidents = generate_incidents(30)
    
    if status:
        incidents = [i for i in incidents if i['status'] == status]
    if severity:
        incidents = [i for i in incidents if i['severity'] == severity]
    if incident_type:
        incidents = [i for i in incidents if i['type'] == incident_type]
    
    start = (page - 1) * limit
    end = start + limit
    paginated = incidents[start:end]
    
    return {
        "incidents": paginated,
        "total": len(incidents),
        "page": page,
        "limit": limit,
        "total_pages": max(1, (len(incidents) + limit - 1) // limit)
    }


@router.get("/stats")
async def get_incident_stats(current_user: User = Depends(get_current_active_user)):
    """Get incident statistics"""
    return {
        "total_incidents": random.randint(50, 200),
        "open_incidents": random.randint(5, 25),
        "investigating": random.randint(3, 15),
        "contained": random.randint(2, 10),
        "resolved": random.randint(20, 100),
        "false_positives": random.randint(5, 30),
        "critical_incidents": random.randint(2, 10),
        "avg_resolution_time_hours": round(random.uniform(4, 48), 1),
        "most_common_type": random.choice(['data_exfiltration', 'insider_threat']),
        "incidents_by_type": {
            "data_exfiltration": random.randint(10, 40),
            "insider_threat": random.randint(5, 25),
            "policy_violation": random.randint(15, 50),
            "unauthorized_access": random.randint(8, 30),
            "suspicious_behavior": random.randint(12, 45),
            "data_leak": random.randint(3, 15)
        }
    }


@router.get("/{incident_id}")
async def get_incident(incident_id: str, current_user: User = Depends(get_current_active_user)):
    """Get specific incident details"""
    incidents = generate_incidents(1)
    incident = incidents[0]
    incident['incident_id'] = incident_id
    
    # Add detailed evidence
    incident['evidence'] = [
        {
            "type": "activity_log",
            "description": "Bulk file download event - 650 files in 3 minutes",
            "timestamp": (datetime.now() - timedelta(hours=2)).isoformat(),
            "severity": "high"
        },
        {
            "type": "usb_log",
            "description": "USB mass storage device connected - 32GB SanDisk",
            "timestamp": (datetime.now() - timedelta(hours=1, minutes=45)).isoformat(),
            "severity": "critical"
        },
        {
            "type": "cloud_log",
            "description": "2.1GB uploaded to Google Drive (personal account)",
            "timestamp": (datetime.now() - timedelta(hours=1, minutes=30)).isoformat(),
            "severity": "critical"
        },
        {
            "type": "network_log",
            "description": "Unusual outbound traffic to external IP addresses",
            "timestamp": (datetime.now() - timedelta(hours=1, minutes=15)).isoformat(),
            "severity": "medium"
        }
    ]
    
    # Add timeline
    incident['timeline'] = [
        {
            "time": (datetime.now() - timedelta(hours=3)).isoformat(),
            "event": "Employee logged in from office workstation",
            "type": "login"
        },
        {
            "time": (datetime.now() - timedelta(hours=2, minutes=45)).isoformat(),
            "event": "Started accessing sensitive directories",
            "type": "file_access"
        },
        {
            "time": (datetime.now() - timedelta(hours=2, minutes=30)).isoformat(),
            "event": "Bulk file download initiated - 650 files",
            "type": "bulk_download"
        },
        {
            "time": (datetime.now() - timedelta(hours=2)).isoformat(),
            "event": "USB device connected",
            "type": "usb"
        },
        {
            "time": (datetime.now() - timedelta(hours=1, minutes=45)).isoformat(),
            "event": "Large file transfer to USB detected",
            "type": "file_transfer"
        },
        {
            "time": (datetime.now() - timedelta(hours=1, minutes=30)).isoformat(),
            "event": "Cloud upload initiated - Google Drive",
            "type": "cloud_upload"
        },
        {
            "time": (datetime.now() - timedelta(hours=1)).isoformat(),
            "event": "AI Engine detected anomaly - Risk score: 95",
            "type": "detection"
        },
        {
            "time": datetime.now().isoformat(),
            "event": "Incident created - Critical severity",
            "type": "incident_created"
        }
    ]
    
    # Add AI explanation
    incident['ai_explanation'] = {
        "risk_score": 95.2,
        "threat_level": "Critical",
        "confidence": 0.97,
        "reasons": [
            "🚨 Bulk file download of 650 files from sensitive directories",
            "🔌 USB mass storage device connected during bulk download",
            "☁️ Large data upload (2.1GB) to personal cloud storage",
            "⏰ Activity occurred at 2:30 AM - outside normal working hours",
            "🌐 Unusual outbound network connections detected",
            "📧 Multiple external emails sent with large attachments"
        ]
    }
    
    # Add suggested actions
    incident['suggested_actions'] = [
        "🚨 IMMEDIATELY disable employee's network access",
        "🔒 Block USB ports on employee's workstation",
        "☁️ Revoke cloud storage access permissions",
        "📋 Preserve all activity logs for investigation",
        "👥 Notify employee's manager and HR",
        "🔐 Reset all access credentials",
        "📊 Conduct full forensic analysis of affected systems"
    ]
    
    return incident


@router.put("/{incident_id}/status")
async def update_incident_status(
    incident_id: str,
    status: str,
    current_user: User = Depends(require_role(["admin", "analyst"]))
):
    """Update incident status"""
    return {
        "message": f"Incident {incident_id} status updated to {status}",
        "incident_id": incident_id,
        "status": status,
        "updated_by": current_user.full_name,
        "timestamp": datetime.now().isoformat()
    }


@router.put("/{incident_id}/assign")
async def assign_incident(
    incident_id: str,
    analyst_name: str,
    current_user: User = Depends(require_role(["admin"]))
):
    """Assign incident to analyst"""
    return {
        "message": f"Incident {incident_id} assigned to {analyst_name}",
        "incident_id": incident_id,
        "assigned_to": analyst_name,
        "assigned_by": current_user.full_name,
        "timestamp": datetime.now().isoformat()
    }


@router.post("/{incident_id}/escalate")
async def escalate_incident(
    incident_id: str,
    reason: str,
    current_user: User = Depends(require_role(["admin", "analyst"]))
):
    """Escalate incident"""
    return {
        "message": f"Incident {incident_id} escalated",
        "reason": reason,
        "escalated_by": current_user.full_name,
        "timestamp": datetime.now().isoformat()
    }

