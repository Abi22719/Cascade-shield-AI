import pytest
from fastapi.testclient import TestClient

def test_global_search_empty_query(client: TestClient):
    res = client.get("/api/search?q=")
    assert res.status_code == 200
    data = res.json()
    assert "total_results" in data
    assert isinstance(data["results"], list)

def test_global_search_query_service(client: TestClient):
    res = client.get("/api/search?q=payment")
    assert res.status_code == 200
    data = res.json()
    assert "results" in data
    # At least payment service or alert should match
    matching = [r for r in data["results"] if "payment" in r["title"].lower() or "payment" in r["record_id"].lower()]
    assert len(matching) > 0
    first = matching[0]
    assert first["record_type"] in ["service", "alert", "incident", "scenario", "plan", "validation", "benchmark"]
    assert first["url_path"].startswith("/?")

def test_global_search_module_filter(client: TestClient):
    res = client.get("/api/search?q=srv&module=module_1")
    assert res.status_code == 200
    data = res.json()
    for item in data["results"]:
        assert item["source_module"] == "module_1"

def test_search_suggestions_api(client: TestClient):
    res = client.get("/api/search/suggestions")
    assert res.status_code == 200
    data = res.json()
    assert "suggestions" in data
    assert isinstance(data["suggestions"], list)
    assert len(data["suggestions"]) > 0
