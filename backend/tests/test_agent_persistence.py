import pytest
from app.database.agent_repository import AgentRepository
from app.models.agent_model import AgentSessionModel, AgentActionHistoryModel

def test_agent_persistence_crud_and_cascade(db_session):
    # Create
    session_data = {
        "incident_id": "inc-test-1",
        "target_service_id": "srv-payment",
        "status": "IDLE",
        "policy_version": "1.0.0",
        "configuration": {"max_actions": 5}
    }
    sess = AgentRepository.create_session(db_session, session_data)
    sess_id = sess.id
    assert sess_id is not None

    # Record Steps
    step_1 = AgentRepository.record_action_step(db_session, {
        "session_id": sess_id,
        "step_number": 1,
        "action_id": "inspect_service_health",
        "parameters": {"service_id": "srv-payment"},
        "selection_score": 0.85,
        "selection_reason": "Top utility",
        "execution_status": "SUCCESS",
        "result_summary": "Healthy check completed."
    })
    assert step_1.id is not None

    step_2 = AgentRepository.record_action_step(db_session, {
        "session_id": sess_id,
        "step_number": 2,
        "action_id": "retrieve_anomaly_alerts",
        "parameters": {"service_id": "srv-payment"},
        "selection_score": 0.78,
        "selection_reason": "Corroboration",
        "execution_status": "SUCCESS",
        "result_summary": "Alerts verified."
    })

    # Read History
    history = AgentRepository.get_action_history(db_session, sess_id)
    assert len(history) == 2
    assert history[0].step_number == 1
    assert history[1].step_number == 2

    # Save Result
    AgentRepository.save_session_result(
        db_session,
        sess_id,
        result_json='{"status":"done"}',
        final_ranking_json='[{"service_id":"srv-payment","score":85.0}]',
        unresolved_questions_json='[]',
        completeness=1.0
    )
    res_rec = AgentRepository.get_session_result(db_session, sess_id)
    assert res_rec is not None
    assert res_rec.evidence_completeness == 1.0

    # Delete with cascade
    deleted = AgentRepository.delete_session(db_session, sess_id)
    assert deleted is True

    # Confirm history is deleted
    remaining_history = db_session.query(AgentActionHistoryModel).filter(
        AgentActionHistoryModel.session_id == sess_id
    ).all()
    assert len(remaining_history) == 0
