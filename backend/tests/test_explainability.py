import pytest
from sqlalchemy.orm import Session
from app.services.insight_service import InsightService

def test_explainable_insights_generation(db_session: Session):
    insights = InsightService.generate_insights(db_session, limit=10)
    assert isinstance(insights, list)

    for ins in insights:
        assert ins.id is not None
        assert ins.title != ""
        assert ins.summary != ""
        assert ins.source_module != ""
        assert ins.data_source in ["observed", "simulated", "synthetic", "inferred"]
        # Non-hallucinatory check: uncertainty notes must disclose assumptions
        assert ins.uncertainty_notes != ""
        assert ins.recommended_next_step != ""
