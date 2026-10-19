import pytest
from app.models import ServiceModel, DependencyModel, AlertModel
from app.database.simulation_repository import SimulationRepository
from app.services.simulation_engine import SimulationEngine
from app.schemas.simulation_schema import (
    ScenarioConfigSchema,
    FailureInjectionConfig,
    PropagationParameters,
    RecoveryParameters
)

def test_simulation_does_not_mutate_live_database(db_session):
    # Snapshot live DB records before simulation
    services_before = db_session.query(ServiceModel).all()
    services_snapshot = [
        (s.id, s.latency_ms, s.error_rate, s.cpu_usage, s.memory_usage, s.health_status)
        for s in services_before
    ]
    deps_count_before = db_session.query(DependencyModel).count()
    alerts_count_before = db_session.query(AlertModel).count()

    # Create and run intensive simulations
    configs = [
        ScenarioConfigSchema(
            failures=[FailureInjectionConfig(target_service_ids=["srv-payment"], failure_type="service_unavailable", severity="severe")],
            propagation=PropagationParameters(max_steps=5),
            recovery=RecoveryParameters(recovery_mode="gradual")
        ),
        ScenarioConfigSchema(
            failures=[FailureInjectionConfig(target_service_ids=["srv-database"], failure_type="database_starvation", severity="severe")],
            propagation=PropagationParameters(max_steps=6),
            recovery=RecoveryParameters(recovery_mode="immediate")
        )
    ]

    for i, cfg in enumerate(configs):
        sc = SimulationRepository.create_scenario(db_session, {"name": f"Safety Scenario {i}", "config": cfg.model_dump()})
        SimulationEngine.run_simulation(db_session, sc.id, sc.name, cfg, random_seed=42)

    # Force session refresh from DB
    db_session.expire_all()

    # Snapshot live DB records after simulations
    services_after = db_session.query(ServiceModel).all()
    services_after_snapshot = [
        (s.id, s.latency_ms, s.error_rate, s.cpu_usage, s.memory_usage, s.health_status)
        for s in services_after
    ]
    deps_count_after = db_session.query(DependencyModel).count()
    alerts_count_after = db_session.query(AlertModel).count()

    # Assert complete zero-mutation guarantee
    assert services_snapshot == services_after_snapshot, "ServiceModel records were mutated during simulation!"
    assert deps_count_before == deps_count_after, "DependencyModel count was modified!"
    assert alerts_count_before == alerts_count_after, "AlertModel count was modified!"
