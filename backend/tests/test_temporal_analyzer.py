import pytest
from datetime import datetime, timezone, timedelta
from app.schemas.rca_schema import EvidenceItemSchema
from app.services.temporal_analyzer import TemporalAnalyzer

def test_temporal_precedence_and_inversion():
    t0 = datetime(2026, 10, 18, 10, 0, 0, tzinfo=timezone.utc)
    t1 = t0 + timedelta(seconds=15)
    t2 = t0 + timedelta(seconds=30)

    ev_db = EvidenceItemSchema(
        id="ev-1",
        service_id="srv-database",
        service_name="Database Service",
        evidence_type="metric_breach",
        timestamp=t0,
        source_module="Module 1",
        evidence_summary="DB latency spike"
    )
    ev_order = EvidenceItemSchema(
        id="ev-2",
        service_id="srv-order",
        service_name="Order Service",
        evidence_type="metric_breach",
        timestamp=t1,
        source_module="Module 1",
        evidence_summary="Order latency spike"
    )
    ev_gw = EvidenceItemSchema(
        id="ev-3",
        service_id="srv-gateway",
        service_name="API Gateway",
        evidence_type="metric_breach",
        timestamp=t2,
        source_module="Module 1",
        evidence_summary="Gateway error surge"
    )

    earliest_map = TemporalAnalyzer.extract_service_earliest_timestamps([ev_db, ev_order, ev_gw])
    assert earliest_map["srv-database"] == t0
    assert earliest_map["srv-order"] == t1
    assert earliest_map["srv-gateway"] == t2

    # Database preceded Order and Gateway -> Precedence score = 1.0
    score, sup, contra = TemporalAnalyzer.evaluate_temporal_precedence(
        "srv-database", ["srv-order", "srv-gateway"], earliest_map
    )
    assert score == 1.0
    assert len(sup) == 2
    assert len(contra) == 0

    # Gateway degraded AFTER Order and DB -> Temporal inversion
    score_gw, sup_gw, contra_gw = TemporalAnalyzer.evaluate_temporal_precedence(
        "srv-gateway", ["srv-database", "srv-order"], earliest_map
    )
    assert score_gw == 0.0
    assert len(contra_gw) == 2
    assert any("Temporal Inversion" in c for c in contra_gw)

def test_timeline_event_generation():
    t0 = datetime(2026, 10, 18, 10, 5, 0, tzinfo=timezone.utc)
    ev = EvidenceItemSchema(
        id="ev-100",
        service_id="srv-payment",
        service_name="Payment Service",
        evidence_type="anomaly_alert",
        timestamp=t0,
        source_module="Module 2: AI Anomaly Detection",
        evidence_summary="[CRITICAL] Latency spike above 500ms"
    )
    timeline = TemporalAnalyzer.build_event_timeline([ev])
    assert len(timeline) == 1
    assert timeline[0].service_id == "srv-payment"
    assert timeline[0].severity == "critical"
    assert "2026-10-18 10:05:00 UTC" in timeline[0].timestamp_formatted
