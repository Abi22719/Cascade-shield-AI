import pytest
from app.services.failure_model import FailureModel
from app.services.propagation_model import PropagationModel
from app.services.simulation_state import SimulationState
from app.schemas.simulation_schema import FailureInjectionConfig, PropagationParameters, ScenarioConfigSchema

def test_propagation_step_callee_to_caller(db_session):
    state = SimulationState.initialize_from_db(db_session, "test-p1", ScenarioConfigSchema())
    
    # 1. Inject failure into payment
    config = FailureInjectionConfig(
        target_service_ids=["srv-payment"],
        failure_type="service_unavailable",
        severity="severe"
    )
    FailureModel.apply_initial_failure(state.services["srv-payment"], config)
    active_failing = {"srv-payment"}

    # 2. Propagate
    params = PropagationParameters(
        max_steps=5,
        attenuation_factor=0.85,
        propagation_threshold=20.0
    )
    newly_impacted, events = PropagationModel.propagate_step(
        G_prop=state.G_prop,
        services=state.services,
        active_failing_services=active_failing,
        params=params,
        current_step=1
    )

    # Order service directly depends on payment, so in reverse propagation graph G_prop: payment -> order
    assert len(events) >= 1
    assert "srv-order" in newly_impacted
    order_svc = state.services["srv-order"]
    assert order_svc.is_impacted is True
    assert order_svc.risk_score >= params.propagation_threshold

def test_propagation_high_threshold_blocking(db_session):
    state = SimulationState.initialize_from_db(db_session, "test-p2", ScenarioConfigSchema())
    
    config = FailureInjectionConfig(
        target_service_ids=["srv-auth"],
        failure_type="high_latency",
        severity="mild"
    )
    FailureModel.apply_initial_failure(state.services["srv-auth"], config)
    active_failing = {"srv-auth"}

    # Extremely high threshold means mild failure will not cause state transition
    params = PropagationParameters(
        max_steps=5,
        attenuation_factor=0.2,
        propagation_threshold=95.0
    )
    newly_impacted, events = PropagationModel.propagate_step(
        G_prop=state.G_prop,
        services=state.services,
        active_failing_services=active_failing,
        params=params,
        current_step=1
    )

    assert len(newly_impacted) == 0
