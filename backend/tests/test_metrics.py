import os
import tempfile
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database.database import Base
from app.database.init_db import init_db
from app.models.service import ServiceModel
from app.models.dependency import DependencyModel

def test_metrics_summary_baseline(client):
    """Verify metrics summary returns aggregate stats and simulated telemetry label."""
    res = client.get("/api/metrics/summary")
    assert res.status_code == 200
    data = res.json()

    assert data["total_services"] == 9
    assert data["healthy_services"] == 9
    assert data["warning_services"] == 0
    assert data["critical_services"] == 0
    assert data["health_score_pct"] == 100.0
    assert data["avg_latency_ms"] > 0
    assert data["total_request_volume"] > 0
    assert data["telemetry_type"] == "simulated"

def test_metrics_summary_with_degraded_services(client):
    """Verify metrics summary updates dynamically when service health changes."""
    # Degrade database to CRITICAL
    client.put("/api/services/srv-database", json={"error_rate": 18.0, "latency_ms": 1500.0})

    # Degrade product to WARNING
    client.put("/api/services/srv-product", json={"cpu_usage": 82.0})

    res = client.get("/api/metrics/summary")
    assert res.status_code == 200
    data = res.json()

    assert data["total_services"] == 9
    assert data["critical_services"] == 1
    assert data["warning_services"] == 1
    assert data["healthy_services"] == 7
    # 7 * 100 + 1 * 50 = 750 / 9 = 83.3%
    assert 80.0 <= data["health_score_pct"] <= 85.0

def test_sqlite_data_persistence():
    """
    Verify data persists after closing and reopening database connection.
    Tests real SQLite file persistence requirement.
    """
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tmp_file:
        tmp_db_path = tmp_file.name

    try:
        engine1 = create_engine(f"sqlite:///{tmp_db_path}")
        Base.metadata.create_all(bind=engine1)
        Session1 = sessionmaker(bind=engine1)
        s1 = Session1()

        # Seed data
        init_db(s1, force_reset=True)
        assert s1.query(ServiceModel).count() == 9
        assert s1.query(DependencyModel).count() == 9

        # Add a custom service
        custom_svc = ServiceModel(
            id="srv-custom-persisted",
            name="Persisted Custom Service",
            service_type="compute",
            health_status="HEALTHY",
            cpu_usage=10.0,
            memory_usage=20.0,
            latency_ms=15.0,
            error_rate=0.0,
            request_volume=100
        )
        s1.add(custom_svc)
        s1.commit()
        s1.close()
        engine1.dispose()

        # Simulate backend restart with a brand new engine pointing to same sqlite file
        engine2 = create_engine(f"sqlite:///{tmp_db_path}")
        Session2 = sessionmaker(bind=engine2)
        s2 = Session2()

        # Verify not duplicating data on second init_db call
        init_db(s2, force_reset=False)

        # Verify the custom service is still there
        retrieved = s2.query(ServiceModel).filter(ServiceModel.id == "srv-custom-persisted").first()
        assert retrieved is not None
        assert retrieved.name == "Persisted Custom Service"
        assert s2.query(ServiceModel).count() == 10

        s2.close()
        engine2.dispose()
    finally:
        import gc
        gc.collect()
        if os.path.exists(tmp_db_path):
            try:
                os.remove(tmp_db_path)
            except Exception:
                pass
