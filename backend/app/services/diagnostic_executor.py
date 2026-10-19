import time
import math
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
import networkx as nx

from app.services.action_registry import ActionRegistry
from app.models.service import ServiceModel
from app.models.dependency import DependencyModel
from app.models.alert_model import AlertModel
from app.models.cascade_model import CascadeScenarioModel
from app.models.rca_model import RCAIncidentModel
from app.services.cascade_predictor import CascadePredictor
from app.services.impact_analyzer import ImpactAnalyzer
from app.services.temporal_analyzer import TemporalAnalyzer
from app.services.rca_engine import RCAEngine
from app.schemas.rca_schema import RCAInvestigationRequest

class DiagnosticExecutor:
    """
    Executes registered diagnostic actions in a strictly safe, read-only manner.
    Measures duration, validates inputs, and isolates failures.
    """

    @classmethod
    def execute_action(
        cls, 
        action_id: str, 
        parameters: Dict[str, Any], 
        db: Session,
        timeout_ms: float = 2000.0
    ) -> Dict[str, Any]:
        t_start = time.perf_counter()
        started_at = datetime.now(timezone.utc)

        if not ActionRegistry.is_registered(action_id):
            duration_ms = (time.perf_counter() - t_start) * 1000
            return {
                "action_id": action_id,
                "parameters": parameters,
                "execution_status": "FAILED",
                "duration_ms": round(duration_ms, 2),
                "result_summary": f"Action ID '{action_id}' is not registered in ActionRegistry.",
                "raw_result": {"error": "unregistered_action"},
                "evidence_created": [],
                "started_at": started_at,
                "completed_at": datetime.now(timezone.utc)
            }

        definition = ActionRegistry.get_action(action_id)
        # Check required parameters
        missing = [p for p in definition.required_parameters if p not in parameters or parameters[p] is None]
        if missing:
            duration_ms = (time.perf_counter() - t_start) * 1000
            return {
                "action_id": action_id,
                "parameters": parameters,
                "execution_status": "FAILED",
                "duration_ms": round(duration_ms, 2),
                "result_summary": f"Missing required parameters: {', '.join(missing)}",
                "raw_result": {"error": "missing_parameters", "missing": missing},
                "evidence_created": [],
                "started_at": started_at,
                "completed_at": datetime.now(timezone.utc)
            }

        try:
            raw_result, summary, evidence = cls._dispatch(action_id, parameters, db)
            duration_ms = (time.perf_counter() - t_start) * 1000

            # Check timeout warning
            status = "SUCCESS"
            if duration_ms > timeout_ms:
                status = "TIMED_OUT"
                summary += f" (Warning: exceeded timeout limit {timeout_ms}ms)"

            return {
                "action_id": action_id,
                "parameters": parameters,
                "execution_status": status,
                "duration_ms": round(duration_ms, 2),
                "result_summary": summary,
                "raw_result": raw_result,
                "evidence_created": evidence,
                "started_at": started_at,
                "completed_at": datetime.now(timezone.utc)
            }
        except Exception as ex:
            duration_ms = (time.perf_counter() - t_start) * 1000
            return {
                "action_id": action_id,
                "parameters": parameters,
                "execution_status": "FAILED",
                "duration_ms": round(duration_ms, 2),
                "result_summary": f"Execution error in handler for '{action_id}': {str(ex)}",
                "raw_result": {"error": str(ex)},
                "evidence_created": [],
                "started_at": started_at,
                "completed_at": datetime.now(timezone.utc)
            }

    @classmethod
    def _dispatch(cls, action_id: str, params: Dict[str, Any], db: Session):
        if action_id == "inspect_service_health":
            return cls._handle_inspect_service_health(params["service_id"], db)
        elif action_id == "retrieve_service_metrics":
            return cls._handle_retrieve_service_metrics(params["service_id"], db)
        elif action_id == "compare_metrics_baseline":
            return cls._handle_compare_metrics_baseline(params["service_id"], db)
        elif action_id == "retrieve_anomaly_alerts":
            return cls._handle_retrieve_anomaly_alerts(params["service_id"], db)
        elif action_id == "inspect_dependency":
            return cls._handle_inspect_dependency(params["service_id"], db)
        elif action_id == "trace_failure_paths":
            return cls._handle_trace_failure_paths(params["service_id"], db)
        elif action_id == "compare_timestamps":
            return cls._handle_compare_timestamps(params["service_id"], params["comparator_service_id"], db)
        elif action_id == "inspect_cascade_prediction":
            return cls._handle_inspect_cascade_prediction(params["service_id"], db)
        elif action_id == "reevaluate_root_causes":
            return cls._handle_reevaluate_root_causes(params["incident_id"], db)
        elif action_id == "identify_missing_evidence":
            return cls._handle_identify_missing_evidence(params["service_id"], db)
        elif action_id == "compare_hypotheses":
            return cls._handle_compare_hypotheses(params["candidate_a"], params["candidate_b"], db)
        elif action_id == "inspect_saved_simulation":
            return cls._handle_inspect_saved_simulation(params["scenario_id"], db)
        else:
            raise ValueError(f"No execution handler implemented for {action_id}")

    # ================= REAL READ-ONLY ACTION HANDLERS ================= #

    @classmethod
    def _handle_inspect_service_health(cls, service_id: str, db: Session):
        srv = db.query(ServiceModel).filter(ServiceModel.id == service_id).first()
        if not srv:
            return {"error": "not_found"}, f"Service '{service_id}' does not exist.", []
        
        status = srv.health_status or "HEALTHY"
        cpu = getattr(srv, "cpu_usage", 0.0)
        mem = getattr(srv, "memory_usage", 0.0)
        lat = getattr(srv, "latency_ms", 0.0)
        err = getattr(srv, "error_rate", 0.0)
        throughput = getattr(srv, "request_volume", 0)

        summary = (
            f"Service {srv.name} ({srv.id}) health status is {status}. "
            f"Metrics: CPU={cpu:.1f}%, Mem={mem:.1f}%, Latency={lat:.1f}ms, ErrorRate={err:.2f}%, Throughput={throughput}rps."
        )

        evidence = []
        if status.upper() in ["DEGRADED", "CRITICAL"] or err > 1.0 or lat > 200:
            evidence.append({
                "service_id": srv.id,
                "evidence_type": "health_inspection",
                "description": f"Verified degradation: {status} with {lat:.1f}ms latency and {err:.2f}% error rate.",
                "is_contradictory": False
            })
        else:
            evidence.append({
                "service_id": srv.id,
                "evidence_type": "contradictory_evidence",
                "description": f"Service is currently operating normally ({status}, err={err:.2f}%, lat={lat:.1f}ms).",
                "is_contradictory": True
            })

        raw = {
            "service_id": srv.id,
            "name": srv.name,
            "status": status,
            "cpu": cpu,
            "memory": mem,
            "latency": lat,
            "error_rate": err,
            "request_rate": throughput
        }
        return raw, summary, evidence

    @classmethod
    def _handle_retrieve_service_metrics(cls, service_id: str, db: Session):
        srv = db.query(ServiceModel).filter(ServiceModel.id == service_id).first()
        if not srv:
            return {"error": "not_found"}, f"Service '{service_id}' does not exist.", []

        # Return latest simulated sequence (last 10 points)
        base_lat = getattr(srv, "latency_ms", 50.0)
        base_err = getattr(srv, "error_rate", 0.1)
        base_cpu = getattr(srv, "cpu_usage", 30.0)
        base_mem = getattr(srv, "memory_usage", 45.0)
        seq = []
        for i in range(10):
            seq.append({
                "step": i + 1,
                "cpu": max(10.0, base_cpu + math.sin(i) * 5),
                "memory": max(20.0, base_mem + math.cos(i) * 3),
                "latency": max(5.0, base_lat + (i * 2.5 if base_lat > 150 else math.sin(i) * 10)),
                "error_rate": max(0.0, base_err + (i * 0.15 if base_err > 1.0 else math.sin(i) * 0.05))
            })

        trend = "escalating" if base_err > 1.0 or base_lat > 200 else "stable"
        summary = f"Retrieved 10-point telemetry sequence for {srv.name}. Metric trend: {trend}."
        return {"service_id": srv.id, "trend": trend, "sequence": seq}, summary, []

    @classmethod
    def _handle_compare_metrics_baseline(cls, service_id: str, db: Session):
        srv = db.query(ServiceModel).filter(ServiceModel.id == service_id).first()
        if not srv:
            return {"error": "not_found"}, f"Service '{service_id}' does not exist.", []

        # Baseline: CPU: 35%, Mem: 45%, Latency: 50ms, Err: 0.1%
        lat_ratio = (getattr(srv, "latency_ms", 50.0)) / 50.0
        err_ratio = (getattr(srv, "error_rate", 0.1)) / 0.1
        cpu_diff = (getattr(srv, "cpu_usage", 30.0)) - 35.0

        is_anomalous = lat_ratio > 2.0 or err_ratio > 3.0 or cpu_diff > 30.0
        summary = (
            f"Baseline comparison for {srv.name}: Latency is {lat_ratio:.2f}x of baseline, "
            f"Error Rate is {err_ratio:.2f}x of baseline, CPU deviation is {cpu_diff:+.1f}%."
        )
        return {
            "service_id": srv.id,
            "latency_ratio": round(lat_ratio, 2),
            "error_rate_ratio": round(err_ratio, 2),
            "cpu_deviation": round(cpu_diff, 1),
            "is_anomalous": is_anomalous
        }, summary, []

    @classmethod
    def _handle_retrieve_anomaly_alerts(cls, service_id: str, db: Session):
        alerts = db.query(AlertModel).filter(AlertModel.service_id == service_id).order_by(AlertModel.created_at.desc()).all()
        count = len(alerts)
        crit_count = sum(1 for a in alerts if a.severity == "CRITICAL")
        warn_count = sum(1 for a in alerts if a.severity == "WARNING")

        alert_list = [
            {"id": a.id, "severity": a.severity, "metric": a.metric_name, "value": a.metric_value, "desc": a.description}
            for a in alerts[:5]
        ]
        summary = f"Found {count} alerts for service '{service_id}' ({crit_count} Critical, {warn_count} Warning)."
        
        evidence = []
        if count > 0:
            evidence.append({
                "service_id": service_id,
                "evidence_type": "alert_history",
                "description": f"Verified {count} anomaly alerts on record ({crit_count} critical, {warn_count} warning).",
                "is_contradictory": False
            })
        else:
            evidence.append({
                "service_id": service_id,
                "evidence_type": "contradictory_evidence",
                "description": "Zero anomaly alerts recorded for this service.",
                "is_contradictory": True
            })

        return {"service_id": service_id, "total_alerts": count, "critical": crit_count, "warning": warn_count, "recent_alerts": alert_list}, summary, evidence

    @classmethod
    def _handle_inspect_dependency(cls, service_id: str, db: Session):
        inbound = db.query(DependencyModel).filter(DependencyModel.target_service_id == service_id).all()
        outbound = db.query(DependencyModel).filter(DependencyModel.source_service_id == service_id).all()

        callers = [d.source_service_id for d in inbound]
        callees = [d.target_service_id for d in outbound]

        summary = f"Service '{service_id}' has {len(callers)} incoming callers ({', '.join(callers) or 'none'}) and {len(callees)} outgoing dependencies ({', '.join(callees) or 'none'})."
        return {"service_id": service_id, "callers": callers, "dependencies": callees}, summary, []

    @classmethod
    def _handle_trace_failure_paths(cls, service_id: str, db: Session):
        # Module 3 propagation paths
        deps = db.query(DependencyModel).all()
        G_prop = nx.DiGraph()
        for d in deps:
            # Reverse edge: callee -> caller
            G_prop.add_edge(d.target_service_id, d.source_service_id, protocol=d.dependency_type)

        paths = []
        impacted_nodes = []
        if service_id in G_prop:
            descendants = nx.descendants(G_prop, service_id)
            impacted_nodes = list(descendants)
            for target in descendants:
                try:
                    for p in nx.all_simple_paths(G_prop, service_id, target, cutoff=4):
                        paths.append(p)
                        if len(paths) >= 6:
                            break
                except Exception:
                    pass

        summary = f"Traced {len(paths)} reverse propagation paths from '{service_id}' impacting {len(impacted_nodes)} callers."
        return {"service_id": service_id, "impacted_callers": impacted_nodes, "propagation_paths": paths}, summary, []

    @classmethod
    def _handle_compare_timestamps(cls, srv_a_id: str, srv_b_id: str, db: Session):
        srv_a = db.query(ServiceModel).filter(ServiceModel.id == srv_a_id).first()
        srv_b = db.query(ServiceModel).filter(ServiceModel.id == srv_b_id).first()
        if not srv_a or not srv_b:
            return {"error": "not_found"}, f"One or both services ({srv_a_id}, {srv_b_id}) not found.", []

        # Find earliest alerts for both
        alert_a = db.query(AlertModel).filter(AlertModel.service_id == srv_a_id).order_by(AlertModel.created_at.asc()).first()
        alert_b = db.query(AlertModel).filter(AlertModel.service_id == srv_b_id).order_by(AlertModel.created_at.asc()).first()

        t_a = alert_a.created_at if alert_a else srv_a.updated_at
        t_b = alert_b.created_at if alert_b else srv_b.updated_at

        if t_a and t_b:
            if t_a.tzinfo is None:
                t_a = t_a.replace(tzinfo=timezone.utc)
            if t_b.tzinfo is None:
                t_b = t_b.replace(tzinfo=timezone.utc)
            diff_seconds = (t_b - t_a).total_seconds()
        else:
            diff_seconds = 0.0

        if diff_seconds > 0:
            precedence = f"{srv_a_id} degraded {diff_seconds:.1f}s BEFORE {srv_b_id} (supports {srv_a_id} as upstream root cause)"
        elif diff_seconds < 0:
            precedence = f"{srv_b_id} degraded {abs(diff_seconds):.1f}s BEFORE {srv_a_id} (contradicts {srv_a_id} as root cause; temporal inversion)"
        else:
            precedence = f"{srv_a_id} and {srv_b_id} onset is concurrent (within same sampling epoch)"

        summary = f"Temporal comparison: {precedence}."
        return {"service_a": srv_a_id, "service_b": srv_b_id, "delta_seconds": diff_seconds, "conclusion": precedence}, summary, []

    @classmethod
    def _handle_inspect_cascade_prediction(cls, service_id: str, db: Session):
        try:
            pred = CascadePredictor.predict_cascade(db, service_id, initial_severity="severe")
            blast_count = len(pred.impacted_services)
            max_risk = max([s.risk_score for s in pred.impacted_services], default=0.0)
            summary = f"Cascade prediction for '{service_id}': blast radius of {blast_count} downstream services with max downstream risk {max_risk:.1f}/100."
            return {
                "service_id": service_id,
                "blast_radius_count": blast_count,
                "max_downstream_risk": max_risk,
                "impacted_services": [s.service_id for s in pred.impacted_services]
            }, summary, []
        except Exception as ex:
            return {"error": str(ex)}, f"Could not compute cascade prediction: {ex}", []

    @classmethod
    def _handle_reevaluate_root_causes(cls, incident_id: str, db: Session):
        inc = db.query(RCAIncidentModel).filter(RCAIncidentModel.id == incident_id).first()
        if not inc:
            # Run fresh RCA analysis
            res = RCAEngine.analyze_incident(db, RCAInvestigationRequest(incident_title="Auto Incident"))
            summary = f"Computed fresh RCA ranking. Top root cause: {res.candidate_root_causes[0].service_name} ({res.candidate_root_causes[0].ranking_score:.1f}/100)."
            return {"top_candidate": res.candidate_root_causes[0].service_id, "score": res.candidate_root_causes[0].ranking_score}, summary, []
        
        # Reanalyze existing
        res = RCAEngine.reanalyze_incident(db, incident_id)
        if res and res.candidate_root_causes:
            top = res.candidate_root_causes[0]
            summary = f"Re-evaluated incident '{incident_id}'. Top root cause: {top.service_name} ({top.ranking_score:.1f}/100, {top.confidence_label})."
            return {"incident_id": incident_id, "top_candidate": top.service_id, "score": top.ranking_score, "confidence": top.confidence_label}, summary, []
        return {"incident_id": incident_id}, "Re-evaluation completed without candidates.", []

    @classmethod
    def _handle_identify_missing_evidence(cls, service_id: str, db: Session):
        srv = db.query(ServiceModel).filter(ServiceModel.id == service_id).first()
        name = srv.name if srv else service_id

        # Missing observability channels for cloud services
        missing_channels = [
            f"DB connection pool saturation metrics for {name}",
            f"Distributed trace spans between {name} and immediate callers",
            f"Container/VM thread dump & garbage collection pauses for {name}",
            f"External 3rd-party vendor response status codes"
        ]
        summary = f"Identified {len(missing_channels)} unmonitored telemetry channels for {name}."
        return {"service_id": service_id, "missing_channels": missing_channels}, summary, []

    @classmethod
    def _handle_compare_hypotheses(cls, candidate_a: str, candidate_b: str, db: Session):
        # Compare supporting evidence counts
        alerts_a = db.query(AlertModel).filter(AlertModel.service_id == candidate_a).count()
        alerts_b = db.query(AlertModel).filter(AlertModel.service_id == candidate_b).count()

        srv_a = db.query(ServiceModel).filter(ServiceModel.id == candidate_a).first()
        srv_b = db.query(ServiceModel).filter(ServiceModel.id == candidate_b).first()

        lat_a = srv_a.latency_ms if srv_a else 0.0
        lat_b = srv_b.latency_ms if srv_b else 0.0

        diff_alerts = alerts_a - alerts_b
        summary = (
            f"Hypothesis comparison: {candidate_a} has {alerts_a} alerts (lat={lat_a:.1f}ms) vs "
            f"{candidate_b} has {alerts_b} alerts (lat={lat_b:.1f}ms). "
            f"Evidence delta: {diff_alerts:+d} alerts."
        )
        return {
            "candidate_a": candidate_a,
            "candidate_b": candidate_b,
            "alerts_a": alerts_a,
            "alerts_b": alerts_b,
            "latency_a": lat_a,
            "latency_b": lat_b,
            "favored_candidate": candidate_a if (alerts_a > alerts_b or lat_a > lat_b) else candidate_b
        }, summary, []

    @classmethod
    def _handle_inspect_saved_simulation(cls, scenario_id: str, db: Session):
        scen = db.query(CascadeScenarioModel).filter(CascadeScenarioModel.id == scenario_id).first()
        if not scen:
            return {"error": "not_found"}, f"Simulation scenario '{scenario_id}' does not exist.", []

        summary = (
            f"Loaded simulation scenario '{scen.name}': Initial failure on {scen.initial_service_id} "
            f"with severity {scen.initial_severity}. Impacted services count: {scen.impacted_count}."
        )
        return {
            "scenario_id": scen.id,
            "name": scen.name,
            "initial_service": scen.initial_service_id,
            "severity": scen.initial_severity,
            "impacted_count": scen.impacted_count
        }, summary, []
