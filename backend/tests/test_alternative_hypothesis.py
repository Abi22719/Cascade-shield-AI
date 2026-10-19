import pytest
import networkx as nx

from app.models.service import ServiceModel
from app.models.dependency import DependencyModel
from app.schemas.rca_schema import CandidateRootCauseSchema
from app.services.alternative_hypothesis import AlternativeHypothesisEngine

def test_shared_dependency_alternative_hypothesis():
    s_db = ServiceModel(id="srv-database", name="Database Service", service_type="database", health_status="healthy", cpu_usage=40, memory_usage=50, latency_ms=45, error_rate=0.01, request_volume=100)
    s_order = ServiceModel(id="srv-order", name="Order Service", service_type="compute", health_status="warning", cpu_usage=50, memory_usage=50, latency_ms=150, error_rate=1.5, request_volume=200)
    s_user = ServiceModel(id="srv-user", name="User Service", service_type="compute", health_status="warning", cpu_usage=50, memory_usage=50, latency_ms=140, error_rate=1.2, request_volume=200)

    # Both Order and User depend on Database
    G_dep = nx.DiGraph()
    G_dep.add_edge("srv-order", "srv-database")
    G_dep.add_edge("srv-user", "srv-database")

    cand = CandidateRootCauseSchema(
        service_id="srv-order",
        service_name="Order Service",
        rank=1,
        ranking_score=65.0,
        confidence_label="Moderate supporting evidence",
        confidence_score=0.65,
        explanation="Order degradation"
    )

    hypotheses = AlternativeHypothesisEngine.generate_hypotheses(
        candidates=[cand],
        affected_service_ids=["srv-order", "srv-user"],
        services=[s_db, s_order, s_user],
        G_dep=G_dep,
        evidence_items=[]
    )

    # Must generate the shared bottleneck hypothesis for srv-database
    assert len(hypotheses) >= 1
    shared_hyp = next((h for h in hypotheses if "Shared Bottleneck" in h.hypothesis_title), None)
    assert shared_hyp is not None
    assert "srv-database" in shared_hyp.related_services
