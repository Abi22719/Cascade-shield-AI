from datetime import datetime, timezone
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, ConfigDict, model_validator
from app.schemas.metric_schema import MetricPoint

class ThresholdConfig(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    cpu_warning: float = Field(75.0, ge=0.0, le=100.0)
    cpu_critical: float = Field(90.0, ge=0.0, le=100.0)
    memory_warning: float = Field(80.0, ge=0.0, le=100.0)
    memory_critical: float = Field(95.0, ge=0.0, le=100.0)
    latency_warning: float = Field(500.0, ge=0.0)
    latency_critical: float = Field(1000.0, ge=0.0)
    error_rate_warning: float = Field(5.0, ge=0.0, le=100.0)
    error_rate_critical: float = Field(10.0, ge=0.0, le=100.0)

    @model_validator(mode="after")
    def validate_threshold_order(self):
        if self.cpu_warning > self.cpu_critical:
            raise ValueError("CPU warning threshold cannot be greater than critical threshold.")
        if self.memory_warning > self.memory_critical:
            raise ValueError("Memory warning threshold cannot be greater than critical threshold.")
        if self.latency_warning > self.latency_critical:
            raise ValueError("Latency warning threshold cannot be greater than critical threshold.")
        if self.error_rate_warning > self.error_rate_critical:
            raise ValueError("Error rate warning threshold cannot be greater than critical threshold.")
        return self

class AnomalyDetectionRequest(BaseModel):
    service_ids: Optional[List[str]] = None
    method: str = Field("combined", description="threshold, isolation_forest, or combined")
    contamination: Optional[float] = Field(None, ge=0.001, le=0.5)
    custom_metrics: Optional[List[MetricPoint]] = None

class AnomalyDetectionResult(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    service_id: str
    service_name: str
    is_anomaly: bool
    severity: str  # Normal, Warning, Critical
    detection_method: str  # threshold, isolation_forest, combined
    anomaly_score: Optional[float] = None  # ML anomaly score
    metric_name: Optional[str] = None
    observed_value: Optional[float] = None
    threshold_value: Optional[float] = None
    evidence_summary: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    alert_created: bool = False
    alert_id: Optional[str] = None

class DetectionBatchResponse(BaseModel):
    total_evaluated: int
    anomalies_detected: int
    method: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    new_alerts_generated: int
    results: List[AnomalyDetectionResult]

class EvaluationMetrics(BaseModel):
    true_positives: int
    false_positives: int
    true_negatives: int
    false_negatives: int
    precision: float
    recall: float
    f1_score: float
    false_positive_rate: float
    accuracy: float
    dataset_size: int

class EvaluationComparisonResponse(BaseModel):
    threshold_detector: EvaluationMetrics
    isolation_forest: EvaluationMetrics
    combined_detector: EvaluationMetrics
    dataset_size: int
    anomalous_samples_count: int
    normal_samples_count: int
    benchmark_description: str
    generated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
