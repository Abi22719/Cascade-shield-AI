from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.models.service import ServiceModel
from app.schemas.metric_schema import MetricPoint, MetricHistoryResponse
from app.services.metric_generator import MetricGenerator

router = APIRouter(prefix="/metrics-stream", tags=["Metrics Stream"])

@router.get("/services/{service_id}", response_model=MetricHistoryResponse)
def get_service_metrics(
    service_id: str,
    points: int = Query(30, ge=5, le=120),
    condition: str = Query("auto", description="auto, normal, degradation, spike, unusual_combination"),
    db: Session = Depends(get_db)
):
    """
    Returns time-series telemetry metrics for a selected service.
    """
    service = db.query(ServiceModel).filter(ServiceModel.id == service_id).first()
    if not service:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Service with ID '{service_id}' was not found."
        )

    history = MetricGenerator.generate_service_metric_history(
        service,
        points_count=points,
        condition_type=condition
    )
    return MetricHistoryResponse(
        service_id=service.id,
        service_name=service.name,
        data_source="simulated",
        total_points=len(history),
        metrics=history
    )

@router.get("/snapshot", response_model=List[MetricPoint])
def get_live_metrics_snapshot(db: Session = Depends(get_db)):
    """
    Returns the latest telemetry point for all registered services in the digital twin.
    """
    return MetricGenerator.get_latest_metrics_from_services(db)
