"""
SentinelAI - Employee Management Routes
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Optional
from datetime import datetime, timedelta
import random

import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from auth import get_current_active_user, require_role
from database import get_session, User, Employee

router = APIRouter(prefix="/api/employees", tags=["Employees"])


def generate_employee_data(employee_id: str):
    """Generate realistic employee data"""
    names = [
        "Alice Johnson", "Bob Smith", "Charlie Brown", "Diana Ross",
        "Edward Chen", "Fiona White", "George Kim", "Hannah Lee",
        "Ivan Patel", "Julia Martinez", "Kevin O'Brien", "Lara Wilson",
        "Mike Zhang", "Nina Andersen", "Oscar Fernandez", "Patricia Lee"
    ]
    
    depts = ['Engineering', 'Sales', 'Marketing', 'HR', 'Finance', 'IT', 'Legal', 'Operations']
    positions = [
        'Software Engineer', 'Sales Manager', 'Marketing Lead', 'HR Coordinator',
        'Financial Analyst', 'IT Administrator', 'Legal Counsel', 'Operations Manager',
        'Data Scientist', 'Product Manager', 'Security Analyst', 'DevOps Engineer'
    ]
    
    return {
        "employee_id": employee_id,
        "name": random.choice(names),
        "email": f"{employee_id.lower()}@company.com",
        "department": random.choice(depts),
        "position": random.choice(positions),
        "location": random.choice(['New York', 'San Francisco', 'London', 'Tokyo', 'Berlin', 'Singapore']),
        "is_remote": random.random() < 0.3,
        "tenure_days": random.randint(30, 1825),
        "working_hours_start": 9,
        "working_hours_end": 17,
        "manager": random.choice(names),
        "clearance_level": random.choice(['low', 'medium', 'high', 'critical']),
        "has_vpn": random.random() < 0.6,
        "os": random.choice(['Windows 11', 'macOS Sonoma', 'Ubuntu 22.04']),
        "is_monitored": True
    }


def generate_risk_history(days: int = 30):
    """Generate risk history for an employee"""
    history = []
    for i in range(days):
        date = datetime.now() - timedelta(days=days - i - 1)
        history.append({
            "date": date.strftime("%Y-%m-%d"),
            "risk_score": round(random.uniform(5, 95), 1),
            "threat_level": random.choice(['Safe', 'Low', 'Medium', 'High', 'Critical']),
            "events_count": random.randint(5, 50)
        })
    return history


def generate_employee_activities(employee_id: str, limit: int = 20):
    """Generate employee activities"""
    activities = []
    activity_types = [
        'login', 'logout', 'file_read', 'file_download', 'file_copy',
        'usb_insert', 'usb_remove', 'cloud_upload', 'email_sent',
        'app_launch', 'network_connection', 'vpn_connect', 'printer_access'
    ]
    
    for i in range(limit):
        activity = {
            "id": f"ACT-{random.randint(10000, 99999)}",
            "employee_id": employee_id,
            "type": random.choice(activity_types),
            "description": random.choice([
                f"Logged in from {random.choice(['Chrome', 'Edge', 'Firefox'])}",
                f"Downloaded {random.randint(5, 100)} files from {random.choice(['SharePoint', 'Network Drive', 'Local Server'])}",
                f"USB device {random.choice(['connected', 'disconnected'])}",
                f"Uploaded {random.randint(1, 50)}MB to {random.choice(['Google Drive', 'Dropbox', 'OneDrive'])}",
                f"Sent email with {random.randint(1, 5)} attachment(s)",
                f"Accessed {random.choice(['admin panel', 'customer database', 'financial records', 'source code repository'])}",
                f"VPN connection from {random.choice(['United States', 'Germany', 'Japan', 'Singapore'])}",
                f"Network transfer of {random.randint(10, 500)}MB"
            ]),
            "risk_score": round(random.uniform(0, 95), 1),
            "timestamp": (datetime.now() - timedelta(hours=random.randint(1, 720))).isoformat(),
            "is_suspicious": random.random() < 0.2,
            "metadata": {}
        }
        activities.append(activity)
    
    return sorted(activities, key=lambda x: x['timestamp'], reverse=True)


@router.get("/")
async def get_all_employees(
    department: Optional[str] = None,
    risk_level: Optional[str] = None,
    search: Optional[str] = None,
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_active_user)
):
    """Get all employees with filtering and pagination"""
    employees = []
    for i in range((page - 1) * limit, page * limit):
        if i >= 1000:
            break
        emp_id = f"EMP{str(i + 1).zfill(5)}"
        emp = generate_employee_data(emp_id)
        
        # Apply filters
        if department and emp['department'] != department:
            continue
        if search and search.lower() not in emp['name'].lower():
            continue
        
        # Generate current risk score
        emp['current_risk_score'] = round(random.uniform(0, 95), 1)
        emp['current_threat_level'] = 'Critical' if emp['current_risk_score'] > 80 else \
                                     'High' if emp['current_risk_score'] > 60 else \
                                     'Medium' if emp['current_risk_score'] > 40 else \
                                     'Low' if emp['current_risk_score'] > 20 else 'Safe'
        
        employees.append(emp)
    
    return {
        "employees": employees,
        "total": 1000,
        "page": page,
        "limit": limit,
        "total_pages": (1000 + limit - 1) // limit
    }


@router.get("/{employee_id}")
async def get_employee(employee_id: str, current_user: User = Depends(get_current_active_user)):
    """Get detailed employee information"""
    emp = generate_employee_data(employee_id)
    emp['current_risk_score'] = round(random.uniform(0, 95), 1)
    emp['current_threat_level'] = 'Critical' if emp['current_risk_score'] > 80 else \
                                 'High' if emp['current_risk_score'] > 60 else \
                                 'Medium' if emp['current_risk_score'] > 40 else \
                                 'Low' if emp['current_risk_score'] > 20 else 'Safe'
    emp['risk_history'] = generate_risk_history(30)
    emp['recent_activities'] = generate_employee_activities(employee_id, 30)
    emp['active_alerts'] = random.randint(0, 5)
    emp['open_incidents'] = random.randint(0, 2)
    
    return emp


@router.get("/{employee_id}/risk-history")
async def get_employee_risk_history(
    employee_id: str,
    days: int = Query(30, ge=1, le=365),
    current_user: User = Depends(get_current_active_user)
):
    """Get risk history for a specific employee"""
    return generate_risk_history(days)


@router.get("/{employee_id}/activities")
async def get_employee_activities(
    employee_id: str,
    limit: int = Query(20, ge=1, le=100),
    activity_type: Optional[str] = None,
    current_user: User = Depends(get_current_active_user)
):
    """Get activities for a specific employee"""
    activities = generate_employee_activities(employee_id, limit)
    
    if activity_type:
        activities = [a for a in activities if a['type'] == activity_type]
    
    return activities


@router.get("/high-risk")
async def get_high_risk_employees(
    threshold: float = Query(60.0, ge=0, le=100),
    limit: int = Query(10, ge=1, le=50),
    current_user: User = Depends(require_role(["admin", "analyst"]))
):
    """Get high risk employees"""
    high_risk = []
    for i in range(limit):
        emp_id = f"EMP{random.randint(1, 1000):05d}"
        emp = generate_employee_data(emp_id)
        emp['current_risk_score'] = round(random.uniform(threshold, 98), 1)
        emp['current_threat_level'] = 'Critical' if emp['current_risk_score'] > 80 else 'High'
        high_risk.append(emp)
    
    return sorted(high_risk, key=lambda x: x['current_risk_score'], reverse=True)


@router.get("/departments")
async def get_departments(current_user: User = Depends(get_current_active_user)):
    """Get department list with stats"""
    departments = [
        {"name": "Engineering", "employee_count": 250, "avg_risk": round(random.uniform(20, 40), 1)},
        {"name": "Sales", "employee_count": 150, "avg_risk": round(random.uniform(15, 30), 1)},
        {"name": "Marketing", "employee_count": 120, "avg_risk": round(random.uniform(15, 25), 1)},
        {"name": "HR", "employee_count": 80, "avg_risk": round(random.uniform(10, 20), 1)},
        {"name": "Finance", "employee_count": 100, "avg_risk": round(random.uniform(25, 45), 1)},
        {"name": "IT", "employee_count": 100, "avg_risk": round(random.uniform(20, 35), 1)},
        {"name": "Legal", "employee_count": 70, "avg_risk": round(random.uniform(15, 25), 1)},
        {"name": "Operations", "employee_count": 130, "avg_risk": round(random.uniform(10, 20), 1)}
    ]
    return departments

