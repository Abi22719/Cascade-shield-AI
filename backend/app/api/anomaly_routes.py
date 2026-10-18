from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.models.service import ServiceModel
from app.schemas.anomaly_schema import (
    ThresholdConfig,
    AnomalyDetectionRequest,
    DetectionBatchResponse,
    EvaluationComparisonResponse
)
from app.schemas.alert_schema import (
    AlertResponse,
    AlertSummaryResponse,
    AlertListResponse
)
from app.schemas.metric_schema import MetricHistoryResponse
from app.database.alert_repository import AlertRepository
from app.services.threshold_detector import threshold_detector
from app.services.anomaly_detector import anomaly_detector
from app.services.metric_generator import MetricGenerator
from app.services.alert_service import AlertService
from app.services.evaluation_service import EvaluationService

router = APIRouter(prefix="/anomalies", tags=["Anomaly Detection"])

@router.get("/health", status_code=status.HTTP_200_OK)
def check_anomaly_subsystem_health():
    """
    Checks the operational availability of the anomaly detection subsystem.
    """
    return {
        "status": "online",
        "subsystem": "CascadeShield AI - Anomaly Detection & Early Warning",
        "version": "2.0.0",
        "threshold_engine": "ready",
        "isolation_forest_engine": "fitted" if anomaly_detector.is_fitted else "ready_to_fit",
        "timestamp": datetime.now()
    }

@router.get("/summary", response_model=AlertSummaryResponse)
def get_anomaly_summary(db: Session = Depends(get_db)):
    """
    Returns aggregate alert statistics: total, critical, warning,
    anomalous observations count, and affected service count.
    """
    stats = AlertRepository.get_summary(db)
    return AlertSummaryResponse(**stats)

@router.get("", response_model=AlertListResponse)
def get_anomalies(
    service_id: Optional[str] = Query(None, description="Filter by service ID"),
    severity: Optional[str] = Query(None, description="Filter by severity (Warning, Critical)"),
    detection_method: Optional[str] = Query(None, description="Filter by method (threshold, isolation_forest, combined)"),
    acknowledged: Optional[bool] = Query(None, description="Filter by acknowledgement status"),
    start_time: Optional[datetime] = Query(None, description="Filter after timestamp"),
    end_time: Optional[datetime] = Query(None, description="Filter before timestamp"),
    page: int = Query(1, ge=1),
    limit: int = Query(25, ge=1, le=200),
    db: Session = Depends(get_db)
):
    """
    Returns historical anomaly alerts with pagination and multidimensional filtering.
    """
    alerts, total = AlertRepository.get_alerts(
        db=db,
        service_id=service_id,
        severity=severity,
        detection_method=detection_method,
        acknowledged=acknowledged,
        start_time=start_time,
        end_time=end_time,
        page=page,
        limit=limit
    )

    alert_responses = [AlertResponse.model_validate(a) for a in alerts]
    return AlertListResponse(alerts=alert_responses, total=total, page=page, limit=limit)

@router.get("/thresholds", response_model=ThresholdConfig)
def get_threshold_configuration():
    """
    Returns the currently active threshold configuration.
    """
    return threshold_detector.get_config()

@router.put("/thresholds", response_model=ThresholdConfig)
def update_threshold_configuration(config: ThresholdConfig):
    """
    Validates and updates the threshold configuration for warning and critical limits.
    """
    threshold_detector.update_config(config)
    return threshold_detector.get_config()

@router.get("/evaluation", response_model=EvaluationComparisonResponse)
def get_detection_evaluation():
    """
    Returns comprehensive benchmark evaluation metrics (Precision, Recall, F1, FPR)
    calculated on a deterministic labeled test dataset, comparing Threshold,
    Isolation Forest, and Combined alerting.
    """
    return EvaluationService.run_benchmark_evaluation()

@router.get("/metrics/{service_id}", response_model=MetricHistoryResponse)
def get_service_metric_history(
    service_id: str,
    points: int = Query(30, ge=5, le=120),
    db: Session = Depends(get_db)
):
    """
    Returns metric time-series history for a selected service with timestamps.
    """
    service = db.query(ServiceModel).filter(ServiceModel.id == service_id).first()
    if not service:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Service with ID '{service_id}' was not found."
        )

    history = MetricGenerator.generate_service_metric_history(service, points_count=points)
    return MetricHistoryResponse(
        service_id=service.id,
        service_name=service.name,
        data_source="simulated",
        total_points=len(history),
        metrics=history
    )

@router.post("/detect", response_model=DetectionBatchResponse)
def run_detection_batch(
    payload: Optional[AnomalyDetectionRequest] = None,
    db: Session = Depends(get_db)
):
    """
    Runs anomaly detection on available service metrics or a validated custom input batch.
    Stores new anomalies as persistent alerts in SQLite.
    """
    req = payload or AnomalyDetectionRequest()
    
    # Configure contamination if passed
    if req.contamination:
        anomaly_detector.contamination = req.contamination

    # Gather metrics to evaluate
    if req.custom_metrics and len(req.custom_metrics) > 0:
        metrics_to_evaluate = req.custom_metrics
    else:
        # Pull latest metrics from digital twin services
        all_metrics = MetricGenerator.get_latest_metrics_from_services(db)
        if req.service_ids and len(req.service_ids) > 0:
            target_ids = set(req.service_ids)
            metrics_to_evaluate = [m for m in all_metrics if m.service_id in target_ids]
        else:
            metrics_to_evaluate = all_metrics

    # Execute detection & alerting
    results = AlertService.run_detection(
        db=db,
        metrics=metrics_to_evaluate,
        method=req.method
    )

    anomalies_detected = sum(1 for r in results if r.is_anomaly)
    new_alerts_generated = sum(1 for r in results if r.alert_created)

    return DetectionBatchResponse(
        total_evaluated=len(results),
        anomalies_detected=anomalies_detected,
        method=req.method,
        new_alerts_generated=new_alerts_generated,
        results=results
    )

@router.post("/{alert_id}/acknowledge", response_model=AlertResponse)
def acknowledge_alert(alert_id: str, db: Session = Depends(get_db)):
    """
    Acknowledges an active anomaly alert.
    """
    alert = AlertRepository.acknowledge_alert(db, alert_id)
    if not alert:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Alert with ID '{alert_id}' was not found."
        )
    return AlertResponse.model_validate(alert)

@router.get("/{alert_id}", response_model=AlertResponse)
def get_alert_detail(alert_id: str, db: Session = Depends(get_db)):
    """
    Returns full details and evidence summary for a single alert.
    """
    alert = AlertRepository.get_alert_by_id(db, alert_id)
    if not alert:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Alert with ID '{alert_id}' was not found."
        )
    return AlertResponse.model_validate(alert)
