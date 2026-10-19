import pytest
from app.services.scenario_builder import ScenarioBuilder

def test_scenario_builder_options(db_session):
    options = ScenarioBuilder.get_simulation_options(db_session)
    assert "services" in options
    assert "failure_types" in options
    assert "severities" in options
    assert "recovery_modes" in options
    assert "presets" in options
    assert "limits" in options
    
    # Check failure types
    ft_ids = [f["id"] for f in options["failure_types"]]
    assert "service_unavailable" in ft_ids
    assert "high_latency" in ft_ids
    assert "error_rate_surge" in ft_ids
    assert "cpu_saturation" in ft_ids
    assert "memory_exhaustion" in ft_ids
    assert "database_starvation" in ft_ids

    # Check presets
    assert len(options["presets"]) >= 4
    preset_names = [p["name"] for p in options["presets"]]
    assert any("Payment" in n for n in preset_names)
    assert any("Database" in n for n in preset_names)

    # Check services loaded from db_session
    svc_ids = [s["id"] for s in options["services"]]
    assert "srv-payment" in svc_ids
    assert "srv-gateway" in svc_ids
