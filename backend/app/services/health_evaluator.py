from typing import List, Tuple
from pydantic import BaseModel

class HealthRuleThresholds(BaseModel):
    # Critical thresholds
    critical_error_rate: float = 10.0      # %
    critical_latency_ms: float = 1000.0    # ms
    critical_cpu_usage: float = 90.0       # %
    critical_memory_usage: float = 92.0    # %

    # Warning thresholds
    warning_error_rate: float = 2.0        # %
    warning_latency_ms: float = 400.0      # ms
    warning_cpu_usage: float = 75.0        # %
    warning_memory_usage: float = 80.0     # %

DEFAULT_THRESHOLDS = HealthRuleThresholds()

def evaluate_service_health(
    cpu_usage: float,
    memory_usage: float,
    latency_ms: float,
    error_rate: float,
    thresholds: HealthRuleThresholds = DEFAULT_THRESHOLDS
) -> Tuple[str, List[str]]:
    """
    Evaluates service health status based on configurable metric rules.
    Returns (status, reasons) where status is HEALTHY, WARNING, or CRITICAL.
    """
    critical_reasons: List[str] = []
    warning_reasons: List[str] = []

    # Check Critical
    if error_rate >= thresholds.critical_error_rate:
        critical_reasons.append(
            f"Error rate critical: {error_rate:.1f}% >= {thresholds.critical_error_rate:.1f}%"
        )
    if latency_ms >= thresholds.critical_latency_ms:
        critical_reasons.append(
            f"Latency critical: {latency_ms:.1f}ms >= {thresholds.critical_latency_ms:.1f}ms"
        )
    if cpu_usage >= thresholds.critical_cpu_usage:
        critical_reasons.append(
            f"CPU usage critical: {cpu_usage:.1f}% >= {thresholds.critical_cpu_usage:.1f}%"
        )
    if memory_usage >= thresholds.critical_memory_usage:
        critical_reasons.append(
            f"Memory usage critical: {memory_usage:.1f}% >= {thresholds.critical_memory_usage:.1f}%"
        )

    if critical_reasons:
        return "CRITICAL", critical_reasons

    # Check Warning
    if error_rate >= thresholds.warning_error_rate:
        warning_reasons.append(
            f"Error rate elevated: {error_rate:.1f}% >= {thresholds.warning_error_rate:.1f}%"
        )
    if latency_ms >= thresholds.warning_latency_ms:
        warning_reasons.append(
            f"Latency elevated: {latency_ms:.1f}ms >= {thresholds.warning_latency_ms:.1f}ms"
        )
    if cpu_usage >= thresholds.warning_cpu_usage:
        warning_reasons.append(
            f"CPU usage elevated: {cpu_usage:.1f}% >= {thresholds.warning_cpu_usage:.1f}%"
        )
    if memory_usage >= thresholds.warning_memory_usage:
        warning_reasons.append(
            f"Memory usage elevated: {memory_usage:.1f}% >= {thresholds.warning_memory_usage:.1f}%"
        )

    if warning_reasons:
        return "WARNING", warning_reasons

    return "HEALTHY", ["All telemetry metrics are within optimal operating thresholds."]
