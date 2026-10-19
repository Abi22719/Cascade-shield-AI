import pytest
from app.services.failure_model import FailureModel
from app.services.recovery_model import RecoveryModel
from app.services.simulation_state import SimulationState
from app.schemas.simulation_schema import (
    FailureInjectionConfig,
    RecoveryParameters,
    ScenarioConfigSchema
)

def test_recovery_immediate(db_session):
    state = SimulationState.initialize_from_db(db_session, "test-r1", ScenarioConfigSchema())
    svc = state.services["srv-payment"]
    base_latency = state.baseline_services["srv-payment"].latency_ms

    # Inject failure
    FailureModel.apply_initial_failure(
        svc,
        FailureInjectionConfig(
            target_service_ids=["srv-payment"],
            failure_type="high_latency",
            severity="severe"
        )
    )
    assert svc.health_status == "CRITICAL"

    params = RecoveryParameters(
        recovery_mode="immediate",
        recovery_step=2
    )

    # Step 1: before recovery step
    recovered, events = RecoveryModel.apply_recovery_step(
        state.services,
        state.baseline_services,
        params,
        current_step=1
    )
    assert len(recovered) == 0

    # Step 2: immediate recovery triggers
    recovered, events = RecoveryModel.apply_recovery_step(
        state.services,
        state.baseline_services,
        params,
        current_step=2
    )
    assert "srv-payment" in recovered
    assert svc.health_status == "RECOVERED"
    assert svc.latency_ms == base_latency
    assert any(e["event_type"] == "RECOVERY_COMPLETE" for e in events)

def test_recovery_gradual(db_session):
    state = SimulationState.initialize_from_db(db_session, "test-r2", ScenarioConfigSchema())
    svc = state.services["srv-order"]

    FailureModel.apply_initial_failure(
        svc,
        FailureInjectionConfig(
            target_service_ids=["srv-order"],
            failure_type="cpu_saturation",
            severity="severe"
        )
    )

    params = RecoveryParameters(
        recovery_mode="gradual",
        recovery_step=2,
        recovery_rate=0.5
    )

    # Step 2: gradual recovery starts
    recovered, events = RecoveryModel.apply_recovery_step(
        state.services,
        state.baseline_services,
        params,
        current_step=2
    )
    assert any(e["event_type"] == "RECOVERY_START" for e in events)
    assert svc.health_status in ["RECOVERING", "RECOVERED"]

def test_recovery_none(db_session):
    state = SimulationState.initialize_from_db(db_session, "test-r3", ScenarioConfigSchema())
    svc = state.services["srv-payment"]
    FailureModel.apply_initial_failure(
        svc,
        FailureInjectionConfig(
            target_service_ids=["srv-payment"],
            failure_type="service_unavailable",
            severity="severe"
        )
    )

    params = RecoveryParameters(recovery_mode="none")
    recovered, events = RecoveryModel.apply_recovery_step(
        state.services,
        state.baseline_services,
        params,
        current_step=3
    )
    assert len(recovered) == 0
    assert svc.health_status == "CRITICAL"
