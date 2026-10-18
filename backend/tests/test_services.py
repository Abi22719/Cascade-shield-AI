import pytest

def test_default_services_initialized(client):
    """Verify default 9 services are initialized on startup."""
    res = client.get("/api/services")
    assert res.status_code == 200
    services = res.json()
    assert len(services) == 9

    names = [s["name"] for s in services]
    assert "API Gateway" in names
    assert "Authentication Service" in names
    assert "User Service" in names
    assert "Product Service" in names
    assert "Order Service" in names
    assert "Payment Service" in names
    assert "Notification Service" in names
    assert "Database Service" in names
    assert "Cache Service" in names

def test_get_service_detail(client):
    """Verify service detail returns incoming and outgoing dependencies."""
    res = client.get("/api/services/srv-gateway")
    assert res.status_code == 200
    data = res.json()
    assert data["id"] == "srv-gateway"
    assert data["name"] == "API Gateway"
    assert data["out_degree"] >= 3  # Gateway connects to auth, product, order
    assert len(data["outgoing_dependencies"]) >= 3
    assert "health_reasons" in data

def test_filter_services_by_type_and_status(client):
    """Verify filtering by service_type and health_status."""
    res = client.get("/api/services?service_type=database")
    assert res.status_code == 200
    services = res.json()
    assert len(services) == 1
    assert services[0]["id"] == "srv-database"

    res_health = client.get("/api/services?health_status=HEALTHY")
    assert res_health.status_code == 200
    assert len(res_health.json()) >= 1

def test_search_services(client):
    """Verify search filter on name and id."""
    res = client.get("/api/services?search=Payment")
    assert res.status_code == 200
    services = res.json()
    assert len(services) == 1
    assert services[0]["id"] == "srv-payment"

def test_create_service_custom_and_auto_id(client):
    """Verify creating a service with custom ID and auto-generated ID."""
    # Custom ID
    payload1 = {
        "id": "srv-analytics",
        "name": "Analytics Service",
        "service_type": "analytics",
        "description": "Stream analytics engine",
        "cpu_usage": 45.0,
        "memory_usage": 50.0,
        "latency_ms": 30.0,
        "error_rate": 0.05,
        "request_volume": 600
    }
    res1 = client.post("/api/services", json=payload1)
    assert res1.status_code == 201
    created1 = res1.json()
    assert created1["id"] == "srv-analytics"
    assert created1["health_status"] == "HEALTHY"

    # Auto-generated ID
    payload2 = {
        "name": "Search Engine",
        "service_type": "search",
        "description": "Full-text search cluster",
        "cpu_usage": 15.0,
        "memory_usage": 25.0,
        "latency_ms": 12.0,
        "error_rate": 0.0,
        "request_volume": 800
    }
    res2 = client.post("/api/services", json=payload2)
    assert res2.status_code == 201
    created2 = res2.json()
    assert created2["id"] == "srv-search-engine"

def test_create_service_duplicate_id_rejected(client):
    """Verify duplicate service IDs are rejected with 400 Bad Request."""
    payload = {
        "id": "srv-gateway",
        "name": "Duplicate Gateway",
        "service_type": "gateway",
        "cpu_usage": 10.0,
        "memory_usage": 10.0,
        "latency_ms": 10.0,
        "error_rate": 0.0,
        "request_volume": 100
    }
    res = client.post("/api/services", json=payload)
    assert res.status_code == 400
    assert "already exists" in res.json()["detail"]

def test_update_service_and_health_recalculation(client):
    """Verify updating telemetry triggers rule-based health recalculation."""
    # Update to warning metrics (e.g. latency 500ms)
    res_warn = client.put("/api/services/srv-auth", json={"latency_ms": 500.0})
    assert res_warn.status_code == 200
    assert res_warn.json()["health_status"] == "WARNING"

    # Update to critical metrics (e.g. error rate 15%)
    res_crit = client.put("/api/services/srv-auth", json={"error_rate": 15.0})
    assert res_crit.status_code == 200
    assert res_crit.json()["health_status"] == "CRITICAL"

    # Update back to healthy
    res_healthy = client.put("/api/services/srv-auth", json={"latency_ms": 25.0, "error_rate": 0.1})
    assert res_healthy.status_code == 200
    assert res_healthy.json()["health_status"] == "HEALTHY"

def test_delete_service_cascades_dependencies(client):
    """Verify deleting a service cascade removes its incoming/outgoing dependencies."""
    # Check dependencies involving srv-auth
    deps_res = client.get("/api/dependencies")
    auth_deps = [d for d in deps_res.json() if d["source_service_id"] == "srv-auth" or d["target_service_id"] == "srv-auth"]
    assert len(auth_deps) >= 2

    # Delete service
    del_res = client.delete("/api/services/srv-auth")
    assert del_res.status_code == 200
    assert del_res.json()["success"] is True

    # Verify service is gone
    get_res = client.get("/api/services/srv-auth")
    assert get_res.status_code == 404

    # Verify dependencies involving srv-auth are also removed
    deps_after = client.get("/api/dependencies").json()
    auth_deps_after = [d for d in deps_after if d["source_service_id"] == "srv-auth" or d["target_service_id"] == "srv-auth"]
    assert len(auth_deps_after) == 0

def test_service_validation_errors(client):
    """Verify invalid payloads return 422 Unprocessable Entity."""
    # Invalid CPU usage (> 100%)
    res = client.post("/api/services", json={
        "name": "Bad CPU",
        "service_type": "compute",
        "cpu_usage": 150.0
    })
    assert res.status_code == 422
