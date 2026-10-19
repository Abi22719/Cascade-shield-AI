from typing import Dict, Any, List, Optional
from app.schemas.validation_schemas import BeforeAfterComparisonSchema, BeforeAfterMetricDiff
from app.services.validation_metrics import ValidationMetricsEngine

class ValidationComparisonEngine:
    """
    Computes before-and-after recovery comparison summaries.
    Contrasts health counts, metric deltas, downstream impact, and stability.
    """

    @classmethod
    def build_comparison(
        cls,
        services_before: Dict[str, Dict[str, Any]],
        services_after: Dict[str, Dict[str, Any]],
        metric_diffs: List[BeforeAfterMetricDiff],
        new_failures: List[str],
        downstream_before_count: int,
        downstream_after_count: int,
        recovery_time_steps: int,
        stability_steps: int,
        is_stable: bool
    ) -> BeforeAfterComparisonSchema:
        # Calculate health counts before
        healthy_b = sum(1 for s in services_before.values() if s.get("health_status") == "HEALTHY")
        degraded_b = sum(1 for s in services_before.values() if s.get("health_status") in ["DEGRADED", "RECOVERING"])
        critical_b = sum(1 for s in services_before.values() if s.get("health_status") == "CRITICAL")

        # Calculate health counts after
        healthy_a = sum(1 for s in services_after.values() if s.get("health_status") == "HEALTHY")
        degraded_a = sum(1 for s in services_after.values() if s.get("health_status") in ["DEGRADED", "RECOVERING"])
        critical_a = sum(1 for s in services_after.values() if s.get("health_status") == "CRITICAL")

        return BeforeAfterComparisonSchema(
            services_before_count={"healthy": healthy_b, "degraded": degraded_b, "critical": critical_b},
            services_after_count={"healthy": healthy_a, "degraded": degraded_a, "critical": critical_a},
            healthy_count_before=healthy_b,
            healthy_count_after=healthy_a,
            degraded_count_before=degraded_b,
            degraded_count_after=degraded_a,
            unavailable_count_before=critical_b,
            unavailable_count_after=critical_a,
            metric_diffs=metric_diffs,
            affected_downstream_before=downstream_before_count,
            affected_downstream_after=downstream_after_count,
            new_simulated_failures=new_failures,
            time_to_recovery_steps=recovery_time_steps,
            stability_window_steps=stability_steps,
            is_stable_across_window=is_stable
        )
