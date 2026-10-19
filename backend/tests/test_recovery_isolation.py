import pytest
from app.models import ServiceModel, DependencyModel, AlertModel, SimulationScenarioModel
from app.database.recovery_repository import RecoveryRepository
from app.services.recovery_simulation_service import RecoverySimulationService
from app.schemas.recovery_schemas import RecoverySimulationRequest

def test_recovery_simulation_zero_db_mutation(db_session):
    # Snapshot real digital twin tables before simulation
    services_before = [
        (s.id, s.latency_ms, s.error_rate, s.cpu_usage, s.health_status)
        for s in db_session.query(ServiceModel).all()
    ]
    deps_count_before = db_session.query(DependencyModel).count()
    alerts_count_before = db_session.query(AlertModel).count()

    # Create and execute multiple recovery plan simulations
    for action_type in ["restart_service", "scale_up", "traffic_reroute", "rollback_deployment"]:
        plan = RecoveryRepository.create_plan(db_session, {
            "plan_name": f"Isolation Test {action_type}",
            "actions": [
                {"action_type": action_type, "target_service_id": "srv-payment", "action_order": 1}
            ]
        })
        RecoverySimulationService.simulate_recovery_plan(db_session, plan.id, RecoverySimulationRequest())

    db_session.expire_all()

    # Snapshot real digital twin tables after simulations
    services_after = [
        (s.id, s.latency_ms, s.error_rate, s.cpu_usage, s.health_status)
        for s in db_session.query(ServiceModel).all()
    ]
    deps_count_after = db_session.query(DependencyModel).count()
    alerts_count_after = db_session.query(AlertModel).count()

    # Verify 100% zero-mutation guarantee on live assets
    assert services_before == services_after, "ServiceModel was mutated during recovery simulation!"
    assert deps_count_before == deps_count_after, "DependencyModel was modified during recovery simulation!"
    assert alerts_count_before == alerts_count_after, "AlertModel was modified during recovery simulation!"
