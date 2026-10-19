import pytest
from app.services.diagnostic_agent import DiagnosticAgent
from app.schemas.agent_schema import CreateSessionRequest, AgentConfigSchema

def test_diagnostic_agent_lifecycle(db_session):
    # 1. Create Session
    req = CreateSessionRequest(target_service_id="srv-payment", custom_config=AgentConfigSchema(max_actions=3))
    session = DiagnosticAgent.create_session(db_session, req)
    assert session.id is not None
    assert session.target_service_id == "srv-payment"
    assert session.status == "IDLE"

    # 2. Step 1
    step_1 = DiagnosticAgent.step(db_session, session.id)
    assert step_1.step_number == 1
    assert step_1.session_status in ["RUNNING", "COMPLETED"]
    assert step_1.executed_action is not None
    assert step_1.executed_action.execution_status == "SUCCESS"

    # 3. Full Run
    final_session = DiagnosticAgent.run(db_session, session.id, max_steps=3)
    assert final_session.total_steps <= 3
    assert final_session.status in ["COMPLETED", "STOPPED"]
    assert len(final_session.action_history) >= 1
    assert final_session.evidence_completeness > 0.0

def test_diagnostic_agent_stop(db_session):
    req = CreateSessionRequest(target_service_id="srv-auth")
    session = DiagnosticAgent.create_session(db_session, req)
    
    stopped = DiagnosticAgent.stop(db_session, session.id)
    assert stopped.status == "STOPPED"
    assert "USER_STOP_REQUESTED" in stopped.stopping_reason
