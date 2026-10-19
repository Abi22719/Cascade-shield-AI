import pytest
from app.services.failure_model import FailureModel
from app.services.simulation_state import SimulationState
from app.schemas.simulation_schema import FailureInjectionConfig, ScenarioConfigSchema

def test_failure_injection_service_unavailable(db_session):
    state = SimulationState.initialize_from_db(db_session, "test-f1", ScenarioConfigSchema())
    svc = state.services["srv-payment"]
    config = FailureInjectionConfig(
        target_service_ids=["srv-payment"],
        failure_type="service_unavailable",
        severity="severe",
        start_step=1,
        duration_steps=3
    )

    res = FailureModel.apply_initial_failure(svc, config)
    assert svc.health_status == "CRITICAL"
    assert svc.is_initial_failure is True
    assert svc.is_impacted is True
    assert svc.error_rate >= 90.0
    assert svc.risk_score >= 90.0
    assert res["service_id"] == "srv-payment"

def test_failure_injection_high_latency(db_session):
    state = SimulationState.initialize_from_db(db_session, "test-f2", ScenarioConfigSchema())
    svc = state.services["srv-payment"]
    orig_latency = svc.latency_ms
    config = FailureInjectionConfig(
        target_service_ids=["srv-payment"],
        failure_type="high_latency",
        severity="moderate",
        start_step=1,
        duration_steps=2
    )

    FailureModel.apply_initial_failure(svc, config)
    assert svc.latency_ms > orig_latency
    assert svc.health_status in ["DEGRADED", "CRITICAL"]

def test_failure_injection_cpu_saturation(db_session):
    state = SimulationState.initialize_from_db(db_session, "test-f3", ScenarioConfigSchema())
    svc = state.services["srv-order"]
    config = FailureInjectionConfig(
        target_service_ids=["srv-order"],
        failure_type="cpu_saturation",
        severity="severe",
        start_step=1,
        duration_steps=2
    )

    FailureModel.apply_initial_failure(svc, config)
    assert svc.cpu_usage >= 90.0

def test_failure_injection_database_starvation(db_session):
    state = SimulationState.initialize_from_db(db_session, "test-f4", ScenarioConfigSchema())
    svc = state.services["srv-database"]
    config = FailureInjectionConfig(
        target_service_ids=["srv-database"],
        failure_type="database_starvation",
        severity="severe",
        start_step=1,
        duration_steps=4
    )

    FailureModel.apply_initial_failure(svc, config)
    assert svc.health_status == "CRITICAL"
    assert svc.risk_score >= 85.0

def test_failure_injection_custom_overrides(db_session):
    state = SimulationState.initialize_from_db(db_session, "test-f5", ScenarioConfigSchema())
    svc = state.services["srv-auth"]
    config = FailureInjectionConfig(
        target_service_ids=["srv-auth"],
        failure_type="error_rate_surge",
        severity="moderate",
        custom_metric_overrides={"error_rate": 42.5, "latency_ms": 1337.0}
    )

    FailureModel.apply_initial_failure(svc, config)
    assert svc.error_rate == 42.5
    assert svc.latency_ms == 1337.0
