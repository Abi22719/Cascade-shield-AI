from typing import Dict, Any, List
from sqlalchemy.orm import Session
from app.models.service import ServiceModel
from app.schemas.simulation_schema import (
    ScenarioConfigSchema,
    FailureInjectionConfig,
    PropagationParameters,
    RecoveryParameters
)

class ScenarioBuilder:
    """
    Constructs and provides default presets and options for what-if simulation scenarios.
    """

    @classmethod
    def get_simulation_options(cls, db: Session) -> Dict[str, Any]:
        services = db.query(ServiceModel).all()
        service_options = [
            {"id": s.id, "name": s.name, "type": s.service_type, "status": s.health_status}
            for s in services
        ]

        failure_types = [
            {"id": "service_unavailable", "name": "Complete Service Outage", "desc": "100% error rate, total HTTP request drop"},
            {"id": "high_latency", "name": "Upstream Latency Storm", "desc": "Sudden 10x-20x latency escalation"},
            {"id": "error_rate_surge", "name": "HTTP 5xx Error Surge", "desc": "Widespread application exception rate"},
            {"id": "cpu_saturation", "name": "CPU Core Exhaustion", "desc": "95%+ thread starvation & queueing delays"},
            {"id": "memory_exhaustion", "name": "Memory Leak / OOM Pressure", "desc": "Heap saturation and GC lockups"},
            {"id": "database_starvation", "name": "Database Pool Starvation", "desc": "Connection pool timeout and deadlock cascade"}
        ]

        severities = [
            {"id": "mild", "name": "Mild (50% Impact)", "factor": 0.5},
            {"id": "moderate", "name": "Moderate (80% Impact)", "factor": 0.8},
            {"id": "severe", "name": "Severe (100% Impact)", "factor": 1.0}
        ]

        recovery_modes = [
            {"id": "none", "name": "No Recovery", "desc": "Failure persists indefinitely across the entire window"},
            {"id": "gradual", "name": "Gradual Metric Convergence", "desc": "Smooth recovery over multiple time steps"},
            {"id": "immediate", "name": "Instant Failover / Rollback", "desc": "Immediate restoration to healthy baseline"}
        ]

        presets = [
            {
                "name": "Payment Gateway Outage",
                "category": "failure_propagation",
                "description": "Severe outage of payment processing propagating to orders and API gateway",
                "target_services": ["srv-payment"],
                "failure_type": "service_unavailable",
                "severity": "severe",
                "recovery_mode": "gradual",
                "recovery_step": 5
            },
            {
                "name": "Database Connection Pool Starvation",
                "category": "database_starvation",
                "description": "Relational database pool exhaustion choking product catalog and order processing",
                "target_services": ["srv-database"],
                "failure_type": "database_starvation",
                "severity": "severe",
                "recovery_mode": "gradual",
                "recovery_step": 6
            },
            {
                "name": "Auth Verifier Latency Storm",
                "category": "latency_storm",
                "description": "JWT/OAuth token validation latency impacting downstream authentication callers",
                "target_services": ["srv-auth"],
                "failure_type": "high_latency",
                "severity": "moderate",
                "recovery_mode": "immediate",
                "recovery_step": 4
            },
            {
                "name": "Dual-Service Simultaneous Failure",
                "category": "failure_propagation",
                "description": "Concurrently injecting failures into Payment and Auth to observe compound cascade blast radius",
                "target_services": ["srv-payment", "srv-auth"],
                "failure_type": "high_latency",
                "severity": "severe",
                "recovery_mode": "gradual",
                "recovery_step": 5
            }
        ]

        return {
            "services": service_options,
            "failure_types": failure_types,
            "severities": severities,
            "recovery_modes": recovery_modes,
            "presets": presets,
            "limits": {
                "min_steps": 1,
                "max_steps": 20,
                "default_steps": 8,
                "min_attenuation": 0.1,
                "max_attenuation": 1.0,
                "default_attenuation": 0.75
            }
        }
