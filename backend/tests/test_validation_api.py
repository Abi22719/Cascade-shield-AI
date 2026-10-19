import pytest

def test_api_validation_health(client):
    resp = client.get("/api/validation/health")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "healthy"
    assert "service_health_validation" in data["capabilities"]

def test_api_validation_config(client):
    resp = client.get("/api/validation/config")
    assert resp.status_code == 200
    data = resp.json()
    assert "max_acceptable_latency_ms" in data

    # Update config
    update_resp = client.put("/api/validation/config", json={"max_acceptable_latency_ms": 450.0})
    assert update_resp.status_code == 200
    assert update_resp.json()["max_acceptable_latency_ms"] == 450.0

    # Reset
    client.put("/api/validation/config", json={"max_acceptable_latency_ms": 500.0})

def test_api_validation_rules(client):
    resp = client.get("/api/validation/rules")
    assert resp.status_code == 200
    assert "rules" in resp.json()

def test_api_run_validation_and_endpoints(client):
    # Auto-generate a recovery plan first using Module 7 endpoint
    plan_resp = client.post("/api/recovery/plan", json={"target_service_id": "srv-payment"})
    assert plan_resp.status_code == 200
    plans = plan_resp.json()
    assert len(plans) > 0
    plan_id = plans[0]["id"]

    # POST /api/validation/run
    run_resp = client.post("/api/validation/run", json={
        "recovery_plan_id": plan_id,
        "verification_window_steps": 3,
        "force_rerun": True
    })
    assert run_resp.status_code == 201
    val_data = run_resp.json()
    val_id = val_data["id"]
    assert val_id is not None
    assert val_data["total_checks"] > 0

    # GET /api/validation/runs
    list_resp = client.get("/api/validation/runs")
    assert list_resp.status_code == 200
    assert list_resp.json()["total"] >= 1

    # GET /api/validation/runs/{id}
    detail_resp = client.get(f"/api/validation/runs/{val_id}")
    assert detail_resp.status_code == 200
    assert detail_resp.json()["id"] == val_id

    # GET /api/validation/runs/{id}/checks
    checks_resp = client.get(f"/api/validation/runs/{val_id}/checks")
    assert checks_resp.status_code == 200
    assert len(checks_resp.json()) > 0

    # GET /api/validation/runs/{id}/evidence
    ev_resp = client.get(f"/api/validation/runs/{val_id}/evidence")
    assert ev_resp.status_code == 200
    assert len(ev_resp.json()) > 0

    # GET /api/validation/runs/{id}/timeline
    tl_resp = client.get(f"/api/validation/runs/{val_id}/timeline")
    assert tl_resp.status_code == 200
    assert "timeline" in tl_resp.json()

    # GET /api/validation/runs/{id}/comparison
    comp_resp = client.get(f"/api/validation/runs/{val_id}/comparison")
    assert comp_resp.status_code == 200
    assert "healthy_count_after" in comp_resp.json()

    # GET /api/validation/runs/{id}/recommendations
    recs_resp = client.get(f"/api/validation/runs/{val_id}/recommendations")
    assert recs_resp.status_code == 200

def test_api_validation_evaluation(client):
    resp = client.get("/api/validation/evaluation")
    assert resp.status_code == 200
    data = resp.json()
    assert data["archetypes_evaluated"] == 10
    assert "full_validation" in data["accuracy_by_validation_mode"]

def test_api_validation_compare(client):
    # Auto-generate a recovery plan first
    plan_resp = client.post("/api/recovery/plan", json={"target_service_id": "srv-payment"})
    assert plan_resp.status_code == 200
    plans = plan_resp.json()
    plan_id = plans[0]["id"]

    # Create two runs
    r1_resp = client.post("/api/validation/run", json={"recovery_plan_id": plan_id, "force_rerun": True})
    assert r1_resp.status_code == 201
    r1 = r1_resp.json()

    r2_resp = client.post("/api/validation/run", json={"recovery_plan_id": plan_id, "force_rerun": True})
    assert r2_resp.status_code == 201
    r2 = r2_resp.json()

    comp_resp = client.post("/api/validation/compare", json={"validation_ids": [r1["id"], r2["id"]]})
    assert comp_resp.status_code == 200
    data = comp_resp.json()
    assert len(data["validations"]) == 2
    assert data["best_validation_id"] is not None
