from typing import Dict, Any, List
from app.schemas.simulation_schema import FailureInjectionConfig, SimulatedServiceState

class FailureModel:
    """
    Applies initial simulated failure injections to target services.
    Calculates deterministic metric deviations and health status transitions.
    """

    SEVERITY_FACTORS = {
        "mild": 0.5,
        "moderate": 0.8,
        "severe": 1.0
    }

    @classmethod
    def apply_initial_failure(
        cls, 
        service: SimulatedServiceState, 
        config: FailureInjectionConfig
    ) -> Dict[str, Any]:
        sev = cls.SEVERITY_FACTORS.get(config.severity.lower(), 1.0)
        ftype = config.failure_type.lower()
        overrides = config.custom_metric_overrides or {}

        service.is_initial_failure = True
        service.is_impacted = True

        if ftype == "service_unavailable":
            service.health_status = "CRITICAL"
            service.error_rate = min(100.0, 95.0 * sev)
            service.latency_ms = min(5000.0, 2500.0 * sev)
            service.cpu_usage = min(100.0, 15.0)
            service.risk_score = min(100.0, 95.0 * sev)
            desc = f"Complete service outage injected ({config.severity}): error_rate={service.error_rate:.1f}%, latency={service.latency_ms:.0f}ms."

        elif ftype == "high_latency":
            service.health_status = "CRITICAL" if sev >= 0.8 else "DEGRADED"
            service.latency_ms = min(4000.0, 300.0 + 1500.0 * sev)
            service.error_rate = min(50.0, 2.0 + 15.0 * sev)
            service.cpu_usage = min(95.0, 40.0 + 35.0 * sev)
            service.risk_score = min(100.0, 75.0 * sev)
            desc = f"Latency storm injected ({config.severity}): latency={service.latency_ms:.0f}ms, error_rate={service.error_rate:.1f}%."

        elif ftype == "error_rate_surge":
            service.health_status = "CRITICAL"
            service.error_rate = min(100.0, 25.0 + 60.0 * sev)
            service.latency_ms = min(2000.0, 150.0 + 500.0 * sev)
            service.risk_score = min(100.0, 85.0 * sev)
            desc = f"Error rate surge injected ({config.severity}): error_rate={service.error_rate:.1f}%."

        elif ftype == "cpu_saturation":
            service.health_status = "DEGRADED" if sev < 0.8 else "CRITICAL"
            service.cpu_usage = min(100.0, 70.0 + 28.0 * sev)
            service.latency_ms = min(1500.0, 120.0 + 450.0 * sev)
            service.error_rate = min(30.0, 1.0 + 10.0 * sev)
            service.risk_score = min(100.0, 70.0 * sev)
            desc = f"CPU resource exhaustion injected ({config.severity}): cpu={service.cpu_usage:.1f}%."

        elif ftype == "memory_exhaustion":
            service.health_status = "CRITICAL"
            service.memory_usage = min(100.0, 80.0 + 18.0 * sev)
            service.latency_ms = min(2500.0, 200.0 + 900.0 * sev)
            service.error_rate = min(45.0, 5.0 + 25.0 * sev)
            service.risk_score = min(100.0, 80.0 * sev)
            desc = f"Memory exhaustion injected ({config.severity}): mem={service.memory_usage:.1f}%."

        elif ftype == "database_starvation":
            service.health_status = "CRITICAL"
            service.latency_ms = min(3500.0, 500.0 + 1600.0 * sev)
            service.error_rate = min(60.0, 10.0 + 35.0 * sev)
            service.cpu_usage = min(98.0, 60.0 + 35.0 * sev)
            service.risk_score = min(100.0, 90.0 * sev)
            desc = f"Database connection pool starvation injected ({config.severity}): latency={service.latency_ms:.0f}ms, error={service.error_rate:.1f}%."

        else:
            # Generic degradation
            service.health_status = "DEGRADED"
            service.latency_ms = min(2000.0, 100.0 + 400.0 * sev)
            service.error_rate = min(40.0, 2.0 + 8.0 * sev)
            service.risk_score = min(100.0, 60.0 * sev)
            desc = f"Degradation injected ({config.severity}): latency={service.latency_ms:.0f}ms."

        # Apply custom overrides if specified
        for metric, val in overrides.items():
            if hasattr(service, metric) and isinstance(val, (int, float)):
                setattr(service, metric, float(val))

        return {
            "service_id": service.service_id,
            "failure_type": ftype,
            "severity": config.severity,
            "description": desc,
            "resulting_health": service.health_status,
            "risk_score": service.risk_score
        }
