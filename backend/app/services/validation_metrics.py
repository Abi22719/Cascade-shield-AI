import math
from typing import Dict, Any, List, Optional, Tuple
from app.schemas.validation_schemas import BeforeAfterMetricDiff, ValidationConfigSchema

class ValidationMetricsEngine:
    """
    Performs rigorous before-and-after telemetry metric validation.
    Handles zero division, missing values, and threshold validations safely.
    """

    @classmethod
    def calculate_percent_change(cls, before: Optional[float], after: Optional[float]) -> Optional[float]:
        if before is None or after is None:
            return None
        if math.isclose(before, 0.0, abs_tol=1e-6):
            if math.isclose(after, 0.0, abs_tol=1e-6):
                return 0.0
            return 100.0  # From 0 to positive represents an increase
        return round(((after - before) / abs(before)) * 100.0, 2)

    @classmethod
    def evaluate_metric_trend(
        cls, 
        metric_name: str, 
        before: Optional[float], 
        after: Optional[float]
    ) -> Tuple[str, Optional[float], Optional[float]]:
        """
        Determines whether the metric trend is IMPROVED, WORSENED, UNCHANGED, or UNKNOWN.
        For latency, error_rate, cpu, and memory: lower is better.
        For request_volume: closer to baseline or higher is better.
        """
        if before is None or after is None:
            return "UNKNOWN", None, None

        delta = round(after - before, 2)
        pct = cls.calculate_percent_change(before, after)

        if math.isclose(delta, 0.0, abs_tol=1e-4):
            return "UNCHANGED", delta, pct

        lower_is_better = ["latency_ms", "error_rate", "cpu_usage", "memory_usage"]
        if metric_name in lower_is_better:
            trend = "IMPROVED" if delta < 0 else "WORSENED"
        else:
            trend = "IMPROVED" if delta > 0 else "WORSENED"

        return trend, delta, pct

    @classmethod
    def validate_service_metrics(
        cls,
        service_id: str,
        service_name: str,
        before_metrics: Dict[str, Any],
        after_metrics: Dict[str, Any],
        config: ValidationConfigSchema
    ) -> List[BeforeAfterMetricDiff]:
        """
        Produces detailed diff records across latency, error_rate, cpu, memory, and request_volume.
        """
        diffs: List[BeforeAfterMetricDiff] = []
        metric_keys = ["latency_ms", "error_rate", "cpu_usage", "memory_usage", "request_volume"]

        for key in metric_keys:
            b_val = before_metrics.get(key)
            a_val = after_metrics.get(key)

            trend, delta, pct = cls.evaluate_metric_trend(key, b_val, a_val)

            status = "UNKNOWN"
            if a_val is None:
                status = "UNKNOWN"
            elif key == "latency_ms":
                if a_val <= config.max_acceptable_latency_ms:
                    status = "PASS"
                elif a_val <= config.max_acceptable_latency_ms * 1.25:
                    status = "WARNING"
                else:
                    status = "FAIL"
            elif key == "error_rate":
                if a_val <= config.max_acceptable_error_rate:
                    status = "PASS"
                elif a_val <= config.max_acceptable_error_rate * 1.5:
                    status = "WARNING"
                else:
                    status = "FAIL"
            elif key == "cpu_usage":
                if a_val <= config.max_acceptable_cpu_percent:
                    status = "PASS"
                elif a_val <= config.max_acceptable_cpu_percent * 1.1:
                    status = "WARNING"
                else:
                    status = "FAIL"
            elif key == "memory_usage":
                if a_val <= config.max_acceptable_memory_percent:
                    status = "PASS"
                elif a_val <= config.max_acceptable_memory_percent * 1.1:
                    status = "WARNING"
                else:
                    status = "FAIL"
            else:
                # request_volume
                status = "PASS" if trend in ["IMPROVED", "UNCHANGED"] else "WARNING"

            diffs.append(BeforeAfterMetricDiff(
                service_id=service_id,
                service_name=service_name,
                metric_name=key,
                before_value=b_val,
                after_value=a_val,
                delta=delta,
                percent_change=pct,
                trend=trend,
                status=status
            ))

        return diffs
