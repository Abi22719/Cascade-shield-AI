from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, ConfigDict

class ValidationConfigSchema(BaseModel):
    max_acceptable_latency_ms: float = Field(500.0, ge=1.0, le=10000.0, description="Max acceptable latency threshold")
    max_acceptable_error_rate: float = Field(5.0, ge=0.0, le=100.0, description="Max acceptable error rate percentage")
    max_acceptable_cpu_percent: float = Field(85.0, ge=1.0, le=100.0, description="Max acceptable CPU utilization")
    max_acceptable_memory_percent: float = Field(85.0, ge=1.0, le=100.0, description="Max acceptable memory utilization")
    min_required_healthy_services: int = Field(1, ge=1, le=50, description="Minimum number of services that must be healthy")
    verification_window_steps: int = Field(3, ge=1, le=20, description="Number of stable steps required after recovery")
    allowed_metric_deviation: float = Field(10.0, ge=0.0, le=100.0, description="Allowed deviation from baseline (%)")
    required_evidence_level: str = Field("strict", description="Evidence strictness: strict, moderate, permissive")
    timeout_seconds: int = Field(30, ge=5, le=300, description="Validation timeout limit")
    critical_services: List[str] = Field(
        default_factory=lambda: ["srv-database", "srv-payment", "srv-gateway"],
        description="Critical service IDs that must be HEALTHY"
    )

class ValidationCheckSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    validation_id: str
    check_type: str  # service_health, metrics, dependency, stability, side_effects, evidence
    target_service_id: Optional[str] = None
    check_name: str
    status: str  # PASS, FAIL, WARNING, UNKNOWN
    expected_value: Optional[str] = None
    actual_value: Optional[str] = None
    explanation: str
    evidence_reference: Optional[str] = None
    simulation_step: Optional[int] = None
    created_at: datetime

class ValidationEvidenceSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    validation_id: str
    check_id: Optional[str] = None
    source_module: str  # module_1, module_2, module_3, module_4, module_5, module_6, module_7
    source_record_id: Optional[str] = None
    evidence_type: str  # service_health, metric_observation, event_log, graph_topology, alert_record, precondition_status
    description: str
    observed_or_simulated: str  # observed, simulated, synthetic, inferred
    timestamp_or_step: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    created_at: datetime

class ValidationRecommendationSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    validation_id: str
    recommendation_type: str  # investigate_service, test_alternative_plan, extend_verification_window, collect_metrics, review_downstream, review_preconditions
    priority: str  # CRITICAL, HIGH, MEDIUM, LOW
    description: str
    related_service_id: Optional[str] = None
    supporting_evidence: Optional[Dict[str, Any]] = None
    created_at: datetime

class ValidationRunRequest(BaseModel):
    recovery_plan_id: str = Field(..., description="ID of the recovery plan to validate")
    recovery_simulation_run_id: Optional[str] = Field(None, description="Optional specific simulation run ID. If omitted, latest run is used")
    source_scenario_id: Optional[str] = Field(None, description="Optional related scenario ID")
    verification_window_steps: Optional[int] = Field(3, ge=1, le=20, description="Verification stability window steps")
    custom_thresholds: Optional[Dict[str, Any]] = Field(default=None, description="Optional override thresholds")
    force_rerun: bool = Field(False, description="Whether to bypass duplicate detection and generate a new validation run")

class BeforeAfterMetricDiff(BaseModel):
    service_id: str
    service_name: str
    metric_name: str
    before_value: Optional[float] = None
    after_value: Optional[float] = None
    delta: Optional[float] = None
    percent_change: Optional[float] = None
    trend: str = "UNCHANGED"  # IMPROVED, WORSENED, UNCHANGED, UNKNOWN
    status: str = "UNKNOWN"  # PASS, FAIL, WARNING, UNKNOWN

class BeforeAfterComparisonSchema(BaseModel):
    services_before_count: Dict[str, int] = Field(default_factory=dict)
    services_after_count: Dict[str, int] = Field(default_factory=dict)
    healthy_count_before: int = 0
    healthy_count_after: int = 0
    degraded_count_before: int = 0
    degraded_count_after: int = 0
    unavailable_count_before: int = 0
    unavailable_count_after: int = 0
    metric_diffs: List[BeforeAfterMetricDiff] = Field(default_factory=list)
    affected_downstream_before: int = 0
    affected_downstream_after: int = 0
    new_simulated_failures: List[str] = Field(default_factory=list)
    time_to_recovery_steps: int = 0
    stability_window_steps: int = 3
    is_stable_across_window: bool = True

class ValidationRunResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    recovery_plan_id: str
    recovery_simulation_run_id: Optional[str] = None
    source_scenario_id: Optional[str] = None
    status: str = "COMPLETED"
    overall_outcome: str = "NOT_RUN"  # VERIFIED_SUCCESS, PARTIAL_SUCCESS, FAILED, INCONCLUSIVE, NOT_RUN
    total_checks: int = 0
    passed_checks: int = 0
    failed_checks: int = 0
    warning_checks: int = 0
    unknown_checks: int = 0
    verification_window_steps: int = 3
    checks: List[ValidationCheckSchema] = Field(default_factory=list)
    evidence: List[ValidationEvidenceSchema] = Field(default_factory=list)
    recommendations: List[ValidationRecommendationSchema] = Field(default_factory=list)
    comparison: Optional[BeforeAfterComparisonSchema] = None
    summary: Optional[Dict[str, Any]] = None
    started_at: datetime
    completed_at: Optional[datetime] = None
    created_at: datetime

class ValidationCompareRequest(BaseModel):
    validation_ids: List[str] = Field(..., min_length=2, max_length=10)

class ValidationCompareResponse(BaseModel):
    validations: List[Dict[str, Any]]
    best_validation_id: Optional[str] = None
    summary_verdict: str

class ValidationEvaluationResponse(BaseModel):
    archetypes_evaluated: int
    accuracy_by_validation_mode: Dict[str, float]
    false_success_rate: Dict[str, float]
    false_failure_rate: Dict[str, float]
    inconclusive_rate: Dict[str, float]
    avg_runtime_ms: Dict[str, float]
    benchmark_details: List[Dict[str, Any]]
