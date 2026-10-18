import pytest

def test_get_graph_cytoscape_format(client):
    """Verify graph returns Cytoscape-compliant node and edge elements."""
    res = client.get("/api/graph")
    assert res.status_code == 200
    data = res.json()

    assert "nodes" in data
    assert "edges" in data
    assert "summary" in data

    assert len(data["nodes"]) == 9
    assert len(data["edges"]) == 9
    assert data["summary"]["is_dag"] is True
    assert data["summary"]["has_cycles"] is False

    # Check node structure
    first_node = data["nodes"][0]
    assert "data" in first_node
    assert "id" in first_node["data"]
    assert "name" in first_node["data"]
    assert "health_status" in first_node["data"]
    assert "cpu_usage" in first_node["data"]

    # Check edge structure
    first_edge = data["edges"][0]
    assert "data" in first_edge
    assert "source" in first_edge["data"]
    assert "target" in first_edge["data"]
    assert "dependency_type" in first_edge["data"]

def test_downstream_impact_gateway(client):
    """
    Verify downstream impact calculation for API Gateway:
    Gateway connects to Auth, Product, Order.
    Auth connects to User.
    Product connects to Database, Cache.
    Order connects to Payment, Database, Notification.
    Total downstream reachable = 8 services.
    """
    res = client.get("/api/graph/impact/srv-gateway")
    assert res.status_code == 200
    impact = res.json()

    assert impact["service_id"] == "srv-gateway"
    assert impact["service_name"] == "API Gateway"
    assert impact["found"] is True
    assert impact["reachable_count"] == 8
    assert impact["direct_dependents_count"] == 3
    assert set(impact["direct_dependents"]) == {"srv-auth", "srv-product", "srv-order"}
    assert "srv-database" in impact["indirect_dependents"]
    assert "srv-user" in impact["indirect_dependents"]

    # Verify impact tiers exist
    assert "1" in impact["impact_tiers"]
    assert "2" in impact["impact_tiers"]

def test_downstream_impact_leaf_service(client):
    """Verify a terminal node (e.g. Cache or User) has 0 downstream reachable services."""
    res = client.get("/api/graph/impact/srv-cache")
    assert res.status_code == 200
    impact = res.json()

    assert impact["service_id"] == "srv-cache"
    assert impact["reachable_count"] == 0
    assert impact["direct_dependents_count"] == 0

def test_downstream_impact_not_found(client):
    """Verify 404 for unknown service."""
    res = client.get("/api/graph/impact/srv-ghost")
    assert res.status_code == 404

def test_reset_graph_topology(client):
    """Verify reset endpoint restores default state after mutations."""
    # Delete a service
    client.delete("/api/services/srv-cache")
    services_before = client.get("/api/services").json()
    assert len(services_before) == 8

    # Reset
    res_reset = client.post("/api/graph/reset")
    assert res_reset.status_code == 200
    assert res_reset.json()["services_count"] == 9
    assert res_reset.json()["dependencies_count"] == 9

    # Verify cache is back
    cache_check = client.get("/api/services/srv-cache")
    assert cache_check.status_code == 200
