import json
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from app.database.validation_repository import ValidationRepository
from app.schemas.validation_schemas import ValidationConfigSchema

DEFAULT_VALIDATION_CONFIG: Dict[str, Any] = {
    "max_acceptable_latency_ms": 500.0,
    "max_acceptable_error_rate": 5.0,
    "max_acceptable_cpu_percent": 85.0,
    "max_acceptable_memory_percent": 85.0,
    "min_required_healthy_services": 1,
    "verification_window_steps": 3,
    "allowed_metric_deviation": 10.0,
    "required_evidence_level": "strict",  # strict, moderate, permissive
    "timeout_seconds": 30,
    "critical_services": ["srv-database", "srv-payment", "srv-gateway"]
}

class ValidationRuleEngine:
    """
    Manages configurable validation rules and operational thresholds.
    Ensures thresholds are transparently documented as configurable demonstration defaults.
    """

    @classmethod
    def get_config(cls, db: Session) -> ValidationConfigSchema:
        db_configs = ValidationRepository.get_all_configs(db)
        merged = dict(DEFAULT_VALIDATION_CONFIG)

        for k, v in db_configs.items():
            if k in merged:
                try:
                    if isinstance(merged[k], (list, dict)):
                        merged[k] = json.loads(v)
                    elif isinstance(merged[k], bool):
                        merged[k] = v.lower() in ("true", "1")
                    elif isinstance(merged[k], int):
                        merged[k] = int(v)
                    elif isinstance(merged[k], float):
                        merged[k] = float(v)
                    else:
                        merged[k] = v
                except Exception:
                    pass

        return ValidationConfigSchema(**merged)

    @classmethod
    def update_config(cls, db: Session, updates: Dict[str, Any]) -> ValidationConfigSchema:
        for k, v in updates.items():
            if k in DEFAULT_VALIDATION_CONFIG:
                val_str = json.dumps(v) if isinstance(v, (list, dict)) else str(v)
                ValidationRepository.set_config(db, k, val_str)
        return cls.get_config(db)

    @classmethod
    def get_rules_documentation(cls) -> List[Dict[str, Any]]:
        return [
            {
                "rule_name": "Service Health Verification",
                "category": "service_health",
                "description": "Verifies that all target services and impacted callers reached HEALTHY status without remaining DEGRADED or CRITICAL.",
                "default_value": "HEALTHY",
                "is_configurable": True
            },
            {
                "rule_name": "Maximum Acceptable Latency",
                "category": "metrics",
                "description": "Ensures post-recovery round-trip latency stays within acceptable bounds.",
                "default_value": "500.0 ms",
                "is_configurable": True
            },
            {
                "rule_name": "Maximum Acceptable Error Rate",
                "category": "metrics",
                "description": "Ensures post-recovery HTTP 5xx error rate stays within acceptable SLA bounds.",
                "default_value": "5.0 %",
                "is_configurable": True
            },
            {
                "rule_name": "Maximum CPU / Memory Utilization",
                "category": "metrics",
                "description": "Validates that compute and memory resources are not saturated post-recovery.",
                "default_value": "85.0 %",
                "is_configurable": True
            },
            {
                "rule_name": "Downstream Dependency Resolution",
                "category": "dependency",
                "description": "Cycle-safe verification that callers depending on the recovered service have also recovered without new cascade waves.",
                "default_value": "Zero residual caller failures",
                "is_configurable": False
            },
            {
                "rule_name": "Post-Recovery Stability Window",
                "category": "stability",
                "description": "Requires the recovered state to remain stable across a configured number of subsequent simulation steps.",
                "default_value": "3 discrete steps",
                "is_configurable": True
            },
            {
                "rule_name": "Zero Unexpected Side-Effects",
                "category": "side_effects",
                "description": "Audits that no previously healthy services suffered unpredicted degradation or failed preconditions.",
                "default_value": "0 unpredicted failures",
                "is_configurable": False
            },
            {
                "rule_name": "Evidence Grounding Verification",
                "category": "evidence",
                "description": "Requires every validation check to link to a valid simulation step, telemetry metric, or event log.",
                "default_value": "Strict evidence grounding",
                "is_configurable": True
            }
        ]
