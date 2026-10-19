import pytest
from app.database.simulation_repository import SimulationRepository
from app.services.simulation_engine import SimulationEngine
from app.schemas.simulation_schema import (
    ScenarioConfigSchema,
    FailureInjectionConfig,
    PropagationParameters,
    RecoveryParameters
)

def test_simulation_engine_run(db_session):
    config = ScenarioConfigSchema(
        failures=[
            FailureInjectionConfig(
                target_service_ids=["srv-payment"],
                failure_type="service_unavailable",
                severity="severe",
                start_step=1,
                duration_steps=3
            )
        ],
        propagation=PropagationParameters(max_steps=5, attenuation_factor=0.8),
        recovery=RecoveryParameters(recovery_mode="gradual", recovery_step=4, recovery_rate=0.5)
    )

    scenario = SimulationRepository.create_scenario(db_session, {
        "name": "Engine Test Scenario",
        "category": "failure_propagation",
        "config": config.model_dump(),
        "source_data_type": "digital_twin"
    })

    result = SimulationEngine.run_simulation(
        db=db_session,
        scenario_id=scenario.id,
        scenario_name=scenario.name,
        config=config,
        random_seed=42
    )

    assert result.status == "COMPLETED"
    assert result.total_steps == 5
    assert len(result.timeline_steps) == 5
    assert result.summary is not None
    assert result.summary.total_impacted_services >= 1
    assert "srv-payment" in result.impacted_services

def test_simulation_engine_reproducibility(db_session):
    config = ScenarioConfigSchema(
        failures=[
            FailureInjectionConfig(
                target_service_ids=["srv-database"],
                failure_type="database_starvation",
                severity="severe",
                start_step=1,
                duration_steps=4
            )
        ],
        propagation=PropagationParameters(max_steps=4),
        recovery=RecoveryParameters(recovery_mode="immediate", recovery_step=3)
    )

    scenario = SimulationRepository.create_scenario(db_session, {
        "name": "Reproducibility Test",
        "category": "database_starvation",
        "config": config.model_dump()
    })

    run1 = SimulationEngine.run_simulation(db_session, scenario.id, scenario.name, config, random_seed=999)
    run2 = SimulationEngine.run_simulation(db_session, scenario.id, scenario.name, config, random_seed=999)

    assert run1.summary.total_impacted_services == run2.summary.total_impacted_services
    assert run1.summary.peak_simultaneous_impact == run2.summary.peak_simultaneous_impact
    assert run1.summary.aggregate_impact_score == run2.summary.aggregate_impact_score
