import pytest
from app.services.risk_scorer import RiskScorer
from app.schemas.cascade_schema import CascadePathInfo
from app.models.alert_model import AlertModel

def test_risk_level_categorization():
    assert RiskScorer.get_risk_level(85.0) == "Critical"
    assert RiskScorer.get_risk_level(75.0) == "Critical"
    assert RiskScorer.get_risk_level(74.9) == "High"
    assert RiskScorer.get_risk_level(50.0) == "High"
    assert RiskScorer.get_risk_level(49.9) == "Moderate"
    assert RiskScorer.get_risk_level(25.0) == "Moderate"
    assert RiskScorer.get_risk_level(24.9) == "Low"
    assert RiskScorer.get_risk_level(0.0) == "Low"

def test_risk_score_attenuates_with_hop_distance():
    service_node = {
        "service_type": "backend",
        "health_status": "healthy",
        "cpu_usage": 30.0,
        "memory_usage": 40.0,
        "latency_ms": 50.0,
        "error_rate": 0.01
    }

    # Direct caller (hop 1)
    p_hop1 = CascadePathInfo(
        path=["srv-db", "srv-order"],
        path_names=["DB", "Order"],
        hop_count=1,
        dependency_types=["sync_http"],
        risk_contribution=0.0,
        evidence=""
    )
    score_hop1, level1, prob1, _ = RiskScorer.calculate_service_cascade_risk(
        service_node=service_node,
        hop_distance=1,
        failure_type="latency_spike",
        failure_severity="severe",
        paths_to_service=[p_hop1],
        recent_alerts=[],
        attenuation_factor=0.75
    )

    # Indirect caller (hop 2)
    p_hop2 = CascadePathInfo(
        path=["srv-db", "srv-order", "srv-gw"],
        path_names=["DB", "Order", "Gateway"],
        hop_count=2,
        dependency_types=["sync_http", "sync_http"],
        risk_contribution=0.0,
        evidence=""
    )
    score_hop2, level2, prob2, _ = RiskScorer.calculate_service_cascade_risk(
        service_node=service_node,
        hop_distance=2,
        failure_type="latency_spike",
        failure_severity="severe",
        paths_to_service=[p_hop2],
        recent_alerts=[],
        attenuation_factor=0.75
    )

    # Score should decay with distance
    assert score_hop1 > score_hop2
    assert prob1 > prob2
    assert 0.0 <= score_hop1 <= 100.0
    assert 0.0 <= score_hop2 <= 100.0

def test_protocol_coupling_weights():
    service_node = {
        "service_type": "backend",
        "health_status": "healthy",
        "cpu_usage": 30.0,
        "memory_usage": 40.0,
        "latency_ms": 50.0,
        "error_rate": 0.01
    }

    # Synchronous HTTP path
    p_sync = CascadePathInfo(
        path=["srv-auth", "srv-order"],
        path_names=["Auth", "Order"],
        hop_count=1,
        dependency_types=["sync_http"],
        risk_contribution=0.0,
        evidence=""
    )
    score_sync, _, _, _ = RiskScorer.calculate_service_cascade_risk(
        service_node=service_node,
        hop_distance=1,
        failure_type="service_unavailable",
        failure_severity="severe",
        paths_to_service=[p_sync],
        recent_alerts=[]
    )

    # Asynchronous Message path
    p_async = CascadePathInfo(
        path=["srv-auth", "srv-audit"],
        path_names=["Auth", "Audit"],
        hop_count=1,
        dependency_types=["async_message"],
        risk_contribution=0.0,
        evidence=""
    )
    score_async, _, _, _ = RiskScorer.calculate_service_cascade_risk(
        service_node=service_node,
        hop_distance=1,
        failure_type="service_unavailable",
        failure_severity="severe",
        paths_to_service=[p_async],
        recent_alerts=[]
    )

    # Sync coupling must produce significantly higher cascade risk than async decoupling
    assert score_sync > score_async

def test_alert_amplification():
    service_node = {
        "id": "srv-order",
        "service_type": "backend",
        "health_status": "healthy",
        "cpu_usage": 30.0,
        "memory_usage": 40.0,
        "latency_ms": 50.0,
        "error_rate": 0.01
    }
    p = CascadePathInfo(
        path=["srv-db", "srv-order"],
        path_names=["DB", "Order"],
        hop_count=1,
        dependency_types=["sync_http"],
        risk_contribution=0.0,
        evidence=""
    )

    # Without alert
    score_clean, _, _, _ = RiskScorer.calculate_service_cascade_risk(
        service_node=service_node,
        hop_distance=1,
        failure_type="latency_spike",
        failure_severity="moderate",
        paths_to_service=[p],
        recent_alerts=[]
    )

    # With critical alert from Module 2
    mock_alert = AlertModel(
        id="alt-1",
        service_id="srv-order",
        service_name="Order Service",
        metric_name="latency_ms",
        severity="Critical",
        detection_method="threshold",
        evidence_summary="High latency alert",
        acknowledged=False
    )
    score_alerted, _, _, evidence = RiskScorer.calculate_service_cascade_risk(
        service_node=service_node,
        hop_distance=1,
        failure_type="latency_spike",
        failure_severity="moderate",
        paths_to_service=[p],
        recent_alerts=[mock_alert]
    )

    assert score_alerted > score_clean
    assert any("Module 2 Anomaly Alert" in e for e in evidence)
