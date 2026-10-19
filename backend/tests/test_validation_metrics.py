import pytest
from app.services.validation_metrics import ValidationMetricsEngine
from app.schemas.validation_schemas import ValidationConfigSchema

def test_zero_and_missing_metric_values():
    # Zero to zero
    pct = ValidationMetricsEngine.calculate_percent_change(0.0, 0.0)
    assert pct == 0.0

    # Zero to positive
    pct_pos = ValidationMetricsEngine.calculate_percent_change(0.0, 50.0)
    assert pct_pos == 100.0

    # Missing value
    pct_none = ValidationMetricsEngine.calculate_percent_change(None, 50.0)
    assert pct_none is None

    # Trend with None
    trend, delta, pct = ValidationMetricsEngine.evaluate_metric_trend("latency_ms", None, 100.0)
    assert trend == "UNKNOWN"
    assert delta is None

def test_metric_trend_lower_is_better():
    # Latency drops from 500 to 120 -> IMPROVED
    trend, delta, pct = ValidationMetricsEngine.evaluate_metric_trend("latency_ms", 500.0, 120.0)
    assert trend == "IMPROVED"
    assert delta == -380.0
    assert pct == -76.0

    # Error rate surges from 1.0 to 15.0 -> WORSENED
    trend_w, delta_w, pct_w = ValidationMetricsEngine.evaluate_metric_trend("error_rate", 1.0, 15.0)
    assert trend_w == "WORSENED"
    assert delta_w == 14.0

def test_metric_threshold_evaluation():
    cfg = ValidationConfigSchema(max_acceptable_latency_ms=400.0, max_acceptable_error_rate=5.0)
    diffs = ValidationMetricsEngine.validate_service_metrics(
        service_id="srv-payment",
        service_name="Payment Gateway",
        before_metrics={"latency_ms": 600.0, "error_rate": 8.0, "cpu_usage": 70.0, "memory_usage": 60.0, "request_volume": 100.0},
        after_metrics={"latency_ms": 150.0, "error_rate": 1.2, "cpu_usage": 50.0, "memory_usage": 55.0, "request_volume": 100.0},
        config=cfg
    )

    latency_diff = next(d for d in diffs if d.metric_name == "latency_ms")
    assert latency_diff.status == "PASS"
    assert latency_diff.trend == "IMPROVED"

    err_diff = next(d for d in diffs if d.metric_name == "error_rate")
    assert err_diff.status == "PASS"
    assert err_diff.trend == "IMPROVED"
