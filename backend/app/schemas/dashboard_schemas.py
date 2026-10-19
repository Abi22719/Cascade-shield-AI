from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, ConfigDict

class DashboardSummaryResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    total_services: int = 0
    healthy_services: int = 0
    degraded_services: int = 0
    unavailable_services: int = 0
    active_anomalies: int = 0
    high_risk_predictions: int = 0
    open_incidents: int = 0
    recovery_plans_pending: int = 0
    latest_benchmark_score: Optional[float] = None
    simulation_mode: bool = True
    last_refresh: datetime = Field(default_factory=datetime.utcnow)

class DashboardHealthResponse(BaseModel):
    status: str = "operational"
    simulation_mode: bool = True
    version: str = "10.0.0"
    modules: Dict[str, str] = Field(default_factory=dict)
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class ActivityEventSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    event_type: str
    source_module: str
    source_record_id: Optional[str] = None
    related_incident_id: Optional[str] = None
    description: str
    metadata: Optional[Dict[str, Any]] = None
    created_at: datetime

class ExplainableInsightSchema(BaseModel):
    id: str
    title: str
    service_id: Optional[str] = None
    incident_id: Optional[str] = None
    summary: str
    evidence_ids: List[str] = Field(default_factory=list)
    source_module: str
    metrics: Dict[str, Any] = Field(default_factory=dict)
    dependency_path: Optional[List[str]] = None
    risk_factors: List[str] = Field(default_factory=list)
    alternative_explanations: List[str] = Field(default_factory=list)
    uncertainty_notes: str = ""
    data_source: str = "simulated"  # observed, simulated, synthetic, inferred
    recommended_next_step: str = ""
    created_at: datetime = Field(default_factory=datetime.utcnow)
