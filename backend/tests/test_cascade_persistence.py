import pytest
from app.database.cascade_repository import CascadeRepository

def test_cascade_scenario_lifecycle(db_session):
    # 1. Create
    scenario = CascadeRepository.create_scenario(
        db=db_session,
        scenario_name="Test Payment Cascade",
        initial_service_id="srv-payment",
        failure_type="service_unavailable",
        failure_severity="severe",
        input_parameters={"propagation_steps": 4, "attenuation_factor": 0.8},
        result_summary={"total_impacted_services": 3, "high_risk_count": 2, "max_risk_score": 95.0}
    )

    assert scenario.id.startswith("scen-")
    assert scenario.scenario_name == "Test Payment Cascade"
    assert scenario.initial_service_id == "srv-payment"

    # 2. Get by ID
    fetched = CascadeRepository.get_scenario_by_id(db_session, scenario.id)
    assert fetched is not None
    assert fetched.scenario_name == "Test Payment Cascade"

    # 3. List
    scenarios, total = CascadeRepository.list_scenarios(db_session, page=1, limit=10)
    assert total >= 1
    assert any(s.id == scenario.id for s in scenarios)

    # 4. Get Latest
    latest = CascadeRepository.get_latest_scenario(db_session)
    assert latest is not None
    assert latest.id == scenario.id

    # 5. Delete
    deleted = CascadeRepository.delete_scenario(db_session, scenario.id)
    assert deleted is True

    # Confirm deletion
    not_found = CascadeRepository.get_scenario_by_id(db_session, scenario.id)
    assert not_found is None

def test_cascade_scenario_api_crud(client):
    payload = {
        "scenario_name": "API Test Scenario",
        "initial_service_id": "srv-order",
        "failure_type": "latency_spike",
        "failure_severity": "moderate",
        "input_parameters": {"propagation_steps": 3},
        "result_summary": {"total_impacted_services": 2}
    }
    # Create
    create_res = client.post("/api/cascade/scenarios", json=payload)
    assert create_res.status_code == 201
    created_data = create_res.json()
    scen_id = created_data["id"]
    assert created_data["scenario_name"] == "API Test Scenario"

    # Get by ID
    get_res = client.get(f"/api/cascade/scenarios/{scen_id}")
    assert get_res.status_code == 200
    assert get_res.json()["id"] == scen_id

    # List
    list_res = client.get("/api/cascade/scenarios")
    assert list_res.status_code == 200
    assert list_res.json()["total"] >= 1

    # Delete
    del_res = client.delete(f"/api/cascade/scenarios/{scen_id}")
    assert del_res.status_code == 200

    # Verify 404 on deleted
    get_del_res = client.get(f"/api/cascade/scenarios/{scen_id}")
    assert get_del_res.status_code == 404
