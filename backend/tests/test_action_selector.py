import pytest
from app.services.action_selector import ActionSelector
from app.schemas.agent_schema import AgentConfigSchema

def test_action_selector_prerequisites():
    config = AgentConfigSchema()
    
    # Empty context: target_service_id is None
    context_no_target = {
        "target_service_id": None,
        "affected_service_ids": [],
        "candidates": [],
        "executed_action_ids": []
    }
    recs = ActionSelector.rank_actions(context_no_target, config)
    for r in recs:
        if r.action_id in ["inspect_service_health", "retrieve_anomaly_alerts"]:
            assert r.eligible is False
            assert "No target service" in r.ineligibility_reason

    # Valid target context
    context_valid = {
        "target_service_id": "srv-payment",
        "affected_service_ids": ["srv-order"],
        "candidates": [{"service_id": "srv-payment", "score": 70.0}, {"service_id": "srv-order", "score": 40.0}],
        "executed_action_ids": []
    }
    recs_valid = ActionSelector.rank_actions(context_valid, config)
    best = ActionSelector.select_best_action(context_valid, config)
    assert best is not None
    assert best.eligible is True
    assert best.utility_score >= config.min_utility_threshold

def test_action_selector_repeated_penalty():
    config = AgentConfigSchema()
    context = {
        "target_service_id": "srv-payment",
        "affected_service_ids": ["srv-order"],
        "candidates": [{"service_id": "srv-payment", "score": 70.0}],
        "executed_action_ids": ["inspect_service_health"]  # Already executed
    }
    recs = ActionSelector.rank_actions(context, config)
    health_rec = next(r for r in recs if r.action_id == "inspect_service_health")
    assert health_rec.repeat_penalty > 0.0

    # Ensure best action is NOT inspect_service_health because of repeat penalty
    best = ActionSelector.select_best_action(context, config)
    assert best is not None
    assert best.action_id != "inspect_service_health"
