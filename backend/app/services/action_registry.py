from typing import Dict, Any, List, Optional, Callable
from pydantic import BaseModel
from app.schemas.agent_schema import AgentActionDefinition

class ActionRegistry:
    """
    Central registry of safe, read-only diagnostic actions supported by CascadeShield AI.
    All actions are strictly non-destructive and query simulation or persisted state.
    """
    _actions: Dict[str, AgentActionDefinition] = {}
    _handlers: Dict[str, Callable] = {}

    @classmethod
    def register(cls, definition: AgentActionDefinition, handler: Callable):
        cls._actions[definition.action_id] = definition
        cls._handlers[definition.action_id] = handler

    @classmethod
    def get_action(cls, action_id: str) -> Optional[AgentActionDefinition]:
        return cls._actions.get(action_id)

    @classmethod
    def get_all_actions(cls) -> List[AgentActionDefinition]:
        return list(cls._actions.values())

    @classmethod
    def get_handler(cls, action_id: str) -> Optional[Callable]:
        return cls._handlers.get(action_id)

    @classmethod
    def is_registered(cls, action_id: str) -> bool:
        return action_id in cls._actions

# Initialize and populate default actions
def register_default_actions():
    if ActionRegistry._actions:
        return  # already registered

    # 1. Inspect Service Health
    ActionRegistry.register(
        AgentActionDefinition(
            action_id="inspect_service_health",
            action_name="Inspect Service Health & Telemetry",
            description="Queries current runtime metrics, status (HEALTHY, DEGRADED, CRITICAL), and error rates.",
            target_type="service",
            required_parameters=["service_id"],
            estimated_cost=0.05,
            estimated_execution_time_ms=5.0,
            risk_level="READ_ONLY",
            information_value=0.75,
            applicable_conditions=["target_service_specified", "suspected_service_exists"]
        ),
        handler=None  # Bound in executor
    )

    # 2. Retrieve Service Historical Metrics
    ActionRegistry.register(
        AgentActionDefinition(
            action_id="retrieve_service_metrics",
            action_name="Retrieve Historical Metric Sequence",
            description="Fetches recent time-series telemetry points for CPU, memory, latency, and error rate.",
            target_type="service",
            required_parameters=["service_id"],
            estimated_cost=0.15,
            estimated_execution_time_ms=12.0,
            risk_level="READ_ONLY",
            information_value=0.80,
            applicable_conditions=["service_metrics_available"]
        ),
        handler=None
    )

    # 3. Compare Metrics with Baseline
    ActionRegistry.register(
        AgentActionDefinition(
            action_id="compare_metrics_baseline",
            action_name="Compare Telemetry Against Baseline",
            description="Evaluates standard deviations and ratio differences between observed metrics and normal baseline operating limits.",
            target_type="service",
            required_parameters=["service_id"],
            estimated_cost=0.10,
            estimated_execution_time_ms=8.0,
            risk_level="READ_ONLY",
            information_value=0.70,
            applicable_conditions=["service_metrics_available"]
        ),
        handler=None
    )

    # 4. Retrieve Anomaly Alerts
    ActionRegistry.register(
        AgentActionDefinition(
            action_id="retrieve_anomaly_alerts",
            action_name="Retrieve Active Anomaly Alerts",
            description="Extracts all persisted warning and critical anomaly alerts from Module 2 for the service.",
            target_type="service",
            required_parameters=["service_id"],
            estimated_cost=0.08,
            estimated_execution_time_ms=6.0,
            risk_level="READ_ONLY",
            information_value=0.85,
            applicable_conditions=["alerts_present_or_checkable"]
        ),
        handler=None
    )

    # 5. Inspect Dependency Relationship
    ActionRegistry.register(
        AgentActionDefinition(
            action_id="inspect_dependency",
            action_name="Inspect Dependency Inbound & Outbound Edges",
            description="Examines architectural callers and downstream callees from the Module 1 NetworkX graph.",
            target_type="service",
            required_parameters=["service_id"],
            estimated_cost=0.06,
            estimated_execution_time_ms=5.0,
            risk_level="READ_ONLY",
            information_value=0.65,
            applicable_conditions=["topology_loaded"]
        ),
        handler=None
    )

    # 6. Trace Possible Failure Paths
    ActionRegistry.register(
        AgentActionDefinition(
            action_id="trace_failure_paths",
            action_name="Trace Propagation Failure Paths",
            description="Traces multi-hop directed propagation paths to downstream impacted callers using cycle-safe traversal.",
            target_type="service",
            required_parameters=["service_id"],
            estimated_cost=0.20,
            estimated_execution_time_ms=15.0,
            risk_level="READ_ONLY",
            information_value=0.85,
            applicable_conditions=["affected_callers_exist"]
        ),
        handler=None
    )

    # 7. Compare Timestamps Across Services
    ActionRegistry.register(
        AgentActionDefinition(
            action_id="compare_timestamps",
            action_name="Compare Temporal Onset Precedence",
            description="Analyzes earliest degradation onset (t_first) across suspected service and downstream callers to test temporal causality.",
            target_type="pair",
            required_parameters=["service_id", "comparator_service_id"],
            estimated_cost=0.12,
            estimated_execution_time_ms=10.0,
            risk_level="READ_ONLY",
            information_value=0.90,
            applicable_conditions=["multiple_services_involved"]
        ),
        handler=None
    )

    # 8. Inspect Cascade Blast Radius Prediction
    ActionRegistry.register(
        AgentActionDefinition(
            action_id="inspect_cascade_prediction",
            action_name="Inspect Cascade Blast Radius Prediction",
            description="Executes Module 3 reverse propagation to calculate attenuation, risk scores, and affected service count.",
            target_type="service",
            required_parameters=["service_id"],
            estimated_cost=0.25,
            estimated_execution_time_ms=20.0,
            risk_level="READ_ONLY",
            information_value=0.80,
            applicable_conditions=["target_service_specified"]
        ),
        handler=None
    )

    # 9. Re-evaluate Root Cause Candidates
    ActionRegistry.register(
        AgentActionDefinition(
            action_id="reevaluate_root_causes",
            action_name="Re-evaluate Multi-Factor Root Causes",
            description="Triggers Module 4 RCA synthesis to recalculate candidate scores based on newly acquired evidence.",
            target_type="incident",
            required_parameters=["incident_id"],
            estimated_cost=0.35,
            estimated_execution_time_ms=25.0,
            risk_level="READ_ONLY",
            information_value=0.95,
            applicable_conditions=["incident_active"]
        ),
        handler=None
    )

    # 10. Identify Missing Diagnostic Data
    ActionRegistry.register(
        AgentActionDefinition(
            action_id="identify_missing_evidence",
            action_name="Audit Telemetry & Evidence Gaps",
            description="Audits unobserved channels (connection pools, queue depth, cache miss rates) to surface observability blind spots.",
            target_type="service",
            required_parameters=["service_id"],
            estimated_cost=0.08,
            estimated_execution_time_ms=6.0,
            risk_level="READ_ONLY",
            information_value=0.60,
            applicable_conditions=["service_exists"]
        ),
        handler=None
    )

    # 11. Compare Two Root Cause Hypotheses
    ActionRegistry.register(
        AgentActionDefinition(
            action_id="compare_hypotheses",
            action_name="Discriminate Between Competing Hypotheses",
            description="Compares the top two competing candidates (e.g. Primary Failure vs Shared Bottleneck) against observed evidence.",
            target_type="incident",
            required_parameters=["candidate_a", "candidate_b"],
            estimated_cost=0.18,
            estimated_execution_time_ms=14.0,
            risk_level="READ_ONLY",
            information_value=0.88,
            applicable_conditions=["at_least_two_candidates"]
        ),
        handler=None
    )

    # 12. Inspect Saved Simulation Scenario
    ActionRegistry.register(
        AgentActionDefinition(
            action_id="inspect_saved_simulation",
            action_name="Inspect Saved Simulation Scenario",
            description="Loads corresponding Module 3 saved simulation parameters and discrete time-step failure progression.",
            target_type="scenario",
            required_parameters=["scenario_id"],
            estimated_cost=0.10,
            estimated_execution_time_ms=8.0,
            risk_level="READ_ONLY",
            information_value=0.65,
            applicable_conditions=["scenario_id_specified"]
        ),
        handler=None
    )

# Run registration on module load
register_default_actions()
