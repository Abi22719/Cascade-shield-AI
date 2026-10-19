import math
from typing import List, Dict, Any, Optional

class BenchmarkStatisticsService:
    """
    Computes statistical summaries across repeated measurements:
    mean, median, standard deviation, min, max, and paired comparisons.
    """

    @classmethod
    def calculate_stats(cls, values: List[float]) -> Dict[str, Any]:
        if not values:
            return {
                "sample_count": 0,
                "count": 0,
                "mean": None,
                "median": None,
                "std_dev": None,
                "min": None,
                "max": None
            }

        n = len(values)
        mean_val = round(sum(values) / n, 4)

        sorted_vals = sorted(values)
        if n % 2 == 1:
            median_val = sorted_vals[n // 2]
        else:
            median_val = round((sorted_vals[(n // 2) - 1] + sorted_vals[n // 2]) / 2.0, 4)

        variance = sum((x - mean_val) ** 2 for x in values) / (n - 1) if n > 1 else 0.0
        std_dev = round(math.sqrt(variance), 4)

        return {
            "sample_count": n,
            "count": n,
            "mean": mean_val,
            "median": median_val,
            "std_dev": std_dev,
            "min": round(min(values), 4),
            "max": round(max(values), 4)
        }

    # Alias
    compute_summary = calculate_stats

    @classmethod
    def compare_paired(
        cls,
        baseline_val: Optional[float] = None,
        candidate_val: Optional[float] = None,
        higher_is_better: bool = True,
        baseline: Optional[float] = None,
        candidate: Optional[float] = None
    ) -> Dict[str, Any]:
        b_val = baseline if baseline is not None else (baseline_val if baseline_val is not None else 0.0)
        c_val = candidate if candidate is not None else (candidate_val if candidate_val is not None else 0.0)

        delta = round(c_val - b_val, 4)
        pct_change = 0.0
        if not math.isclose(b_val, 0.0, abs_tol=1e-6):
            pct_change = round(((c_val - b_val) / abs(b_val)) * 100.0, 2)
        elif not math.isclose(c_val, 0.0, abs_tol=1e-6):
            pct_change = 100.0

        is_improvement = (delta > 0) if higher_is_better else (delta < 0)

        return {
            "baseline": b_val,
            "candidate": c_val,
            "delta": delta,
            "percent_change": pct_change,
            "percentage_diff": pct_change,
            "is_improvement": is_improvement
        }
