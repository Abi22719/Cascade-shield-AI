import pytest
from datetime import datetime, timezone
from app.schemas.metric_schema import MetricPoint
from app.services.anomaly_detector import IsolationForestDetector

def test_isolation_forest_cold_start_without_prior_fit():
    """Verify detector auto-fits baseline cluster safely if called without explicit fit."""
    detector = IsolationForestDetector(contamination=0.1, random_state=42)
    metric = MetricPoint(
        timestamp=datetime.now(timezone.utc),
        service_id="srv-test",
        cpu_usage=30.0,
        memory_usage=40.0,
        latency_ms=45.0,
        error_rate=0.1,
        request_volume=1500
    )
    result = detector.detect_single(metric)
    assert "is_anomaly" in result
    assert "anomaly_score" in result
    assert detector.is_fitted is True

def test_isolation_forest_insufficient_training_data():
    """Verify fitting on 0 or 1 observation produces controlled response via baseline synthesis."""
    detector = IsolationForestDetector(contamination=0.1, random_state=42)
    single_metric = [
        MetricPoint(
            timestamp=datetime.now(timezone.utc),
            service_id="srv-solo",
            cpu_usage=20.0,
            memory_usage=30.0,
            latency_ms=25.0,
            error_rate=0.05,
            request_volume=500
        )
    ]
    # Should not crash on len < 2
    success = detector.fit(single_metric)
    assert success is True
    assert detector.training_sample_count > 0

def test_isolation_forest_detects_multivariate_outliers():
    """Verify Isolation Forest flags multidimensional anomalous combinations."""
    detector = IsolationForestDetector(contamination=0.1, random_state=42)
    # Fit baseline
    detector.fit([])

    # Extremely unusual combination: 1.0% CPU with 15000 req/s and 1200ms latency
    weird_metric = MetricPoint(
        timestamp=datetime.now(timezone.utc),
        service_id="srv-anomaly",
        cpu_usage=1.0,
        memory_usage=95.0,
        latency_ms=1800.0,
        error_rate=12.0,
        request_volume=15000
    )
    result = detector.detect_single(weird_metric)
    assert result["is_anomaly"] is True
    assert result["top_deviating_feature"] is not None

def test_isolation_forest_reproducibility():
    """Verify identical random state produces identical anomaly scores."""
    d1 = IsolationForestDetector(contamination=0.1, random_state=99)
    d2 = IsolationForestDetector(contamination=0.1, random_state=99)
    d1.fit([])
    d2.fit([])

    m = MetricPoint(
        timestamp=datetime.now(timezone.utc),
        service_id="srv-gw",
        cpu_usage=45.0,
        memory_usage=55.0,
        latency_ms=85.0,
        error_rate=0.3,
        request_volume=2200
    )
    res1 = d1.detect_single(m)
    res2 = d2.detect_single(m)
    assert res1["anomaly_score"] == res2["anomaly_score"]
