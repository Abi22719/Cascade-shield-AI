from typing import List, Optional, Dict, Any, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import desc

from app.database.dashboard_repository import DashboardRepository
from app.models.alert_model import AlertModel
from app.models.rca_model import RCAIncidentModel
from app.models.recovery_models import RecoveryPlanModel
from app.models.validation_models import ValidationRunModel
from app.models.benchmark_models import BenchmarkExperimentModel
from app.schemas.notification_schemas import NotificationSchema, NotificationListResponse

class NotificationService:
    """
    Manages centralized system notifications, deduplication, and read-status tracking
    derived from real stored operational records.
    """

    @classmethod
    def get_notifications(
        cls,
        db: Session,
        unread_only: bool = False,
        severity: Optional[str] = None,
        source_module: Optional[str] = None,
        limit: int = 50
    ) -> NotificationListResponse:
        # Check if notifications table is populated; if empty, sync from stored alerts/events
        items, unread_count, total_count = DashboardRepository.list_notifications(
            db, unread_only=unread_only, severity=severity, source_module=source_module, limit=limit
        )

        if total_count == 0:
            cls.sync_from_stored_records(db)
            items, unread_count, total_count = DashboardRepository.list_notifications(
                db, unread_only=unread_only, severity=severity, source_module=source_module, limit=limit
            )

        schema_items = [
            NotificationSchema(
                id=n.id,
                event_type=n.event_type,
                source_module=n.source_module,
                source_record_id=n.source_record_id,
                title=n.title,
                message=n.message,
                severity=n.severity,
                read_status=n.read_status,
                created_at=n.created_at
            )
            for n in items
        ]

        return NotificationListResponse(
            unread_count=unread_count,
            total_count=total_count,
            notifications=schema_items
        )

    @classmethod
    def mark_as_read(cls, db: Session, notification_id: str) -> Optional[NotificationSchema]:
        notif = DashboardRepository.mark_notification_read(db, notification_id)
        if not notif:
            return None
        return NotificationSchema(
            id=notif.id,
            event_type=notif.event_type,
            source_module=notif.source_module,
            source_record_id=notif.source_record_id,
            title=notif.title,
            message=notif.message,
            severity=notif.severity,
            read_status=notif.read_status,
            created_at=notif.created_at
        )

    @classmethod
    def mark_all_as_read(cls, db: Session) -> int:
        return DashboardRepository.mark_all_notifications_read(db)

    @classmethod
    def sync_from_stored_records(cls, db: Session) -> int:
        """Populates notifications from actual stored records across modules."""
        count = 0

        # 1. Alerts
        alerts = db.query(AlertModel).order_by(desc(AlertModel.created_at)).limit(10).all()
        for a in alerts:
            DashboardRepository.create_notification(db, {
                "event_type": "ANOMALY_ALERT",
                "source_module": "module_2",
                "source_record_id": a.id,
                "title": f"Anomaly Alert: {a.metric_name} on {a.service_id}",
                "message": a.message or f"Metric {a.metric_name} breached threshold with value {a.current_value:.1f}.",
                "severity": a.severity,
                "read_status": a.is_resolved
            })
            count += 1

        # 2. RCA Incidents
        incidents = db.query(RCAIncidentModel).order_by(desc(RCAIncidentModel.created_at)).limit(5).all()
        for inc in incidents:
            DashboardRepository.create_notification(db, {
                "event_type": "RCA_INCIDENT",
                "source_module": "module_4",
                "source_record_id": inc.id,
                "title": f"RCA Incident Investigated: {inc.name}",
                "message": f"Root Cause Analysis completed for incident on service '{inc.service_id}' with status {inc.status}.",
                "severity": inc.severity or "WARNING",
                "read_status": inc.status != "OPEN"
            })
            count += 1

        # 3. Recovery Validations
        validations = db.query(ValidationRunModel).order_by(desc(ValidationRunModel.created_at)).limit(5).all()
        for v in validations:
            DashboardRepository.create_notification(db, {
                "event_type": "RECOVERY_VALIDATION",
                "source_module": "module_8",
                "source_record_id": v.id,
                "title": f"Recovery Validation: {v.overall_outcome}",
                "message": f"Verification completed with {v.passed_checks}/{v.total_checks} checks passing across 5 pillars.",
                "severity": "SUCCESS" if v.overall_outcome == "VERIFIED_SUCCESS" else "WARNING",
                "read_status": False
            })
            count += 1

        # 4. Benchmark Runs
        bms = db.query(BenchmarkExperimentModel).filter(
            BenchmarkExperimentModel.status == "COMPLETED"
        ).order_by(desc(BenchmarkExperimentModel.created_at)).limit(3).all()
        for b in bms:
            DashboardRepository.create_notification(db, {
                "event_type": "BENCHMARK_COMPLETED",
                "source_module": "module_9",
                "source_record_id": b.id,
                "title": f"Benchmark Run: {b.name}",
                "message": f"Overall Resilience Score: {b.overall_resilience_score or 'N/A'}/100.0 across 10 failure archetypes.",
                "severity": "INFO",
                "read_status": True
            })
            count += 1

        db.commit()
        return count
