import pytest
from app.services.action_registry import ActionRegistry, register_default_actions

def test_action_registry_defaults():
    register_default_actions()
    actions = ActionRegistry.get_all_actions()
    assert len(actions) == 12
    
    expected_ids = [
        "inspect_service_health",
        "retrieve_service_metrics",
        "compare_metrics_baseline",
        "retrieve_anomaly_alerts",
        "inspect_dependency",
        "trace_failure_paths",
        "compare_timestamps",
        "inspect_cascade_prediction",
        "reevaluate_root_causes",
        "identify_missing_evidence",
        "compare_hypotheses",
        "inspect_saved_simulation"
    ]
    for act_id in expected_ids:
        assert ActionRegistry.is_registered(act_id)
        action_def = ActionRegistry.get_action(act_id)
        assert action_def is not None
        assert action_def.action_id == act_id
        assert 0.0 <= action_def.estimated_cost <= 1.0
        assert action_def.risk_level in ["READ_ONLY", "MINIMAL", "LOW"]
        assert len(action_def.required_parameters) >= 1

def test_action_registry_invalid_action():
    assert ActionRegistry.is_registered("non_existent_action_xyz") is False
    assert ActionRegistry.get_action("non_existent_action_xyz") is None
