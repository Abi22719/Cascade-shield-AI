import pytest

def test_rca_health_endpoint(client):
    res = client.get("/api/rca/health")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "healthy"
    assert "Module 4" in data["module"]
    assert "connected_source_modules" in data
    assert data["connected_source_modules"]["module_1_digital_twin"]["available"] is True

def test_rca_analyze_and_sub_endpoints(client):
    payload = {
        "incident_title": "API Test Incident",
        "target_service_id": "srv-payment",
        "affected_service_ids": ["srv-order", "srv-payment"],
        "include_alternatives": True,
        "include_recommendations": True
    }
    # 1. Analyze
    res = client.post("/api/rca/analyze", json=payload)
    assert res.status_code == 200
    report = res.json()
    inc_id = report["incident_id"]
    assert report["title"] == "API Test Incident"
    assert len(report["ranked_candidates"]) >= 1

    # 2. Get incident by ID
    get_res = client.get(f"/api/rca/incidents/{inc_id}")
    assert get_res.status_code == 200
    assert get_res.json()["incident_id"] == inc_id

    # 3. List incidents
    list_res = client.get("/api/rca/incidents")
    assert list_res.status_code == 200
    assert list_res.json()["total"] >= 1

    # 4. Get evidence
    ev_res = client.get(f"/api/rca/incidents/{inc_id}/evidence")
    assert ev_res.status_code == 200
    assert isinstance(ev_res.json(), list)

    # 5. Get candidates
    cand_res = client.get(f"/api/rca/incidents/{inc_id}/candidates")
    assert cand_res.status_code == 200
    assert len(cand_res.json()) >= 1

    # 6. Get timeline
    time_res = client.get(f"/api/rca/incidents/{inc_id}/timeline")
    assert time_res.status_code == 200

    # 7. Get recommendations
    rec_res = client.get(f"/api/rca/incidents/{inc_id}/recommendations")
    assert rec_res.status_code == 200
    assert len(rec_res.json()) >= 1

    # 8. Reanalyze
    re_res = client.post(f"/api/rca/incidents/{inc_id}/reanalyze")
    assert re_res.status_code == 200

    # 9. Delete
    del_res = client.delete(f"/api/rca/incidents/{inc_id}")
    assert del_res.status_code == 200

def test_rca_evaluation_endpoint(client):
    res = client.get("/api/rca/evaluation")
    assert res.status_code == 200
    data = res.json()
    assert data["benchmark_scenarios_count"] == 5
    assert "evidence_grounded_rca" in data
    assert data["evidence_grounded_rca"]["top_1_accuracy"] >= 0.8

def test_rca_compare_endpoint(client):
    payload = {
        "custom_requests": [
            {
                "incident_title": "Incident A",
                "target_service_id": "srv-payment",
                "affected_service_ids": ["srv-order"]
            },
            {
                "incident_title": "Incident B",
                "target_service_id": "srv-auth",
                "affected_service_ids": ["srv-user"]
            }
        ]
    }
    res = client.post("/api/rca/compare", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data["compared_count"] == 2
    assert len(data["comparisons"]) == 2
