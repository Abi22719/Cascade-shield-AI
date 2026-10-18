import pytest
from app.services.propagation_simulator import PropagationSimulator
from app.schemas.cascade_schema import ImpactedServiceResult, CascadePathInfo

def test_propagation_timeline_generation():
    root_result = ImpactedServiceResult(
        service_id="srv-payment",
        service_name="Payment Service",
        service_type="backend",
        impact_type="Root Failure",
        hop_distance=0,
        estimated_risk_score=95.0,
        risk_level="Critical",
        propagation_probability_estimate=1.0,
        contributing_evidence=[],
        impacted_by_services=[],
        failure_paths=[],
        recommended_monitoring_action="Restart service",
        estimated_step_onset=0
    )

    order_result = ImpactedServiceResult(
        service_id="srv-order",
        service_name="Order Service",
        service_type="backend",
        impact_type="Direct",
        hop_distance=1,
        estimated_risk_score=75.0,
        risk_level="Critical",
        propagation_probability_estimate=0.8,
        contributing_evidence=[],
        impacted_by_services=["srv-payment"],
        failure_paths=[],
        recommended_monitoring_action="Trip circuit breaker",
        estimated_step_onset=1
    )

    gw_result = ImpactedServiceResult(
        service_id="srv-gw",
        service_name="API Gateway",
        service_type="gateway",
        impact_type="Indirect",
        hop_distance=2,
        estimated_risk_score=55.0,
        risk_level="High",
        propagation_probability_estimate=0.6,
        contributing_evidence=[],
        impacted_by_services=["srv-order"],
        failure_paths=[],
        recommended_monitoring_action="Rate limit ingress",
        estimated_step_onset=2
    )

    timeline = PropagationSimulator.simulate_propagation_timeline(
        root_service_id="srv-payment",
        root_service_name="Payment Service",
        failure_type="service_unavailable",
        failure_severity="severe",
        impacted_results=[root_result, order_result, gw_result],
        max_steps=4
    )

    # Must contain step 0 through 4 (5 records)
    assert len(timeline) == 5
    assert timeline[0].step == 0
    assert timeline[0].newly_affected_services == ["Payment Service"]
    assert timeline[0].cumulative_affected_count == 1

    assert timeline[1].step == 1
    assert "Order Service" in timeline[1].newly_affected_services
    assert timeline[1].cumulative_affected_count == 2

    assert timeline[2].step == 2
    assert "API Gateway" in timeline[2].newly_affected_services
    assert timeline[2].cumulative_affected_count == 3

    # Steps after max propagation should stabilize
    assert timeline[3].step == 3
    assert timeline[3].newly_affected_services == []
    assert timeline[3].cumulative_affected_count == 3
