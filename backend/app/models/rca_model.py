from datetime import datetime, timezone
from sqlalchemy import Column, String, Float, Boolean, Integer, DateTime, Text, ForeignKey, Index
from sqlalchemy.orm import relationship
from app.database.database import Base

class RCAIncidentModel(Base):
    __tablename__ = "rca_incidents"

    id = Column(String(64), primary_key=True, index=True)
    title = Column(String(128), nullable=False, index=True)
    status = Column(String(32), nullable=False, default="investigating")  # investigating, completed, inconclusive
    investigation_window_start = Column(DateTime, nullable=True)
    investigation_window_end = Column(DateTime, nullable=True)
    affected_service_ids = Column(Text, nullable=False)  # JSON-encoded list of service IDs
    target_service_id = Column(String(64), nullable=True, index=True)
    scenario_id = Column(String(64), nullable=True, index=True)  # Optional linked Module 3 scenario ID
    data_source = Column(String(32), nullable=False, default="simulated")
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), index=True)
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    # Relationships
    evidence_items = relationship("RCAEvidenceModel", back_populates="incident", cascade="all, delete-orphan", order_by="RCAEvidenceModel.timestamp")
    candidates = relationship("RCACandidateModel", back_populates="incident", cascade="all, delete-orphan", order_by="RCACandidateModel.rank")
    report = relationship("RCAReportModel", back_populates="incident", uselist=False, cascade="all, delete-orphan")


class RCAEvidenceModel(Base):
    __tablename__ = "rca_evidence"

    id = Column(String(64), primary_key=True, index=True)
    incident_id = Column(String(64), ForeignKey("rca_incidents.id", ondelete="CASCADE"), nullable=False, index=True)
    service_id = Column(String(64), nullable=False, index=True)
    service_name = Column(String(128), nullable=False)
    evidence_type = Column(String(64), nullable=False, index=True)
    metric_name = Column(String(64), nullable=True)
    observed_value = Column(Float, nullable=True)
    expected_or_threshold_value = Column(Float, nullable=True)
    timestamp = Column(DateTime, nullable=True, index=True)
    source_module = Column(String(32), nullable=False)  # Module 1, Module 2, Module 3, Temporal Engine
    source_record_id = Column(String(64), nullable=True)
    evidence_summary = Column(Text, nullable=False)
    data_source = Column(String(32), nullable=False, default="simulated")
    reliability_score = Column(Float, nullable=False, default=0.9)
    is_contradictory = Column(Boolean, nullable=False, default=False)
    evidence_json = Column(Text, nullable=True)  # Supplementary JSON metadata

    incident = relationship("RCAIncidentModel", back_populates="evidence_items")

    __table_args__ = (
        Index("ix_rca_evidence_incident_service", "incident_id", "service_id"),
    )


class RCACandidateModel(Base):
    __tablename__ = "rca_candidates"

    id = Column(String(64), primary_key=True, index=True)
    incident_id = Column(String(64), ForeignKey("rca_incidents.id", ondelete="CASCADE"), nullable=False, index=True)
    service_id = Column(String(64), nullable=False, index=True)
    service_name = Column(String(128), nullable=False)
    rank = Column(Integer, nullable=False)
    ranking_score = Column(Float, nullable=False)  # Normalized 0-100 score
    confidence_label = Column(String(32), nullable=False)  # Strong, Moderate, Weak, Insufficient
    confidence_score = Column(Float, nullable=False)  # Normalized 0.0 - 1.0 heuristic confidence
    result_json = Column(Text, nullable=False)  # JSON-encoded details (evidence_for, evidence_against, paths, etc.)

    incident = relationship("RCAIncidentModel", back_populates="candidates")

    __table_args__ = (
        Index("ix_rca_candidates_incident_rank", "incident_id", "rank"),
    )


class RCAReportModel(Base):
    __tablename__ = "rca_reports"

    id = Column(String(64), primary_key=True, index=True)
    incident_id = Column(String(64), ForeignKey("rca_incidents.id", ondelete="CASCADE"), nullable=False, unique=True, index=True)
    report_json = Column(Text, nullable=False)  # Full JSON investigation audit report
    algorithm_version = Column(String(32), nullable=False, default="4.0.0")
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), index=True)

    incident = relationship("RCAIncidentModel", back_populates="report")
