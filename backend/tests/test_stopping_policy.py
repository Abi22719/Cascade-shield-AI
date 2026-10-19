import pytest
from app.services.stopping_policy import StoppingPolicy
from app.schemas.agent_schema import AgentConfigSchema, ActionRecommendation

def test_stopping_on_max_actions():
    config = AgentConfigSchema(max_actions=3)
    stop, reason, manual = StoppingPolicy.evaluate(
        step_number=3,
        elapsed_seconds=5.0,
        current_candidates=[{"service_id": "srv-payment", "score": 60.0}],
        next_best_action=None,
        config=config,
        unresolved_questions=[]
    )
    assert stop is True
    assert "MAX_ACTIONS_REACHED" in reason

def test_stopping_on_timeout():
    config = AgentConfigSchema(max_execution_time_seconds=10.0)
    stop, reason, manual = StoppingPolicy.evaluate(
        step_number=1,
        elapsed_seconds=11.5,
        current_candidates=[{"service_id": "srv-payment", "score": 60.0}],
        next_best_action=None,
        config=config,
        unresolved_questions=[]
    )
    assert stop is True
    assert "MAX_EXECUTION_TIME_REACHED" in reason

def test_stopping_on_user_request():
    config = AgentConfigSchema()
    stop, reason, manual = StoppingPolicy.evaluate(
        step_number=1,
        elapsed_seconds=1.0,
        current_candidates=[{"service_id": "srv-payment", "score": 60.0}],
        next_best_action=None,
        config=config,
        unresolved_questions=[],
        user_stop_requested=True
    )
    assert stop is True
    assert "USER_STOP_REQUESTED" in reason

def test_stopping_on_sufficient_evidence():
    config = AgentConfigSchema(sufficient_confidence_threshold=0.75, confidence_margin_threshold=20.0)
    candidates = [
        {"service_id": "srv-payment", "score": 85.0},
        {"service_id": "srv-order", "score": 40.0}
    ]
    stop, reason, manual = StoppingPolicy.evaluate(
        step_number=2,
        elapsed_seconds=3.0,
        current_candidates=candidates,
        next_best_action=None,
        config=config,
        unresolved_questions=[]
    )
    assert stop is True
    assert "SUFFICIENT_EVIDENCE" in reason
    assert manual is False
