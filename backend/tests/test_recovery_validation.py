import pytest
from app.services.recovery_validation_service import RecoveryValidationService
from app.schemas.recovery_schemas import (
    RecoveryPlanCreateRequest,
    RecoveryActionCreate
)

def test_validation_success_valid_plan(db_session):
    req = RecoveryPlanCreateRequest(
        plan_name="Valid Test Plan",
        actions=[
            RecoveryActionCreate(
                action_type="restart_service",
                target_service_id="srv-payment",
                action_order=1
            )
        ]
    )
    res = RecoveryValidationService.validate_plan_creation(db_session, req)
    assert res["valid"] is True
    assert res["actions_count"] == 1

def test_validation_fails_unknown_service(db_session):
    req = RecoveryPlanCreateRequest(
        plan_name="Invalid Service Plan",
        actions=[
            RecoveryActionCreate(
                action_type="restart_service",
                target_service_id="srv-nonexistent-cloud-node",
                action_order=1
            )
        ]
    )
    with pytest.raises(ValueError, match="does not exist in the digital twin"):
        RecoveryValidationService.validate_plan_creation(db_session, req)

def test_validation_fails_unsupported_action(db_session):
    req = RecoveryPlanCreateRequest(
        plan_name="Unsupported Action Plan",
        actions=[
            RecoveryActionCreate(
                action_type="format_hard_drive",
                target_service_id="srv-payment",
                action_order=1
            )
        ]
    )
    with pytest.raises(ValueError, match="Unsupported action type"):
        RecoveryValidationService.validate_plan_creation(db_session, req)

def test_validation_fails_empty_actions(db_session):
    req = RecoveryPlanCreateRequest(
        plan_name="Empty Plan",
        actions=[]
    )
    with pytest.raises(ValueError, match="must contain at least one recovery action"):
        RecoveryValidationService.validate_plan_creation(db_session, req)
