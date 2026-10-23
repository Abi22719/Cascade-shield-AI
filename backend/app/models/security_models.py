import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Integer, Float, Text, DateTime, ForeignKey, Boolean
from app.database.database import Base

def generate_uuid() -> str:
    return str(uuid.uuid4())

class UserModel(Base):
    __tablename__ = "users"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    username = Column(String(64), unique=True, nullable=False, index=True)
    full_name = Column(String(128), nullable=False)
    email = Column(String(128), unique=True, nullable=False)
    role = Column(String(32), nullable=False, default="Analyst", index=True)
    # Roles: Administrator, Cloud Operator, Incident Responder, Analyst, Developer, Read-Only Viewer
    is_active = Column(Boolean, nullable=False, default=True)
    last_login = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

class AuditLogModel(Base):
    __tablename__ = "audit_logs"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    actor_id = Column(String(64), nullable=False, index=True)
    actor_name = Column(String(128), nullable=False)
    actor_role = Column(String(32), nullable=False)
    action = Column(String(64), nullable=False, index=True)
    # Actions: SERVICE_CREATE, SERVICE_UPDATE, SERVICE_DELETE, DEPENDENCY_CREATE, DEPENDENCY_DELETE,
    # SIMULATION_RUN, RECOVERY_APPLY, INCIDENT_UPDATE, PERMISSION_CHANGE, SETTINGS_UPDATE, REPORT_GENERATE
    resource_type = Column(String(64), nullable=False, index=True)
    resource_id = Column(String(64), nullable=True, index=True)
    status = Column(String(16), nullable=False, default="SUCCESS", index=True)  # SUCCESS, DENIED, FAILED
    details_json = Column(Text, nullable=True)
    ip_address = Column(String(45), nullable=True, default="127.0.0.1")
    timestamp = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False, index=True)
