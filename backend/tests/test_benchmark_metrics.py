import pytest
from app.services.benchmark_metrics_service import BenchmarkMetricsService

def test_safe_divide():
    assert BenchmarkMetricsService.safe_divide(10, 2) == 5.0
    assert BenchmarkMetricsService.safe_divide(10, 0) == 0.0
    assert BenchmarkMetricsService.safe_divide(10, 0, default=1.0) == 1.0

def test_anomaly_metrics():
    metrics = BenchmarkMetricsService.compute_anomaly_metrics(tp=4, fp=1, tn=5, fn=0, delay_ms=10.0)
    assert metrics["precision"] == 0.8
    assert metrics["recall"] == 1.0
    assert metrics["f1_score"] == pytest.approx(0.8889, rel=1e-3)
    assert metrics["false_positive_rate"] == pytest.approx(0.1667, rel=1e-3)
    assert metrics["detection_delay_ms"] == 10.0

def test_cascade_metrics():
    pred = ["srv-gateway", "srv-order", "srv-payment"]
    exp = ["srv-order", "srv-payment"]
    metrics = BenchmarkMetricsService.compute_cascade_metrics(pred, exp, runtime_ms=2.5)
    assert metrics["cascade_recall"] == 1.0
    assert metrics["cascade_precision"] == pytest.approx(0.6667, rel=1e-3)
    assert metrics["execution_time_ms"] == 2.5

def test_rca_metrics():
    ranked = ["srv-payment", "srv-order", "srv-gateway"]
    metrics = BenchmarkMetricsService.compute_rca_metrics(ranked, "srv-payment", runtime_ms=1.5)
    assert metrics["top1_accuracy"] == 1.0
    assert metrics["top3_accuracy"] == 1.0
    assert metrics["mean_reciprocal_rank"] == 1.0

    # Tested when rank is 2
    metrics2 = BenchmarkMetricsService.compute_rca_metrics(ranked, "srv-order", runtime_ms=1.5)
    assert metrics2["top1_accuracy"] == 0.0
    assert metrics2["top3_accuracy"] == 1.0
    assert metrics2["mean_reciprocal_rank"] == 0.5

def test_agent_metrics():
    metrics = BenchmarkMetricsService.compute_agent_metrics(actions_executed=3, useful_findings=3, repeated_actions=0)
    assert metrics["useful_ratio"] == 1.0
    assert metrics["repeated_action_rate"] == 0.0
    assert metrics["budget_efficiency"] == 0.4

def test_simulation_metrics():
    metrics = BenchmarkMetricsService.compute_simulation_metrics(steps_simulated=5, propagated_events=4, is_reproducible=True)
    assert metrics["steps_simulated"] == 5.0
    assert metrics["reproducibility_rate"] == 1.0
    assert metrics["simulation_error_rate"] == 0.0

def test_recovery_metrics():
    metrics = BenchmarkMetricsService.compute_recovery_metrics(is_success=True, recovery_time_steps=3, risk_score=25.0, cost=15.0)
    assert metrics["recovery_success"] == 1.0
    assert metrics["recovery_time_steps"] == 3.0
    assert metrics["maximum_risk_score"] == 25.0

def test_validation_metrics():
    metrics = BenchmarkMetricsService.compute_validation_metrics(
        predicted_outcome="VERIFIED_SUCCESS",
        ground_truth_outcome="VERIFIED_SUCCESS",
        residual_failures_detected=0
    )
    assert metrics["validation_accuracy"] == 1.0
    assert metrics["false_success_rate"] == 0.0

def test_overall_resilience_score():
    scores = {
        "detection": 95.0,
        "prediction": 90.0,
        "rca": 100.0,
        "diagnostic": 85.0,
        "simulation": 100.0,
        "recovery": 95.0,
        "validation": 90.0
    }
    score, breakdown = BenchmarkMetricsService.compute_overall_resilience_score(scores)
    assert 90.0 <= score <= 100.0
    assert len(breakdown) == 7
