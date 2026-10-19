import pytest

def test_agent_health_endpoint(client):
    res = client.get("/api/agent/health")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "healthy"
    assert data["registered_actions"] == 12

def test_agent_actions_endpoint(client):
    res = client.get("/api/agent/actions")
    assert res.status_code == 200
    actions = res.json()
    assert len(actions) == 12

def test_agent_config_endpoint(client):
    # GET
    res = client.get("/api/agent/config")
    assert res.status_code == 200
    cfg = res.json()
    assert cfg["max_actions"] >= 1

    # PUT
    cfg["max_actions"] = 8
    put_res = client.put("/api/agent/config", json=cfg)
    assert put_res.status_code == 200
    assert put_res.json()["max_actions"] == 8

def test_agent_session_endpoints(client):
    # 1. Create Session
    create_res = client.post("/api/agent/sessions", json={"target_service_id": "srv-payment"})
    assert create_res.status_code == 201
    sess = create_res.json()
    sess_id = sess["id"]
    assert sess["target_service_id"] == "srv-payment"

    # 2. Step
    step_res = client.post(f"/api/agent/sessions/{sess_id}/step")
    assert step_res.status_code == 200
    assert step_res.json()["step_number"] == 1

    # 3. Recommendations
    rec_res = client.get(f"/api/agent/sessions/{sess_id}/recommendations")
    assert rec_res.status_code == 200
    assert isinstance(rec_res.json(), list)

    # 4. History
    hist_res = client.get(f"/api/agent/sessions/{sess_id}/history")
    assert hist_res.status_code == 200
    assert len(hist_res.json()) >= 1

    # 5. Run full
    run_res = client.post(f"/api/agent/sessions/{sess_id}/run", json={"max_steps": 3})
    assert run_res.status_code == 200

    # 6. Stop
    stop_res = client.post(f"/api/agent/sessions/{sess_id}/stop")
    assert stop_res.status_code == 200
    assert stop_res.json()["status"] == "STOPPED"

    # 7. List
    list_res = client.get("/api/agent/sessions")
    assert list_res.status_code == 200
    assert list_res.json()["total"] >= 1

    # 8. Delete
    del_res = client.delete(f"/api/agent/sessions/{sess_id}")
    assert del_res.status_code == 200

def test_agent_evaluation_endpoint(client):
    res = client.get("/api/agent/evaluation")
    assert res.status_code == 200
    data = res.json()
    assert data["benchmark_scenarios_count"] == 5
    assert data["adaptive_utility_agent"]["accuracy_top1"] == 1.0

def test_agent_compare_endpoint(client):
    res = client.post("/api/agent/compare", json={"target_service_id": "srv-payment"})
    assert res.status_code == 200
    data = res.json()
    assert len(data["comparisons"]) == 3
