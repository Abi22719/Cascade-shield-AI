from typing import Dict, Any, List
from app.services.benchmark_statistics_service import BenchmarkStatisticsService

class BenchmarkComparisonService:
    """
    Computes side-by-side benchmark comparisons between baseline and candidate resilience methods.
    Generates clear interpretations and percentage improvement metrics.
    """

    @classmethod
    def compare_module_methods(
        cls,
        module_name: str,
        baseline_name: str,
        baseline_metrics: Dict[str, float],
        candidate_name: str,
        candidate_metrics: Dict[str, float]
    ) -> Dict[str, Any]:
        metric_comparisons = {}
        improvements_count = 0
        total_metrics = 0

        lower_is_better_keys = [
            "false_positive_rate", "false_positives", "false_negatives", "detection_delay_ms",
            "execution_time_ms", "rca_execution_time_ms", "agent_execution_time_ms",
            "simulation_runtime_ms", "maximum_risk_score", "estimated_cost",
            "constraint_violations", "false_success_rate", "false_failure_rate",
            "validation_runtime_ms", "repeated_action_rate"
        ]

        for k, cand_val in candidate_metrics.items():
            if k in baseline_metrics:
                base_val = baseline_metrics[k]
                higher_is_better = k not in lower_is_better_keys
                comp = BenchmarkStatisticsService.compare_paired(base_val, cand_val, higher_is_better=higher_is_better)
                metric_comparisons[k] = comp
                total_metrics += 1
                if comp["is_improvement"]:
                    improvements_count += 1

        win_rate = round((improvements_count / total_metrics) * 100.0, 1) if total_metrics > 0 else 0.0

        interpretation = (
            f"Candidate method '{candidate_name}' outperformed baseline '{baseline_name}' across {improvements_count}/{total_metrics} evaluated dimensions ({win_rate}% win rate)."
        )

        return {
            "module_name": module_name,
            "comparison_name": f"{module_name}:{candidate_name}_vs_{baseline_name}",
            "baseline_name": baseline_name,
            "candidate_name": candidate_name,
            "comparison_metrics": metric_comparisons,
            "interpretation": interpretation
        }
