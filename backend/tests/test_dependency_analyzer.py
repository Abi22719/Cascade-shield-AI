import pytest
from app.models.service import ServiceModel
from app.models.dependency import DependencyModel
from app.services.dependency_analyzer import DependencyAnalyzer

def test_dependency_analyzer_graphs_and_paths():
    s1 = ServiceModel(id="srv-gw", name="Gateway", service_type="gateway", health_status="healthy", cpu_usage=20, memory_usage=30, latency_ms=10, error_rate=0.0, request_volume=100)
    s2 = ServiceModel(id="srv-order", name="Order", service_type="compute", health_status="healthy", cpu_usage=20, memory_usage=30, latency_ms=10, error_rate=0.0, request_volume=100)
    s3 = ServiceModel(id="srv-db", name="DB", service_type="database", health_status="healthy", cpu_usage=20, memory_usage=30, latency_ms=10, error_rate=0.0, request_volume=100)

    # Gateway depends on Order, Order depends on DB
    d1 = DependencyModel(id="d1", source_service_id="srv-gw", target_service_id="srv-order", dependency_type="sync_http")
    d2 = DependencyModel(id="d2", source_service_id="srv-order", target_service_id="srv-db", dependency_type="database_read_write")

    G_dep, G_impact = DependencyAnalyzer.build_networkx_graphs([s1, s2, s3], [d1, d2])

    assert G_dep.has_edge("srv-gw", "srv-order")
    assert G_impact.has_edge("srv-order", "srv-gw")
    assert G_impact.has_edge("srv-db", "srv-order")

    # If srv-db is candidate, affected services are srv-order and srv-gw
    coverage, paths, reachable, unreachable = DependencyAnalyzer.analyze_candidate_dependencies(
        "srv-db", ["srv-order", "srv-gw"], G_impact
    )

    assert coverage == 1.0
    assert len(reachable) == 2
    assert len(unreachable) == 0
    assert len(paths) >= 2
