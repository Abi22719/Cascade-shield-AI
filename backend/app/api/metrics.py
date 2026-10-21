from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.database.database import get_db
from app.models.service import ServiceModel
from app.schemas.metrics import MetricsSummaryResponse

router = APIRouter(prefix="/metrics", tags=["Metrics"])

@router.get("/summary", response_model=MetricsSummaryResponse)
def get_metrics_summary(db: Session = Depends(get_db)):
    """
    Compute aggregate health and telemetry metrics across all cloud services.
    All data is clearly marked as simulated telemetry.
    """
    services = db.query(ServiceModel).all()
    total = len(services)

    if total == 0:
        return MetricsSummaryResponse(
            total_services=0,
            healthy_services=0,
            warning_services=0,
            critical_services=0,
            health_score_pct=100.0,
            avg_latency_ms=0.0,
            avg_error_rate=0.0,
            avg_cpu_usage=0.0,
            avg_memory_usage=0.0,
            total_request_volume=0,
            telemetry_type="simulated"
        )

    healthy_count = sum(1 for s in services if s.health_status == "HEALTHY")
    warning_count = sum(1 for s in services if s.health_status == "WARNING")
    critical_count = sum(1 for s in services if s.health_status == "CRITICAL")

    # Weighted health score: healthy = 100%, warning = 50%, critical = 0%
    health_score = round(((healthy_count * 100.0) + (warning_count * 50.0)) / total, 1)

    avg_latency = round(sum(s.latency_ms for s in services) / total, 2)
    avg_error_rate = round(sum(s.error_rate for s in services) / total, 3)
    avg_cpu = round(sum(s.cpu_usage for s in services) / total, 1)
    avg_memory = round(sum(s.memory_usage for s in services) / total, 1)
    total_volume = sum(s.request_volume for s in services)

    return MetricsSummaryResponse(
        total_services=total,
        healthy_services=healthy_count,
        warning_services=warning_count,
        critical_services=critical_count,
        health_score_pct=health_score,
        avg_latency_ms=avg_latency,
        avg_error_rate=avg_error_rate,
        avg_cpu_usage=avg_cpu,
        avg_memory_usage=avg_memory,
        total_request_volume=total_volume,
        telemetry_type="simulated"
    )

@router.post("/refresh", response_model=MetricsSummaryResponse)
def refresh_telemetry_metrics(
    jitter: bool = True,
    db: Session = Depends(get_db)
):
    """
    Triggers a live telemetry refresh across all services in the digital twin.
    Simulates operational fluctuation (jitter) on healthy/warning services,
    updates updated_at timestamps, recalculates health statuses,
    logs an activity record, and returns the updated metrics summary.
    """
    import random
    from datetime import datetime, timezone
    from app.services.health_evaluator import evaluate_service_health

    services = db.query(ServiceModel).all()
    now = datetime.now(timezone.utc)

    for s in services:
        if jitter and s.health_status in ["HEALTHY", "WARNING"]:
            s.cpu_usage = round(max(2.0, min(95.0, s.cpu_usage + random.uniform(-1.8, 1.8))), 1)
            s.memory_usage = round(max(5.0, min(95.0, s.memory_usage + random.uniform(-1.2, 1.2))), 1)
            lat_delta = random.uniform(-2.5, 2.5)
            s.latency_ms = round(max(1.0, min(5000.0, s.latency_ms + lat_delta)), 1)
            if s.error_rate < 5.0:
                s.error_rate = round(max(0.0, min(10.0, s.error_rate + random.uniform(-0.03, 0.03))), 2)
            s.request_volume = max(10, int(s.request_volume + random.randint(-40, 40)))

            new_health, _ = evaluate_service_health(
                cpu_usage=s.cpu_usage,
                memory_usage=s.memory_usage,
                latency_ms=s.latency_ms,
                error_rate=s.error_rate
            )
            s.health_status = new_health

        s.updated_at = now

    db.commit()

    try:
        from app.database.dashboard_repository import DashboardRepository
        DashboardRepository.record_activity(db, {
            "event_type": "TELEMETRY_REFRESH",
            "source_module": "module_1",
            "description": f"Telemetry refresh executed across {len(services)} digital twin services.",
            "metadata": {"refreshed_count": len(services), "timestamp": now.isoformat()}
        })
        db.commit()
    except Exception:
        pass

    return get_metrics_summary(db=db)
