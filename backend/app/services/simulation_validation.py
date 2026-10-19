from typing import Dict, Any, List
from sqlalchemy.orm import Session
from app.models.service import ServiceModel
from app.schemas.simulation_schema import ScenarioConfigSchema

class SimulationValidationService:
    """
    Validates scenario parameters against the digital twin and ensures safe simulation bounds.
    """

    VALID_FAILURE_TYPES = {
        "service_unavailable",
        "high_latency",
        "error_rate_surge",
        "cpu_saturation",
        "memory_exhaustion",
        "database_starvation"
    }

    VALID_SEVERITIES = {"mild", "moderate", "severe"}
    VALID_RECOVERY_MODES = {"none", "immediate", "gradual"}

    @classmethod
    def validate_scenario_config(cls, db: Session, config: ScenarioConfigSchema):
        # 1. Verify target services exist
        existing_services = {s.id for s in db.query(ServiceModel).all()}
        
        if not config.failures:
            raise ValueError("Scenario must specify at least one failure injection definition.")

        for f in config.failures:
            if not f.target_service_ids:
                raise ValueError("Failure injection must include at least one target service ID.")

            for sid in f.target_service_ids:
                if sid not in existing_services:
                    raise ValueError(f"Target service '{sid}' does not exist in the digital twin.")

            if f.failure_type.lower() not in cls.VALID_FAILURE_TYPES:
                raise ValueError(
                    f"Invalid failure_type '{f.failure_type}'. Supported: {', '.join(cls.VALID_FAILURE_TYPES)}"
                )

            if f.severity.lower() not in cls.VALID_SEVERITIES:
                raise ValueError(
                    f"Invalid severity '{f.severity}'. Supported: {', '.join(cls.VALID_SEVERITIES)}"
                )

            if f.start_step > config.propagation.max_steps:
                raise ValueError(
                    f"Failure start_step ({f.start_step}) cannot exceed propagation max_steps ({config.propagation.max_steps})."
                )

        # 2. Validate propagation
        if not (1 <= config.propagation.max_steps <= 20):
            raise ValueError("max_steps must be between 1 and 20.")
        if not (0.1 <= config.propagation.attenuation_factor <= 1.0):
            raise ValueError("attenuation_factor must be between 0.1 and 1.0.")

        # 3. Validate recovery
        rec = config.recovery
        if rec.recovery_mode.lower() not in cls.VALID_RECOVERY_MODES:
            raise ValueError(
                f"Invalid recovery_mode '{rec.recovery_mode}'. Supported: {', '.join(cls.VALID_RECOVERY_MODES)}"
            )

        if rec.recovery_mode != "none" and rec.recovery_step is not None:
            if rec.recovery_step > config.propagation.max_steps:
                raise ValueError(
                    f"recovery_step ({rec.recovery_step}) cannot be greater than max_steps ({config.propagation.max_steps})."
                )
