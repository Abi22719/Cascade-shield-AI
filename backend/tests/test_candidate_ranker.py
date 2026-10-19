import pytest
from datetime import datetime, timezone, timedelta
import networkx as nx

from app.models.service import ServiceModel
from app.models.dependency import DependencyModel
from app.schemas.rca_schema import EvidenceItemSchema
from app.services.candidate_ranker import CandidateRanker
from app.services.dependency_analyzer import DependencyAnalyzer

def test_candidate_ranking_identifies_true_root():
    t0 = datetime(2026, 10, 18, 10, 0, 0, tzinfo=timezone.utc)
    t1 = t0 + timedelta(seconds=20)

    s_db = ServiceModel(id="srv-database", name="Database Service", service_type="database", health_status="critical", cpu_usage=85.0, memory_usage=88.0, latency_ms=450.0, error_rate=4.5, request_volume=200)
    s_order = ServiceModel(id="srv-order", name="Order Service", service_type="compute", health_status="warning", cpu_usage=35.0, memory_usage=45.0, latency_ms=180.0, error_rate=1.8, request_volume=500)
    s_gw = ServiceModel(id="srv-gateway", name="API Gateway", service_type="gateway", health_status="healthy", cpu_usage=20.0, memory_usage=30.0, latency_ms=25.0, error_rate=0.01, request_volume=1000)

    dep1 = DependencyModel(id="d1", source_service_id="srv-order", target_service_id="srv-database", dependency_type="database_read_write")
    dep2 = DependencyModel(id="d2", source_service_id="srv-gateway", target_service_id="srv-order", dependency_type="sync_http")

    _, G_impact = DependencyAnalyzer.build_networkx_graphs([s_db, s_order, s_gw], [dep1, dep2])

    ev1 = EvidenceItemSchema(
        id="ev-1",
        service_id="srv-database",
        service_name="Database Service",
        evidence_type="metric_breach",
        timestamp=t0,
        source_module="Module 1",
        evidence_summary="Database latency critical"
    )
    ev2 = EvidenceItemSchema(
        id="ev-2",
        service_id="srv-order",
        service_name="Order Service",
        evidence_type="metric_breach",
        timestamp=t1,
        source_module="Module 1",
        evidence_summary="Order latency warning"
    )

    candidates = CandidateRanker.rank_candidates(
        services=[s_db, s_order, s_gw],
        affected_service_ids=["srv-order", "srv-gateway"],
        evidence_items=[ev1, ev2],
        G_impact=G_impact
    )

    assert len(candidates) >= 2
    # srv-database must be ranked #1
    assert candidates[0].service_id == "srv-database"
    assert candidates[0].rank == 1
    assert candidates[0].ranking_score > candidates[1].ranking_score
    assert candidates[0].confidence_label in ["Strong supporting evidence", "Moderate supporting evidence"]
