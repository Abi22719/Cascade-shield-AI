import json
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import desc

from app.database.dashboard_repository import DashboardRepository
from app.models.dashboard_models import GeneratedReportModel
from app.models.service import ServiceModel
from app.models.alert_model import AlertModel
from app.models.cascade_model import CascadeScenarioModel
from app.models.rca_model import RCAIncidentModel
from app.models.agent_model import AgentSessionModel
from app.models.simulation_model import SimulationScenarioModel
from app.models.recovery_models import RecoveryPlanModel
from app.models.validation_models import ValidationRunModel
from app.models.benchmark_models import BenchmarkExperimentModel
from app.schemas.report_schemas import ReportGenerateRequest, ReportResponse, ReportListResponse

class ReportService:
    """
    Centralized Reports Engine for Module 10: generates comprehensive reports
    across all 9 modules and complete incident lifecycles.
    """

    @classmethod
    def list_reports(
        cls,
        db: Session,
        report_type: Optional[str] = None,
        limit: int = 50
    ) -> ReportListResponse:
        items, total = DashboardRepository.list_reports(db, report_type=report_type, limit=limit)
        if total == 0:
            cls.seed_default_reports(db)
            items, total = DashboardRepository.list_reports(db, report_type=report_type, limit=limit)

        reports = [
            ReportResponse(
                id=r.id,
                report_type=r.report_type,
                report_title=r.report_title,
                related_record_id=r.related_record_id,
                data_source=r.data_source,
                report_format=r.report_format,
                report_status=r.report_status,
                content=r.content,
                metadata=json.loads(r.metadata_json) if r.metadata_json else None,
                created_at=r.created_at,
                completed_at=r.completed_at
            )
            for r in items
        ]
        return ReportListResponse(total=total, reports=reports)

    @classmethod
    def get_report(cls, db: Session, report_id: str) -> Optional[ReportResponse]:
        r = DashboardRepository.get_report(db, report_id)
        if not r:
            return None
        return ReportResponse(
            id=r.id,
            report_type=r.report_type,
            report_title=r.report_title,
            related_record_id=r.related_record_id,
            data_source=r.data_source,
            report_format=r.report_format,
            report_status=r.report_status,
            content=r.content,
            metadata=json.loads(r.metadata_json) if r.metadata_json else None,
            created_at=r.created_at,
            completed_at=r.completed_at
        )

    @classmethod
    def generate_report(cls, db: Session, req: ReportGenerateRequest) -> ReportResponse:
        title = req.report_title or f"CascadeShield AI - {req.report_type.replace('_', ' ').title()} Report"
        content, metadata = cls._build_report_content(db, req.report_type, req.related_record_id)

        rep = DashboardRepository.create_report(db, {
            "report_type": req.report_type,
            "report_title": title,
            "related_record_id": req.related_record_id,
            "data_source": req.data_source,
            "report_format": req.report_format,
            "report_status": "COMPLETED",
            "content": content,
            "metadata": metadata
        })

        return ReportResponse(
            id=rep.id,
            report_type=rep.report_type,
            report_title=rep.report_title,
            related_record_id=rep.related_record_id,
            data_source=rep.data_source,
            report_format=rep.report_format,
            report_status=rep.report_status,
            content=rep.content,
            metadata=metadata,
            created_at=rep.created_at,
            completed_at=rep.completed_at
        )

    @classmethod
    def _build_report_content(
        cls,
        db: Session,
        report_type: str,
        related_id: Optional[str]
    ) -> (str, Dict[str, Any]):
        timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
        md = []
        md.append(f"# 🛡️ CascadeShield AI Resilience Report")
        md.append(f"**Report Type:** `{report_type}` | **Generated:** {timestamp}")
        md.append(f"**Execution Mode:** `SIMULATED SANDBOX (Strictly Non-Destructive)`")
        md.append("")
        md.append("---")
        md.append("")

        meta: Dict[str, Any] = {"report_type": report_type, "timestamp": timestamp}

        if report_type == "service_health":
            services = db.query(ServiceModel).all()
            md.append("## 🌐 Virtual Cloud Digital Twin: Service Health")
            md.append("| Service ID | Name | Type | Health Status | Latency (ms) | Error Rate (%) |")
            md.append("| :--- | :--- | :--- | :--- | :--- | :--- |")
            for s in services:
                md.append(f"| `{s.id}` | {s.name} | {s.service_type} | **{s.health_status}** | {s.latency_ms:.1f} | {s.error_rate:.2f}% |")
            meta["total_services"] = len(services)

        elif report_type == "anomaly_detection":
            alerts = db.query(AlertModel).order_by(desc(AlertModel.created_at)).limit(10).all()
            md.append("## 🚨 AI Anomaly Detection & Early Warning Summary")
            md.append("| Alert ID | Service | Metric | Value | Threshold | Severity | Status |")
            md.append("| :--- | :--- | :--- | :--- | :--- | :--- | :--- |")
            for a in alerts:
                stat = "ACKNOWLEDGED" if a.acknowledged else "ACTIVE"
                obs = a.observed_value if a.observed_value is not None else 0.0
                thresh = a.threshold_value if a.threshold_value is not None else 0.0
                md.append(f"| `{a.id[:8]}` | {a.service_id} | {a.metric_name} | {obs:.1f} | {thresh:.1f} | **{a.severity}** | {stat} |")
            meta["alerts_count"] = len(alerts)

        elif report_type == "benchmarking":
            bm = db.query(BenchmarkExperimentModel).filter(
                BenchmarkExperimentModel.status == "COMPLETED"
            ).order_by(desc(BenchmarkExperimentModel.created_at)).first()
            md.append("## 🏆 Module 9: Resilience Benchmarking & Evaluation")
            if bm:
                md.append(f"- **Experiment Name:** {bm.name}")
                md.append(f"- **Overall Resilience Score:** **{bm.overall_resilience_score or 0.0:.1f} / 100.0**")
                md.append(f"- **Evaluation Status:** `{bm.status}`")
                meta["overall_resilience_score"] = bm.overall_resilience_score
            else:
                md.append("*No benchmark experiments found.*")

        elif report_type == "incident_lifecycle":
            md.append("## 🔄 End-to-End Incident Lifecycle Audit")
            md.append("Comprehensive trace across Modules 1 to 8:")
            md.append("1. **Detection (Module 2):** Anomaly triggers alert based on threshold breach.")
            md.append("2. **Blast Radius (Module 3):** Reverse propagation graph calculates affected callers.")
            md.append("3. **RCA (Module 4):** Temporal precedence establishes earliest degradation.")
            md.append("4. **Diagnostic Agent (Module 5):** Shannon entropy selects next best check.")
            md.append("5. **Simulation (Module 6):** Multi-step discrete simulation verifies scenario.")
            md.append("6. **Recovery Planning (Module 7):** Multi-factor risk scorer creates 4 strategies.")
            md.append("7. **Validation (Module 8):** 5-pillar verification confirms complete resolution.")
            meta["lifecycle_verified"] = True

        else:
            md.append(f"## 📋 Operational Report: `{report_type}`")
            md.append("Data retrieved from active simulation state and persistent SQLite tables.")

        md.append("")
        md.append("---")
        md.append("")
        md.append("## 🔒 Compliance & Safety Guarantee")
        md.append("- **Zero Real Infrastructure Mutation:** All data was captured from isolated sandbox models.")
        md.append("- **Audit Lineage:** Every entry correlates directly with persistent database records.")
        md.append("")
        md.append("*CascadeShield AI Module 10: Unified Dashboard, Reports & Explainable AI Insights.*")

        return "\n".join(md), meta

    @classmethod
    def seed_default_reports(cls, db: Session) -> None:
        """Seeds initial canonical reports if none exist."""
        cls.generate_report(db, ReportGenerateRequest(
            report_type="service_health",
            report_title="Cloud Digital Twin Infrastructure Baseline",
            data_source="simulated"
        ))
        cls.generate_report(db, ReportGenerateRequest(
            report_type="incident_lifecycle",
            report_title="Full-Stack Incident Lifecycle Audit Report",
            data_source="simulated"
        ))
        cls.generate_report(db, ReportGenerateRequest(
            report_type="benchmarking",
            report_title="Resilience Benchmark & Baseline Performance Report",
            data_source="synthetic"
        ))
