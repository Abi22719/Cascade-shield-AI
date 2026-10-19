from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, ConfigDict

class FailureInjectionConfig(BaseModel):
    target_service_ids: List[str] = Field(..., min_length=1, description="One or more target services to inject failure into")
    failure_type: str = Field(
        "service_unavailable", 
        description="Type of failure: service_unavailable, high_latency, error_rate_surge, cpu_saturation, memory_exhaustion, database_starvation"
    )
    severity: str = Field("severe", description="Severity: mild, moderate, severe")
    start_step: int = Field(1, ge=1, le=20, description="Step at which failure injection begins")
    duration_steps: int = Field(5, ge=1, le=20, description="Duration in steps that the failure persists")
    custom_metric_overrides: Optional[Dict[str, float]] = Field(default_factory=dict, description="Optional custom values for cpu, latency, error_rate")

class PropagationParameters(BaseModel):
    max_steps: int = Field(8, ge=1, le=20, description="Maximum discrete time steps to simulate")
    attenuation_factor: float = Field(0.75, ge=0.1, le=1.0, description="Rate of risk and failure decay per hop")
    propagation_threshold: float = Field(25.0, ge=0.0, le=100.0, description="Minimum risk score required to cause downstream state transition")
    protocol_coupling_weights: Optional[Dict[str, float]] = Field(
        default_factory=lambda: {
            "sync_http": 1.0,
            "database_read_write": 0.95,
            "async_message": 0.45,
            "cache_lookup": 0.40
        }
    )

class RecoveryParameters(BaseModel):
    recovery_mode: str = Field("gradual", description="Mode: none, immediate, gradual")
    recovery_step: Optional[int] = Field(5, ge=1, le=20, description="Step at which recovery process begins")
    recovery_rate: float = Field(0.35, ge=0.05, le=1.0, description="Rate of metric recovery per step towards baseline")
    restored_services: Optional[List[str]] = Field(default_factory=list, description="Explicit list of services to recover, empty for all")

class ScenarioConfigSchema(BaseModel):
    failures: List[FailureInjectionConfig] = Field(default_factory=list)
    propagation: PropagationParameters = Field(default_factory=PropagationParameters)
    recovery: RecoveryParameters = Field(default_factory=RecoveryParameters)
    random_seed: Optional[int] = Field(None, description="Optional seed for deterministic reproducibility")

class ScenarioCreateRequest(BaseModel):
    name: str = Field(..., min_length=2, max_length=128, description="Human-readable scenario name")
    description: Optional[str] = Field(None, max_length=512)
    category: str = Field("failure_propagation", description="failure_propagation, latency_storm, database_starvation, recovery_test")
    config: ScenarioConfigSchema
    source_data_type: str = Field("digital_twin", description="digital_twin or synthetic")

class ScenarioUpdateRequest(BaseModel):
    name: Optional[str] = Field(None, min_length=2, max_length=128)
    description: Optional[str] = None
    category: Optional[str] = None
    config: Optional[ScenarioConfigSchema] = None

class ScenarioResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    name: str
    description: Optional[str] = None
    category: str
    config: ScenarioConfigSchema
    source_data_type: str
    created_at: datetime
    updated_at: datetime
    runs_count: int = 0
    latest_run_id: Optional[str] = None

class SimulationRunRequest(BaseModel):
    random_seed: Optional[int] = None
    max_steps_override: Optional[int] = Field(None, ge=1, le=20)

class SimulationEventSchema(BaseModel):
    id: str
    step_number: int
    event_type: str
    service_id: str
    event_data: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime

class SimulatedServiceState(BaseModel):
    service_id: str
    service_name: str
    health_status: str  # HEALTHY, DEGRADED, CRITICAL, RECOVERING, RECOVERED
    cpu_usage: float
    memory_usage: float
    latency_ms: float
    error_rate: float
    request_volume: int
    risk_score: float
    is_initial_failure: bool = False
    is_impacted: bool = False
    is_recovered: bool = False

class SimulationStepState(BaseModel):
    step_number: int
    active_failures: List[str] = Field(default_factory=list)
    newly_impacted: List[str] = Field(default_factory=list)
    recovered: List[str] = Field(default_factory=list)
    services: Dict[str, SimulatedServiceState] = Field(default_factory=dict)
    events: List[Dict[str, Any]] = Field(default_factory=list)

class SimulationSummary(BaseModel):
    total_impacted_services: int
    peak_simultaneous_impact: int
    time_to_first_downstream_impact: Optional[int] = None
    time_to_recovery: Optional[int] = None
    max_risk_score: float
    avg_risk_score: float
    aggregate_impact_score: float  # 0 to 100 aggregate resilience penalty
    propagation_events_count: int
    residual_impacted_services: List[str] = Field(default_factory=list)

class SimulationRunResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    scenario_id: str
    scenario_name: str
    status: str
    random_seed: Optional[int] = None
    model_version: str
    total_steps: int
    started_at: datetime
    completed_at: Optional[datetime] = None
    summary: Optional[SimulationSummary] = None
    error_summary: Optional[str] = None
    timeline_steps: List[SimulationStepState] = Field(default_factory=list)
    impacted_services: List[str] = Field(default_factory=list)
    propagation_paths: List[List[str]] = Field(default_factory=list)

class ScenarioComparisonRequest(BaseModel):
    run_ids: Optional[List[str]] = Field(default_factory=list)
    scenario_ids: Optional[List[str]] = Field(default_factory=list)

class ScenarioComparisonItem(BaseModel):
    run_id: str
    scenario_name: str
    category: str
    initial_failures: List[str]
    total_impacted_services: int
    peak_simultaneous_impact: int
    time_to_first_impact_step: Optional[int] = None
    time_to_recovery_step: Optional[int] = None
    max_risk_score: float
    avg_risk_score: float
    aggregate_impact_score: float
    residual_impact_count: int

class ScenarioComparisonResponse(BaseModel):
    comparisons: List[ScenarioComparisonItem]
    summary_insights: str
    recommended_scenario: Optional[str] = None

class SimulationEvaluationMetrics(BaseModel):
    model_name: str
    coverage_accuracy: float
    transition_consistency: float
    recovery_consistency: float
    reproducibility_rate: float
    avg_runtime_ms: float
    max_graph_nodes_supported: int

class SimulationEvaluationResponse(BaseModel):
    benchmark_scenarios_count: int
    baseline_static_traversal: SimulationEvaluationMetrics
    baseline_cascade_mod3: SimulationEvaluationMetrics
    timestep_simulator_mod6: SimulationEvaluationMetrics
    methodology_notes: str
    summary_findings: str
