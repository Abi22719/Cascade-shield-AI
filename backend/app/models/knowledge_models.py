import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Integer, Float, Text, DateTime, ForeignKey, Boolean
from app.database.database import Base

def generate_uuid() -> str:
    return str(uuid.uuid4())

class KnowledgeArticleModel(Base):
    __tablename__ = "knowledge_articles"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    title = Column(String(160), nullable=False, index=True)
    category = Column(String(32), nullable=False, default="troubleshooting", index=True)
    # Categories: troubleshooting, sop, playbook, postmortem, faq
    summary = Column(Text, nullable=False)
    content = Column(Text, nullable=False)
    service_id = Column(String(64), nullable=True, index=True)
    tags_json = Column(Text, nullable=True)  # JSON array of tags
    author = Column(String(128), nullable=False, default="CascadeShield Reliability Team")
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False, index=True)
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)
