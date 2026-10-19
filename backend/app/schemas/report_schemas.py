from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, ConfigDict

class ReportGenerateRequest(BaseModel):
    report_type: str = Field(
        ...,
        description="Type of report: service_health, anomaly_detection, cascade_prediction, rca, diagnostic_agent, simulation, recovery_planning, recovery_validation, benchmarking, incident_lifecycle"
    )
    report_title: Optional[str] = None
    related_record_id: Optional[str] = None
    data_source: str = "simulated"  # observed, simulated, synthetic, inferred
    report_format: str = "markdown"  # markdown, json, csv

class ReportResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    report_type: str
    report_title: str
    related_record_id: Optional[str] = None
    data_source: str = "simulated"
    report_format: str = "markdown"
    report_status: str = "COMPLETED"
    content: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    created_at: datetime
    completed_at: Optional[datetime] = None

class ReportListResponse(BaseModel):
    total: int
    reports: List[ReportResponse] = Field(default_factory=list)
