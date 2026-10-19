from typing import Dict, Any, List, Optional
import networkx as nx
from app.schemas.recovery_schemas import (
    RecoveryActionCreate, 
    RiskFactorBreakdown, 
    RecoveryConfigSchema
)

class RecoveryRiskService:
    """
    Computes explainable, transparent multi-factor risk scores (0 to 100) for recovery plans.
    Evaluates service criticality, blast radius, execution duration, resource cost,
    reversibility, potential data loss, and precondition uncertainty.
    """

    CRITICAL_SERVICES = {"srv-database", "srv-gateway", "srv-auth"}
    TIER2_SERVICES = {"srv-order", "srv-payment", "srv-user"}

    DEFAULT_CONFIG = RecoveryConfigSchema()

    @classmethod
    def calculate_plan_risk(
        cls,
        actions: List[RecoveryActionCreate],
        G_dep: Optional[nx.DiGraph] = None,
        config: Optional[RecoveryConfigSchema] = None
    ) -> Dict[str, Any]:
        cfg = config or cls.DEFAULT_CONFIG

        if not actions:
            return {
                "risk_score": 0.0,
                "risk_level": "Low",
                "estimated_recovery_time": 0,
                "estimated_cost": 0.0,
                "data_loss_exposure": "None",
                "reversibility": "fully_reversible",
                "unresolved_preconditions_count": 0,
                "breakdown": []
            }

        # 1. Total Duration & Cost
        total_duration = sum(act.estimated_duration for act in actions)
        total_cost = 0.0
        cost_weights = {
            "scale_up": 25.0,
            "restore_database": 35.0,
            "traffic_reroute": 15.0,
            "rollback_deployment": 12.0,
            "restart_service": 8.0,
            "isolate_dependency": 10.0,
            "retry_request": 3.0,
            "wait_auto_recovery": 0.0
        }
        for act in actions:
            total_cost += cost_weights.get(act.action_type, 10.0)

        # 2. Service Criticality Factor (0 - 100)
        target_sids = [act.target_service_id for act in actions if act.target_service_id]
        crit_count = sum(1 for s in target_sids if s in cls.CRITICAL_SERVICES)
        tier2_count = sum(1 for s in target_sids if s in cls.TIER2_SERVICES)
        crit_score = min(100.0, (crit_count * 45.0) + (tier2_count * 25.0) + (len(target_sids) * 10.0))

        # 3. Blast Radius / Downstream Dependencies Factor (0 - 100)
        downstream_impacted = set()
        if G_dep and target_sids:
            for sid in target_sids:
                if sid in G_dep:
                    # In G_dep (caller -> callee), services calling sid depend on sid
                    # For blast radius of mutating sid, callers may experience temporary interruptions
                    callers = [u for u, v in G_dep.edges() if v == sid]
                    downstream_impacted.update(callers)
        blast_score = min(100.0, len(downstream_impacted) * 22.0)

        # 4. Duration Factor (0 - 100)
        # 1 step = ~10, 5 steps = 50, 10+ steps = 100
        duration_score = min(100.0, total_duration * 12.0)

        # 5. Resource Cost Factor (0 - 100)
        cost_score = min(100.0, total_cost * 1.5)

        # 6. Reversibility & Data Loss Factor (0 - 100)
        has_irreversible = any(act.reversibility == "irreversible" for act in actions)
        has_partially = any(act.reversibility == "partially_reversible" for act in actions)
        has_data_risk = any(act.action_type in ["restore_database", "rollback_deployment"] for act in actions)

        if has_irreversible:
            rev_score = 90.0
            overall_rev = "irreversible"
        elif has_partially:
            rev_score = 45.0
            overall_rev = "partially_reversible"
        else:
            rev_score = 15.0
            overall_rev = "fully_reversible"

        data_loss_exp = "High" if (has_data_risk and has_irreversible) else ("Moderate" if has_data_risk else "None")
        if data_loss_exp == "High":
            rev_score = min(100.0, rev_score + 15.0)
        elif data_loss_exp == "Moderate":
            rev_score = min(100.0, rev_score + 8.0)

        # 7. Uncertainty & Precondition Factor (0 - 100)
        all_preconditions = [p for act in actions for p in (act.preconditions or [])]
        unresolved_count = sum(1 for p in all_preconditions if getattr(p, "status", "satisfied") in ["unresolved", "unknown"])
        violated_count = sum(1 for p in all_preconditions if getattr(p, "status", "satisfied") == "violated")
        uncertainty_score = min(100.0, (unresolved_count * 25.0) + (violated_count * 40.0))

        # Weighted Aggregation
        raw_weighted = (
            crit_score * cfg.service_criticality_weight +
            blast_score * cfg.blast_radius_weight +
            duration_score * cfg.recovery_duration_weight +
            cost_score * cfg.resource_cost_weight +
            rev_score * cfg.reversibility_weight +
            uncertainty_score * cfg.uncertainty_weight
        )

        final_risk = round(min(100.0, max(0.0, raw_weighted)), 1)

        # Categorize demonstration risk level
        if final_risk < 25.0:
            risk_level = "Low"
        elif final_risk < 50.0:
            risk_level = "Moderate"
        elif final_risk < 75.0:
            risk_level = "High"
        else:
            risk_level = "Critical"

        # Factor breakdown for explainability
        breakdown = [
            RiskFactorBreakdown(
                factor_name="Service Criticality",
                raw_score=round(crit_score, 1),
                weight=cfg.service_criticality_weight,
                weighted_score=round(crit_score * cfg.service_criticality_weight, 1),
                impact_direction="increases_risk" if crit_score > 40 else "neutral",
                explanation=f"Target services include {crit_count} Tier-1 critical infrastructure services."
            ),
            RiskFactorBreakdown(
                factor_name="Downstream Blast Radius",
                raw_score=round(blast_score, 1),
                weight=cfg.blast_radius_weight,
                weighted_score=round(blast_score * cfg.blast_radius_weight, 1),
                impact_direction="increases_risk" if blast_score > 30 else "reduces_risk",
                explanation=f"{len(downstream_impacted)} dependent caller services exposed to recovery transition disturbances."
            ),
            RiskFactorBreakdown(
                factor_name="Recovery Duration",
                raw_score=round(duration_score, 1),
                weight=cfg.recovery_duration_weight,
                weighted_score=round(duration_score * cfg.recovery_duration_weight, 1),
                impact_direction="increases_risk" if total_duration > 6 else "reduces_risk",
                explanation=f"Estimated {total_duration} discrete time-steps to execute full recovery sequence."
            ),
            RiskFactorBreakdown(
                factor_name="Resource Cost",
                raw_score=round(cost_score, 1),
                weight=cfg.resource_cost_weight,
                weighted_score=round(cost_score * cfg.resource_cost_weight, 1),
                impact_direction="increases_risk" if total_cost > 40 else "neutral",
                explanation=f"Estimated resource consumption cost units: {total_cost:.1f}."
            ),
            RiskFactorBreakdown(
                factor_name="Reversibility & Data Loss",
                raw_score=round(rev_score, 1),
                weight=cfg.reversibility_weight,
                weighted_score=round(rev_score * cfg.reversibility_weight, 1),
                impact_direction="increases_risk" if rev_score > 40 else "reduces_risk",
                explanation=f"Plan reversibility is '{overall_rev}' with '{data_loss_exp}' potential data loss exposure."
            ),
            RiskFactorBreakdown(
                factor_name="Precondition Uncertainty",
                raw_score=round(uncertainty_score, 1),
                weight=cfg.uncertainty_weight,
                weighted_score=round(uncertainty_score * cfg.uncertainty_weight, 1),
                impact_direction="increases_risk" if unresolved_count > 0 else "reduces_risk",
                explanation=f"{unresolved_count} unresolved preconditions and {violated_count} violated constraints detected."
            )
        ]

        return {
            "risk_score": final_risk,
            "risk_level": risk_level,
            "estimated_recovery_time": total_duration,
            "estimated_cost": total_cost,
            "data_loss_exposure": data_loss_exp,
            "reversibility": overall_rev,
            "unresolved_preconditions_count": unresolved_count,
            "breakdown": [b.model_dump() for b in breakdown]
        }
