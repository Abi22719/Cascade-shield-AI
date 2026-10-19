from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import or_

from app.models.service import ServiceModel
from app.models.alert_model import AlertModel
from app.models.rca_model import RCAIncidentModel
from app.models.simulation_model import SimulationScenarioModel
from app.models.recovery_models import RecoveryPlanModel
from app.models.validation_models import ValidationRunModel
from app.models.benchmark_models import BenchmarkExperimentModel
from app.schemas.search_schemas import SearchResultItem, SearchResponse, SearchSuggestionsResponse

class SearchService:
    """
    Unified global search service indexing and querying across services,
    alerts, incidents, simulation scenarios, recovery plans, validation runs,
    and benchmark experiments.
    """

    @classmethod
    def search(
        cls,
        db: Session,
        query: str,
        module_filter: Optional[str] = None,
        severity_filter: Optional[str] = None,
        service_filter: Optional[str] = None,
        status_filter: Optional[str] = None,
        skip: int = 0,
        limit: int = 50
    ) -> SearchResponse:
        q_clean = query.strip().lower()
        results: List[SearchResultItem] = []

        # 1. Services (Module 1)
        if not module_filter or module_filter in ["module_1", "digital_twin"]:
            svc_query = db.query(ServiceModel)
            if q_clean:
                svc_query = svc_query.filter(
                    or_(
                        ServiceModel.id.ilike(f"%{q_clean}%"),
                        ServiceModel.name.ilike(f"%{q_clean}%"),
                        ServiceModel.service_type.ilike(f"%{q_clean}%")
                    )
                )
            if status_filter:
                svc_query = svc_query.filter(ServiceModel.health_status == status_filter)

            for s in svc_query.limit(20).all():
                results.append(SearchResultItem(
                    record_id=s.id,
                    record_type="service",
                    title=f"Service: {s.name} ({s.id})",
                    subtitle=f"Type: {s.service_type} | Health: {s.health_status} | Latency: {s.latency_ms}ms",
                    source_module="module_1",
                    status=s.health_status,
                    severity=s.health_status,
                    created_at=s.updated_at,
                    url_path=f"/?module=digital-twin&serviceId={s.id}"
                ))

        # 2. Alerts (Module 2)
        if not module_filter or module_filter in ["module_2", "anomaly"]:
            alert_query = db.query(AlertModel)
            if q_clean:
                alert_query = alert_query.filter(
                    or_(
                        AlertModel.id.ilike(f"%{q_clean}%"),
                        AlertModel.service_id.ilike(f"%{q_clean}%"),
                        AlertModel.metric_name.ilike(f"%{q_clean}%"),
                        AlertModel.evidence_summary.ilike(f"%{q_clean}%")
                    )
                )
            if severity_filter:
                alert_query = alert_query.filter(AlertModel.severity == severity_filter)
            if service_filter:
                alert_query = alert_query.filter(AlertModel.service_id == service_filter)

            for a in alert_query.limit(20).all():
                obs = a.observed_value if a.observed_value is not None else 0.0
                thresh = a.threshold_value if a.threshold_value is not None else 0.0
                results.append(SearchResultItem(
                    record_id=a.id,
                    record_type="alert",
                    title=f"Alert: {a.metric_name} on {a.service_id}",
                    subtitle=f"Severity: {a.severity} | Val: {obs:.1f} vs Threshold: {thresh:.1f}",
                    source_module="module_2",
                    status="ACKNOWLEDGED" if a.acknowledged else "ACTIVE",
                    severity=a.severity,
                    created_at=a.created_at,
                    url_path=f"/?module=anomaly-detection&alertId={a.id}"
                ))

        # 3. Incidents (Module 4)
        if not module_filter or module_filter in ["module_4", "rca"]:
            inc_query = db.query(RCAIncidentModel)
            if q_clean:
                inc_query = inc_query.filter(
                    or_(
                        RCAIncidentModel.id.ilike(f"%{q_clean}%"),
                        RCAIncidentModel.title.ilike(f"%{q_clean}%"),
                        RCAIncidentModel.target_service_id.ilike(f"%{q_clean}%")
                    )
                )
            if service_filter:
                inc_query = inc_query.filter(RCAIncidentModel.target_service_id == service_filter)

            for inc in inc_query.limit(15).all():
                results.append(SearchResultItem(
                    record_id=inc.id,
                    record_type="incident",
                    title=f"RCA Incident: {inc.title}",
                    subtitle=f"Target: {inc.target_service_id} | Status: {inc.status}",
                    source_module="module_4",
                    status=inc.status,
                    severity="HIGH" if inc.status == "investigating" else "INFO",
                    created_at=inc.created_at,
                    url_path=f"/?module=root-cause-analysis&incidentId={inc.id}"
                ))

        # 4. Simulation Scenarios (Module 6)
        if not module_filter or module_filter in ["module_6", "simulation"]:
            sim_query = db.query(SimulationScenarioModel)
            if q_clean:
                sim_query = sim_query.filter(
                    or_(
                        SimulationScenarioModel.id.ilike(f"%{q_clean}%"),
                        SimulationScenarioModel.name.ilike(f"%{q_clean}%"),
                        SimulationScenarioModel.category.ilike(f"%{q_clean}%")
                    )
                )

            for sim in sim_query.limit(10).all():
                results.append(SearchResultItem(
                    record_id=sim.id,
                    record_type="scenario",
                    title=f"What-If Scenario: {sim.name}",
                    subtitle=f"Category: {sim.category} | Mode: {sim.source_data_type}",
                    source_module="module_6",
                    status="ACTIVE",
                    severity="WARNING",
                    created_at=sim.created_at,
                    url_path=f"/?module=what-if-simulation&scenarioId={sim.id}"
                ))

        # 5. Recovery Plans (Module 7)
        if not module_filter or module_filter in ["module_7", "recovery"]:
            plan_query = db.query(RecoveryPlanModel)
            if q_clean:
                plan_query = plan_query.filter(
                    or_(
                        RecoveryPlanModel.id.ilike(f"%{q_clean}%"),
                        RecoveryPlanModel.plan_name.ilike(f"%{q_clean}%"),
                        RecoveryPlanModel.strategy_type.ilike(f"%{q_clean}%")
                    )
                )

            for p in plan_query.limit(10).all():
                results.append(SearchResultItem(
                    record_id=p.id,
                    record_type="plan",
                    title=f"Recovery Plan: {p.plan_name}",
                    subtitle=f"Strategy: {p.strategy_type} | Est Risk: {p.risk_score:.1f}",
                    source_module="module_7",
                    status="GENERATED",
                    severity="INFO",
                    created_at=p.created_at,
                    url_path=f"/?module=recovery-planning&planId={p.id}"
                ))

        # 6. Validation Runs (Module 8)
        if not module_filter or module_filter in ["module_8", "validation"]:
            val_query = db.query(ValidationRunModel)
            if q_clean:
                val_query = val_query.filter(
                    or_(
                        ValidationRunModel.id.ilike(f"%{q_clean}%"),
                        ValidationRunModel.overall_outcome.ilike(f"%{q_clean}%"),
                        ValidationRunModel.recovery_plan_id.ilike(f"%{q_clean}%")
                    )
                )

            for v in val_query.limit(10).all():
                results.append(SearchResultItem(
                    record_id=v.id,
                    record_type="validation",
                    title=f"Validation Run: {v.id[:8]}",
                    subtitle=f"Outcome: {v.overall_outcome} | Checks Passed: {v.passed_checks}/{v.total_checks}",
                    source_module="module_8",
                    status=v.overall_outcome,
                    severity="SUCCESS" if v.overall_outcome == "VERIFIED_SUCCESS" else "WARNING",
                    created_at=v.created_at,
                    url_path=f"/?module=recovery-validation&validationId={v.id}"
                ))

        # 7. Benchmark Experiments (Module 9)
        if not module_filter or module_filter in ["module_9", "benchmark"]:
            bm_query = db.query(BenchmarkExperimentModel)
            if q_clean:
                bm_query = bm_query.filter(
                    or_(
                        BenchmarkExperimentModel.id.ilike(f"%{q_clean}%"),
                        BenchmarkExperimentModel.name.ilike(f"%{q_clean}%"),
                        BenchmarkExperimentModel.status.ilike(f"%{q_clean}%")
                    )
                )

            for b in bm_query.limit(10).all():
                results.append(SearchResultItem(
                    record_id=b.id,
                    record_type="benchmark",
                    title=f"Benchmark: {b.name}",
                    subtitle=f"Score: {b.overall_resilience_score or 'N/A'}/100 | Status: {b.status}",
                    source_module="module_9",
                    status=b.status,
                    severity="INFO",
                    created_at=b.created_at,
                    url_path=f"/?module=resilience-benchmark&experimentId={b.id}"
                ))

        # Paginate
        paginated_results = results[skip : skip + limit]

        return SearchResponse(
            query=query,
            total_results=len(results),
            results=paginated_results
        )

    @classmethod
    def get_suggestions(cls, db: Session, limit: int = 8) -> SearchSuggestionsResponse:
        services = db.query(ServiceModel.name).limit(5).all()
        svc_names = [s[0] for s in services]
        common = [
            "database latency",
            "payment service unavailable",
            "api gateway connection storm",
            "auth verification failure"
        ]
        return SearchSuggestionsResponse(suggestions=list(dict.fromkeys(svc_names + common))[:limit])
