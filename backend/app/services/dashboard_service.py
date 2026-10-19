from datetime import datetime, timezone
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import desc

from app.database.dashboard_repository import DashboardRepository
from app.models.alert_model import AlertModel
from app.models.rca_model import RCAIncidentModel
from app.models.recovery_models import RecoveryPlanModel
from app.models.validation_models import ValidationRunModel
from app.models.benchmark_models import BenchmarkExperimentModel
from app.schemas.dashboard_schemas import DashboardSummaryResponse, DashboardHealthResponse

class DashboardService:
    """
    Core orchestrator for high-level system summaries, module health status,
    and unified activity timelines across Modules 1 to 10.
    """

    @classmethod
    def get_summary(cls, db: Session) -> DashboardSummaryResponse:
        summary_dict = DashboardRepository.get_system_summary(db)
        return DashboardSummaryResponse(**summary_dict)

    @classmethod
    def get_health(cls, db: Session) -> DashboardHealthResponse:
        modules_map = {
            "module_1": "OPERATIONAL",
            "module_2": "OPERATIONAL",
            "module_3": "OPERATIONAL",
            "module_4": "OPERATIONAL",
            "module_5": "OPERATIONAL",
            "module_6": "OPERATIONAL",
            "module_7": "OPERATIONAL",
            "module_8": "OPERATIONAL",
            "module_9": "OPERATIONAL",
            "module_10": "OPERATIONAL"
        }
        return DashboardHealthResponse(
            status="operational",
            simulation_mode=True,
            version="10.0.0",
            modules=modules_map,
            timestamp=datetime.now(timezone.utc)
        )

    @classmethod
    def get_activity_timeline(cls, db: Session, limit: int = 50) -> List[Dict[str, Any]]:
        # Check if activity events exist; if empty, sync recent milestone records from DB
        activities = DashboardRepository.list_activities(db, limit=limit)
        if not activities:
            cls._seed_recent_milestones(db)
            activities = DashboardRepository.list_activities(db, limit=limit)

        result = []
        for act in activities:
            result.append({
                "id": act.id,
                "event_type": act.event_type,
                "source_module": act.source_module,
                "source_record_id": act.source_record_id,
                "related_incident_id": act.related_incident_id,
                "description": act.description,
                "created_at": act.created_at
            })
        return result

    @classmethod
    def _seed_recent_milestones(cls, db: Session) -> None:
        """Auto-syncs stored records into the activity event stream if empty."""
        # Alerts
        recent_alerts = db.query(AlertModel).order_by(desc(AlertModel.created_at)).limit(5).all()
        for a in recent_alerts:
            DashboardRepository.record_activity(db, {
                "event_type": "ANOMALY_ALERT_DETECTED",
                "source_module": "module_2",
                "source_record_id": a.id,
                "description": f"AI Anomaly Alert [{a.severity}] on service '{a.service_id}': {a.metric_name} exceeded threshold."
            })

        # Incidents
        recent_incidents = db.query(RCAIncidentModel).order_by(desc(RCAIncidentModel.created_at)).limit(3).all()
        for inc in recent_incidents:
            DashboardRepository.record_activity(db, {
                "event_type": "RCA_INVESTIGATION_INITIALIZED",
                "source_module": "module_4",
                "source_record_id": inc.id,
                "related_incident_id": inc.id,
                "description": f"Root Cause Analysis initiated for incident '{inc.title}' on {inc.target_service_id}."
            })

        # Recovery Plans
        recent_plans = db.query(RecoveryPlanModel).order_by(desc(RecoveryPlanModel.created_at)).limit(3).all()
        for p in recent_plans:
            DashboardRepository.record_activity(db, {
                "event_type": "RECOVERY_PLAN_GENERATED",
                "source_module": "module_7",
                "source_record_id": p.id,
                "description": f"Recovery plan generated: {p.plan_name} (Strategy: {p.strategy_type})."
            })

        # Validation Runs
        recent_vals = db.query(ValidationRunModel).order_by(desc(ValidationRunModel.created_at)).limit(3).all()
        for v in recent_vals:
            DashboardRepository.record_activity(db, {
                "event_type": "RECOVERY_VALIDATION_COMPLETED",
                "source_module": "module_8",
                "source_record_id": v.id,
                "description": f"Recovery validation completed: Outcome {v.overall_outcome} with {v.passed_checks}/{v.total_checks} checks passing."
            })

        # Benchmark Experiments
        recent_bms = db.query(BenchmarkExperimentModel).order_by(desc(BenchmarkExperimentModel.created_at)).limit(2).all()
        for b in recent_bms:
            DashboardRepository.record_activity(db, {
                "event_type": "BENCHMARK_EVALUATION_COMPLETED",
                "source_module": "module_9",
                "source_record_id": b.id,
                "description": f"Resilience benchmark '{b.name}' finished with Resilience Score {b.overall_resilience_score or 'N/A'}/100."
            })

        db.commit()
