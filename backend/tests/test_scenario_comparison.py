import pytest
from app.database.simulation_repository import SimulationRepository
from app.services.simulation_engine import SimulationEngine
from app.services.scenario_comparator import ScenarioComparator
from app.schemas.simulation_schema import (
    ScenarioConfigSchema,
    FailureInjectionConfig,
    PropagationParameters,
    RecoveryParameters
)

def test_scenario_comparison_two_runs(db_session):
    # Scenario 1: Payment outage
    cfg1 = ScenarioConfigSchema(
        failures=[
            FailureInjectionConfig(
                target_service_ids=["srv-payment"],
                failure_type="service_unavailable",
                severity="severe"
            )
        ],
        propagation=PropagationParameters(max_steps=4),
        recovery=RecoveryParameters(recovery_mode="immediate", recovery_step=3)
    )
    sc1 = SimulationRepository.create_scenario(db_session, {"name": "Payment Scenario", "config": cfg1.model_dump()})
    run1 = SimulationEngine.run_simulation(db_session, sc1.id, sc1.name, cfg1, random_seed=42)

    # Scenario 2: Auth outage
    cfg2 = ScenarioConfigSchema(
        failures=[
            FailureInjectionConfig(
                target_service_ids=["srv-auth"],
                failure_type="high_latency",
                severity="mild"
            )
        ],
        propagation=PropagationParameters(max_steps=4),
        recovery=RecoveryParameters(recovery_mode="immediate", recovery_step=2)
    )
    sc2 = SimulationRepository.create_scenario(db_session, {"name": "Auth Scenario", "config": cfg2.model_dump()})
    run2 = SimulationEngine.run_simulation(db_session, sc2.id, sc2.name, cfg2, random_seed=42)

    comparison = ScenarioComparator.compare_runs(db_session, [run1.id, run2.id])
    assert len(comparison.comparisons) == 2
    assert comparison.recommended_scenario is not None
    assert len(comparison.summary_insights) > 0
