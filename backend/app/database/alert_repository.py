import uuid
from datetime import datetime, timezone, timedelta
from typing import List, Optional, Tuple, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from app.models.alert_model import AlertModel

class AlertRepository:
    @staticmethod
    def create_alert(
        db: Session,
        service_id: str,
        service_name: str,
        metric_name: str,
        observed_value: Optional[float],
        threshold_value: Optional[float],
        severity: str,
        detection_method: str,
        anomaly_score: Optional[float],
        evidence_summary: str,
        data_source: str = "simulated"
    ) -> AlertModel:
        """
        Creates and persists a new alert record.
        """
        alert_id = f"alt-{uuid.uuid4().hex[:10]}"
        alert = AlertModel(
            id=alert_id,
            service_id=service_id,
            service_name=service_name,
            metric_name=metric_name,
            observed_value=observed_value,
            threshold_value=threshold_value,
            severity=severity,
            detection_method=detection_method,
            anomaly_score=anomaly_score,
            evidence_summary=evidence_summary,
            data_source=data_source,
            acknowledged=False,
            created_at=datetime.now(timezone.utc)
        )
        db.add(alert)
        db.commit()
        db.refresh(alert)
        return alert

    @staticmethod
    def is_duplicate_alert(
        db: Session,
        service_id: str,
        metric_name: str,
        severity: str,
        window_minutes: int = 15
    ) -> bool:
        """
        Deduplication: Checks if an unacknowledged alert already exists
        for the same service, metric, and severity within the recent time window.
        """
        window_start = datetime.now(timezone.utc) - timedelta(minutes=window_minutes)
        existing = db.query(AlertModel).filter(
            AlertModel.service_id == service_id,
            AlertModel.metric_name == metric_name,
            AlertModel.severity == severity,
            AlertModel.acknowledged == False,
            AlertModel.created_at >= window_start
        ).first()
        return existing is not None

    @staticmethod
    def get_alert_by_id(db: Session, alert_id: str) -> Optional[AlertModel]:
        return db.query(AlertModel).filter(AlertModel.id == alert_id).first()

    @staticmethod
    def get_alerts(
        db: Session,
        service_id: Optional[str] = None,
        severity: Optional[str] = None,
        detection_method: Optional[str] = None,
        acknowledged: Optional[bool] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        page: int = 1,
        limit: int = 50
    ) -> Tuple[List[AlertModel], int]:
        query = db.query(AlertModel)

        if service_id:
            query = query.filter(AlertModel.service_id == service_id)
        if severity:
            query = query.filter(AlertModel.severity == severity.capitalize())
        if detection_method:
            query = query.filter(AlertModel.detection_method == detection_method)
        if acknowledged is not None:
            query = query.filter(AlertModel.acknowledged == acknowledged)
        if start_time:
            query = query.filter(AlertModel.created_at >= start_time)
        if end_time:
            query = query.filter(AlertModel.created_at <= end_time)

        total = query.count()
        offset = (page - 1) * limit
        alerts = query.order_by(desc(AlertModel.created_at)).offset(offset).limit(limit).all()

        return alerts, total

    @staticmethod
    def get_summary(db: Session) -> Dict[str, int]:
        total_alerts = db.query(AlertModel).count()
        critical_alerts = db.query(AlertModel).filter(AlertModel.severity == "Critical").count()
        warning_alerts = db.query(AlertModel).filter(AlertModel.severity == "Warning").count()
        anomalous_observations = db.query(AlertModel).filter(
            AlertModel.detection_method.in_(["isolation_forest", "combined"])
        ).count()
        
        # Count distinct services with at least one active alert
        affected_services = db.query(func.count(func.distinct(AlertModel.service_id))).scalar() or 0
        acknowledged_alerts = db.query(AlertModel).filter(AlertModel.acknowledged == True).count()
        unacknowledged_alerts = total_alerts - acknowledged_alerts

        return {
            "total_alerts": total_alerts,
            "critical_alerts": critical_alerts,
            "warning_alerts": warning_alerts,
            "anomalous_observations": anomalous_observations,
            "affected_services": affected_services,
            "acknowledged_alerts": acknowledged_alerts,
            "unacknowledged_alerts": unacknowledged_alerts
        }

    @staticmethod
    def acknowledge_alert(db: Session, alert_id: str) -> Optional[AlertModel]:
        alert = db.query(AlertModel).filter(AlertModel.id == alert_id).first()
        if not alert:
            return None
        alert.acknowledged = True
        db.commit()
        db.refresh(alert)
        return alert
