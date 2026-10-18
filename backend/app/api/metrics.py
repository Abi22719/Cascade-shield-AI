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
