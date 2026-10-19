import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Integer, Float, Text, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from app.database.database import Base

def generate_uuid() -> str:
    return str(uuid.uuid4())

class RecoveryPlanModel(Base):
    __tablename__ = "recovery_plans"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    incident_id = Column(String(64), nullable=True, index=True)
    scenario_id = Column(String(64), nullable=True, index=True)
    plan_name = Column(String(128), nullable=False)
    description = Column(Text, nullable=True)
    strategy_type = Column(String(32), nullable=False, default="balanced")  # lowest_risk, fastest_recovery, lowest_cost, balanced, custom
    risk_score = Column(Float, nullable=False, default=0.0)  # 0 to 100
    risk_level = Column(String(16), nullable=False, default="Low")  # Low, Moderate, High, Critical
    estimated_recovery_time = Column(Integer, nullable=False, default=0)  # steps or seconds
    estimated_cost = Column(Float, nullable=False, default=0.0)  # abstract resource cost units
    status = Column(String(32), nullable=False, default="DRAFT")  # DRAFT, VALIDATED, SIMULATED, RECOMMENDED, REJECTED
    risk_breakdown_json = Column(Text, nullable=True)  # JSON factor breakdown
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)

    # Relationships
    actions = relationship("RecoveryActionModel", back_populates="plan", cascade="all, delete-orphan", order_by="RecoveryActionModel.action_order")
    runs = relationship("RecoverySimulationRunModel", back_populates="plan", cascade="all, delete-orphan", order_by="desc(RecoverySimulationRunModel.created_at)")

class RecoveryActionModel(Base):
    __tablename__ = "recovery_actions"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    plan_id = Column(String(36), ForeignKey("recovery_plans.id", ondelete="CASCADE"), nullable=False, index=True)
    action_type = Column(String(64), nullable=False)  # restart_service, rollback_deployment, traffic_reroute, scale_up, isolate_dependency, restore_database, retry_request, wait_auto_recovery
    target_service_id = Column(String(64), nullable=True, index=True)
    action_order = Column(Integer, nullable=False, default=1)
    parameters_json = Column(Text, nullable=True)  # JSON action params
    preconditions_json = Column(Text, nullable=True)  # JSON required preconditions
    estimated_duration = Column(Integer, nullable=False, default=1)  # discrete steps
    risk_score = Column(Float, nullable=False, default=0.0)  # individual action risk
    reversibility = Column(String(32), nullable=False, default="fully_reversible")  # fully_reversible, partially_reversible, irreversible
    status = Column(String(32), nullable=False, default="PENDING")  # PENDING, SUCCESS, FAILED, ROLLED_BACK
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    # Relationships
    plan = relationship("RecoveryPlanModel", back_populates="actions")

class RecoverySimulationRunModel(Base):
    __tablename__ = "recovery_simulation_runs"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    plan_id = Column(String(36), ForeignKey("recovery_plans.id", ondelete="CASCADE"), nullable=False, index=True)
    simulation_run_id = Column(String(64), nullable=True, index=True)  # link to Module 6 SimulationRunModel if applicable
    outcome = Column(String(32), nullable=False, default="SUCCESSFUL_RECOVERY")  # SUCCESSFUL_RECOVERY, PARTIAL_RECOVERY, FAILED_RECOVERY
    total_recovery_time = Column(Integer, nullable=False, default=0)
    maximum_risk = Column(Float, nullable=False, default=0.0)
    final_health_summary = Column(Text, nullable=True)  # JSON dict {service_id: final_health}
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    # Relationships
    plan = relationship("RecoveryPlanModel", back_populates="runs")
    events = relationship("RecoveryEventModel", back_populates="simulation_run", cascade="all, delete-orphan", order_by="RecoveryEventModel.timestamp_or_step")

class RecoveryEventModel(Base):
    __tablename__ = "recovery_events"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    simulation_run_id = Column(String(36), ForeignKey("recovery_simulation_runs.id", ondelete="CASCADE"), nullable=False, index=True)
    event_type = Column(String(64), nullable=False)  # ACTION_STARTED, ACTION_COMPLETED, ACTION_FAILED, PRECONDITION_FAILED, METRIC_IMPROVED, CASCADE_RESOLVED, ROLLBACK_TRIGGERED
    description = Column(Text, nullable=False)
    evidence_json = Column(Text, nullable=True)  # JSON evidence details
    timestamp_or_step = Column(Integer, nullable=False, default=0)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    # Relationships
    simulation_run = relationship("RecoverySimulationRunModel", back_populates="events")

class RecoveryEvaluationModel(Base):
    __tablename__ = "recovery_evaluations"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    evaluation_name = Column(String(128), nullable=False)
    baseline_name = Column(String(128), nullable=False)
    metrics_json = Column(Text, nullable=False)  # JSON metrics
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
