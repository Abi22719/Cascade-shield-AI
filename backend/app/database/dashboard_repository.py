import json
from datetime import datetime, timezone
from typing import List, Optional, Dict, Any, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import desc, func

from app.models.dashboard_models import NotificationModel, ActivityEventModel, GeneratedReportModel
from app.models.service import ServiceModel
from app.models.alert_model import AlertModel
from app.models.cascade_model import CascadeScenarioModel
from app.models.rca_model import RCAIncidentModel
from app.models.recovery_models import RecoveryPlanModel
from app.models.validation_models import ValidationRunModel
from app.models.benchmark_models import BenchmarkExperimentModel

class DashboardRepository:
    """
    CRUD repository for Module 10: Notifications, Activity Events, Generated Reports,
    and cross-module aggregation queries across Modules 1 to 9.
    """

    # --- Notifications ---
    @classmethod
    def create_notification(cls, db: Session, data: Dict[str, Any]) -> NotificationModel:
        # Check duplicate
        if data.get("source_record_id") and data.get("event_type"):
            existing = db.query(NotificationModel).filter(
                NotificationModel.event_type == data["event_type"],
                NotificationModel.source_record_id == data["source_record_id"]
            ).first()
            if existing:
                return existing

        notif = NotificationModel(
            event_type=data["event_type"],
            source_module=data["source_module"],
            source_record_id=data.get("source_record_id"),
            title=data["title"],
            message=data["message"],
            severity=data.get("severity", "INFO"),
            read_status=data.get("read_status", False)
        )
        db.add(notif)
        db.flush()
        return notif

    @classmethod
    def list_notifications(
        cls,
        db: Session,
        unread_only: bool = False,
        severity: Optional[str] = None,
        source_module: Optional[str] = None,
        limit: int = 50
    ) -> Tuple[List[NotificationModel], int, int]:
        query = db.query(NotificationModel)
        total_count = query.count()
        unread_count = db.query(NotificationModel).filter(NotificationModel.read_status == False).count()

        if unread_only:
            query = query.filter(NotificationModel.read_status == False)
        if severity:
            query = query.filter(NotificationModel.severity == severity)
        if source_module:
            query = query.filter(NotificationModel.source_module == source_module)

        items = query.order_by(desc(NotificationModel.created_at)).limit(limit).all()
        return items, unread_count, total_count

    @classmethod
    def mark_notification_read(cls, db: Session, notification_id: str) -> Optional[NotificationModel]:
        notif = db.query(NotificationModel).filter(NotificationModel.id == notification_id).first()
        if notif:
            notif.read_status = True
            db.commit()
            db.refresh(notif)
        return notif

    @classmethod
    def mark_all_notifications_read(cls, db: Session) -> int:
        updated = db.query(NotificationModel).filter(NotificationModel.read_status == False).update(
            {"read_status": True}
        )
        db.commit()
        return updated

    # --- Activity Events ---
    @classmethod
    def record_activity(cls, db: Session, data: Dict[str, Any]) -> ActivityEventModel:
        activity = ActivityEventModel(
            event_type=data["event_type"],
            source_module=data["source_module"],
            source_record_id=data.get("source_record_id"),
            related_incident_id=data.get("related_incident_id"),
            description=data["description"],
            metadata_json=json.dumps(data.get("metadata", {})) if data.get("metadata") else None
        )
        db.add(activity)
        db.flush()
        return activity

    @classmethod
    def list_activities(
        cls,
        db: Session,
        limit: int = 50,
        source_module: Optional[str] = None,
        related_incident_id: Optional[str] = None
    ) -> List[ActivityEventModel]:
        query = db.query(ActivityEventModel)
        if source_module:
            query = query.filter(ActivityEventModel.source_module == source_module)
        if related_incident_id:
            query = query.filter(ActivityEventModel.related_incident_id == related_incident_id)

        return query.order_by(desc(ActivityEventModel.created_at)).limit(limit).all()

    # --- Reports ---
    @classmethod
    def create_report(cls, db: Session, data: Dict[str, Any]) -> GeneratedReportModel:
        rep = GeneratedReportModel(
            report_type=data["report_type"],
            report_title=data["report_title"],
            related_record_id=data.get("related_record_id"),
            data_source=data.get("data_source", "simulated"),
            report_format=data.get("report_format", "markdown"),
            report_status=data.get("report_status", "COMPLETED"),
            content=data.get("content"),
            metadata_json=json.dumps(data.get("metadata", {})) if data.get("metadata") else None,
            completed_at=datetime.now(timezone.utc)
        )
        db.add(rep)
        db.commit()
        db.refresh(rep)
        return rep

    @classmethod
    def get_report(cls, db: Session, report_id: str) -> Optional[GeneratedReportModel]:
        return db.query(GeneratedReportModel).filter(GeneratedReportModel.id == report_id).first()

    @classmethod
    def list_reports(
        cls,
        db: Session,
        report_type: Optional[str] = None,
        limit: int = 50
    ) -> Tuple[List[GeneratedReportModel], int]:
        query = db.query(GeneratedReportModel)
        if report_type:
            query = query.filter(GeneratedReportModel.report_type == report_type)
        total = query.count()
        items = query.order_by(desc(GeneratedReportModel.created_at)).limit(limit).all()
        return items, total

    # --- Cross-Module System Aggregations ---
    @classmethod
    def get_system_summary(cls, db: Session) -> Dict[str, Any]:
        # 1. Services
        services = db.query(ServiceModel).all()
        total_services = len(services)
        healthy = sum(1 for s in services if s.health_status == "HEALTHY")
        degraded = sum(1 for s in services if s.health_status == "DEGRADED")
        unavailable = sum(1 for s in services if s.health_status in ["CRITICAL", "UNAVAILABLE"])

        # 2. Alerts
        active_anomalies = db.query(AlertModel).filter(AlertModel.acknowledged == False).count()

        # 3. Cascades
        high_risk_cascades = db.query(CascadeScenarioModel).count()

        # 4. Incidents
        open_incidents = db.query(RCAIncidentModel).filter(
            RCAIncidentModel.status.in_(["investigating", "OPEN", "open"])
        ).count()

        # 5. Recovery Plans
        total_plans = db.query(RecoveryPlanModel).count()
        validated_runs = db.query(ValidationRunModel.recovery_plan_id).distinct().all()
        validated_plan_ids = {r[0] for r in validated_runs}
        pending_validation = max(0, total_plans - len(validated_plan_ids))

        # 6. Benchmark
        latest_bm = db.query(BenchmarkExperimentModel).filter(
            BenchmarkExperimentModel.status == "COMPLETED"
        ).order_by(desc(BenchmarkExperimentModel.created_at)).first()
        latest_score = latest_bm.overall_resilience_score if latest_bm else None

        return {
            "total_services": total_services,
            "healthy_services": healthy,
            "degraded_services": degraded,
            "unavailable_services": unavailable,
            "active_anomalies": active_anomalies,
            "high_risk_predictions": high_risk_cascades,
            "open_incidents": open_incidents,
            "recovery_plans_pending": pending_validation,
            "latest_benchmark_score": latest_score,
            "simulation_mode": True,
            "last_refresh": datetime.now(timezone.utc)
        }
