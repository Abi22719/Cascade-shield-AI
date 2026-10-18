from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, ConfigDict

class AlertResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    service_id: str
    service_name: str
    metric_name: str
    observed_value: Optional[float] = None
    threshold_value: Optional[float] = None
    severity: str
    detection_method: str
    anomaly_score: Optional[float] = None
    evidence_summary: str
    data_source: str
    acknowledged: bool
    created_at: datetime

class AlertSummaryResponse(BaseModel):
    total_alerts: int
    critical_alerts: int
    warning_alerts: int
    anomalous_observations: int
    affected_services: int
    acknowledged_alerts: int
    unacknowledged_alerts: int

class AlertListResponse(BaseModel):
    alerts: List[AlertResponse]
    total: int
    page: int
    limit: int
