import pytest
from app.schemas.simulation_schema import (
    ScenarioConfigSchema,
    FailureInjectionConfig,
    PropagationParameters,
    RecoveryParameters
)

def test_api_health(client):
    res = client.get("/api/simulation/health")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "healthy"
    assert data["module"] == "Module 6: What-If Scenario Simulation Engine"
    assert data["isolated_environment"] is True

def test_api_options(client):
    res = client.get("/api/simulation/options")
    assert res.status_code == 200
    data = res.json()
    assert "failure_types" in data
    assert "severities" in data
    assert "recovery_modes" in data
    assert "presets" in data

def test_api_scenario_lifecycle(client):
    cfg = ScenarioConfigSchema(
        failures=[
            FailureInjectionConfig(
                target_service_ids=["srv-payment"],
                failure_type="service_unavailable",
                severity="severe",
                start_step=1,
                duration_steps=3
            )
        ],
        propagation=PropagationParameters(max_steps=5),
        recovery=RecoveryParameters(recovery_mode="gradual", recovery_step=4)
    )

    payload = {
        "name": "API Payment Outage Scenario",
        "description": "Integration test scenario via API",
        "category": "failure_propagation",
        "config": cfg.model_dump(),
        "source_data_type": "digital_twin"
    }

    # 1. Create
    create_res = client.post("/api/simulation/scenarios", json=payload)
    assert create_res.status_code == 201
    sc_data = create_res.json()
    sc_id = sc_data["id"]
    assert sc_data["name"] == "API Payment Outage Scenario"

    # 2. Get
    get_res = client.get(f"/api/simulation/scenarios/{sc_id}")
    assert get_res.status_code == 200
    assert get_res.json()["id"] == sc_id

    # 3. List
    list_res = client.get("/api/simulation/scenarios")
    assert list_res.status_code == 200
    list_data = list_res.json()
    assert list_data["total"] >= 1
    assert any(s["id"] == sc_id for s in list_data["scenarios"])

    # 4. Update
    upd_res = client.put(f"/api/simulation/scenarios/{sc_id}", json={"name": "API Payment Outage Renamed"})
    assert upd_res.status_code == 200
    assert upd_res.json()["name"] == "API Payment Outage Renamed"

    # 5. Clone
    clone_res = client.post(f"/api/simulation/scenarios/{sc_id}/clone", params={"new_name": "API Cloned Scenario"})
    assert clone_res.status_code == 200
    cloned_id = clone_res.json()["id"]
    assert cloned_id != sc_id

    # 6. Delete cloned
    del_res = client.delete(f"/api/simulation/scenarios/{cloned_id}")
    assert del_res.status_code == 200
    assert del_res.json()["deleted"] is True

def test_api_run_timeline_metrics_impact_and_reset(client):
    cfg = ScenarioConfigSchema(
        failures=[
            FailureInjectionConfig(
                target_service_ids=["srv-database"],
                failure_type="database_starvation",
                severity="severe",
                start_step=1,
                duration_steps=4
            )
        ],
        propagation=PropagationParameters(max_steps=5),
        recovery=RecoveryParameters(recovery_mode="immediate", recovery_step=4)
    )

    create_res = client.post("/api/simulation/scenarios", json={
        "name": "Database API Test",
        "config": cfg.model_dump()
    })
    sc_id = create_res.json()["id"]

    # Run
    run_res = client.post(f"/api/simulation/scenarios/{sc_id}/run", json={"random_seed": 42})
    assert run_res.status_code == 200
    run_data = run_res.json()
    run_id = run_data["id"]
    assert run_data["status"] == "COMPLETED"
    assert len(run_data["timeline_steps"]) == 5

    # Get Run
    get_run = client.get(f"/api/simulation/runs/{run_id}")
    assert get_run.status_code == 200
    assert get_run.json()["id"] == run_id

    # Timeline
    timeline = client.get(f"/api/simulation/runs/{run_id}/timeline")
    assert timeline.status_code == 200
    assert isinstance(timeline.json(), list)

    # Metrics
    metrics = client.get(f"/api/simulation/runs/{run_id}/metrics")
    assert metrics.status_code == 200
    assert isinstance(metrics.json(), list)

    # Impact
    impact = client.get(f"/api/simulation/runs/{run_id}/impact")
    assert impact.status_code == 200
    assert "initial_failures" in impact.json()
    assert "total_impacted_count" in impact.json()

    # Reset
    reset = client.post(f"/api/simulation/scenarios/{sc_id}/reset")
    assert reset.status_code == 200
    assert reset.json()["reset"] is True

def test_api_compare_and_evaluation(client):
    cfg1 = ScenarioConfigSchema(
        failures=[FailureInjectionConfig(target_service_ids=["srv-payment"], failure_type="high_latency", severity="severe")],
        propagation=PropagationParameters(max_steps=3),
        recovery=RecoveryParameters(recovery_mode="immediate", recovery_step=2)
    )
    sc1 = client.post("/api/simulation/scenarios", json={"name": "Comp 1", "config": cfg1.model_dump()}).json()
    run1 = client.post(f"/api/simulation/scenarios/{sc1['id']}/run", json={}).json()

    cfg2 = ScenarioConfigSchema(
        failures=[FailureInjectionConfig(target_service_ids=["srv-auth"], failure_type="cpu_saturation", severity="moderate")],
        propagation=PropagationParameters(max_steps=3),
        recovery=RecoveryParameters(recovery_mode="immediate", recovery_step=2)
    )
    sc2 = client.post("/api/simulation/scenarios", json={"name": "Comp 2", "config": cfg2.model_dump()}).json()
    run2 = client.post(f"/api/simulation/scenarios/{sc2['id']}/run", json={}).json()

    # Compare
    compare_res = client.post("/api/simulation/compare", json={"run_ids": [run1["id"], run2["id"]]})
    assert compare_res.status_code == 200
    comp_data = compare_res.json()
    assert len(comp_data["comparisons"]) == 2
    assert "summary_insights" in comp_data

    # Evaluation
    eval_res = client.get("/api/simulation/evaluation")
    assert eval_res.status_code == 200
    eval_data = eval_res.json()
    assert "baseline_static_traversal" in eval_data
    assert "baseline_cascade_mod3" in eval_data
    assert "timestep_simulator_mod6" in eval_data
