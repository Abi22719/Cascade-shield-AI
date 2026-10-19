from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, ConfigDict

class RecoveryPreconditionSchema(BaseModel):
    name: str = Field(..., description="Precondition identifier or name")
    description: str = Field(..., description="Details of what must hold before execution")
    status: str = Field("satisfied", description="Status: satisfied, unresolved, violated")
    checked_at: Optional[datetime] = None

class RecoveryActionCreate(BaseModel):
    action_type: str = Field(..., description="restart_service, rollback_deployment, traffic_reroute, scale_up, isolate_dependency, restore_database, retry_request, wait_auto_recovery")
    target_service_id: Optional[str] = Field(None, description="Service ID this action acts upon")
    action_order: int = Field(1, ge=1, le=20, description="Order index in the sequence")
    parameters: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Action specific parameters")
    preconditions: Optional[List[RecoveryPreconditionSchema]] = Field(default_factory=list, description="Preconditions required before action can execute")
    estimated_duration: int = Field(1, ge=1, le=20, description="Estimated time-steps to apply")
    risk_score: float = Field(15.0, ge=0.0, le=100.0, description="Heuristic action risk score")
    reversibility: str = Field("fully_reversible", description="fully_reversible, partially_reversible, irreversible")
    possible_side_effects: Optional[List[str]] = Field(default_factory=list, description="Possible cascading or degradation risks")
    expected_result: Optional[str] = None
    rollback_procedure: Optional[str] = None

class RecoveryActionSchema(RecoveryActionCreate):
    model_config = ConfigDict(from_attributes=True)

    id: str
    plan_id: str
    status: str = "PENDING"
    created_at: datetime

class RiskFactorBreakdown(BaseModel):
    factor_name: str
    raw_score: float
    weight: float
    weighted_score: float
    impact_direction: str  # increases_risk, reduces_risk, neutral
    explanation: str

class RecoveryPlanCreateRequest(BaseModel):
    incident_id: Optional[str] = None
    scenario_id: Optional[str] = None
    plan_name: str = Field(..., min_length=2, max_length=128)
    description: Optional[str] = Field(None, max_length=512)
    strategy_type: str = Field("balanced", description="lowest_risk, fastest_recovery, lowest_cost, balanced, custom")
    actions: List[RecoveryActionCreate] = Field(default_factory=list)

class RecoveryPlanGenerateRequest(BaseModel):
    incident_id: Optional[str] = None
    scenario_id: Optional[str] = None
    target_service_id: Optional[str] = None
    optimization_goal: str = Field("balanced", description="balanced, lowest_risk, fastest_recovery, lowest_cost")

class RecoveryPlanUpdateRequest(BaseModel):
    plan_name: Optional[str] = None
    description: Optional[str] = None
    strategy_type: Optional[str] = None
    actions: Optional[List[RecoveryActionCreate]] = None
    status: Optional[str] = None

class RecoveryPlanResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    incident_id: Optional[str] = None
    scenario_id: Optional[str] = None
    plan_name: str
    description: Optional[str] = None
    strategy_type: str
    risk_score: float
    risk_level: str
    estimated_recovery_time: int
    estimated_cost: float
    status: str
    risk_breakdown: List[RiskFactorBreakdown] = Field(default_factory=list)
    actions: List[RecoveryActionSchema] = Field(default_factory=list)
    created_at: datetime
    updated_at: datetime
    runs_count: int = 0
    latest_run_id: Optional[str] = None

class RecoverySimulationRequest(BaseModel):
    random_seed: Optional[int] = Field(42, description="Deterministic seed for reproducibility")
    max_steps: Optional[int] = Field(None, ge=1, le=20)
    stop_on_failure: bool = Field(False, description="Whether to abort remaining actions if a step fails")

class RecoveryEventSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    simulation_run_id: str
    event_type: str
    description: str
    evidence_json: Optional[str] = None
    timestamp_or_step: int
    created_at: datetime

class RecoverySimulationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    plan_id: str
    simulation_run_id: Optional[str] = None
    outcome: str  # SUCCESSFUL_RECOVERY, PARTIAL_RECOVERY, FAILED_RECOVERY
    total_recovery_time: int
    maximum_risk: float
    final_health_summary: Dict[str, str] = Field(default_factory=dict)
    events: List[Dict[str, Any]] = Field(default_factory=list)
    step_comparisons: List[Dict[str, Any]] = Field(default_factory=list)
    created_at: datetime

class RecoveryComparisonRequest(BaseModel):
    plan_ids: List[str] = Field(..., min_length=2, max_length=5)
    optimization_priority: Optional[str] = Field("balanced", description="lowest_risk, fastest_recovery, lowest_cost, balanced")

class RecoveryComparisonItem(BaseModel):
    plan_id: str
    plan_name: str
    strategy_type: str
    risk_score: float
    risk_level: str
    estimated_recovery_time: int
    estimated_cost: float
    data_loss_exposure: str
    reversibility: str
    unresolved_preconditions_count: int
    simulated_outcome: Optional[str] = None

class RecoveryComparisonResponse(BaseModel):
    compared_plans: List[RecoveryComparisonItem]
    tradeoff_analysis: str
    recommended_plan_id: Optional[str] = None
    recommendation_reason: str
    alternative_plans_rejection_reasons: Dict[str, str] = Field(default_factory=dict)

class RecoveryConfigSchema(BaseModel):
    service_criticality_weight: float = Field(0.25, ge=0.0, le=1.0)
    blast_radius_weight: float = Field(0.25, ge=0.0, le=1.0)
    recovery_duration_weight: float = Field(0.15, ge=0.0, le=1.0)
    resource_cost_weight: float = Field(0.10, ge=0.0, le=1.0)
    reversibility_weight: float = Field(0.15, ge=0.0, le=1.0)
    uncertainty_weight: float = Field(0.10, ge=0.0, le=1.0)
    max_allowed_recovery_duration: int = Field(15, ge=1, le=30)

class RecoveryEvaluationMetrics(BaseModel):
    strategy_name: str
    success_rate: float
    mean_recovery_time: float
    max_risk: float
    avg_risk: float
    additional_failures_count: int
    avg_resource_cost: float
    failed_steps_count: int
    unresolved_preconditions_count: int

class RecoveryEvaluationResponse(BaseModel):
    benchmark_scenarios_count: int
    strategies: List[RecoveryEvaluationMetrics]
    methodology_notes: str
    summary_findings: str
