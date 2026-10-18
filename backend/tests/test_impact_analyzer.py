import pytest
import networkx as nx
from app.models.service import ServiceModel
from app.models.dependency import DependencyModel
from app.services.impact_analyzer import ImpactAnalyzer

def test_propagation_graph_reverses_dependencies():
    """
    In the digital twin, u -> v means u depends on v (Order -> Payment).
    Propagation graph must reverse this: Payment -> Order,
    because when Payment fails, failure propagates to Order.
    """
    s1 = ServiceModel(id="srv-order", name="Order Service", service_type="backend", health_status="healthy", cpu_usage=20, memory_usage=30, latency_ms=50, error_rate=0.01, request_volume=100)
    s2 = ServiceModel(id="srv-payment", name="Payment Service", service_type="backend", health_status="healthy", cpu_usage=25, memory_usage=35, latency_ms=45, error_rate=0.02, request_volume=80)
    
    dep = DependencyModel(id="dep-1", source_service_id="srv-order", target_service_id="srv-payment", dependency_type="sync_http")

    G_prop = ImpactAnalyzer.build_propagation_graph([s1, s2], [dep])

    assert G_prop.has_node("srv-order")
    assert G_prop.has_node("srv-payment")
    assert G_prop.has_edge("srv-payment", "srv-order")
    assert not G_prop.has_edge("srv-order", "srv-payment")

def test_affected_services_direct_and_indirect():
    """
    db -> order (direct) -> gateway (indirect)
    """
    s_db = ServiceModel(id="srv-db", name="Database", service_type="database", health_status="healthy", cpu_usage=30, memory_usage=40, latency_ms=10, error_rate=0.0, request_volume=200)
    s_order = ServiceModel(id="srv-order", name="Order Service", service_type="backend", health_status="healthy", cpu_usage=20, memory_usage=30, latency_ms=50, error_rate=0.01, request_volume=100)
    s_gw = ServiceModel(id="srv-gw", name="API Gateway", service_type="gateway", health_status="healthy", cpu_usage=15, memory_usage=25, latency_ms=15, error_rate=0.0, request_volume=500)

    # Order depends on DB; Gateway depends on Order
    d1 = DependencyModel(id="dep-1", source_service_id="srv-order", target_service_id="srv-db", dependency_type="database_read_write")
    d2 = DependencyModel(id="dep-2", source_service_id="srv-gw", target_service_id="srv-order", dependency_type="sync_http")

    G_prop = ImpactAnalyzer.build_propagation_graph([s_db, s_order, s_gw], [d1, d2])

    affected, paths = ImpactAnalyzer.find_affected_services_and_paths(G_prop, "srv-db", max_hops=4)

    assert "srv-order" in affected
    assert affected["srv-order"]["impact_type"] == "Direct"
    assert affected["srv-order"]["hop_distance"] == 1

    assert "srv-gw" in affected
    assert affected["srv-gw"]["impact_type"] == "Indirect"
    assert affected["srv-gw"]["hop_distance"] == 2

    assert len(paths) >= 2

def test_cycle_safety_in_propagation():
    """
    Ensure cyclic dependencies (A -> B -> C -> A) do not cause infinite loops.
    """
    s_a = ServiceModel(id="srv-a", name="Service A", service_type="backend", health_status="healthy", cpu_usage=20, memory_usage=30, latency_ms=50, error_rate=0.01, request_volume=100)
    s_b = ServiceModel(id="srv-b", name="Service B", service_type="backend", health_status="healthy", cpu_usage=20, memory_usage=30, latency_ms=50, error_rate=0.01, request_volume=100)
    s_c = ServiceModel(id="srv-c", name="Service C", service_type="backend", health_status="healthy", cpu_usage=20, memory_usage=30, latency_ms=50, error_rate=0.01, request_volume=100)

    # Cycle: A depends on B, B depends on C, C depends on A
    d1 = DependencyModel(id="dep-1", source_service_id="srv-a", target_service_id="srv-b", dependency_type="sync_http")
    d2 = DependencyModel(id="dep-2", source_service_id="srv-b", target_service_id="srv-c", dependency_type="sync_http")
    d3 = DependencyModel(id="dep-3", source_service_id="srv-c", target_service_id="srv-a", dependency_type="sync_http")

    G_prop = ImpactAnalyzer.build_propagation_graph([s_a, s_b, s_c], [d1, d2, d3])

    affected, paths = ImpactAnalyzer.find_affected_services_and_paths(G_prop, "srv-a", max_hops=3)

    # Should safely terminate
    assert "srv-c" in affected
    assert "srv-b" in affected
    assert len(paths) > 0
