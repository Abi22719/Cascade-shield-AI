import pytest
from app.services.diagnostic_executor import DiagnosticExecutor
from app.models.service import ServiceModel

def test_executor_unregistered_action(db_session):
    res = DiagnosticExecutor.execute_action("fake_action_123", {"service_id": "srv-payment"}, db_session)
    assert res["execution_status"] == "FAILED"
    assert "not registered" in res["result_summary"]

def test_executor_missing_parameters(db_session):
    res = DiagnosticExecutor.execute_action("inspect_service_health", {}, db_session)
    assert res["execution_status"] == "FAILED"
    assert "Missing required parameters" in res["result_summary"]

def test_executor_inspect_service_health(db_session):
    res = DiagnosticExecutor.execute_action("inspect_service_health", {"service_id": "srv-payment"}, db_session)
    assert res["execution_status"] == "SUCCESS"
    assert res["duration_ms"] >= 0.0
    assert "srv-payment" in res["result_summary"]
    raw = res["raw_result"]
    assert raw["service_id"] == "srv-payment"
    assert "status" in raw

def test_executor_inspect_dependency(db_session):
    res = DiagnosticExecutor.execute_action("inspect_dependency", {"service_id": "srv-order"}, db_session)
    assert res["execution_status"] == "SUCCESS"
    raw = res["raw_result"]
    assert "callers" in raw
    assert "dependencies" in raw

def test_executor_compare_timestamps(db_session):
    res = DiagnosticExecutor.execute_action(
        "compare_timestamps", 
        {"service_id": "srv-payment", "comparator_service_id": "srv-order"}, 
        db_session
    )
    assert res["execution_status"] == "SUCCESS"
    raw = res["raw_result"]
    assert "delta_seconds" in raw
    assert "conclusion" in raw

def test_executor_read_only_guarantee(db_session):
    # Verify srv-payment is unchanged after multiple diagnostics
    srv_before = db_session.query(ServiceModel).filter(ServiceModel.id == "srv-payment").first()
    before_status = srv_before.health_status
    before_err = srv_before.error_rate

    DiagnosticExecutor.execute_action("inspect_service_health", {"service_id": "srv-payment"}, db_session)
    DiagnosticExecutor.execute_action("retrieve_anomaly_alerts", {"service_id": "srv-payment"}, db_session)
    DiagnosticExecutor.execute_action("trace_failure_paths", {"service_id": "srv-payment"}, db_session)

    srv_after = db_session.query(ServiceModel).filter(ServiceModel.id == "srv-payment").first()
    assert srv_after.health_status == before_status
    assert srv_after.error_rate == before_err
