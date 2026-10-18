from sqlalchemy import Column, String, Text, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from app.database.database import Base

class DependencyModel(Base):
    __tablename__ = "dependencies"

    id = Column(String(128), primary_key=True, index=True)
    source_service_id = Column(
        String(64),
        ForeignKey("services.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    target_service_id = Column(
        String(64),
        ForeignKey("services.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    dependency_type = Column(String(64), nullable=False, default="sync_http")
    description = Column(Text, nullable=True)

    __table_args__ = (
        UniqueConstraint("source_service_id", "target_service_id", name="uq_source_target_dependency"),
    )

    source_service = relationship(
        "ServiceModel",
        foreign_keys=[source_service_id],
        back_populates="outgoing_dependencies"
    )
    target_service = relationship(
        "ServiceModel",
        foreign_keys=[target_service_id],
        back_populates="incoming_dependencies"
    )
