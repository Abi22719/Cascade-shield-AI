from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from app.models.service import ServiceModel
from app.models.dependency import DependencyModel
from app.schemas.recovery_schemas import (
    RecoveryActionCreate, 
    RecoveryConfigSchema,
    RecoveryPlanCreateRequest
)

class RecoveryValidationService:
    """
    Strict validation for proposed recovery plans and individual recovery actions.
    Ensures safe action types, existing service IDs, valid sequencing, and duration limits.
    """

    SUPPORTED_ACTION_TYPES = {
        "restart_service",
        "rollback_deployment",
        "traffic_reroute",
        "scale_up",
        "isolate_dependency",
        "restore_database",
        "retry_request",
        "wait_auto_recovery"
    }

    @classmethod
    def validate_plan_creation(
        cls, 
        db: Session, 
        req: RecoveryPlanCreateRequest,
        config: Optional[RecoveryConfigSchema] = None
    ) -> Dict[str, Any]:
        cfg = config or RecoveryConfigSchema()
        errors = []
        warnings = []

        if not req.plan_name or len(req.plan_name.strip()) < 2:
            errors.append("Plan name must be at least 2 characters long.")

        if not req.actions:
            errors.append("Plan must contain at least one recovery action.")

        # Check existing service IDs
        all_services = {s.id for s in db.query(ServiceModel).all()}

        action_orders = []
        total_duration = 0

        for idx, act in enumerate(req.actions):
            # 1. Action type check
            if act.action_type not in cls.SUPPORTED_ACTION_TYPES:
                errors.append(f"Action #{idx+1}: Unsupported action type '{act.action_type}'. Must be one of: {sorted(list(cls.SUPPORTED_ACTION_TYPES))}.")

            # 2. Target service check
            if act.target_service_id:
                if act.target_service_id not in all_services:
                    errors.append(f"Action #{idx+1}: Target service '{act.target_service_id}' does not exist in the digital twin infrastructure.")

            # 3. Action order validation
            if act.action_order in action_orders:
                warnings.append(f"Action #{idx+1}: Duplicate action_order {act.action_order} detected. Sequence will execute concurrently.")
            action_orders.append(act.action_order)

            # 4. Duration
            total_duration += act.estimated_duration

            # 5. Irreversible action warning
            if act.reversibility == "irreversible":
                warnings.append(f"Action #{idx+1} ({act.action_type} on '{act.target_service_id}'): Action is marked IRREVERSIBLE and requires rollback contingency.")

            # 6. Preconditions check
            for p in (act.preconditions or []):
                if getattr(p, "status", "satisfied") in ["unresolved", "unknown"]:
                    warnings.append(f"Action #{idx+1}: Precondition '{p.name}' is unresolved and will be validated dynamically during simulation.")

        if total_duration > cfg.max_allowed_recovery_duration:
            warnings.append(f"Total estimated recovery duration ({total_duration} steps) exceeds configured threshold ({cfg.max_allowed_recovery_duration} steps).")

        if errors:
            raise ValueError("; ".join(errors))

        return {
            "valid": True,
            "actions_count": len(req.actions),
            "total_estimated_duration": total_duration,
            "warnings": warnings
        }
