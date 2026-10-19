import pytest
from fastapi.testclient import TestClient

def test_api_benchmark_health(client: TestClient):
    res = client.get("/api/benchmark/health")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "healthy"
    assert "Module 9" in data["module"]
    assert data["version"] == "9.0.0"

def test_api_benchmark_config(client: TestClient):
    res = client.get("/api/benchmark/config")
    assert res.status_code == 200
    config = res.json()
    assert "timeout_seconds" in config
    assert "component_weights" in config

    # Update config
    update_res = client.put("/api/benchmark/config", json={"timeout_seconds": 120})
    assert update_res.status_code == 200
    assert update_res.json()["timeout_seconds"] == 120

def test_api_benchmark_datasets_and_scenarios(client: TestClient):
    # Datasets
    res = client.get("/api/benchmark/datasets")
    assert res.status_code == 200
    data = res.json()
    assert data["total"] >= 1
    ds_id = data["items"][0]["id"]

    # Single dataset
    ds_res = client.get(f"/api/benchmark/datasets/{ds_id}")
    assert ds_res.status_code == 200
    assert ds_res.json()["id"] == ds_id

    # Scenarios list
    scn_res = client.get(f"/api/benchmark/scenarios?dataset_id={ds_id}")
    assert scn_res.status_code == 200
    scenarios = scn_res.json()
    assert len(scenarios) == 10
    first_scn_id = scenarios[0]["id"]

    # Single scenario
    single_scn = client.get(f"/api/benchmark/scenarios/{first_scn_id}")
    assert single_scn.status_code == 200
    assert single_scn.json()["id"] == first_scn_id

def test_api_benchmark_baselines(client: TestClient):
    res = client.get("/api/benchmark/baselines")
    assert res.status_code == 200
    data = res.json()
    assert "module_2" in data
    assert "module_8" in data

def test_api_benchmark_experiments_lifecycle(client: TestClient):
    # Create and run experiment
    payload = {
        "name": "Integration API Benchmark",
        "description": "API Test",
        "selected_modules": ["module_2", "module_3", "module_4"],
        "random_seed": 42
    }
    create_res = client.post("/api/benchmark/experiments?auto_run=true", json=payload)
    assert create_res.status_code == 200
    exp = create_res.json()
    assert exp["status"] == "COMPLETED"
    assert exp["overall_resilience_score"] is not None
    exp_id = exp["id"]

    # Progress
    prog_res = client.get(f"/api/benchmark/experiments/{exp_id}/progress")
    assert prog_res.status_code == 200
    assert prog_res.json()["progress"] == 100.0

    # Results
    res_list = client.get(f"/api/benchmark/experiments/{exp_id}/results")
    assert res_list.status_code == 200
    assert len(res_list.json()) > 0

    # Reports
    rep_res = client.get(f"/api/benchmark/reports/{exp_id}?format=markdown")
    assert rep_res.status_code == 200
    assert "CascadeShield AI" in rep_res.text

    # JSON Export
    export_json = client.get(f"/api/benchmark/export/{exp_id}/json")
    assert export_json.status_code == 200
    assert export_json.json()["experiment_id"] == exp_id

    # CSV Export
    export_csv = client.get(f"/api/benchmark/export/{exp_id}/csv")
    assert export_csv.status_code == 200
    assert "Experiment ID" in export_csv.text

def test_api_benchmark_summary_and_compare(client: TestClient):
    # Create an experiment first
    payload = {
        "name": "Summary Compare Test Experiment",
        "selected_modules": ["module_2"],
        "random_seed": 42
    }
    exp_res = client.post("/api/benchmark/experiments?auto_run=true", json=payload)
    assert exp_res.status_code == 200
    exp_id = exp_res.json()["id"]

    # Summary
    sum_res = client.get("/api/benchmark/summary")
    assert sum_res.status_code == 200
    data = sum_res.json()
    assert data["total_experiments"] >= 1
    assert data["average_resilience_score"] >= 0.0

    # Compare
    comp_res = client.post("/api/benchmark/compare", json={"experiment_ids": [exp_id]})
    # Min length for compare is 2, so 1 returns 422
    assert comp_res.status_code in [200, 422]
