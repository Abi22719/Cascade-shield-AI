import tempfile
import os
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database.database import Base
from app.models.service import ServiceModel
from app.models.alert_model import AlertModel
from app.database.alert_repository import AlertRepository

def test_alert_persistence_across_sessions():
    """Verify alerts persist in SQLite after closing and reopening database connection."""
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tmp:
        db_path = tmp.name

    try:
        engine1 = create_engine(f"sqlite:///{db_path}")
        Base.metadata.create_all(bind=engine1)
        Session1 = sessionmaker(bind=engine1)
        s1 = Session1()

        # Create service first for foreign key
        svc = ServiceModel(
            id="srv-persist-test",
            name="Persistence Test Service",
            service_type="compute",
            health_status="CRITICAL",
            cpu_usage=95.0,
            memory_usage=90.0,
            latency_ms=1200.0,
            error_rate=15.0,
            request_volume=1000
        )
        s1.add(svc)
        s1.commit()

        # Create alert
        alert = AlertRepository.create_alert(
            db=s1,
            service_id="srv-persist-test",
            service_name="Persistence Test Service",
            metric_name="latency_ms",
            observed_value=1200.0,
            threshold_value=1000.0,
            severity="Critical",
            detection_method="threshold",
            anomaly_score=None,
            evidence_summary="Latency critical spike: 1200ms >= 1000ms."
        )
        saved_id = alert.id
        s1.close()
        engine1.dispose()

        # Reopen with fresh engine pointing to same sqlite file
        engine2 = create_engine(f"sqlite:///{db_path}")
        Session2 = sessionmaker(bind=engine2)
        s2 = Session2()

        retrieved = AlertRepository.get_alert_by_id(s2, saved_id)
        assert retrieved is not None
        assert retrieved.service_id == "srv-persist-test"
        assert retrieved.severity == "Critical"
        assert retrieved.observed_value == 1200.0

        s2.close()
        engine2.dispose()
    finally:
        if os.path.exists(db_path):
            os.remove(db_path)

def test_alert_deduplication(db_session):
    """Verify duplicate unacknowledged alerts for identical condition are blocked."""
    # First alert
    AlertRepository.create_alert(
        db=db_session,
        service_id="srv-gateway",
        service_name="API Gateway",
        metric_name="cpu_usage",
        observed_value=92.0,
        threshold_value=90.0,
        severity="Critical",
        detection_method="threshold",
        anomaly_score=None,
        evidence_summary="CPU spike"
    )

    # Check deduplication check
    is_dup = AlertRepository.is_duplicate_alert(
        db=db_session,
        service_id="srv-gateway",
        metric_name="cpu_usage",
        severity="Critical",
        window_minutes=15
    )
    assert is_dup is True

    # Different metric or severity is not duplicate
    is_not_dup = AlertRepository.is_duplicate_alert(
        db=db_session,
        service_id="srv-gateway",
        metric_name="latency_ms",
        severity="Critical",
        window_minutes=15
    )
    assert is_not_dup is False
