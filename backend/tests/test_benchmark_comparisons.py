import pytest
from app.services.benchmark_statistics_service import BenchmarkStatisticsService
from app.services.benchmark_comparison_service import BenchmarkComparisonService

def test_statistics_summary():
    data = [10.0, 20.0, 30.0, 40.0, 50.0]
    summary = BenchmarkStatisticsService.compute_summary(data)
    assert summary["sample_count"] == 5
    assert summary["mean"] == 30.0
    assert summary["median"] == 30.0
    assert summary["min"] == 10.0
    assert summary["max"] == 50.0
    assert summary["std_dev"] > 0

def test_statistics_paired_comparison():
    comp = BenchmarkStatisticsService.compare_paired(baseline=50.0, candidate=80.0, higher_is_better=True)
    assert comp["is_improvement"] is True
    assert comp["percentage_diff"] == 60.0

    comp_lower = BenchmarkStatisticsService.compare_paired(baseline=100.0, candidate=20.0, higher_is_better=False)
    assert comp_lower["is_improvement"] is True
    assert comp_lower["percentage_diff"] == -80.0

def test_compare_module_methods():
    base_metrics = {"f1_score": 0.70, "false_positive_rate": 0.15, "detection_delay_ms": 25.0}
    cand_metrics = {"f1_score": 0.95, "false_positive_rate": 0.02, "detection_delay_ms": 12.0}

    res = BenchmarkComparisonService.compare_module_methods(
        module_name="module_2",
        baseline_name="threshold_rules",
        baseline_metrics=base_metrics,
        candidate_name="combined_alerting",
        candidate_metrics=cand_metrics
    )
    assert res["candidate_name"] == "combined_alerting"
    assert res["baseline_name"] == "threshold_rules"
    assert "interpretation" in res
    assert "comparison_metrics" in res
    assert res["comparison_metrics"]["f1_score"]["is_improvement"] is True
    assert res["comparison_metrics"]["false_positive_rate"]["is_improvement"] is True
