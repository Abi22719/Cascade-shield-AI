import pytest
from app.database.recovery_repository import RecoveryRepository
from app.services.recovery_simulation_service import RecoverySimulationService
from app.schemas.recovery_schemas import (
    RecoverySimulationRequest,
    RecoveryActionCreate,
    RecoveryPreconditionSchema
)

def test_recovery_simulation_successful_run(db_session):
    plan = RecoveryRepository.create_plan(db_session, {
        "plan_name": "Simulation Test Plan",
        "strategy_type": "balanced",
        "actions": [
            {
                "action_type": "traffic_reroute",
                "target_service_id": "srv-payment",
                "action_order": 1,
                "estimated_duration": 1
            },
            {
                "action_type": "restart_service",
                "target_service_id": "srv-payment",
                "action_order": 2,
                "estimated_duration": 1
            }
        ]
    })

    req = RecoverySimulationRequest(random_seed=42)
    res = RecoverySimulationService.simulate_recovery_plan(db_session, plan.id, req)

    assert res.outcome in ["SUCCESSFUL_RECOVERY", "PARTIAL_RECOVERY"]
    assert res.total_recovery_time >= 2
    assert len(res.events) >= 2
    assert any(e["event_type"] == "ACTION_COMPLETED" for e in res.events)

def test_recovery_simulation_precondition_violation(db_session):
    plan = RecoveryRepository.create_plan(db_session, {
        "plan_name": "Violated Precondition Plan",
        "actions": [
            {
                "action_type": "rollback_deployment",
                "target_service_id": "srv-payment",
                "action_order": 1,
                "preconditions": [
                    {"name": "Schema Compatibility", "description": "Compatibility", "status": "violated"}
                ]
            }
        ]
    })

    req = RecoverySimulationRequest(random_seed=42, stop_on_failure=True)
    res = RecoverySimulationService.simulate_recovery_plan(db_session, plan.id, req)

    assert any(e["event_type"] == "PRECONDITION_FAILED" for e in res.events)
    assert any(e["event_type"] == "ROLLBACK_TRIGGERED" for e in res.events)
