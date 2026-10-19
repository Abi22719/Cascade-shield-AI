import json
import pytest
from app.services.validation_engine import ValidationEngine
from app.schemas.validation_schemas import ValidationRunRequest
from app.database.recovery_repository import RecoveryRepository

def test_verified_success_outcome(db_session):
    # Create plan and successful simulation run with all services HEALTHY
    plan = RecoveryRepository.create_plan(db_session, {
        "plan_name": "Verified Success Plan",
        "strategy_type": "balanced",
        "risk_score": 20.0,
        "actions": [
            {
                "action_type": "restart_service",
                "target_service_id": "srv-payment",
                "action_order": 1,
                "estimated_duration": 3
            }
        ]
    })
    run = RecoveryRepository.create_run(db_session, {
        "plan_id": plan.id,
        "outcome": "SUCCESSFUL_RECOVERY",
        "total_recovery_time": 4,
        "final_health_summary": {
            "srv-payment": "HEALTHY",
            "srv-database": "HEALTHY",
            "srv-order": "HEALTHY",
            "srv-gateway": "HEALTHY"
        }
    })

    resp = ValidationEngine.validate_recovery(db_session, ValidationRunRequest(
        recovery_plan_id=plan.id,
        recovery_simulation_run_id=run.id,
        verification_window_steps=3,
        force_rerun=True
    ))

    assert resp.overall_outcome == "VERIFIED_SUCCESS"
    assert resp.passed_checks > 0
    assert resp.failed_checks == 0

def test_failed_outcome_due_to_rollback(db_session):
    plan = RecoveryRepository.create_plan(db_session, {
        "plan_name": "Failed Rollback Plan",
        "strategy_type": "fastest_recovery",
        "risk_score": 60.0,
        "actions": [
            {
                "action_type": "restart_service",
                "target_service_id": "srv-database",
                "action_order": 1,
                "estimated_duration": 1
            }
        ]
    })
    run = RecoveryRepository.create_run(db_session, {
        "plan_id": plan.id,
        "outcome": "FAILED_RECOVERY",
        "total_recovery_time": 1,
        "final_health_summary": {
            "srv-database": "CRITICAL",
            "srv-payment": "CRITICAL"
        }
    })
    RecoveryRepository.record_event(
        db=db_session,
        run_id=run.id,
        event_type="ROLLBACK_TRIGGERED",
        description="Rollback triggered: Precondition violated on database restart",
        step=1
    )

    resp = ValidationEngine.validate_recovery(db_session, ValidationRunRequest(
        recovery_plan_id=plan.id,
        recovery_simulation_run_id=run.id,
        force_rerun=True
    ))

    assert resp.overall_outcome == "FAILED"
    assert resp.failed_checks > 0
    assert any(r.priority == "CRITICAL" for r in resp.recommendations)

def test_partial_success_outcome(db_session):
    plan = RecoveryRepository.create_plan(db_session, {
        "plan_name": "Partial Success Plan",
        "strategy_type": "lowest_risk",
        "risk_score": 15.0,
        "actions": [
            {
                "action_type": "wait_auto_recovery",
                "target_service_id": "srv-payment",
                "action_order": 1,
                "estimated_duration": 1
            }
        ]
    })
    run = RecoveryRepository.create_run(db_session, {
        "plan_id": plan.id,
        "outcome": "PARTIAL_RECOVERY",
        "total_recovery_time": 1,
        "final_health_summary": {
            "srv-payment": "RECOVERING"
        }
    })

    resp = ValidationEngine.validate_recovery(db_session, ValidationRunRequest(
        recovery_plan_id=plan.id,
        recovery_simulation_run_id=run.id,
        verification_window_steps=3,
        force_rerun=True
    ))

    assert resp.overall_outcome == "PARTIAL_SUCCESS"
