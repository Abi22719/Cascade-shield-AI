from datetime import datetime
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.schemas.alert_schema import AlertResponse, AlertListResponse, AlertSummaryResponse
from app.database.alert_repository import AlertRepository

router = APIRouter(prefix="/alerts", tags=["Alerts"])

@router.get("", response_model=AlertListResponse)
def list_alerts(
    service_id: Optional[str] = Query(None),
    severity: Optional[str] = Query(None),
    detection_method: Optional[str] = Query(None),
    acknowledged: Optional[bool] = Query(None),
    page: int = Query(1, ge=1),
    limit: int = Query(25, ge=1, le=200),
    db: Session = Depends(get_db)
):
    """
    Query persistent anomaly alerts with pagination and filters.
    """
    alerts, total = AlertRepository.get_alerts(
        db=db,
        service_id=service_id,
        severity=severity,
        detection_method=detection_method,
        acknowledged=acknowledged,
        page=page,
        limit=limit
    )
    return AlertListResponse(
        alerts=[AlertResponse.model_validate(a) for a in alerts],
        total=total,
        page=page,
        limit=limit
    )

@router.get("/summary", response_model=AlertSummaryResponse)
def get_alerts_summary(db: Session = Depends(get_db)):
    """
    Returns summary statistics for all alerts.
    """
    stats = AlertRepository.get_summary(db)
    return AlertSummaryResponse(**stats)

@router.get("/{alert_id}", response_model=AlertResponse)
def get_alert(alert_id: str, db: Session = Depends(get_db)):
    """
    Fetch an individual alert by its unique identifier.
    """
    alert = AlertRepository.get_alert_by_id(db, alert_id)
    if not alert:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Alert with ID '{alert_id}' was not found."
        )
    return AlertResponse.model_validate(alert)

@router.post("/{alert_id}/acknowledge", response_model=AlertResponse)
def acknowledge_alert(alert_id: str, db: Session = Depends(get_db)):
    """
    Acknowledge an active alert.
    """
    alert = AlertRepository.acknowledge_alert(db, alert_id)
    if not alert:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Alert with ID '{alert_id}' was not found."
        )
    return AlertResponse.model_validate(alert)
