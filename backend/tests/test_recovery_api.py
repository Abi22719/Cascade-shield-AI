import pytest

def test_api_health(client):
    res = client.get("/api/recovery/health")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "healthy"
    assert data["module"] == "Module 7: Intelligent Recovery Planning and Risk Assessment"
    assert data["non_destructive"] is True

def test_api_options_and_config(client):
    res = client.get("/api/recovery/options")
    assert res.status_code == 200
    data = res.json()
    assert "action_types" in data
    assert "strategies" in data
    assert "services" in data

    # Config GET & PUT
    cfg_res = client.get("/api/recovery/config")
    assert cfg_res.status_code == 200
    cfg_data = cfg_res.json()
    assert "service_criticality_weight" in cfg_data

    cfg_data["service_criticality_weight"] = 0.30
    put_res = client.put("/api/recovery/config", json=cfg_data)
    assert put_res.status_code == 200
    assert put_res.json()["service_criticality_weight"] == 0.30

def test_api_plan_generation_and_crud(client):
    # Auto-generate plans
    gen_res = client.post("/api/recovery/plan", json={"target_service_id": "srv-payment"})
    assert gen_res.status_code == 200
    plans = gen_res.json()
    assert len(plans) == 4

    # Create custom plan
    payload = {
        "plan_name": "API Custom Recovery Plan",
        "strategy_type": "balanced",
        "actions": [
            {
                "action_type": "traffic_reroute",
                "target_service_id": "srv-payment",
                "action_order": 1,
                "estimated_duration": 1
            }
        ]
    }
    create_res = client.post("/api/recovery/plans", json=payload)
    assert create_res.status_code == 201
    plan_data = create_res.json()
    plan_id = plan_data["id"]

    # Get plan
    get_res = client.get(f"/api/recovery/plans/{plan_id}")
    assert get_res.status_code == 200
    assert get_res.json()["plan_name"] == "API Custom Recovery Plan"

    # List plans
    list_res = client.get("/api/recovery/plans")
    assert list_res.status_code == 200
    assert list_res.json()["total"] >= 1

    # Update plan
    upd_res = client.put(f"/api/recovery/plans/{plan_id}", json={"plan_name": "API Renamed Plan"})
    assert upd_res.status_code == 200
    assert upd_res.json()["plan_name"] == "API Renamed Plan"

    # Delete plan
    del_res = client.delete(f"/api/recovery/plans/{plan_id}")
    assert del_res.status_code == 200
    assert del_res.json()["deleted"] is True

def test_api_simulate_results_timeline_and_compare(client):
    # Generate 2 plans
    gen = client.post("/api/recovery/plan", json={"target_service_id": "srv-payment"}).json()
    plan1_id = gen[0]["id"]
    plan2_id = gen[1]["id"]

    # Simulate plan 1
    sim_res = client.post(f"/api/recovery/plans/{plan1_id}/simulate", json={"random_seed": 42})
    assert sim_res.status_code == 200
    assert sim_res.json()["outcome"] in ["SUCCESSFUL_RECOVERY", "PARTIAL_RECOVERY"]

    # Results
    res_res = client.get(f"/api/recovery/plans/{plan1_id}/results")
    assert res_res.status_code == 200
    assert "outcome" in res_res.json()

    # Timeline
    timeline_res = client.get(f"/api/recovery/plans/{plan1_id}/timeline")
    assert timeline_res.status_code == 200
    assert isinstance(timeline_res.json(), list)

    # Compare
    comp_res = client.post("/api/recovery/compare", json={"plan_ids": [plan1_id, plan2_id]})
    assert comp_res.status_code == 200
    comp_data = comp_res.json()
    assert len(comp_data["compared_plans"]) == 2
    assert comp_data["recommended_plan_id"] is not None

def test_api_evaluation(client):
    eval_res = client.get("/api/recovery/evaluation")
    assert eval_res.status_code == 200
    data = eval_res.json()
    assert data["benchmark_scenarios_count"] == 10
    assert len(data["strategies"]) == 4
