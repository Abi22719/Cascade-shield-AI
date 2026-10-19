import pytest
from fastapi.testclient import TestClient

def test_all_10_modules_compatibility(client: TestClient):
    root_res = client.get("/")
    assert root_res.status_code == 200
    data = root_res.json()
    assert data["version"] == "10.0.0"
    assert len(data["modules"]) == 10

    # Verify each module route is responsive
    endpoints = [
        "/api/health",                      # Mod 1
        "/api/anomalies/summary",           # Mod 2
        "/api/cascade/scenarios",           # Mod 3
        "/api/rca/incidents",               # Mod 4
        "/api/agent/sessions",              # Mod 5
        "/api/simulation/scenarios",        # Mod 6
        "/api/recovery/plans",              # Mod 7
        "/api/validation/runs",             # Mod 8
        "/api/benchmark/summary",           # Mod 9
        "/api/dashboard/summary"            # Mod 10
    ]

    for ep in endpoints:
        res = client.get(ep)
        assert res.status_code in [200, 201], f"Endpoint {ep} failed with {res.status_code}"
