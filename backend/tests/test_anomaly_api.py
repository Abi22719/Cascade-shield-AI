import pytest

def test_anomaly_health_endpoint(client):
    """Verify health endpoint of anomaly subsystem returns 200."""
    res = client.get("/api/anomalies/health")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "online"
    assert data["threshold_engine"] == "ready"

def test_anomaly_summary_endpoint(client):
    """Verify anomaly summary returns expected counters."""
    res = client.get("/api/anomalies/summary")
    assert res.status_code == 200
    data = res.json()
    assert "total_alerts" in data
    assert "critical_alerts" in data
    assert "warning_alerts" in data
    assert "affected_services" in data

def test_detect_anomalies_endpoint(client):
    """Verify triggering anomaly detection on default services."""
    res = client.post("/api/anomalies/detect", json={"method": "combined"})
    assert res.status_code == 200
    data = res.json()
    assert "total_evaluated" in data
    assert data["total_evaluated"] >= 9
    assert "anomalies_detected" in data
    assert "results" in data

def test_detect_with_custom_metrics_spike(client):
    """Verify detection endpoint detects injected custom metric spike."""
    custom_metrics = [
        {
            "service_id": "srv-gateway",
            "service_name": "API Gateway",
            "cpu_usage": 98.0,
            "memory_usage": 95.0,
            "latency_ms": 1500.0,
            "error_rate": 22.0,
            "request_volume": 6000,
            "data_source": "simulated"
        }
    ]
    res = client.post("/api/anomalies/detect", json={
        "method": "combined",
        "custom_metrics": custom_metrics
    })
    assert res.status_code == 200
    data = res.json()
    assert data["anomalies_detected"] == 1
    assert data["results"][0]["severity"] == "Critical"
    assert data["results"][0]["is_anomaly"] is True

def test_thresholds_get_and_put(client):
    """Verify retrieving and updating thresholds."""
    get_res = client.get("/api/anomalies/thresholds")
    assert get_res.status_code == 200
    cfg = get_res.json()
    assert "cpu_warning" in cfg

    # Update thresholds
    update_res = client.put("/api/anomalies/thresholds", json={
        "cpu_warning": 70.0,
        "cpu_critical": 88.0,
        "memory_warning": 75.0,
        "memory_critical": 90.0,
        "latency_warning": 450.0,
        "latency_critical": 900.0,
        "error_rate_warning": 4.0,
        "error_rate_critical": 8.0
    })
    assert update_res.status_code == 200
    updated = update_res.json()
    assert updated["cpu_warning"] == 70.0

def test_service_metrics_history(client):
    """Verify fetching metric history for an existing service."""
    res = client.get("/api/anomalies/metrics/srv-gateway?points=20")
    assert res.status_code == 200
    data = res.json()
    assert data["service_id"] == "srv-gateway"
    assert len(data["metrics"]) == 20
    assert data["data_source"] == "simulated"

def test_service_metrics_history_not_found(client):
    """Verify 404 for non-existent service ID."""
    res = client.get("/api/anomalies/metrics/srv-nonexistent")
    assert res.status_code == 404

def test_acknowledge_alert_flow(client):
    """Verify creating an alert and acknowledging it."""
    # Inject anomaly to create an alert
    inject_res = client.post("/api/anomalies/detect", json={
        "method": "threshold",
        "custom_metrics": [
            {
                "service_id": "srv-user",
                "service_name": "User Service",
                "cpu_usage": 96.0,
                "memory_usage": 50.0,
                "latency_ms": 100.0,
                "error_rate": 0.1,
                "request_volume": 1000
            }
        ]
    })
    results = inject_res.json()["results"]
    assert len(results) > 0
    alert_id = results[0]["alert_id"]
    assert alert_id is not None

    # Fetch alert by ID
    get_alt = client.get(f"/api/anomalies/{alert_id}")
    assert get_alt.status_code == 200
    assert get_alt.json()["acknowledged"] is False

    # Acknowledge
    ack_res = client.post(f"/api/anomalies/{alert_id}/acknowledge")
    assert ack_res.status_code == 200
    assert ack_res.json()["acknowledged"] is True
