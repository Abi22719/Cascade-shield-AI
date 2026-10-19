import pytest
from app.schemas.rca_schema import RCAInvestigationRequest
from app.services.rca_engine import RCAEngine

def test_rca_engine_end_to_end(db_session):
    req = RCAInvestigationRequest(
        incident_title="Database Starvation Incident",
        target_service_id="srv-database",
        affected_service_ids=["srv-order", "srv-database"]
    )

    report = RCAEngine.analyze_incident(db_session, req)

    assert report.incident_id.startswith("inc-")
    assert report.title == "Database Starvation Incident"
    assert len(report.ranked_candidates) >= 1
    assert len(report.evidence_timeline) >= 0
    assert len(report.diagnostic_recommendations) >= 1
    assert report.confidence_and_uncertainty_explanation is not None

def test_rca_engine_reanalyze(db_session):
    req = RCAInvestigationRequest(
        incident_title="Initial Scan",
        target_service_id="srv-payment",
        affected_service_ids=["srv-payment", "srv-order"]
    )
    report1 = RCAEngine.analyze_incident(db_session, req)
    inc_id = report1.incident_id

    # Reanalyze
    report2 = RCAEngine.reanalyze_incident(db_session, inc_id)
    assert report2.incident_id == inc_id
    assert "Reanalyzed" in report2.title
