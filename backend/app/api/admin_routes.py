import json
from datetime import datetime, timezone
from typing import Optional, Dict, Any, List
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy.orm import Session
from app.database.database import get_db
from app.models.service import ServiceModel
from app.models.dependency import DependencyModel
from app.models.alert_model import AlertModel
from app.models.security_models import AuditLogModel
from app.services.health_evaluator import evaluate_service_health

router = APIRouter(prefix="/admin", tags=["Portal 1: Cloud Administrator"])

class SettingsUpdatePayload(BaseModel):
    simulation_step_limit: Optional[int] = 20
    simulation_default_duration: Optional[int] = 10
    telemetry_refresh_interval_sec: Optional[int] = 5
    cpu_critical_threshold: Optional[float] = 90.0
    memory_critical_threshold: Optional[float] = 90.0
    latency_critical_threshold_ms: Optional[float] = 1000.0
    error_rate_critical_threshold: Optional[float] = 5.0
    notification_slack_enabled: Optional[bool] = False
    actor_id: Optional[str] = "usr-admin-01"
    actor_name: Optional[str] = "Sarah Connor"

# In-memory settings fallback cache (persisted across sessions via audit and memory)
_PLATFORM_SETTINGS = {
    "simulation_step_limit": 20,
    "simulation_default_duration": 10,
    "telemetry_refresh_interval_sec": 5,
    "cpu_critical_threshold": 90.0,
    "memory_critical_threshold": 90.0,
    "latency_critical_threshold_ms": 1000.0,
    "error_rate_critical_threshold": 5.0,
    "notification_slack_enabled": False,
    "last_updated": datetime.now(timezone.utc).isoformat()
}

@router.get("/summary")
def get_admin_summary(db: Session = Depends(get_db)):
    services = db.query(ServiceModel).all()
    total_services = len(services)
    healthy_services = sum(1 for s in services if s.health_status == "HEALTHY")
    degraded_services = sum(1 for s in services if s.health_status == "DEGRADED")
    unavailable_services = sum(1 for s in services if s.health_status in ["CRITICAL", "UNAVAILABLE"])
    high_risk_services = sum(1 for s in services if s.error_rate > 2.0 or s.latency_ms > 500)

    total_dependencies = db.query(DependencyModel).count()
    active_anomalies = db.query(AlertModel).filter(AlertModel.acknowledged == False).count()
    recent_changes_count = db.query(AuditLogModel).count()

    return {
        "total_services": total_services,
        "healthy_services": healthy_services,
        "degraded_services": degraded_services,
        "unavailable_services": unavailable_services,
        "high_risk_services": high_risk_services,
        "total_dependencies": total_dependencies,
        "active_anomalies": active_anomalies,
        "recent_configuration_changes": recent_changes_count,
        "simulation_mode": True,
        "infrastructure_provider": "AWS / Kubernetes (Virtual Digital Twin)",
        "platform_uptime_pct": 99.98
    }

@router.get("/settings")
def get_admin_settings():
    return _PLATFORM_SETTINGS

@router.put("/settings")
def update_admin_settings(payload: SettingsUpdatePayload, db: Session = Depends(get_db)):
    global _PLATFORM_SETTINGS
    _PLATFORM_SETTINGS.update({
        "simulation_step_limit": payload.simulation_step_limit,
        "simulation_default_duration": payload.simulation_default_duration,
        "telemetry_refresh_interval_sec": payload.telemetry_refresh_interval_sec,
        "cpu_critical_threshold": payload.cpu_critical_threshold,
        "memory_critical_threshold": payload.memory_critical_threshold,
        "latency_critical_threshold_ms": payload.latency_critical_threshold_ms,
        "error_rate_critical_threshold": payload.error_rate_critical_threshold,
        "notification_slack_enabled": payload.notification_slack_enabled,
        "last_updated": datetime.now(timezone.utc).isoformat()
    })

    # Record audit log
    audit = AuditLogModel(
        actor_id=payload.actor_id or "usr-admin-01",
        actor_name=payload.actor_name or "Sarah Connor",
        actor_role="Administrator",
        action="SETTINGS_UPDATE",
        resource_type="platform_settings",
        resource_id="global-settings",
        status="SUCCESS",
        details_json=json.dumps(_PLATFORM_SETTINGS)
    )
    db.add(audit)
    db.commit()

    return {"message": "Platform settings updated successfully", "settings": _PLATFORM_SETTINGS}
