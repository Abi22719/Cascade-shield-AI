import pytest
from fastapi.testclient import TestClient

def test_workflow_lifecycle_api(client: TestClient):
    res = client.get("/api/workflow/incidents/default-incident?service_id=srv-payment")
    assert res.status_code == 200
    data = res.json()
    assert "incident_id" in data
    assert "service_id" in data
    assert "steps" in data
    assert len(data["steps"]) == 10
    assert 1 <= data["current_step"] <= 10

    # Step verification
    step_names = [s["step_name"] for s in data["steps"]]
    assert any("Alert" in name for name in step_names)
    assert any("Root Cause" in name for name in step_names)
    assert any("Recovery" in name for name in step_names)

def test_workflow_timeline_and_summary_api(client: TestClient):
    # Timeline
    tl_res = client.get("/api/workflow/incidents/default-incident/timeline")
    assert tl_res.status_code == 200
    tl_data = tl_res.json()
    assert "steps" in tl_data
    assert len(tl_data["steps"]) == 10

    # Summary
    sum_res = client.get("/api/workflow/incidents/default-incident/summary")
    assert sum_res.status_code == 200
    sum_data = sum_res.json()
    assert "recommendations" in sum_data
    assert isinstance(sum_data["recommendations"], list)
