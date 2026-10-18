import pytest

def test_default_dependencies_initialized(client):
    """Verify default 9 dependencies exist."""
    res = client.get("/api/dependencies")
    assert res.status_code == 200
    deps = res.json()
    assert len(deps) == 9

def test_create_valid_dependency(client):
    """Verify creating a new valid dependency."""
    # Create User -> Database dependency
    payload = {
        "source_service_id": "srv-user",
        "target_service_id": "srv-database",
        "dependency_type": "database_read_write",
        "description": "User Service reads and writes user profile data to database"
    }
    res = client.post("/api/dependencies", json=payload)
    assert res.status_code == 201
    data = res.json()
    assert data["source_service_id"] == "srv-user"
    assert data["target_service_id"] == "srv-database"
    assert data["has_cycle"] is False

def test_prevent_self_dependency(client):
    """Verify self-dependencies are blocked with 400."""
    payload = {
        "source_service_id": "srv-user",
        "target_service_id": "srv-user",
        "dependency_type": "sync_http"
    }
    res = client.post("/api/dependencies", json=payload)
    assert res.status_code == 422 or res.status_code == 400

def test_prevent_invalid_source_or_target(client):
    """Verify dependencies referencing non-existent services are rejected with 404."""
    # Invalid source
    res1 = client.post("/api/dependencies", json={
        "source_service_id": "srv-ghost",
        "target_service_id": "srv-database",
        "dependency_type": "sync_http"
    })
    assert res1.status_code == 404
    assert "does not exist" in res1.json()["detail"]

    # Invalid target
    res2 = client.post("/api/dependencies", json={
        "source_service_id": "srv-gateway",
        "target_service_id": "srv-phantom",
        "dependency_type": "sync_http"
    })
    assert res2.status_code == 404
    assert "does not exist" in res2.json()["detail"]

def test_prevent_duplicate_dependency(client):
    """Verify duplicate edges between existing pair are rejected with 400."""
    payload = {
        "source_service_id": "srv-gateway",
        "target_service_id": "srv-auth",
        "dependency_type": "sync_http"
    }
    res = client.post("/api/dependencies", json=payload)
    assert res.status_code == 400
    assert "already exists" in res.json()["detail"]

def test_detect_circular_dependency(client):
    """
    Verify circular dependency detection and reporting:
    In default topology: srv-gateway -> srv-auth -> srv-user.
    If we add srv-user -> srv-gateway, it forms a cycle:
    srv-user -> srv-gateway -> srv-auth -> srv-user.
    """
    payload = {
        "source_service_id": "srv-user",
        "target_service_id": "srv-gateway",
        "dependency_type": "sync_http",
        "description": "Feedback cycle"
    }
    res = client.post("/api/dependencies", json=payload)
    assert res.status_code == 201
    data = res.json()
    assert data["has_cycle"] is True
    assert data["cycle_warning"] is not None
    assert "Circular dependency detected" in data["cycle_warning"]
    assert "srv-user" in data["cycle_path"]
    assert "srv-gateway" in data["cycle_path"]

def test_delete_dependency(client):
    """Verify removing a dependency."""
    res_del = client.delete("/api/dependencies/dep-gateway-auth")
    assert res_del.status_code == 200
    assert res_del.json()["success"] is True

    # Try deleting again - should return 404
    res_del_again = client.delete("/api/dependencies/dep-gateway-auth")
    assert res_del_again.status_code == 404
