from datetime import datetime, timezone
from sqlalchemy import Column, String, Float, Integer, DateTime, Text
from sqlalchemy.orm import relationship
from app.database.database import Base

class ServiceModel(Base):
    __tablename__ = "services"

    id = Column(String(64), primary_key=True, index=True)
    name = Column(String(128), nullable=False, index=True)
    service_type = Column(String(64), nullable=False, index=True)
    description = Column(Text, nullable=True)
    health_status = Column(String(32), nullable=False, default="HEALTHY", index=True)
    cpu_usage = Column(Float, nullable=False, default=20.0)
    memory_usage = Column(Float, nullable=False, default=30.0)
    latency_ms = Column(Float, nullable=False, default=45.0)
    error_rate = Column(Float, nullable=False, default=0.1)
    request_volume = Column(Integer, nullable=False, default=150)
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    # Relationships
    outgoing_dependencies = relationship(
        "DependencyModel",
        foreign_keys="DependencyModel.source_service_id",
        back_populates="source_service",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )

    incoming_dependencies = relationship(
        "DependencyModel",
        foreign_keys="DependencyModel.target_service_id",
        back_populates="target_service",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )
