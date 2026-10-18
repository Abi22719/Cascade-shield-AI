from typing import List, Dict, Any, Optional
import math
from app.schemas.anomaly_schema import ThresholdConfig
from app.schemas.metric_schema import MetricPoint

class ThresholdViolation:
    def __init__(
        self,
        metric_name: str,
        observed_value: float,
        threshold_value: float,
        severity: str,
        message: str
    ):
        self.metric_name = metric_name
        self.observed_value = observed_value
        self.threshold_value = threshold_value
        self.severity = severity  # "Warning" or "Critical"
        self.message = message

class ThresholdDetector:
    def __init__(self, config: Optional[ThresholdConfig] = None):
        self.config = config or ThresholdConfig()

    def update_config(self, new_config: ThresholdConfig):
        self.config = new_config

    def get_config(self) -> ThresholdConfig:
        return self.config

    def evaluate(self, metric: MetricPoint) -> List[ThresholdViolation]:
        """
        Evaluates a single service metric point against configured warning and critical thresholds.
        Returns a list of violations (if any).
        """
        violations: List[ThresholdViolation] = []

        # Validate finite values
        for val, name in [
            (metric.cpu_usage, "cpu_usage"),
            (metric.memory_usage, "memory_usage"),
            (metric.latency_ms, "latency_ms"),
            (metric.error_rate, "error_rate")
        ]:
            if val is None or math.isnan(val) or math.isinf(val):
                return [
                    ThresholdViolation(
                        metric_name=name,
                        observed_value=0.0,
                        threshold_value=0.0,
                        severity="Critical",
                        message=f"Invalid non-finite value detected for {name}."
                    )
                ]

        # 1. Error Rate check
        if metric.error_rate >= self.config.error_rate_critical:
            violations.append(ThresholdViolation(
                metric_name="error_rate",
                observed_value=metric.error_rate,
                threshold_value=self.config.error_rate_critical,
                severity="Critical",
                message=f"Error rate critical: {metric.error_rate:.2f}% >= {self.config.error_rate_critical:.2f}%"
            ))
        elif metric.error_rate >= self.config.error_rate_warning:
            violations.append(ThresholdViolation(
                metric_name="error_rate",
                observed_value=metric.error_rate,
                threshold_value=self.config.error_rate_warning,
                severity="Warning",
                message=f"Error rate warning: {metric.error_rate:.2f}% >= {self.config.error_rate_warning:.2f}%"
            ))

        # 2. Latency check
        if metric.latency_ms >= self.config.latency_critical:
            violations.append(ThresholdViolation(
                metric_name="latency_ms",
                observed_value=metric.latency_ms,
                threshold_value=self.config.latency_critical,
                severity="Critical",
                message=f"Latency critical: {metric.latency_ms:.1f}ms >= {self.config.latency_critical:.1f}ms"
            ))
        elif metric.latency_ms >= self.config.latency_warning:
            violations.append(ThresholdViolation(
                metric_name="latency_ms",
                observed_value=metric.latency_ms,
                threshold_value=self.config.latency_warning,
                severity="Warning",
                message=f"Latency warning: {metric.latency_ms:.1f}ms >= {self.config.latency_warning:.1f}ms"
            ))

        # 3. CPU check
        if metric.cpu_usage >= self.config.cpu_critical:
            violations.append(ThresholdViolation(
                metric_name="cpu_usage",
                observed_value=metric.cpu_usage,
                threshold_value=self.config.cpu_critical,
                severity="Critical",
                message=f"CPU utilization critical: {metric.cpu_usage:.1f}% >= {self.config.cpu_critical:.1f}%"
            ))
        elif metric.cpu_usage >= self.config.cpu_warning:
            violations.append(ThresholdViolation(
                metric_name="cpu_usage",
                observed_value=metric.cpu_usage,
                threshold_value=self.config.cpu_warning,
                severity="Warning",
                message=f"CPU utilization warning: {metric.cpu_usage:.1f}% >= {self.config.cpu_warning:.1f}%"
            ))

        # 4. Memory check
        if metric.memory_usage >= self.config.memory_critical:
            violations.append(ThresholdViolation(
                metric_name="memory_usage",
                observed_value=metric.memory_usage,
                threshold_value=self.config.memory_critical,
                severity="Critical",
                message=f"Memory utilization critical: {metric.memory_usage:.1f}% >= {self.config.memory_critical:.1f}%"
            ))
        elif metric.memory_usage >= self.config.memory_warning:
            violations.append(ThresholdViolation(
                metric_name="memory_usage",
                observed_value=metric.memory_usage,
                threshold_value=self.config.memory_warning,
                severity="Warning",
                message=f"Memory utilization warning: {metric.memory_usage:.1f}% >= {self.config.memory_warning:.1f}%"
            ))

        return violations

# Shared singleton instance
threshold_detector = ThresholdDetector()
