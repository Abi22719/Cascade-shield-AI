import pytest
from app.models.service import ServiceModel
from app.models.dependency import DependencyModel
from app.services.validation_engine import ValidationEngine
from app.schemas.validation_schemas import ValidationRunRequest
from app.database.recovery_repository import RecoveryRepository

def test_validation_isolation_from_live_database(db_session):
    # Capture baseline service state before running validation
    services_before = {s.id: (s.health_status, s.latency_ms, s.error_rate) for s in db_session.query(ServiceModel).all()}
    deps_before = {(d.source_service_id, d.target_service_id) for d in db_session.query(DependencyModel).all()}

    # Create plan and run validation
    plan = RecoveryRepository.create_plan(db_session, {
        "plan_name": "Isolation Safety Plan",
        "strategy_type": "fastest_recovery",
        "risk_score": 75.0,
        "actions": [
            {
                "action_type": "restart_service",
                "target_service_id": "srv-database",
                "action_order": 1,
                "estimated_duration": 2
            }
        ]
    })

    resp = ValidationEngine.validate_recovery(db_session, ValidationRunRequest(
        recovery_plan_id=plan.id,
        force_rerun=True
    ))

    assert resp.id is not None

    # Verify live database records remain 100% identical
    services_after = {s.id: (s.health_status, s.latency_ms, s.error_rate) for s in db_session.query(ServiceModel).all()}
    deps_after = {(d.source_service_id, d.target_service_id) for d in db_session.query(DependencyModel).all()}

    assert services_before == services_after
    assert deps_before == deps_after
