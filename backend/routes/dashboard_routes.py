"""
SentinelAI - Dashboard Routes
"""

from fastapi import APIRouter, Depends, HTTPException
from typing import List, Dict, Any
from datetime import datetime, timedelta
import pandas as pd
import numpy as np
import random

import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from auth import get_current_active_user
from database import get_session, User

router = APIRouter(prefix="/api/dashboard", tags=["Dashboard"])


def generate_dashboard_stats():
    """Generate realistic dashboard statistics"""
    return {
        "active_users": random.randint(42, 78),
        "online_now": random.randint(12, 28),
        "high_risk_employees": random.randint(3, 8),
        "critical_risk_employees": random.randint(1, 3),
        "total_employees": 1000,
        "total_alerts_today": random.randint(5, 25),
        "open_incidents": random.randint(2, 10),
        "average_risk_score": round(random.uniform(15, 35), 1),
        "avg_response_time_minutes": random.randint(5, 30),
        "threats_blocked_today": random.randint(3, 15),
        "system_health": "healthy",
        "last_updated": datetime.now().isoformat()
    }


def generate_risk_distribution():
    """Generate risk distribution data"""
    return {
        "safe": random.randint(600, 750),
        "low": random.randint(100, 200),
        "medium": random.randint(50, 100),
        "high": random.randint(20, 40),
        "critical": random.randint(5, 15)
    }


def generate_recent_activities(limit: int = 10):
    """Generate recent activities"""
    activities = []
    activity_types = ['login', 'file_download', 'usb_insert', 'cloud_upload', 
                     'email_sent', 'vpn_connect', 'app_launch', 'network_transfer']
    
    depts = ['Engineering', 'Sales', 'Marketing', 'HR', 'Finance', 'IT']
    severity = ['low', 'medium', 'high', 'critical']
    
    for i in range(limit):
        activity = {
            "id": f"ACT-{random.randint(10000, 99999)}",
            "employee": f"EMP{random.randint(1, 1000):05d}",
            "employee_name": random.choice([
                "Alice Johnson", "Bob Smith", "Charlie Brown", "Diana Ross",
                "Edward Chen", "Fiona White", "George Kim", "Hannah Lee"
            ]),
            "department": random.choice(depts),
            "type": random.choice(activity_types),
            "description": random.choice([
                "Bulk file download detected",
                "Late night login from new device",
                "USB mass storage device connected",
                "Large file upload to Google Drive",
                "Multiple external emails with attachments",
                "VPN connection from unusual location",
                "Accessing sensitive directories",
                "High volume network data transfer"
            ]),
            "risk_score": round(random.uniform(10, 95), 1),
            "severity": random.choice(severity),
            "timestamp": (datetime.now() - timedelta(minutes=random.randint(1, 1440))).isoformat(),
            "is_anomaly": random.random() < 0.3
        }
        activities.append(activity)
    
    return sorted(activities, key=lambda x: x['timestamp'], reverse=True)


def generate_risk_trend(days: int = 30):
    """Generate risk score trend data"""
    trend = []
    for i in range(days):
        date = datetime.now() - timedelta(days=days - i - 1)
        trend.append({
            "date": date.strftime("%Y-%m-%d"),
            "avg_risk": round(random.uniform(15, 45), 1),
            "max_risk": round(random.uniform(50, 95), 1),
            "high_risk_count": random.randint(5, 30),
            "incidents": random.randint(1, 10)
        })
    return trend


def generate_heatmap_data():
    """Generate activity heatmap data"""
    heatmap = []
    departments = ['Engineering', 'Sales', 'Marketing', 'HR', 'Finance', 'IT', 'Legal', 'Operations']
    hours = list(range(24))
    
    for dept in departments:
        row = {"department": dept}
        for hour in hours:
            # Simulate realistic activity patterns
            if 9 <= hour <= 17:
                row[f"hour_{hour}"] = random.randint(20, 100)
            elif 0 <= hour <= 5:
                row[f"hour_{hour}"] = random.randint(0, 10)
            else:
                row[f"hour_{hour}"] = random.randint(5, 30)
        heatmap.append(row)
    
    return heatmap


@router.get("/stats")
async def get_dashboard_stats(current_user: User = Depends(get_current_active_user)):
    """Get dashboard statistics"""
    return generate_dashboard_stats()


@router.get("/risk-distribution")
async def get_risk_distribution(current_user: User = Depends(get_current_active_user)):
    """Get risk score distribution"""
    return generate_risk_distribution()


@router.get("/recent-activities")
async def get_recent_activities(limit: int = 10, current_user: User = Depends(get_current_active_user)):
    """Get recent activities"""
    return generate_recent_activities(limit)


@router.get("/risk-trend")
async def get_risk_trend(days: int = 30, current_user: User = Depends(get_current_active_user)):
    """Get risk score trend"""
    return generate_risk_trend(days)


@router.get("/heatmap")
async def get_activity_heatmap(current_user: User = Depends(get_current_active_user)):
    """Get activity heatmap data"""
    return generate_heatmap_data()


@router.get("/overview")
async def get_overview(current_user: User = Depends(get_current_active_user)):
    """Get complete dashboard overview"""
    return {
        "stats": generate_dashboard_stats(),
        "risk_distribution": generate_risk_distribution(),
        "recent_activities": generate_recent_activities(10),
        "risk_trend": generate_risk_trend(30),
        "heatmap": generate_heatmap_data()
    }

