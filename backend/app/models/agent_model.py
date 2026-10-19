from datetime import datetime, timezone
import uuid
from sqlalchemy import Column, String, Integer, Float, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.database.database import Base

def generate_uuid():
    return str(uuid.uuid4())

class AgentSessionModel(Base):
    __tablename__ = "agent_sessions"

    id = Column(String, primary_key=True, default=generate_uuid)
    incident_id = Column(String, nullable=True, index=True)
    scenario_id = Column(String, nullable=True, index=True)
    target_service_id = Column(String, nullable=True, index=True)
    status = Column(String, default="IDLE", index=True)  # IDLE, RUNNING, COMPLETED, STOPPED, FAILED
    policy_version = Column(String, default="1.0.0")
    configuration_json = Column(Text, nullable=True)
    stopping_reason = Column(String, nullable=True)
    total_steps = Column(Integer, default=0)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    completed_at = Column(DateTime, nullable=True)

    # Relationships
    action_history = relationship("AgentActionHistoryModel", back_populates="session", cascade="all, delete-orphan", order_by="AgentActionHistoryModel.step_number")
    session_result = relationship("AgentSessionResultModel", back_populates="session", uselist=False, cascade="all, delete-orphan")


class AgentActionHistoryModel(Base):
    __tablename__ = "agent_action_history"

    id = Column(String, primary_key=True, default=generate_uuid)
    session_id = Column(String, ForeignKey("agent_sessions.id", ondelete="CASCADE"), nullable=False, index=True)
    step_number = Column(Integer, nullable=False)
    action_id = Column(String, nullable=False, index=True)
    parameters_json = Column(Text, nullable=True)
    selection_score = Column(Float, default=0.0)
    selection_reason = Column(Text, nullable=True)
    execution_status = Column(String, default="SUCCESS")  # SUCCESS, FAILED, TIMED_OUT
    result_summary = Column(Text, nullable=True)
    raw_result_json = Column(Text, nullable=True)
    evidence_ids_json = Column(Text, nullable=True)  # List of newly generated or referenced evidence IDs
    started_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    completed_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    duration_ms = Column(Float, default=0.0)

    session = relationship("AgentSessionModel", back_populates="action_history")


class AgentSessionResultModel(Base):
    __tablename__ = "agent_session_results"

    id = Column(String, primary_key=True, default=generate_uuid)
    session_id = Column(String, ForeignKey("agent_sessions.id", ondelete="CASCADE"), nullable=False, unique=True, index=True)
    result_json = Column(Text, nullable=True)
    final_ranking_json = Column(Text, nullable=True)
    unresolved_questions_json = Column(Text, nullable=True)
    evidence_completeness = Column(Float, default=0.0)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    session = relationship("AgentSessionModel", back_populates="session_result")
