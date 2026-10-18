from datetime import datetime, timezone
from sqlalchemy import Column, String, Text, DateTime, ForeignKey, Index
from sqlalchemy.orm import relationship
from app.database.database import Base

class CascadeScenarioModel(Base):
    __tablename__ = "cascade_scenarios"

    id = Column(String(64), primary_key=True, index=True)
    scenario_name = Column(String(128), nullable=False, index=True)
    initial_service_id = Column(
        String(64),
        ForeignKey("services.id", ondelete="SET NULL"),
        nullable=True,
        index=True
    )
    failure_type = Column(String(64), nullable=False)  # service_unavailable, latency_spike, error_surge, cpu_exhaustion, memory_leak
    failure_severity = Column(String(32), nullable=False)  # mild, moderate, severe
    input_parameters = Column(Text, nullable=False)  # JSON-encoded input configuration
    result_summary = Column(Text, nullable=False)  # JSON-encoded simulation outcomes
    data_source = Column(String(32), nullable=False, default="simulated")
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), index=True)

    # Relationship to ServiceModel
    initial_service = relationship("ServiceModel", foreign_keys=[initial_service_id])

    __table_args__ = (
        Index("ix_cascade_scenarios_created", "created_at"),
    )
