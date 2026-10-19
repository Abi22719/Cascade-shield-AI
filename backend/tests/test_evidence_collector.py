import pytest
from datetime import datetime, timezone
from app.models.service import ServiceModel
from app.models.alert_model import AlertModel
from app.services.evidence_collector import EvidenceCollector

def test_evidence_collector_gathers_health_and_metrics(db_session):
    # Retrieve evidence from seeded database
    evidence = EvidenceCollector.collect_evidence(
        db=db_session,
        affected_service_ids=["srv-gateway", "srv-order"]
    )

    assert isinstance(evidence, list)
    assert len(evidence) >= 1

    # Check structure
    for ev in evidence:
        assert ev.id.startswith("ev-")
        assert ev.service_id is not None
        assert ev.service_name is not None
        assert ev.evidence_type in [
            "health_degraded", "metric_breach", "anomaly_alert", 
            "cascade_risk", "contradictory_evidence"
        ]
        assert ev.source_module is not None
        assert 0.0 <= ev.reliability_score <= 1.0

def test_evidence_collector_contradictory_healthy_state(db_session):
    # srv-gateway is typically healthy in baseline
    evidence = EvidenceCollector.collect_evidence(
        db=db_session,
        affected_service_ids=["srv-gateway"]
    )

    # Should flag contradictory evidence since srv-gateway was in affected list but is healthy
    has_contra = any(e.is_contradictory for e in evidence)
    assert has_contra is True
