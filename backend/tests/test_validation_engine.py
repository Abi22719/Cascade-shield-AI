import pytest
from app.services.validation_engine import ValidationEngine
from app.schemas.validation_schemas import ValidationRunRequest
from app.database.recovery_repository import RecoveryRepository

def test_validation_engine_auto_simulation(db_session):
    # Create plan with no pre-existing simulation run
    plan = RecoveryRepository.create_plan(db_session, {
        "plan_name": "Auto Simulate Plan",
        "strategy_type": "balanced",
        "risk_score": 25.0,
        "actions": [
            {
                "action_type": "scale_up",
                "target_service_id": "srv-payment",
                "action_order": 1,
                "estimated_duration": 2
            }
        ]
    })

    # Validate should automatically execute an isolated simulation run and evaluate it
    resp = ValidationEngine.validate_recovery(db_session, ValidationRunRequest(
        recovery_plan_id=plan.id,
        force_rerun=True
    ))

    assert resp.id is not None
    assert resp.recovery_simulation_run_id is not None
    assert resp.total_checks > 0
    assert resp.overall_outcome in ["VERIFIED_SUCCESS", "PARTIAL_SUCCESS"]

def test_validation_duplicate_prevention(db_session):
    plan = RecoveryRepository.create_plan(db_session, {
        "plan_name": "Deduplication Plan",
        "strategy_type": "balanced",
        "risk_score": 20.0
    })

    resp1 = ValidationEngine.validate_recovery(db_session, ValidationRunRequest(
        recovery_plan_id=plan.id,
        force_rerun=True
    ))

    # Second call without force_rerun should return the exact same run ID
    resp2 = ValidationEngine.validate_recovery(db_session, ValidationRunRequest(
        recovery_plan_id=plan.id,
        force_rerun=False
    ))

    assert resp1.id == resp2.id

def test_validation_invalid_plan_id(db_session):
    with pytest.raises(ValueError, match="does not exist"):
        ValidationEngine.validate_recovery(db_session, ValidationRunRequest(
            recovery_plan_id="non-existent-plan-id"
        ))
