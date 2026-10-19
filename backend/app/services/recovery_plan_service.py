import json
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session

from app.models.service import ServiceModel
from app.models.alert_model import AlertModel
from app.models.rca_model import RCAIncidentModel
from app.models.simulation_model import SimulationScenarioModel
from app.services.graph_service import GraphService
from app.services.recovery_risk_service import RecoveryRiskService
from app.schemas.recovery_schemas import (
    RecoveryActionCreate, 
    RecoveryPreconditionSchema, 
    RecoveryPlanCreateRequest,
    RecoveryPlanGenerateRequest
)

class RecoveryPlanService:
    """
    Intelligent generator for multi-strategy recovery plans.
    Generates Lowest-Risk, Fastest-Recovery, Lowest-Cost, and Balanced recovery strategies
    grounded in real evidence from Modules 1-6.
    """

    @classmethod
    def generate_candidate_plans(
        cls,
        db: Session,
        req: RecoveryPlanGenerateRequest
    ) -> List[RecoveryPlanCreateRequest]:
        # 1. Determine target service(s) from request, incident, or scenario
        target_sids = []
        incident_context = "General service degradation"

        if req.target_service_id:
            target_sids.append(req.target_service_id)

        if req.incident_id:
            incident = db.query(RCAIncidentModel).filter(RCAIncidentModel.id == req.incident_id).first()
            if incident:
                incident_context = incident.title
                if incident.service_id and incident.service_id not in target_sids:
                    target_sids.append(incident.service_id)

        if req.scenario_id:
            scenario = db.query(SimulationScenarioModel).filter(SimulationScenarioModel.id == req.scenario_id).first()
            if scenario and scenario.scenario_config_json:
                cfg = json.loads(scenario.scenario_config_json)
                for f in cfg.get("failures", []):
                    for ts in f.get("target_service_ids", []):
                        if ts not in target_sids:
                            target_sids.append(ts)

        if not target_sids:
            # Fallback to current unhealthy service in DB, or payment/database
            unhealthy = db.query(ServiceModel).filter(ServiceModel.health_status.in_(["DEGRADED", "CRITICAL"])).first()
            target_sids.append(unhealthy.id if unhealthy else "srv-payment")

        primary_target = target_sids[0]
        G_dep = GraphService.get_dependency_graph(db)

        # 2. Build 4 distinct architectural strategies
        plans: List[RecoveryPlanCreateRequest] = []

        # Strategy 1: Lowest-Risk Strategy (Circuit Breaker / Isolation / Cache Fallback)
        plans.append(cls._build_lowest_risk_plan(primary_target, incident_context, req.incident_id, req.scenario_id))

        # Strategy 2: Fastest-Recovery Strategy (Immediate Restart / Rollback)
        plans.append(cls._build_fastest_recovery_plan(primary_target, incident_context, req.incident_id, req.scenario_id))

        # Strategy 3: Lowest-Cost Strategy (Traffic Throttling / Rate-Limiting / Auto-Heal Wait)
        plans.append(cls._build_lowest_cost_plan(primary_target, incident_context, req.incident_id, req.scenario_id))

        # Strategy 4: Risk-Aware Balanced Strategy (Traffic Reroute -> Graceful Restart -> Verification)
        plans.append(cls._build_balanced_plan(primary_target, incident_context, req.incident_id, req.scenario_id))

        return plans

    @classmethod
    def _build_lowest_risk_plan(cls, target_sid: str, context: str, inc_id: Optional[str], scen_id: Optional[str]) -> RecoveryPlanCreateRequest:
        actions = [
            RecoveryActionCreate(
                action_type="isolate_dependency",
                target_service_id=target_sid,
                action_order=1,
                parameters={"circuit_breaker_threshold": 0.5, "fallback_mode": "mock_cache"},
                preconditions=[
                    RecoveryPreconditionSchema(name="Cache Availability", description="Fallback cache or mock responses must be operational.", status="satisfied"),
                    RecoveryPreconditionSchema(name="Degraded SLA Agreement", description="Stakeholders accept temporary read-only mode.", status="satisfied")
                ],
                estimated_duration=1,
                risk_score=12.0,
                reversibility="fully_reversible",
                possible_side_effects=["Stale cache responses served to callers"],
                expected_result="Immediately stops upstream queueing and halts failure cascade.",
                rollback_procedure="Disable circuit breaker; resume normal upstream passthrough."
            ),
            RecoveryActionCreate(
                action_type="retry_request",
                target_service_id=target_sid,
                action_order=2,
                parameters={"backoff_factor": 2.0, "max_retries": 3},
                preconditions=[
                    RecoveryPreconditionSchema(name="Idempotency Key", description="Requests must support safe idempotency.", status="satisfied")
                ],
                estimated_duration=2,
                risk_score=8.0,
                reversibility="fully_reversible",
                possible_side_effects=["Slight request latency escalation"],
                expected_result="Recovers transient failures smoothly without restarting instances.",
                rollback_procedure="Abort retry sequence."
            )
        ]

        return RecoveryPlanCreateRequest(
            incident_id=inc_id,
            scenario_id=scen_id,
            plan_name=f"Safe Isolation & Cache Fallback ({target_sid})",
            description=f"Lowest-risk non-destructive strategy: isolates {target_sid} with circuit breaker and serves cached fallbacks.",
            strategy_type="lowest_risk",
            actions=actions
        )

    @classmethod
    def _build_fastest_recovery_plan(cls, target_sid: str, context: str, inc_id: Optional[str], scen_id: Optional[str]) -> RecoveryPlanCreateRequest:
        actions = [
            RecoveryActionCreate(
                action_type="restart_service",
                target_service_id=target_sid,
                action_order=1,
                parameters={"force_kill": True, "grace_period_seconds": 0},
                preconditions=[
                    RecoveryPreconditionSchema(name="Stateless Process", description="Target service container must be stateless.", status="satisfied")
                ],
                estimated_duration=1,
                risk_score=48.0,
                reversibility="partially_reversible",
                possible_side_effects=["In-flight active requests will be dropped", "Temporary connection refusal during boot"],
                expected_result="Clears memory leaks, thread locks, and deadlock queues instantly.",
                rollback_procedure="Spawn secondary instance from backup image."
            ),
            RecoveryActionCreate(
                action_type="rollback_deployment",
                target_service_id=target_sid,
                action_order=2,
                parameters={"target_revision": "v_previous_stable"},
                preconditions=[
                    RecoveryPreconditionSchema(name="Artifact Repository Accessible", description="Previous container image exists in registry.", status="satisfied"),
                    RecoveryPreconditionSchema(name="Database Schema Backward Compatibility", description="Current DB schema must support previous code revision.", status="unresolved")
                ],
                estimated_duration=2,
                risk_score=55.0,
                reversibility="partially_reversible",
                possible_side_effects=["Schema mismatch if recent DB migration occurred"],
                expected_result="Eliminates newly introduced regressions.",
                rollback_procedure="Redeploy original release revision."
            )
        ]

        return RecoveryPlanCreateRequest(
            incident_id=inc_id,
            scenario_id=scen_id,
            plan_name=f"Immediate Container Restart & Rollback ({target_sid})",
            description=f"Fastest recovery strategy: instantly restarts {target_sid} and rolls back to previous revision.",
            strategy_type="fastest_recovery",
            actions=actions
        )

    @classmethod
    def _build_lowest_cost_plan(cls, target_sid: str, context: str, inc_id: Optional[str], scen_id: Optional[str]) -> RecoveryPlanCreateRequest:
        actions = [
            RecoveryActionCreate(
                action_type="wait_auto_recovery",
                target_service_id=target_sid,
                action_order=1,
                parameters={"wait_steps": 3, "watch_metric": "error_rate"},
                preconditions=[
                    RecoveryPreconditionSchema(name="Self-Healing Configured", description="Container platform has liveness/readiness probes.", status="satisfied")
                ],
                estimated_duration=3,
                risk_score=22.0,
                reversibility="fully_reversible",
                possible_side_effects=["Incident duration extended while waiting"],
                expected_result="Consumes 0 additional cloud resources while allowing transient spikes to clear.",
                rollback_procedure="Trigger active intervention if threshold not met."
            ),
            RecoveryActionCreate(
                action_type="traffic_reroute",
                target_service_id=target_sid,
                action_order=2,
                parameters={"throttle_percentage": 30.0, "shed_non_critical": True},
                preconditions=[
                    RecoveryPreconditionSchema(name="API Gateway Routing Rule", description="Gateway supports weight-based traffic shedding.", status="satisfied")
                ],
                estimated_duration=1,
                risk_score=18.0,
                reversibility="fully_reversible",
                possible_side_effects=["Non-critical customer requests deferred"],
                expected_result="Relieves server queue load with zero infrastructure scaling costs.",
                rollback_procedure="Restore 100% gateway traffic allocation."
            )
        ]

        return RecoveryPlanCreateRequest(
            incident_id=inc_id,
            scenario_id=scen_id,
            plan_name=f"Traffic Throttling & Self-Healing Watch ({target_sid})",
            description=f"Lowest-cost strategy: sheds non-essential traffic and monitors autonomous platform recovery.",
            strategy_type="lowest_cost",
            actions=actions
        )

    @classmethod
    def _build_balanced_plan(cls, target_sid: str, context: str, inc_id: Optional[str], scen_id: Optional[str]) -> RecoveryPlanCreateRequest:
        actions = [
            RecoveryActionCreate(
                action_type="traffic_reroute",
                target_service_id=target_sid,
                action_order=1,
                parameters={"reroute_to": f"{target_sid}-replica", "percentage": 80.0},
                preconditions=[
                    RecoveryPreconditionSchema(name="Replica Pool Health", description="Secondary replica or failover zone is online.", status="satisfied")
                ],
                estimated_duration=1,
                risk_score=20.0,
                reversibility="fully_reversible",
                possible_side_effects=["Brief latency fluctuation during DNS/router convergence"],
                expected_result="Diverts traffic away from degraded node to prevent cascade.",
                rollback_procedure="Re-route traffic back to primary cluster."
            ),
            RecoveryActionCreate(
                action_type="scale_up",
                target_service_id=target_sid,
                action_order=2,
                parameters={"additional_replicas": 2, "target_cpu_threshold": 60.0},
                preconditions=[
                    RecoveryPreconditionSchema(name="Cluster Capacity Available", description="Cloud provider quota supports 2 additional instances.", status="satisfied")
                ],
                estimated_duration=2,
                risk_score=24.0,
                reversibility="fully_reversible",
                possible_side_effects=["Modest cloud resource cost increase"],
                expected_result="Expands concurrency capacity to absorb peak load.",
                rollback_procedure="Scale down instances to baseline replica count."
            ),
            RecoveryActionCreate(
                action_type="restart_service",
                target_service_id=target_sid,
                action_order=3,
                parameters={"rolling_restart": True, "batch_size": 1},
                preconditions=[
                    RecoveryPreconditionSchema(name="Minimum Healthy Replicas", description="At least one replica remains live during rolling bounce.", status="satisfied")
                ],
                estimated_duration=2,
                risk_score=25.0,
                reversibility="fully_reversible",
                possible_side_effects=["Minor connection churn"],
                expected_result="Rolling restart flushes corrupted state with zero dropped requests.",
                rollback_procedure="Halt rolling update."
            )
        ]

        return RecoveryPlanCreateRequest(
            incident_id=inc_id,
            scenario_id=scen_id,
            plan_name=f"Traffic Diversion & Rolling Elastic Scale ({target_sid})",
            description=f"Risk-aware balanced strategy: gracefully diverts traffic, elastically scales capacity, and conducts rolling recovery.",
            strategy_type="balanced",
            actions=actions
        )
