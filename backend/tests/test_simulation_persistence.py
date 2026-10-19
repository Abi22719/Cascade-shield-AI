import pytest
from app.database.simulation_repository import SimulationRepository
from app.schemas.simulation_schema import ScenarioConfigSchema

def test_scenario_repository_crud(db_session):
    cfg = ScenarioConfigSchema()

    # Create
    scenario = SimulationRepository.create_scenario(db_session, {
        "name": "Persistence Test Scenario",
        "description": "Validating DB CRUD",
        "category": "failure_propagation",
        "config": cfg.model_dump()
    })
    assert scenario.id is not None
    assert scenario.name == "Persistence Test Scenario"

    # Read
    fetched = SimulationRepository.get_scenario(db_session, scenario.id)
    assert fetched is not None
    assert fetched.id == scenario.id

    # List
    items, total = SimulationRepository.list_scenarios(db_session)
    assert total >= 1
    assert any(s.id == scenario.id for s in items)

    # Update
    updated = SimulationRepository.update_scenario(db_session, scenario.id, {
        "name": "Updated Scenario Name",
        "description": "Updated Description"
    })
    assert updated.name == "Updated Scenario Name"

    # Clone
    cloned = SimulationRepository.clone_scenario(db_session, scenario.id, new_name="Cloned Test Scenario")
    assert cloned is not None
    assert cloned.id != scenario.id
    assert cloned.name == "Cloned Test Scenario"

    # Delete
    deleted = SimulationRepository.delete_scenario(db_session, scenario.id)
    assert deleted is True
    assert SimulationRepository.get_scenario(db_session, scenario.id) is None

def test_simulation_run_events_and_service_states(db_session):
    scenario = SimulationRepository.create_scenario(db_session, {
        "name": "Run Logging Test",
        "config": ScenarioConfigSchema().model_dump()
    })

    run = SimulationRepository.create_run(db_session, {
        "scenario_id": scenario.id,
        "status": "RUNNING",
        "random_seed": 42
    })
    assert run.id is not None

    # Record event
    event = SimulationRepository.record_event(
        db=db_session,
        run_id=run.id,
        step_number=1,
        event_type="FAILURE_INJECTION",
        service_id="srv-payment",
        event_data={"detail": "Injected outage"}
    )
    assert event.id is not None

    # Record service state
    st = SimulationRepository.record_service_state(
        db=db_session,
        run_id=run.id,
        step_number=1,
        service_id="srv-payment",
        health_status="CRITICAL",
        state_dict={"latency_ms": 3500.0, "error_rate": 80.0}
    )
    assert st.id is not None

    # Query events and states
    events = SimulationRepository.get_run_events(db_session, run.id)
    assert len(events) == 1
    assert events[0].event_type == "FAILURE_INJECTION"

    states = SimulationRepository.get_run_service_states(db_session, run.id)
    assert len(states) == 1
    assert states[0].health_status == "CRITICAL"
