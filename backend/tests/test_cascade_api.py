import pytest

def test_cascade_health_endpoint(client):
    res = client.get("/api/cascade/health")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "healthy"
    assert "Module 3" in data["module"]
    assert len(data["capabilities"]) > 0

def test_cascade_summary_endpoint(client):
    res = client.get("/api/cascade/summary")
    assert res.status_code == 200
    data = res.json()
    assert "total_services" in data
    assert "total_dependencies" in data
    assert data["total_services"] >= 9

def test_predict_endpoint_valid(client):
    payload = {
        "initial_service_id": "srv-payment",
        "failure_type": "latency_spike",
        "failure_severity": "severe",
        "propagation_steps": 4,
        "attenuation_factor": 0.8
    }
    res = client.post("/api/cascade/predict", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data["initial_service_id"] == "srv-payment"
    assert data["failure_type"] == "latency_spike"
    assert len(data["impacted_services"]) >= 2
    assert len(data["simulation_timeline"]) >= 4

def test_predict_endpoint_invalid_service(client):
    payload = {
        "initial_service_id": "invalid-id",
        "failure_type": "service_unavailable",
        "failure_severity": "mild"
    }
    res = client.post("/api/cascade/predict", json=payload)
    assert res.status_code == 404

def test_simulate_endpoint(client):
    payload = {
        "initial_service_id": "srv-database",
        "failure_type": "cpu_exhaustion",
        "failure_severity": "moderate",
        "propagation_steps": 3,
        "attenuation_factor": 0.7
    }
    res = client.post("/api/cascade/simulate", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data["initial_service_id"] == "srv-database"
    assert len(data["simulation_timeline"]) >= 3

def test_impact_and_paths_endpoints(client):
    res_impact = client.get("/api/cascade/impact/srv-payment")
    assert res_impact.status_code == 200
    impact_data = res_impact.json()
    assert impact_data["root_service_id"] == "srv-payment"
    assert "direct_services" in impact_data

    res_paths = client.get("/api/cascade/paths/srv-payment")
    assert res_paths.status_code == 200
    paths_data = res_paths.json()
    assert isinstance(paths_data, list)
    assert len(paths_data) >= 1

def test_cascade_evaluation_endpoint(client):
    res = client.get("/api/cascade/evaluation")
    assert res.status_code == 200
    data = res.json()
    assert data["benchmark_scenario_count"] == 5
    assert "baseline_simple_traversal" in data
    assert "static_rule_scoring" in data
    assert "evidence_aware_cascade" in data
    assert data["evidence_aware_cascade"]["f1_score"] >= 0.7

def test_compare_scenarios_endpoint(client):
    payload = {
        "custom_scenarios": [
            {
                "initial_service_id": "srv-payment",
                "failure_type": "service_unavailable",
                "failure_severity": "severe"
            },
            {
                "initial_service_id": "srv-auth",
                "failure_type": "latency_spike",
                "failure_severity": "mild"
            }
        ]
    }
    res = client.post("/api/cascade/compare", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data["compared_count"] == 2
    assert len(data["scenarios"]) == 2
    assert "highest_blast_radius" in data
