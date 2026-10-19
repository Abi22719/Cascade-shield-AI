import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Integer, Float, Text, DateTime, ForeignKey, Index
from sqlalchemy.orm import relationship
from app.database.database import Base

def generate_uuid():
    return str(uuid.uuid4())

class SimulationScenarioModel(Base):
    __tablename__ = "simulation_scenarios"

    id = Column(String(64), primary_key=True, default=generate_uuid)
    name = Column(String(128), nullable=False, index=True)
    description = Column(Text, nullable=True)
    category = Column(String(64), nullable=False, default="failure_propagation")  # failure_propagation, latency_storm, database_starvation, recovery_test
    scenario_config_json = Column(Text, nullable=False)
    source_data_type = Column(String(32), nullable=False, default="digital_twin")  # digital_twin, synthetic
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    # Relationships
    runs = relationship("SimulationRunModel", back_populates="scenario", cascade="all, delete-orphan", order_by="desc(SimulationRunModel.started_at)")


class SimulationRunModel(Base):
    __tablename__ = "simulation_runs"

    id = Column(String(64), primary_key=True, default=generate_uuid)
    scenario_id = Column(String(64), ForeignKey("simulation_scenarios.id", ondelete="CASCADE"), nullable=False, index=True)
    status = Column(String(32), nullable=False, default="PENDING", index=True)  # PENDING, RUNNING, COMPLETED, FAILED, CANCELLED
    random_seed = Column(Integer, nullable=True)
    model_version = Column(String(32), nullable=False, default="1.0.0")
    total_steps = Column(Integer, nullable=False, default=0)
    summary_json = Column(Text, nullable=True)
    error_summary = Column(Text, nullable=True)
    started_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    completed_at = Column(DateTime, nullable=True)

    # Relationships
    scenario = relationship("SimulationScenarioModel", back_populates="runs")
    events = relationship("SimulationEventModel", back_populates="run", cascade="all, delete-orphan", order_by="SimulationEventModel.step_number")
    service_states = relationship("SimulationServiceStateModel", back_populates="run", cascade="all, delete-orphan")


class SimulationEventModel(Base):
    __tablename__ = "simulation_events"

    id = Column(String(64), primary_key=True, default=generate_uuid)
    run_id = Column(String(64), ForeignKey("simulation_runs.id", ondelete="CASCADE"), nullable=False, index=True)
    step_number = Column(Integer, nullable=False, index=True)
    event_type = Column(String(64), nullable=False, index=True)  # FAILURE_INJECTION, PROPAGATION_WAVE, RECOVERY_START, RECOVERY_COMPLETE, METRIC_DEVIATION
    service_id = Column(String(64), nullable=False, index=True)
    event_data_json = Column(Text, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    run = relationship("SimulationRunModel", back_populates="events")


class SimulationServiceStateModel(Base):
    __tablename__ = "simulation_service_states"

    id = Column(String(64), primary_key=True, default=generate_uuid)
    run_id = Column(String(64), ForeignKey("simulation_runs.id", ondelete="CASCADE"), nullable=False, index=True)
    step_number = Column(Integer, nullable=False, index=True)
    service_id = Column(String(64), nullable=False, index=True)
    health_status = Column(String(32), nullable=False, default="HEALTHY")  # HEALTHY, DEGRADED, CRITICAL, RECOVERING, RECOVERED
    state_json = Column(Text, nullable=False)  # includes simulated cpu, memory, latency, error_rate, request_volume, risk_score
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    run = relationship("SimulationRunModel", back_populates="service_states")
