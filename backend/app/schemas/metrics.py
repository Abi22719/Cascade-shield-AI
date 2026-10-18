from typing import Dict, Any
from pydantic import BaseModel

class MetricsSummaryResponse(BaseModel):
    total_services: int
    healthy_services: int
    warning_services: int
    critical_services: int
    health_score_pct: float
    avg_latency_ms: float
    avg_error_rate: float
    avg_cpu_usage: float
    avg_memory_usage: float
    total_request_volume: int
    telemetry_type: str = "simulated"
