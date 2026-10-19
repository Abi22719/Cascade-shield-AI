import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Integer, Float, Text, DateTime, ForeignKey, Boolean
from app.database.database import Base

def generate_uuid() -> str:
    return str(uuid.uuid4())

class NotificationModel(Base):
    __tablename__ = "notifications"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    event_type = Column(String(64), nullable=False, index=True)
    source_module = Column(String(32), nullable=False, index=True)
    source_record_id = Column(String(64), nullable=True, index=True)
    title = Column(String(128), nullable=False)
    message = Column(Text, nullable=False)
    severity = Column(String(16), nullable=False, default="INFO", index=True)  # CRITICAL, WARNING, INFO, SUCCESS
    read_status = Column(Boolean, nullable=False, default=False, index=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False, index=True)

class ActivityEventModel(Base):
    __tablename__ = "activity_events"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    event_type = Column(String(64), nullable=False, index=True)
    source_module = Column(String(32), nullable=False, index=True)
    source_record_id = Column(String(64), nullable=True, index=True)
    related_incident_id = Column(String(64), nullable=True, index=True)
    description = Column(Text, nullable=False)
    metadata_json = Column(Text, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False, index=True)

class GeneratedReportModel(Base):
    __tablename__ = "generated_reports"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    report_type = Column(String(64), nullable=False, index=True)
    report_title = Column(String(128), nullable=False)
    related_record_id = Column(String(64), nullable=True, index=True)
    data_source = Column(String(32), nullable=False, default="simulated")  # observed, simulated, synthetic, inferred
    report_format = Column(String(16), nullable=False, default="json")     # json, csv, markdown, pdf_text
    report_status = Column(String(32), nullable=False, default="COMPLETED")  # PENDING, COMPLETED, FAILED
    content = Column(Text, nullable=True)
    metadata_json = Column(Text, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False, index=True)
    completed_at = Column(DateTime, nullable=True)
