import pytest
from app.database.rca_repository import RCARepository

def test_rca_persistence_lifecycle(db_session):
    # 1. Create incident
    inc = RCARepository.create_incident(
        db=db_session,
        title="Persistence Test Incident",
        affected_service_ids=["srv-db", "srv-order"]
    )
    assert inc.id.startswith("inc-")
    assert inc.title == "Persistence Test Incident"

    # 2. Save evidence
    ev_list = [
        {
            "service_id": "srv-db",
            "service_name": "Database",
            "evidence_type": "metric_breach",
            "evidence_summary": "High latency"
        }
    ]
    ev_saved = RCARepository.save_evidence_items(db_session, inc.id, ev_list)
    assert len(ev_saved) == 1

    # 3. Save candidates
    cand_list = [
        {
            "service_id": "srv-db",
            "service_name": "Database",
            "rank": 1,
            "ranking_score": 88.5,
            "confidence_label": "Strong supporting evidence",
            "confidence_score": 0.88,
            "explanation": "Plausible cause"
        }
    ]
    cand_saved = RCARepository.save_candidates(db_session, inc.id, cand_list)
    assert len(cand_saved) == 1

    # 4. Save report
    rep = RCARepository.save_report(
        db_session,
        inc.id,
        {"incident_id": inc.id, "title": inc.title, "evidence_count": 1}
    )
    assert rep.id.startswith("rep-")

    # 5. Fetch report
    fetched_rep = RCARepository.get_report_by_incident(db_session, inc.id)
    assert fetched_rep is not None

    # 6. Delete incident (cascade deletes evidence and candidates)
    deleted = RCARepository.delete_incident(db_session, inc.id)
    assert deleted is True

    # 7. Verify deletion
    assert RCARepository.get_incident_by_id(db_session, inc.id) is None
    assert len(RCARepository.get_evidence_by_incident(db_session, inc.id)) == 0
    assert len(RCARepository.get_candidates_by_incident(db_session, inc.id)) == 0
