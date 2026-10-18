import pytest
from fastapi import HTTPException
from app.services.cascade_predictor import CascadePredictor
from app.schemas.cascade_schema import CascadePredictRequest

def test_predict_cascade_with_real_db(db_session):
    """
    Test cascade prediction on seeded database (e.g., srv-payment failure).
    Payment Service has callers: Order Service -> API Gateway.
    """
    req = CascadePredictRequest(
        initial_service_id="srv-payment",
        failure_type="service_unavailable",
        failure_severity="severe",
        propagation_steps=4,
        attenuation_factor=0.75
    )

    response = CascadePredictor.predict_cascade(db_session, req)

    assert response.initial_service_id == "srv-payment"
    assert response.failure_severity == "severe"
    assert response.total_services_analyzed >= 9
    assert response.total_impacted_services >= 2

    # Check impacted services list
    impacted_ids = [s.service_id for s in response.impacted_services]
    assert "srv-payment" in impacted_ids  # Root failure
    assert "srv-order" in impacted_ids    # Direct dependent caller
    assert "srv-gateway" in impacted_ids  # Indirect dependent caller (Order -> Gateway)

    # Validate simulation timeline
    assert len(response.simulation_timeline) >= 4
    assert response.simulation_timeline[0].step == 0

    # Validate recommendations
    assert len(response.recommendations) >= 2

def test_predict_cascade_nonexistent_service(db_session):
    req = CascadePredictRequest(
        initial_service_id="srv-nonexistent-999",
        failure_type="latency_spike",
        failure_severity="moderate"
    )

    with pytest.raises(HTTPException) as exc_info:
        CascadePredictor.predict_cascade(db_session, req)
    assert exc_info.value.status_code == 404

def test_get_impact_and_paths(db_session):
    impact = CascadePredictor.get_impact_for_service(db_session, "srv-payment", max_hops=4)
    assert impact["root_service_id"] == "srv-payment"
    assert impact["direct_impact_count"] >= 1
    assert impact["total_impacted_count"] >= 2

    paths = CascadePredictor.get_paths_for_service(db_session, "srv-payment", max_hops=4)
    assert len(paths) >= 1
    # Check that paths lead to callers
    assert any("srv-order" in p.path for p in paths)

def test_get_summary(db_session):
    summary = CascadePredictor.get_summary(db_session)
    assert summary.total_services >= 9
    assert summary.total_dependencies >= 8
    assert summary.last_simulation_status is not None
