from datetime import datetime, timezone
from sqlalchemy import Column, String, Float, Boolean, DateTime, Text, ForeignKey, Index
from sqlalchemy.orm import relationship
from app.database.database import Base

class AlertModel(Base):
    __tablename__ = "alerts"

    id = Column(String(64), primary_key=True, index=True)
    service_id = Column(
        String(64),
        ForeignKey("services.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    service_name = Column(String(128), nullable=False)
    metric_name = Column(String(64), nullable=False, index=True)
    observed_value = Column(Float, nullable=True)
    threshold_value = Column(Float, nullable=True)
    severity = Column(String(32), nullable=False, index=True)  # Normal, Warning, Critical
    detection_method = Column(String(32), nullable=False, index=True)  # threshold, isolation_forest, combined
    anomaly_score = Column(Float, nullable=True)
    evidence_summary = Column(Text, nullable=False)
    data_source = Column(String(32), nullable=False, default="simulated")
    acknowledged = Column(Boolean, nullable=False, default=False, index=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), index=True)

    # Relationship to ServiceModel
    service = relationship("ServiceModel", foreign_keys=[service_id])

    __table_args__ = (
        Index("ix_alerts_service_severity", "service_id", "severity"),
        Index("ix_alerts_created_severity", "created_at", "severity"),
    )
