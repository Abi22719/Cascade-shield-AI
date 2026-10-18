import pytest
import math
from datetime import datetime, timezone
from app.schemas.metric_schema import MetricPoint
from app.schemas.anomaly_schema import ThresholdConfig
from app.services.threshold_detector import ThresholdDetector

@pytest.fixture
def detector():
    return ThresholdDetector(
        ThresholdConfig(
            cpu_warning=75.0,
            cpu_critical=90.0,
            memory_warning=80.0,
            memory_critical=95.0,
            latency_warning=500.0,
            latency_critical=1000.0,
            error_rate_warning=5.0,
            error_rate_critical=10.0
        )
    )

def test_normal_metrics_no_violations(detector):
    """Verify normal metrics do not generate any warnings or critical alerts."""
    metric = MetricPoint(
        timestamp=datetime.now(timezone.utc),
        service_id="srv-gw",
        cpu_usage=25.0,
        memory_usage=40.0,
        latency_ms=45.0,
        error_rate=0.1,
        request_volume=2000
    )
    violations = detector.evaluate(metric)
    assert len(violations) == 0

def test_warning_thresholds(detector):
    """Verify warning alerts are triggered when metrics exceed warning but below critical."""
    # Elevated CPU (80%)
    m_cpu = MetricPoint(
        timestamp=datetime.now(timezone.utc),
        service_id="srv-gw",
        cpu_usage=80.0,
        memory_usage=40.0,
        latency_ms=50.0,
        error_rate=0.1,
        request_volume=1000
    )
    v_cpu = detector.evaluate(m_cpu)
    assert len(v_cpu) == 1
    assert v_cpu[0].severity == "Warning"
    assert v_cpu[0].metric_name == "cpu_usage"

    # Elevated Latency (650ms)
    m_lat = MetricPoint(
        timestamp=datetime.now(timezone.utc),
        service_id="srv-gw",
        cpu_usage=30.0,
        memory_usage=40.0,
        latency_ms=650.0,
        error_rate=0.1,
        request_volume=1000
    )
    v_lat = detector.evaluate(m_lat)
    assert len(v_lat) == 1
    assert v_lat[0].severity == "Warning"
    assert v_lat[0].metric_name == "latency_ms"

def test_critical_thresholds(detector):
    """Verify critical alerts are triggered when metrics exceed critical threshold."""
    m_crit = MetricPoint(
        timestamp=datetime.now(timezone.utc),
        service_id="srv-db",
        cpu_usage=95.0,
        memory_usage=96.0,
        latency_ms=1200.0,
        error_rate=15.0,
        request_volume=4000
    )
    violations = detector.evaluate(m_crit)
    assert len(violations) == 4
    for v in violations:
        assert v.severity == "Critical"

def test_threshold_updates_affect_detection(detector):
    """Verify modifying threshold config changes detection behavior."""
    metric = MetricPoint(
        timestamp=datetime.now(timezone.utc),
        service_id="srv-auth",
        cpu_usage=70.0,
        memory_usage=50.0,
        latency_ms=100.0,
        error_rate=1.0,
        request_volume=1000
    )
    # Initially 70% CPU is below warning (75%)
    assert len(detector.evaluate(metric)) == 0

    # Lower warning threshold to 65%
    new_cfg = ThresholdConfig(
        cpu_warning=65.0,
        cpu_critical=90.0
    )
    detector.update_config(new_cfg)
    violations = detector.evaluate(metric)
    assert len(violations) == 1
    assert violations[0].severity == "Warning"
    assert violations[0].metric_name == "cpu_usage"

def test_invalid_threshold_order_rejected():
    """Verify warning > critical is rejected by schema validator."""
    with pytest.raises(ValueError):
        ThresholdConfig(cpu_warning=95.0, cpu_critical=80.0)
