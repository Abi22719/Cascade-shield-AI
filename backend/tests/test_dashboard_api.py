import pytest
from fastapi.testclient import TestClient

def test_dashboard_summary_api(client: TestClient):
    res = client.get("/api/dashboard/summary")
    assert res.status_code == 200
    data = res.json()
    assert "total_services" in data
    assert "healthy_services" in data
    assert "active_anomalies" in data
    assert "high_risk_predictions" in data
    assert "open_incidents" in data
    assert "recovery_plans_pending" in data
    assert data["simulation_mode"] is True

def test_dashboard_health_api(client: TestClient):
    res = client.get("/api/dashboard/health")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "operational"
    assert data["simulation_mode"] is True
    assert data["version"] == "10.0.0"
    assert "module_10" in data["modules"]
    assert data["modules"]["module_10"] == "OPERATIONAL"

def test_dashboard_activity_api(client: TestClient):
    res = client.get("/api/dashboard/activity?limit=10")
    assert res.status_code == 200
    data = res.json()
    assert isinstance(data, list)
    if len(data) > 0:
        first = data[0]
        assert "event_type" in first
        assert "source_module" in first
        assert "description" in first

def test_dashboard_insights_api(client: TestClient):
    res = client.get("/api/dashboard/insights?limit=5")
    assert res.status_code == 200
    insights = res.json()
    assert isinstance(insights, list)
    for ins in insights:
        assert "id" in ins
        assert "title" in ins
        assert "summary" in ins
        assert "source_module" in ins
        assert "data_source" in ins
        assert "uncertainty_notes" in ins
        assert "recommended_next_step" in ins
