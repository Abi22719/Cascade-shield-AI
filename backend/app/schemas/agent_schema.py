from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, ConfigDict

class AgentActionDefinition(BaseModel):
    action_id: str
    action_name: str
    description: str
    target_type: str  # service, pair, incident, cluster
    required_parameters: List[str] = Field(default_factory=list)
    estimated_cost: float = Field(..., ge=0.0, le=1.0)
    estimated_execution_time_ms: float = Field(..., ge=0.0)
    risk_level: str  # READ_ONLY, MINIMAL, LOW
    information_value: float = Field(..., ge=0.0, le=1.0)
    applicable_conditions: List[str] = Field(default_factory=list)

class AgentConfigSchema(BaseModel):
    weight_information_gain: float = Field(0.35, ge=0.0, le=1.0)
    weight_relevance: float = Field(0.30, ge=0.0, le=1.0)
    weight_hypothesis_discrimination: float = Field(0.20, ge=0.0, le=1.0)
    weight_cost: float = Field(0.10, ge=0.0, le=1.0)
    weight_risk: float = Field(0.05, ge=0.0, le=1.0)
    repeated_action_penalty: float = Field(0.70, ge=0.0, le=1.0)
    max_actions: int = Field(5, ge=1, le=20)
    max_execution_time_seconds: float = Field(30.0, ge=1.0, le=300.0)
    min_utility_threshold: float = Field(0.12, ge=0.0, le=1.0)
    sufficient_confidence_threshold: float = Field(0.75, ge=0.0, le=1.0)
    confidence_margin_threshold: float = Field(20.0, ge=0.0, le=100.0)
    policy_version: str = "1.0.0"

class CreateSessionRequest(BaseModel):
    incident_id: Optional[str] = None
    scenario_id: Optional[str] = None
    target_service_id: Optional[str] = None
    custom_config: Optional[AgentConfigSchema] = None

class ActionRecommendation(BaseModel):
    action_id: str
    action_name: str
    target_service_id: Optional[str] = None
    utility_score: float
    information_gain: float
    relevance_score: float
    discrimination_score: float
    cost: float
    risk: float
    repeat_penalty: float
    eligible: bool
    ineligibility_reason: Optional[str] = None
    selection_reason: str

class ActionExecutionResult(BaseModel):
    step_number: int
    action_id: str
    action_name: str
    parameters: Dict[str, Any] = Field(default_factory=dict)
    selection_score: float = 0.0
    selection_reason: str = ""
    execution_status: str = "SUCCESS"  # SUCCESS, FAILED, TIMED_OUT
    duration_ms: float = 0.0
    result_summary: str = ""
    raw_result: Optional[Dict[str, Any]] = None
    evidence_created: List[Dict[str, Any]] = Field(default_factory=list)
    started_at: datetime
    completed_at: datetime

class AgentSessionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    incident_id: Optional[str] = None
    scenario_id: Optional[str] = None
    target_service_id: Optional[str] = None
    status: str
    policy_version: str
    total_steps: int
    stopping_reason: Optional[str] = None
    configuration: AgentConfigSchema
    created_at: datetime
    updated_at: datetime
    completed_at: Optional[datetime] = None
    action_history: List[ActionExecutionResult] = Field(default_factory=list)
    latest_ranking: List[Dict[str, Any]] = Field(default_factory=list)
    unresolved_questions: List[str] = Field(default_factory=list)
    evidence_completeness: float = 0.0

class AgentRunRequest(BaseModel):
    max_steps: Optional[int] = Field(None, ge=1, le=20)
    force_stop_on_ambiguity: bool = True

class AgentStepResponse(BaseModel):
    session_id: str
    step_number: int
    session_status: str
    stopping_reason: Optional[str] = None
    executed_action: Optional[ActionExecutionResult] = None
    next_recommendations: List[ActionRecommendation] = Field(default_factory=list)
    latest_ranking: List[Dict[str, Any]] = Field(default_factory=list)
    unresolved_questions: List[str] = Field(default_factory=list)
    evidence_completeness: float = 0.0

class AgentEvaluationMetrics(BaseModel):
    strategy_name: str
    accuracy_top1: float
    accuracy_top3: float
    avg_actions_required: float
    repeated_action_rate: float
    action_failure_rate: float
    unresolved_incident_rate: float
    avg_execution_time_ms: float
    avg_cost: float

class AgentEvaluationResponse(BaseModel):
    benchmark_scenarios_count: int
    baseline_fixed_order: AgentEvaluationMetrics
    baseline_relevance_first: AgentEvaluationMetrics
    adaptive_utility_agent: AgentEvaluationMetrics
    methodology_notes: str
    summary_findings: str

class AgentCompareRequest(BaseModel):
    incident_id: Optional[str] = None
    target_service_id: Optional[str] = None
    scenario_id: Optional[str] = None
    strategies: List[str] = Field(default_factory=lambda: ["fixed_order", "relevance_first", "adaptive_utility"])

class AgentCompareResponse(BaseModel):
    incident_target: str
    comparisons: List[AgentEvaluationMetrics]
    comparison_summary: str
