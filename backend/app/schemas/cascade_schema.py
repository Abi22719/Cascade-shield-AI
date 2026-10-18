from datetime import datetime, timezone
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, ConfigDict, field_validator

class CascadePredictRequest(BaseModel):
    initial_service_id: str = Field(..., min_length=1, max_length=64, description="Service ID where the failure or degradation originates")
    failure_type: str = Field("latency_spike", description="service_unavailable, latency_spike, error_rate_surge, cpu_exhaustion, memory_leak")
    failure_severity: str = Field("severe", description="mild, moderate, severe")
    propagation_steps: int = Field(4, ge=1, le=8, description="Maximum traversal steps for simulation")
    attenuation_factor: float = Field(0.75, ge=0.1, le=1.0, description="Rate at which failure risk decays per dependency hop")
    custom_weights: Optional[Dict[str, float]] = Field(None, description="Optional override weights for dependency protocols")

    @field_validator("failure_type")
    @classmethod
    def validate_failure_type(cls, v: str) -> str:
        valid_types = {
            "service_unavailable",
            "latency_spike",
            "error_rate_surge",
            "cpu_exhaustion",
            "memory_leak"
        }
        val = v.strip().lower()
        if val not in valid_types:
            raise ValueError(f"Invalid failure_type '{v}'. Must be one of: {', '.join(sorted(valid_types))}")
        return val

    @field_validator("failure_severity")
    @classmethod
    def validate_severity(cls, v: str) -> str:
        valid = {"mild", "moderate", "severe"}
        val = v.strip().lower()
        if val not in valid:
            raise ValueError(f"Invalid failure_severity '{v}'. Must be one of: mild, moderate, severe")
        return val

class CascadePathInfo(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    path: List[str]
    path_names: List[str]
    hop_count: int
    dependency_types: List[str]
    risk_contribution: float
    evidence: str

class ImpactedServiceResult(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    service_id: str
    service_name: str
    service_type: str
    impact_type: str  # Root Failure, Direct, Indirect
    hop_distance: int
    estimated_risk_score: float = Field(..., ge=0.0, le=100.0)
    risk_level: str  # Low, Moderate, High, Critical
    propagation_probability_estimate: float = Field(..., ge=0.0, le=1.0)
    contributing_evidence: List[str]
    impacted_by_services: List[str]
    failure_paths: List[CascadePathInfo]
    recommended_monitoring_action: str
    estimated_step_onset: int

class SimulationStepRecord(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    step: int
    timestamp_offset_seconds: int
    newly_affected_services: List[str]
    cumulative_affected_count: int
    average_risk_score: float
    step_description: str

class CascadePredictionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    initial_service_id: str
    initial_service_name: str
    failure_type: str
    failure_severity: str
    total_services_analyzed: int
    total_impacted_services: int
    direct_impact_count: int
    indirect_impact_count: int
    high_risk_count: int
    critical_risk_count: int
    max_risk_score: float
    impacted_services: List[ImpactedServiceResult]
    simulation_timeline: List[SimulationStepRecord]
    primary_propagation_paths: List[CascadePathInfo]
    recommendations: List[str]
    data_source: str = "simulated"
    generated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class CascadeScenarioSaveRequest(BaseModel):
    scenario_name: str = Field(..., min_length=1, max_length=128)
    initial_service_id: str = Field(..., min_length=1, max_length=64)
    failure_type: str = Field(..., min_length=1, max_length=64)
    failure_severity: str = Field(..., min_length=1, max_length=32)
    input_parameters: Dict[str, Any]
    result_summary: Dict[str, Any]

class CascadeScenarioResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    scenario_name: str
    initial_service_id: Optional[str]
    failure_type: str
    failure_severity: str
    input_parameters: Dict[str, Any]
    result_summary: Dict[str, Any]
    created_at: datetime
    data_source: str = "simulated"

class CascadeSummaryResponse(BaseModel):
    total_services: int
    total_dependencies: int
    predicted_impacted_services: int
    high_risk_services: int
    critical_risk_services: int
    last_simulation_status: str
    last_simulation_time: Optional[datetime] = None

class ScenarioComparisonRequest(BaseModel):
    scenario_ids: Optional[List[str]] = None
    custom_scenarios: Optional[List[CascadePredictRequest]] = None

class CascadeEvaluationMetrics(BaseModel):
    true_positives: int
    false_positives: int
    true_negatives: int
    false_negatives: int
    precision: float
    recall: float
    f1_score: float
    false_positive_rate: float
    impacted_detection_coverage_pct: float
    avg_runtime_ms: float

class CascadeEvaluationResponse(BaseModel):
    benchmark_scenario_count: int
    baseline_simple_traversal: CascadeEvaluationMetrics
    static_rule_scoring: CascadeEvaluationMetrics
    evidence_aware_cascade: CascadeEvaluationMetrics
    evaluation_criteria_summary: str
    methodology_notes: str
