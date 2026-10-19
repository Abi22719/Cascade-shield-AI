import pytest
from app.models import ServiceModel
from app.schemas.simulation_schema import ScenarioConfigSchema
from app.services.simulation_state import SimulationState

def test_simulation_state_initialization(db_session):
    config = ScenarioConfigSchema()
    state = SimulationState.initialize_from_db(
        db=db_session,
        scenario_id="scen-test-1",
        config=config,
        random_seed=42
    )
    assert len(state.services) > 0
    assert "srv-payment" in state.services
    assert "srv-order" in state.services

    # Verify G_dep and G_prop
    assert state.G_dep.has_node("srv-payment")
    assert state.G_prop.has_node("srv-payment")

    # Order depends on payment (caller -> callee in G_dep, callee -> caller in G_prop)
    if state.G_dep.has_edge("srv-order", "srv-payment"):
        assert state.G_prop.has_edge("srv-payment", "srv-order")

def test_simulation_state_isolation(db_session):
    config = ScenarioConfigSchema()
    state = SimulationState.initialize_from_db(
        db=db_session,
        scenario_id="scen-test-2",
        config=config
    )
    original_db_service = db_session.query(ServiceModel).filter_by(id="srv-payment").first()
    original_latency = original_db_service.latency_ms

    # Mutate simulation in-memory state
    sim_svc = state.services.get("srv-payment")
    assert sim_svc is not None
    sim_svc.latency_ms = 99999.0
    sim_svc.health_status = "CRITICAL"

    # Refresh DB session to verify DB was not touched
    db_session.expire_all()
    reloaded_db_service = db_session.query(ServiceModel).filter_by(id="srv-payment").first()

    assert reloaded_db_service.latency_ms == original_latency
    assert reloaded_db_service.health_status != "CRITICAL"

def test_simulation_state_step_snapshot(db_session):
    config = ScenarioConfigSchema()
    state = SimulationState.initialize_from_db(
        db=db_session,
        scenario_id="scen-test-3",
        config=config
    )
    state.current_step = 1
    state.record_step_snapshot(
        newly_impacted=["srv-order"],
        recovered_in_step=[],
        step_events=[{"event_type": "PROPAGATION_WAVE", "service_id": "srv-order"}]
    )
    assert len(state.step_history) == 1
    assert state.step_history[0].step_number == 1
    assert "srv-order" in state.step_history[0].newly_impacted
    assert len(state.all_events) == 1
