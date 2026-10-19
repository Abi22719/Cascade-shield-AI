import pytest
from app.services.validation_evidence import ValidationEvidenceEngine
from app.database.validation_repository import ValidationRepository
from app.database.recovery_repository import RecoveryRepository

def test_evidence_collection_and_lineage(db_session):
    # Create a test plan and run
    plan = RecoveryRepository.create_plan(db_session, {
        "plan_name": "Test Evidence Plan",
        "strategy_type": "balanced",
        "risk_score": 25.0
    })
    val_run = ValidationRepository.create_run(db_session, {
        "recovery_plan_id": plan.id,
        "overall_outcome": "NOT_RUN"
    })

    items = [
        {
            "source_module": "module_7",
            "source_record_id": plan.id,
            "evidence_type": "metric_observation",
            "description": "Latency dropped below 200ms",
            "observed_or_simulated": "simulated",
            "timestamp_or_step": "3",
            "metadata": {"metric": "latency_ms", "value": 140}
        },
        {
            "source_module": "module_1",
            "source_record_id": "srv-database",
            "evidence_type": "graph_topology",
            "description": "PostgreSQL database verified in topology",
            "observed_or_simulated": "observed",
            "timestamp_or_step": "0"
        }
    ]

    ev_records = ValidationEvidenceEngine.collect_and_link_evidence(db_session, val_run.id, items)
    assert len(ev_records) == 2
    assert ev_records[0].observed_or_simulated == "simulated"
    assert ev_records[1].observed_or_simulated == "observed"

    # Check retrieval from DB
    fetched = ValidationRepository.get_evidence_for_run(db_session, val_run.id)
    assert len(fetched) == 2
