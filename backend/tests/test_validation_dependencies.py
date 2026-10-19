import pytest
from app.services.validation_dependency import ValidationDependencyEngine

def test_downstream_dependency_recovery(db_session):
    # Suppose target srv-database recovered and all callers are healthy
    sim_healths = {
        "srv-database": "HEALTHY",
        "srv-payment": "HEALTHY",
        "srv-order": "HEALTHY",
        "srv-gateway": "HEALTHY",
        "srv-user": "HEALTHY",
        "srv-product": "HEALTHY",
        "srv-auth": "HEALTHY",
        "srv-notify": "HEALTHY",
        "srv-cache": "HEALTHY"
    }
    res = ValidationDependencyEngine.analyze_downstream_recovery(
        db=db_session,
        target_service_ids=["srv-database"],
        simulated_healths=sim_healths,
        baseline_healths={k: "HEALTHY" for k in sim_healths}
    )
    assert res["all_downstream_recovered"] is True
    assert len(res["still_unhealthy_callers"]) == 0
    assert len(res["newly_affected_services"]) == 0

def test_unhealthy_downstream_callers_detected(db_session):
    # srv-database is HEALTHY, but its caller srv-order remained DEGRADED
    sim_healths = {
        "srv-database": "HEALTHY",
        "srv-payment": "HEALTHY",
        "srv-order": "DEGRADED",
        "srv-gateway": "HEALTHY",
        "srv-user": "HEALTHY",
        "srv-product": "HEALTHY",
        "srv-auth": "HEALTHY",
        "srv-notify": "HEALTHY",
        "srv-cache": "HEALTHY"
    }
    res = ValidationDependencyEngine.analyze_downstream_recovery(
        db=db_session,
        target_service_ids=["srv-database"],
        simulated_healths=sim_healths,
        baseline_healths={k: "HEALTHY" for k in sim_healths}
    )
    assert res["all_downstream_recovered"] is False
    assert any(c["service_id"] == "srv-order" for c in res["still_unhealthy_callers"])
