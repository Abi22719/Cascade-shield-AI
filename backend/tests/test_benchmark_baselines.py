import pytest
from app.services.benchmark_baseline_service import BenchmarkBaselineService

def test_supported_baselines_catalog():
    catalog = BenchmarkBaselineService.get_supported_baselines()
    assert "module_2" in catalog
    assert "module_3" in catalog
    assert "module_4" in catalog
    assert "module_5" in catalog
    assert "module_6" in catalog
    assert "module_7" in catalog
    assert "module_8" in catalog

    for mod, data in catalog.items():
        assert "candidate" in data
        assert "baselines" in data
        assert len(data["baselines"]) >= 1

def test_evaluate_module_candidates_and_baselines():
    gt = {
        "expected_anomalies": ["srv-payment", "srv-order"],
        "expected_affected_services": ["srv-payment", "srv-order", "srv-gateway"],
        "expected_root_cause": "srv-payment",
        "expected_diagnostic_actions": ["inspect_service_health", "retrieve_anomaly_alerts"],
        "expected_recovery_strategy": "balanced",
        "expected_validation_outcome": "VERIFIED_SUCCESS"
    }

    # Module 2
    m2_cand = BenchmarkBaselineService.evaluate_module_2(gt, "combined_alerting")
    m2_base = BenchmarkBaselineService.evaluate_module_2(gt, "threshold_rules")
    assert m2_cand["f1_score"] >= m2_base["f1_score"]

    # Module 3
    m3_cand = BenchmarkBaselineService.evaluate_module_3(gt, "evidence_aware_cascade")
    m3_base = BenchmarkBaselineService.evaluate_module_3(gt, "simple_dependency_traversal")
    assert m3_cand["cascade_precision"] >= m3_base["cascade_precision"]

    # Module 4
    m4_cand = BenchmarkBaselineService.evaluate_module_4(gt, "evidence_grounded_rca")
    m4_base = BenchmarkBaselineService.evaluate_module_4(gt, "earliest_anomaly_baseline")
    assert m4_cand["top1_accuracy"] >= m4_base["top1_accuracy"]

    # Module 5
    m5_cand = BenchmarkBaselineService.evaluate_module_5(gt, "adaptive_utility_agent")
    m5_base = BenchmarkBaselineService.evaluate_module_5(gt, "fixed_order_sequence")
    assert m5_cand["useful_ratio"] >= m5_base["useful_ratio"]

    # Module 6
    m6_cand = BenchmarkBaselineService.evaluate_module_6({"duration_steps": 4}, gt, "time_step_simulator")
    m6_base = BenchmarkBaselineService.evaluate_module_6({"duration_steps": 4}, gt, "static_reachability")
    assert m6_cand["steps_simulated"] >= m6_base["steps_simulated"]

    # Module 7
    m7_cand = BenchmarkBaselineService.evaluate_module_7(gt, "risk_aware_balanced")
    m7_base = BenchmarkBaselineService.evaluate_module_7(gt, "lowest_cost_strategy")
    assert m7_cand["recovery_success"] >= m7_base["recovery_success"]

    # Module 8
    m8_cand = BenchmarkBaselineService.evaluate_module_8(gt, "full_5_pillar_validation")
    m8_base = BenchmarkBaselineService.evaluate_module_8(gt, "basic_health_only")
    assert m8_cand["validation_accuracy"] >= m8_base["validation_accuracy"]
