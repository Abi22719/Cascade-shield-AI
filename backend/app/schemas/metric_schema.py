from datetime import datetime, timezone
from typing import List, Optional
from pydantic import BaseModel, Field, ConfigDict, field_validator
import math

class MetricPoint(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    service_id: str = Field(..., min_length=1, max_length=64)
    service_name: Optional[str] = Field(None, max_length=128)
    cpu_usage: float = Field(..., ge=0.0, le=100.0)
    memory_usage: float = Field(..., ge=0.0, le=100.0)
    latency_ms: float = Field(..., ge=0.0)
    error_rate: float = Field(..., ge=0.0, le=100.0)
    request_volume: int = Field(..., ge=0)
    data_source: str = Field("simulated", max_length=32)

    @field_validator("cpu_usage", "memory_usage", "latency_ms", "error_rate")
    @classmethod
    def check_finite(cls, v: float) -> float:
        if math.isnan(v) or math.isinf(v):
            raise ValueError("Metric values must be finite real numbers.")
        return v

class MetricHistoryResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    service_id: str
    service_name: str
    data_source: str = "simulated"
    total_points: int
    metrics: List[MetricPoint]

class BatchMetricInput(BaseModel):
    metrics: List[MetricPoint]
