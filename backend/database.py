"""
SentinelAI - Database Models
SQLAlchemy models for all entities
"""

from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Boolean, Text, ForeignKey, JSON, Enum as SQLEnum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime
import enum
from config import settings

Base = declarative_base()


# === Enums ===
class UserRole(str, enum.Enum):
    ADMIN = "admin"
    ANALYST = "analyst"
    COMPLIANCE = "compliance"
    VIEWER = "viewer"

class ThreatLevel(str, enum.Enum):
    SAFE = "Safe"
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"
    CRITICAL = "Critical"

class IncidentStatus(str, enum.Enum):
    OPEN = "open"
    INVESTIGATING = "investigating"
    CONTAINED = "contained"
    RESOLVED = "resolved"
    FALSE_POSITIVE = "false_positive"

class ActivityType(str, enum.Enum):
    LOGIN = "login"
    LOGOUT = "logout"
    FILE = "file"
    USB = "usb"
    CLOUD = "cloud"
    EMAIL = "email"
    APP = "app"
    NETWORK = "network"


# === Models ===

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    username = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String, nullable=False)
    role = Column(String, default=UserRole.ANALYST.value)
    department = Column(String, default="Engineering")
    is_active = Column(Boolean, default=True)
    avatar_url = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_login = Column(DateTime, nullable=True)
    
    # Relationships
    assigned_incidents = relationship("Incident", back_populates="assigned_analyst")

class Employee(Base):
    __tablename__ = "employees"
    
    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(String, unique=True, index=True, nullable=False)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    department = Column(String, nullable=False)
    position = Column(String, nullable=False)
    location = Column(String, nullable=False)
    is_remote = Column(Boolean, default=False)
    risk_profile = Column(String, default="normal")
    tenure_days = Column(Integer, default=0)
    working_hours_start = Column(Integer, default=9)
    working_hours_end = Column(Integer, default=17)
    manager = Column(String, nullable=True)
    clearance_level = Column(String, default="low")
    has_vpn = Column(Boolean, default=False)
    device_id = Column(String, nullable=True)
    os = Column(String, nullable=True)
    department_risk_factor = Column(Float, default=1.0)
    is_monitored = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Current risk score (updated by AI engine)
    current_risk_score = Column(Float, default=0.0)
    current_threat_level = Column(String, default=ThreatLevel.SAFE.value)
    last_evaluated = Column(DateTime, nullable=True)
    
    # Relationships
    activities = relationship("Activity", back_populates="employee")
    risk_history = relationship("RiskHistory", back_populates="employee")

class Activity(Base):
    __tablename__ = "activities"
    
    id = Column(Integer, primary_key=True, index=True)
    log_id = Column(String, unique=True, nullable=True)
    employee_id = Column(String, ForeignKey("employees.employee_id"), nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)
    hour = Column(Integer, default=0)
    day_of_week = Column(Integer, default=0)
    activity_type = Column(String, nullable=False)
    is_weekend = Column(Boolean, default=False)
    department = Column(String, nullable=True)
    risk_profile = Column(String, default="normal")
    
    # Activity-specific data (JSON)
    activity_metadata = Column("metadata", JSON, nullable=True)
    
    # Relationships
    employee = relationship("Employee", back_populates="activities")

class RiskHistory(Base):
    __tablename__ = "risk_history"
    
    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(String, ForeignKey("employees.employee_id"), nullable=False)
    risk_score = Column(Float, nullable=False)
    threat_level = Column(String, nullable=False)
    confidence = Column(Float, default=0.0)
    reasons = Column(JSON, nullable=True)
    shap_values = Column(JSON, nullable=True)
    is_anomaly = Column(Boolean, default=False)
    model_version = Column(String, default="SentinelAI v1.0")
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    employee = relationship("Employee", back_populates="risk_history")

class Alert(Base):
    __tablename__ = "alerts"
    
    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(String, ForeignKey("employees.employee_id"), nullable=False)
    alert_type = Column(String, nullable=False)
    severity = Column(String, nullable=False)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    risk_score = Column(Float, default=0.0)
    is_read = Column(Boolean, default=False)
    is_acknowledged = Column(Boolean, default=False)
    acknowledged_by = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    resolved_at = Column(DateTime, nullable=True)
    
    # Relationships
    employee = relationship("Employee")

class Incident(Base):
    __tablename__ = "incidents"
    
    id = Column(Integer, primary_key=True, index=True)
    incident_id = Column(String, unique=True, nullable=False)
    employee_id = Column(String, ForeignKey("employees.employee_id"), nullable=False)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    severity = Column(String, default="medium")
    status = Column(String, default=IncidentStatus.OPEN.value)
    risk_score = Column(Float, default=0.0)
    threat_level = Column(String, nullable=True)
    
    # Related activities
    related_activities = Column(JSON, nullable=True)
    evidence = Column(JSON, nullable=True)
    
    # Assignee
    assigned_to = Column(Integer, ForeignKey("users.id"), nullable=True)
    
    # Timeline
    detected_at = Column(DateTime, default=datetime.utcnow)
    started_at = Column(DateTime, nullable=True)
    resolved_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    employee = relationship("Employee")
    assigned_analyst = relationship("User", back_populates="assigned_incidents")

class AuditLog(Base):
    __tablename__ = "audit_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    action = Column(String, nullable=False)
    resource = Column(String, nullable=False)
    resource_id = Column(String, nullable=True)
    details = Column(JSON, nullable=True)
    ip_address = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


# Create all tables
def init_db():
    """Initialize database"""
    connect_args = {}
    if settings.DATABASE_URL.startswith("sqlite"):
        connect_args["check_same_thread"] = False
    engine = create_engine(settings.DATABASE_URL, connect_args=connect_args)
    Base.metadata.create_all(bind=engine)
    return engine

def get_session():
    """Get database session"""
    connect_args = {}
    if settings.DATABASE_URL.startswith("sqlite"):
        connect_args["check_same_thread"] = False
    engine = create_engine(settings.DATABASE_URL, connect_args=connect_args)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    return SessionLocal()

if __name__ == '__main__':
    print("Creating database tables...")
    engine = init_db()
    print("✅ Database tables created successfully!")

