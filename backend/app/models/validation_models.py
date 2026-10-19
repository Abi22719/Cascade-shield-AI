import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Integer, Float, Text, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from app.database.database import Base

def generate_uuid() -> str:
    return str(uuid.uuid4())

class ValidationRunModel(Base):
    __tablename__ = "validation_runs"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    recovery_plan_id = Column(String(36), ForeignKey("recovery_plans.id", ondelete="CASCADE"), nullable=False, index=True)
    recovery_simulation_run_id = Column(String(36), ForeignKey("recovery_simulation_runs.id", ondelete="SET NULL"), nullable=True, index=True)
    source_scenario_id = Column(String(64), nullable=True, index=True)
    status = Column(String(32), nullable=False, default="COMPLETED")  # PENDING, RUNNING, COMPLETED, FAILED
    overall_outcome = Column(String(32), nullable=False, default="NOT_RUN")  # VERIFIED_SUCCESS, PARTIAL_SUCCESS, FAILED, INCONCLUSIVE, NOT_RUN
    total_checks = Column(Integer, nullable=False, default=0)
    passed_checks = Column(Integer, nullable=False, default=0)
    failed_checks = Column(Integer, nullable=False, default=0)
    warning_checks = Column(Integer, nullable=False, default=0)
    unknown_checks = Column(Integer, nullable=False, default=0)
    verification_window_steps = Column(Integer, nullable=False, default=3)
    summary_json = Column(Text, nullable=True)
    comparison_json = Column(Text, nullable=True)
    started_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    completed_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    # Relationships
    recovery_plan = relationship("RecoveryPlanModel")
    simulation_run = relationship("RecoverySimulationRunModel")
    checks = relationship("ValidationCheckModel", back_populates="validation_run", cascade="all, delete-orphan", order_by="ValidationCheckModel.created_at")
    evidence = relationship("ValidationEvidenceModel", back_populates="validation_run", cascade="all, delete-orphan", order_by="ValidationEvidenceModel.created_at")
    recommendations = relationship("ValidationRecommendationModel", back_populates="validation_run", cascade="all, delete-orphan", order_by="ValidationRecommendationModel.created_at")

class ValidationCheckModel(Base):
    __tablename__ = "validation_checks"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    validation_id = Column(String(36), ForeignKey("validation_runs.id", ondelete="CASCADE"), nullable=False, index=True)
    check_type = Column(String(64), nullable=False, index=True)  # service_health, metrics, dependency, stability, side_effects, evidence
    target_service_id = Column(String(64), nullable=True, index=True)
    check_name = Column(String(128), nullable=False)
    status = Column(String(32), nullable=False, default="UNKNOWN")  # PASS, FAIL, WARNING, UNKNOWN
    expected_value = Column(Text, nullable=True)
    actual_value = Column(Text, nullable=True)
    explanation = Column(Text, nullable=False)
    evidence_reference = Column(String(128), nullable=True)
    simulation_step = Column(Integer, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    # Relationships
    validation_run = relationship("ValidationRunModel", back_populates="checks")

class ValidationEvidenceModel(Base):
    __tablename__ = "validation_evidence"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    validation_id = Column(String(36), ForeignKey("validation_runs.id", ondelete="CASCADE"), nullable=False, index=True)
    check_id = Column(String(36), nullable=True, index=True)
    source_module = Column(String(32), nullable=False)  # module_1, module_2, module_3, module_4, module_5, module_6, module_7
    source_record_id = Column(String(64), nullable=True)
    evidence_type = Column(String(64), nullable=False)  # service_health, metric_observation, event_log, graph_topology, alert_record, precondition_status
    description = Column(Text, nullable=False)
    observed_or_simulated = Column(String(32), nullable=False, default="simulated")  # observed, simulated, synthetic, inferred
    timestamp_or_step = Column(String(32), nullable=True)
    metadata_json = Column(Text, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    # Relationships
    validation_run = relationship("ValidationRunModel", back_populates="evidence")

class ValidationRecommendationModel(Base):
    __tablename__ = "validation_recommendations"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    validation_id = Column(String(36), ForeignKey("validation_runs.id", ondelete="CASCADE"), nullable=False, index=True)
    recommendation_type = Column(String(64), nullable=False)  # investigate_service, test_alternative_plan, extend_verification_window, collect_metrics, review_downstream, review_preconditions
    priority = Column(String(16), nullable=False, default="MEDIUM")  # CRITICAL, HIGH, MEDIUM, LOW
    description = Column(Text, nullable=False)
    related_service_id = Column(String(64), nullable=True)
    supporting_evidence_json = Column(Text, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    # Relationships
    validation_run = relationship("ValidationRunModel", back_populates="recommendations")

class ValidationConfigModel(Base):
    __tablename__ = "validation_config"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    config_key = Column(String(64), unique=True, index=True, nullable=False)
    config_value = Column(Text, nullable=False)
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)
