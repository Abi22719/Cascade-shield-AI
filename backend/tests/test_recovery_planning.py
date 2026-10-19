import pytest
from app.services.recovery_plan_service import RecoveryPlanService
from app.schemas.recovery_schemas import RecoveryPlanGenerateRequest

def test_generate_candidate_plans_default(db_session):
    req = RecoveryPlanGenerateRequest(target_service_id="srv-payment")
    plans = RecoveryPlanService.generate_candidate_plans(db_session, req)

    assert len(plans) == 4
    strategy_types = [p.strategy_type for p in plans]
    assert "lowest_risk" in strategy_types
    assert "fastest_recovery" in strategy_types
    assert "lowest_cost" in strategy_types
    assert "balanced" in strategy_types

    # Validate action attributes
    for p in plans:
        assert len(p.actions) >= 1
        for act in p.actions:
            assert act.action_type in [
                "restart_service", "rollback_deployment", "traffic_reroute", 
                "scale_up", "isolate_dependency", "restore_database", 
                "retry_request", "wait_auto_recovery"
            ]
            assert act.target_service_id == "srv-payment"
            assert act.estimated_duration >= 1
            assert act.risk_score >= 0.0

def test_generate_candidate_plans_database_target(db_session):
    req = RecoveryPlanGenerateRequest(target_service_id="srv-database")
    plans = RecoveryPlanService.generate_candidate_plans(db_session, req)

    assert len(plans) == 4
    for p in plans:
        assert any(act.target_service_id == "srv-database" for act in p.actions)
