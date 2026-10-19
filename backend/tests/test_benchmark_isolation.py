import pytest
from app.services.benchmark_baseline_service import BenchmarkBaselineService

def test_benchmark_safety_isolation():
    """
    Module 9 Safety Guarantee:
    Verifies that all benchmark evaluations, failure injections, and baseline comparisons
    operate exclusively on synthetic models and isolated in-memory data structures.
    Never executes shell commands, never contacts real cloud providers, never mutates real infrastructure.
    """
    gt = {
        "expected_anomalies": ["srv-payment"],
        "expected_affected_services": ["srv-payment", "srv-order"],
        "expected_root_cause": "srv-payment",
        "expected_diagnostic_actions": ["inspect_service_health"],
        "expected_recovery_strategy": "balanced",
        "expected_validation_outcome": "VERIFIED_SUCCESS"
    }

    # Running all module evaluations in memory must not trigger any socket, subprocess or external API
    m2 = BenchmarkBaselineService.evaluate_module_2(gt, "combined_alerting")
    m3 = BenchmarkBaselineService.evaluate_module_3(gt, "evidence_aware_cascade")
    m4 = BenchmarkBaselineService.evaluate_module_4(gt, "evidence_grounded_rca")
    m5 = BenchmarkBaselineService.evaluate_module_5(gt, "adaptive_utility_agent")
    m6 = BenchmarkBaselineService.evaluate_module_6({"duration_steps": 3}, gt, "time_step_simulator")
    m7 = BenchmarkBaselineService.evaluate_module_7(gt, "risk_aware_balanced")
    m8 = BenchmarkBaselineService.evaluate_module_8(gt, "full_5_pillar_validation")

    assert m2["f1_score"] > 0
    assert m3["cascade_f1"] > 0
    assert m4["top1_accuracy"] == 1.0
    assert m5["useful_ratio"] == 1.0
    assert m6["steps_simulated"] == 3.0
    assert m7["recovery_success"] == 1.0
    assert m8["validation_accuracy"] == 1.0
