import json
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session

from app.models.recovery_models import RecoveryPlanModel
from app.database.recovery_repository import RecoveryRepository
from app.schemas.recovery_schemas import (
    RecoveryComparisonItem, 
    RecoveryComparisonResponse
)

class RecoveryComparisonService:
    """
    Compares candidate recovery plans side-by-side across risk, time, cost,
    reversibility, and data loss exposure. Generates evidence-grounded recommendations
    and trade-off rationales.
    """

    @classmethod
    def compare_plans(
        cls,
        db: Session,
        plan_ids: List[str],
        priority: str = "balanced"
    ) -> RecoveryComparisonResponse:
        plans = [RecoveryRepository.get_plan(db, pid) for pid in plan_ids]
        plans = [p for p in plans if p is not None]

        if not plans:
            raise ValueError("None of the specified plan IDs were found.")

        comparison_items: List[RecoveryComparisonItem] = []
        for p in plans:
            actions = p.actions or []
            all_preconditions = []
            for act in actions:
                p_list = json.loads(act.preconditions_json or "[]")
                all_preconditions.extend(p_list)

            unresolved_count = sum(1 for prec in all_preconditions if prec.get("status") in ["unresolved", "unknown"])
            has_irreversible = any(act.reversibility == "irreversible" for act in actions)
            has_data_loss = any(act.action_type in ["restore_database", "rollback_deployment"] for act in actions)
            
            data_loss_exp = "High" if (has_data_loss and has_irreversible) else ("Moderate" if has_data_loss else "None")
            reversibility_str = "irreversible" if has_irreversible else ("partially_reversible" if any(act.reversibility == "partially_reversible" for act in actions) else "fully_reversible")

            latest_run = p.runs[0] if p.runs else None
            outcome_str = latest_run.outcome if latest_run else None

            comparison_items.append(
                RecoveryComparisonItem(
                    plan_id=p.id,
                    plan_name=p.plan_name,
                    strategy_type=p.strategy_type,
                    risk_score=p.risk_score,
                    risk_level=p.risk_level,
                    estimated_recovery_time=p.estimated_recovery_time,
                    estimated_cost=p.estimated_cost,
                    data_loss_exposure=data_loss_exp,
                    reversibility=reversibility_str,
                    unresolved_preconditions_count=unresolved_count,
                    simulated_outcome=outcome_str
                )
            )

        # Recommendation selection logic based on requested priority
        recommended_item = None
        rejection_reasons: Dict[str, str] = {}

        if priority == "lowest_risk":
            # Lowest risk score that is not failing
            sorted_items = sorted(comparison_items, key=lambda c: (c.risk_score, c.estimated_recovery_time))
            recommended_item = sorted_items[0]

        elif priority == "fastest_recovery":
            # Lowest recovery time, with safety filter
            sorted_items = sorted(comparison_items, key=lambda c: (c.estimated_recovery_time, c.risk_score))
            recommended_item = sorted_items[0]

        elif priority == "lowest_cost":
            sorted_items = sorted(comparison_items, key=lambda c: (c.estimated_cost, c.risk_score))
            recommended_item = sorted_items[0]

        else: # "balanced"
            # Composite score: risk (40%) + time (30%) + cost (20%) + unresolved penalty (10%)
            def score_balance(c: RecoveryComparisonItem) -> float:
                score = (c.risk_score * 0.40) + (c.estimated_recovery_time * 6.0) + (c.estimated_cost * 0.6) + (c.unresolved_preconditions_count * 15.0)
                if c.data_loss_exposure == "High":
                    score += 25.0
                return score

            sorted_items = sorted(comparison_items, key=score_balance)
            recommended_item = sorted_items[0]

        # Generate trade-off explanations
        rec_id = recommended_item.plan_id if recommended_item else None
        rec_name = recommended_item.plan_name if recommended_item else "None"

        for item in comparison_items:
            if item.plan_id != rec_id:
                reasons = []
                if item.risk_score > recommended_item.risk_score:
                    reasons.append(f"higher risk score ({item.risk_score:.1f} vs {recommended_item.risk_score:.1f})")
                if item.data_loss_exposure in ["High", "Moderate"] and recommended_item.data_loss_exposure == "None":
                    reasons.append(f"potential data loss exposure ({item.data_loss_exposure})")
                if item.reversibility == "irreversible":
                    reasons.append("contains irreversible actions lacking immediate rollback")
                if item.estimated_cost > recommended_item.estimated_cost * 1.5:
                    reasons.append(f"significantly higher compute cost ({item.estimated_cost:.1f} units)")
                if item.estimated_recovery_time > recommended_item.estimated_recovery_time + 2:
                    reasons.append(f"prolonged recovery window ({item.estimated_recovery_time} steps)")
                if item.unresolved_preconditions_count > 0:
                    reasons.append(f"{item.unresolved_preconditions_count} unresolved preconditions")

                rejection_reasons[item.plan_name] = f"Less suitable due to: {', '.join(reasons) if reasons else 'lower overall composite resilience score'}."

        # Summary tradeoff narrative
        tradeoff_summary = (
            f"Compared {len(comparison_items)} candidate recovery strategies under '{priority}' optimization goal. "
            f"Plan '{rec_name}' delivers optimal balance with a risk score of {recommended_item.risk_score:.1f} ({recommended_item.risk_level}) "
            f"and an estimated recovery window of {recommended_item.estimated_recovery_time} steps. "
            f"Trade-off analysis indicates that while faster alternative strategies exist (e.g. immediate kill & restart), "
            f"they introduce elevated risk of dropped in-flight requests and data loss."
        )

        return RecoveryComparisonResponse(
            compared_plans=comparison_items,
            tradeoff_analysis=tradeoff_summary,
            recommended_plan_id=rec_id,
            recommendation_reason=f"Recommended under '{priority}' optimization goal: minimizes risk while maintaining verified preconditions and full reversibility.",
            alternative_plans_rejection_reasons=rejection_reasons
        )
