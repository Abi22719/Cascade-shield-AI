from datetime import datetime, timezone
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, ConfigDict

class RCAInvestigationRequest(BaseModel):
    incident_title: Optional[str] = Field(None, max_length=128, description="User-assigned incident title")
    target_service_id: Optional[str] = Field(None, description="Primary degraded service to investigate")
    affected_service_ids: Optional[List[str]] = Field(default_factory=list, description="Explicit list of affected services")
    window_start: Optional[datetime] = Field(None, description="Investigation start timestamp")
    window_end: Optional[datetime] = Field(None, description="Investigation end timestamp")
    scenario_id: Optional[str] = Field(None, description="Optional Module 3 scenario ID to link")
    custom_weights: Optional[Dict[str, float]] = Field(None, description="Optional algorithm weight overrides")
    include_alternatives: bool = Field(True, description="Whether to generate alternative hypotheses")
    include_recommendations: bool = Field(True, description="Whether to generate next diagnostic checks")

class EvidenceItemSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    service_id: str
    service_name: str
    evidence_type: str  # metric_breach, anomaly_alert, health_degraded, temporal_precedence, dependency_path, cascade_risk, contradictory_evidence
    metric_name: Optional[str] = None
    observed_value: Optional[float] = None
    expected_or_threshold_value: Optional[float] = None
    timestamp: Optional[datetime] = None
    source_module: str  # Module 1, Module 2, Module 3, Temporal Engine
    source_record_id: Optional[str] = None
    evidence_summary: str
    data_source: str = "simulated"
    reliability_score: float = 0.9
    is_contradictory: bool = False

class CandidateRootCauseSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    service_id: str
    service_name: str
    rank: int
    ranking_score: float = Field(..., ge=0.0, le=100.0)
    confidence_label: str  # Strong supporting evidence, Moderate supporting evidence, Weak supporting evidence, Insufficient evidence
    confidence_score: float = Field(..., ge=0.0, le=1.0)
    evidence_for: List[str] = Field(default_factory=list)
    evidence_against: List[str] = Field(default_factory=list)
    affected_services: List[str] = Field(default_factory=list)
    supporting_paths: List[List[str]] = Field(default_factory=list)
    missing_evidence: List[str] = Field(default_factory=list)
    explanation: str

class AlternativeHypothesisSchema(BaseModel):
    hypothesis_id: str
    hypothesis_title: str
    related_services: List[str] = Field(default_factory=list)
    supporting_evidence: List[str] = Field(default_factory=list)
    contradictory_evidence: List[str] = Field(default_factory=list)
    missing_information: List[str] = Field(default_factory=list)
    plausibility_reason: str

class DiagnosticRecommendationSchema(BaseModel):
    recommendation_id: str
    action_description: str
    target_service_id: Optional[str] = None
    reason: str
    evidence_gap: str
    expected_information_gain: str
    priority: str  # P1_Immediate, P2_High, P3_Medium, P4_Low
    manual_confirmation_required: bool = True
    reviewed: bool = False

class TimelineEventSchema(BaseModel):
    timestamp: datetime
    timestamp_formatted: str
    service_id: str
    service_name: str
    event_type: str
    source_module: str
    description: str
    severity: str
    evidence_id: Optional[str] = None

class RCAReportSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    incident_id: str
    title: str
    status: str
    investigation_window: Dict[str, Optional[datetime]]
    affected_services: List[str]
    primary_root_cause: Optional[CandidateRootCauseSchema] = None
    ranked_candidates: List[CandidateRootCauseSchema] = Field(default_factory=list)
    evidence_timeline: List[TimelineEventSchema] = Field(default_factory=list)
    evidence_count: int = 0
    evidence_items: List[EvidenceItemSchema] = Field(default_factory=list)
    alternative_hypotheses: List[AlternativeHypothesisSchema] = Field(default_factory=list)
    diagnostic_recommendations: List[DiagnosticRecommendationSchema] = Field(default_factory=list)
    confidence_and_uncertainty_explanation: str
    missing_data_gaps: List[str] = Field(default_factory=list)
    investigation_limitations: List[str] = Field(default_factory=list)
    data_sources: List[str] = Field(default_factory=lambda: ["simulated"])
    algorithm_version: str = "4.0.0"
    analyzed_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class RCAIncidentSummarySchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    title: str
    status: str
    target_service_id: Optional[str] = None
    affected_services_count: int
    top_candidate: Optional[str] = None
    top_confidence: Optional[str] = None
    created_at: datetime

class RCAIncidentListResponse(BaseModel):
    items: List[RCAIncidentSummarySchema]
    total: int
    page: int
    limit: int

class RCAEvaluationMetrics(BaseModel):
    top_1_accuracy: float
    top_3_accuracy: float
    mrr_score: float  # Mean Reciprocal Rank
    precision: float
    recall: float
    insufficient_evidence_rate: float
    avg_runtime_ms: float

class RCAEvaluationResponse(BaseModel):
    benchmark_scenarios_count: int
    baseline_earliest_anomaly: RCAEvaluationMetrics
    baseline_dependency_only: RCAEvaluationMetrics
    evidence_grounded_rca: RCAEvaluationMetrics
    methodology_notes: str
    summary_findings: str

class RCACompareRequest(BaseModel):
    incident_ids: Optional[List[str]] = None
    custom_requests: Optional[List[RCAInvestigationRequest]] = None

class RCACompareResponse(BaseModel):
    compared_count: int
    comparisons: List[Dict[str, Any]]
    comparative_analysis: List[str]
