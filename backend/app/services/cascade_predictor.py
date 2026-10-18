import logging
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from fastapi import HTTPException

from app.models.service import ServiceModel
from app.models.dependency import DependencyModel
from app.models.alert_model import AlertModel
from app.schemas.cascade_schema import (
    CascadePredictRequest,
    CascadePredictionResponse,
    ImpactedServiceResult,
    CascadePathInfo,
    CascadeSummaryResponse
)
from app.services.impact_analyzer import ImpactAnalyzer
from app.services.risk_scorer import RiskScorer
from app.services.evidence_builder import EvidenceBuilder
from app.services.propagation_simulator import PropagationSimulator
from app.database.cascade_repository import CascadeRepository

logger = logging.getLogger("cascadeshield.cascade_predictor")

class CascadePredictor:
    @staticmethod
    def predict_cascade(
        db: Session,
        request: CascadePredictRequest
    ) -> CascadePredictionResponse:
        """
        Orchestrates full cascading failure prediction:
        1. Validates root service existence in digital twin.
        2. Retrieves all digital twin services, dependencies, and active alerts.
        3. Constructs failure propagation directed graph (reversing callee -> caller dependencies).
        4. Traverses reachable callers, identifies multi-hop propagation paths.
        5. Computes normalized risk scores (0-100), risk bands, and heuristic probabilities.
        6. Generates tailored cloud resilience recommendations.
        7. Simulates step-by-step propagation timeline.
        """
        # 1. Fetch root service
        root_service = db.query(ServiceModel).filter(ServiceModel.id == request.initial_service_id).first()
        if not root_service:
            raise HTTPException(
                status_code=404,
                detail=f"Service with ID '{request.initial_service_id}' was not found in the Digital Twin."
            )

        # 2. Fetch all services and dependencies
        services = db.query(ServiceModel).all()
        dependencies = db.query(DependencyModel).all()
        
        # Fetch active unacknowledged alerts from Module 2 to amplify risk
        try:
            active_alerts = db.query(AlertModel).filter(AlertModel.acknowledged == False).all()
        except Exception as e:
            logger.warning(f"Could not load active alerts for cascade risk scoring: {e}")
            active_alerts = []

        # 3. Build reverse failure propagation graph
        G_prop = ImpactAnalyzer.build_propagation_graph(services, dependencies)

        # 4. Cycle-safe traversal to find affected callers and paths
        affected_nodes_dict, all_paths = ImpactAnalyzer.find_affected_services_and_paths(
            G_prop=G_prop,
            root_service_id=request.initial_service_id,
            max_hops=request.propagation_steps
        )

        impacted_results: List[ImpactedServiceResult] = []

        # 5a. Root service itself as Root Failure
        root_base_risk = 95.0 if request.failure_severity == "severe" else (
            70.0 if request.failure_severity == "moderate" else 40.0
        )
        root_evidence = [
            f"Ground-zero origin: {request.failure_severity.upper()} {request.failure_type.replace('_', ' ')} incident injected.",
            f"Initial resource baseline: CPU {root_service.cpu_usage}%, Memory {root_service.memory_usage}%, Latency {root_service.latency_ms}ms, Error Rate {root_service.error_rate}%."
        ]
        root_rec = EvidenceBuilder.generate_recommendation(
            service_name=root_service.name,
            service_type=root_service.service_type,
            risk_level=RiskScorer.get_risk_level(root_base_risk),
            hop_distance=0,
            failure_type=request.failure_type
        )

        root_result = ImpactedServiceResult(
            service_id=root_service.id,
            service_name=root_service.name,
            service_type=root_service.service_type,
            impact_type="Root Failure",
            hop_distance=0,
            estimated_risk_score=root_base_risk,
            risk_level=RiskScorer.get_risk_level(root_base_risk),
            propagation_probability_estimate=1.0,
            contributing_evidence=root_evidence,
            impacted_by_services=[],
            failure_paths=[],
            recommended_monitoring_action=root_rec,
            estimated_step_onset=0
        )
        impacted_results.append(root_result)

        # 5b. Compute risk and evidence for each affected downstream service
        service_lookup = {s.id: s for s in services}

        # Index paths by target service
        paths_by_target: Dict[str, List[CascadePathInfo]] = {}
        for p in all_paths:
            target_id = p.path[-1]
            if target_id not in paths_by_target:
                paths_by_target[target_id] = []
            paths_by_target[target_id].append(p)

        for svc_id, info in affected_nodes_dict.items():
            node_data = G_prop.nodes[svc_id] if G_prop.has_node(svc_id) else {}
            service_paths = paths_by_target.get(svc_id, [])
            service_alerts = [a for a in active_alerts if a.service_id == svc_id]

            risk_score, risk_level, prop_prob, evidence = RiskScorer.calculate_service_cascade_risk(
                service_node=node_data,
                hop_distance=info["hop_distance"],
                failure_type=request.failure_type,
                failure_severity=request.failure_severity,
                paths_to_service=service_paths,
                recent_alerts=service_alerts,
                attenuation_factor=request.attenuation_factor,
                custom_weights=request.custom_weights
            )

            service_rec = EvidenceBuilder.generate_recommendation(
                service_name=info["service_name"],
                service_type=node_data.get("service_type", "service"),
                risk_level=risk_level,
                hop_distance=info["hop_distance"],
                failure_type=request.failure_type
            )

            svc_result = ImpactedServiceResult(
                service_id=svc_id,
                service_name=info["service_name"],
                service_type=node_data.get("service_type", "service"),
                impact_type=info["impact_type"],
                hop_distance=info["hop_distance"],
                estimated_risk_score=risk_score,
                risk_level=risk_level,
                propagation_probability_estimate=prop_prob,
                contributing_evidence=evidence,
                impacted_by_services=info["impacted_by"],
                failure_paths=service_paths,
                recommended_monitoring_action=service_rec,
                estimated_step_onset=info["hop_distance"]
            )
            impacted_results.append(svc_result)

        # Sort impacted services by hop_distance ascending, then risk_score descending
        impacted_results.sort(key=lambda x: (x.hop_distance, -x.estimated_risk_score))

        # 6. Discrete time-step simulation timeline
        timeline = PropagationSimulator.simulate_propagation_timeline(
            root_service_id=root_service.id,
            root_service_name=root_service.name,
            failure_type=request.failure_type,
            failure_severity=request.failure_severity,
            impacted_results=impacted_results,
            max_steps=request.propagation_steps
        )

        # 7. Aggregate statistics
        direct_count = sum(1 for s in impacted_results if s.impact_type == "Direct")
        indirect_count = sum(1 for s in impacted_results if s.impact_type == "Indirect")
        high_risk_count = sum(1 for s in impacted_results if s.risk_level == "High")
        critical_risk_count = sum(1 for s in impacted_results if s.risk_level == "Critical")
        max_risk = max((s.estimated_risk_score for s in impacted_results), default=0.0)

        # Executive summary recommendations
        exec_recs = EvidenceBuilder.build_executive_summary_recommendations(
            impacted_count=len(impacted_results) - 1,  # exclude root itself
            high_risk_count=high_risk_count,
            critical_risk_count=critical_risk_count,
            root_service_name=root_service.name
        )

        return CascadePredictionResponse(
            initial_service_id=root_service.id,
            initial_service_name=root_service.name,
            failure_type=request.failure_type,
            failure_severity=request.failure_severity,
            total_services_analyzed=len(services),
            total_impacted_services=len(impacted_results),
            direct_impact_count=direct_count,
            indirect_impact_count=indirect_count,
            high_risk_count=high_risk_count,
            critical_risk_count=critical_risk_count,
            max_risk_score=round(max_risk, 1),
            impacted_services=impacted_results,
            simulation_timeline=timeline,
            primary_propagation_paths=all_paths[:15],  # top 15 most prominent paths
            recommendations=exec_recs,
            data_source="simulated",
            generated_at=datetime.now(timezone.utc)
        )

    @staticmethod
    def get_impact_for_service(
        db: Session,
        service_id: str,
        max_hops: int = 5
    ) -> Dict[str, Any]:
        """
        Calculates and returns directly and indirectly impacted callers for a given service.
        """
        service = db.query(ServiceModel).filter(ServiceModel.id == service_id).first()
        if not service:
            raise HTTPException(status_code=404, detail=f"Service '{service_id}' not found.")

        services = db.query(ServiceModel).all()
        dependencies = db.query(DependencyModel).all()
        G_prop = ImpactAnalyzer.build_propagation_graph(services, dependencies)

        affected, paths = ImpactAnalyzer.find_affected_services_and_paths(G_prop, service_id, max_hops)

        direct_services = [v for v in affected.values() if v["impact_type"] == "Direct"]
        indirect_services = [v for v in affected.values() if v["impact_type"] == "Indirect"]

        return {
            "root_service_id": service.id,
            "root_service_name": service.name,
            "direct_impact_count": len(direct_services),
            "indirect_impact_count": len(indirect_services),
            "total_impacted_count": len(affected),
            "direct_services": direct_services,
            "indirect_services": indirect_services,
            "propagation_paths_count": len(paths),
            "max_hops_explored": max_hops,
            "data_source": "simulated"
        }

    @staticmethod
    def get_paths_for_service(
        db: Session,
        service_id: str,
        max_hops: int = 5
    ) -> List[CascadePathInfo]:
        """
        Returns all failure propagation paths emerging from service_id.
        """
        service = db.query(ServiceModel).filter(ServiceModel.id == service_id).first()
        if not service:
            raise HTTPException(status_code=404, detail=f"Service '{service_id}' not found.")

        services = db.query(ServiceModel).all()
        dependencies = db.query(DependencyModel).all()
        G_prop = ImpactAnalyzer.build_propagation_graph(services, dependencies)

        _, paths = ImpactAnalyzer.find_affected_services_and_paths(G_prop, service_id, max_hops)
        return paths

    @staticmethod
    def get_summary(db: Session) -> CascadeSummaryResponse:
        """
        Generates overall summary metrics for the cascade prediction engine.
        """
        services_count = db.query(ServiceModel).count()
        dependencies_count = db.query(DependencyModel).count()

        latest_scenario = CascadeRepository.get_latest_scenario(db)
        last_status = "Ready"
        last_time = None
        predicted_impacted = 0
        high_risk = 0
        critical_risk = 0

        if latest_scenario:
            last_status = f"Simulated: {latest_scenario.scenario_name}"
            last_time = latest_scenario.created_at
            try:
                import json
                summary_data = json.loads(latest_scenario.result_summary)
                predicted_impacted = summary_data.get("total_impacted_services", 0)
                high_risk = summary_data.get("high_risk_count", 0)
                critical_risk = summary_data.get("critical_risk_count", 0)
            except Exception:
                pass

        return CascadeSummaryResponse(
            total_services=services_count,
            total_dependencies=dependencies_count,
            predicted_impacted_services=predicted_impacted,
            high_risk_services=high_risk,
            critical_risk_services=critical_risk,
            last_simulation_status=last_status,
            last_simulation_time=last_time
        )
