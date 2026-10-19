from typing import Dict, Any, List, Optional
from app.services.action_registry import ActionRegistry
from app.schemas.agent_schema import (
    AgentActionDefinition, 
    AgentConfigSchema, 
    ActionRecommendation
)
from app.services.agent_policy import AgentPolicy

class ActionSelector:
    """
    Evaluates all registered actions, validates dynamic prerequisites,
    computes utilities, and ranks the next best actions with deterministic tie-breaking.
    """

    @classmethod
    def rank_actions(
        cls, 
        context: Dict[str, Any], 
        config: AgentConfigSchema
    ) -> List[ActionRecommendation]:
        all_defs = ActionRegistry.get_all_actions()
        recommendations = []

        target_service = context.get("target_service_id")
        affected_services = context.get("affected_service_ids", [])
        candidates = context.get("candidates", [])
        incident_id = context.get("incident_id")
        scenario_id = context.get("scenario_id")

        for action_def in all_defs:
            act_id = action_def.action_id
            eligible = True
            ineligible_reason = None
            resolved_target = target_service

            # Prerequisite checking
            if act_id in [
                "inspect_service_health", 
                "retrieve_service_metrics", 
                "compare_metrics_baseline",
                "retrieve_anomaly_alerts", 
                "inspect_dependency", 
                "trace_failure_paths",
                "inspect_cascade_prediction", 
                "identify_missing_evidence"
            ]:
                if not target_service:
                    eligible = False
                    ineligible_reason = "No target service specified for this investigation."

            elif act_id == "compare_timestamps":
                if not target_service:
                    eligible = False
                    ineligible_reason = "Target service must be specified to compare timestamps."
                elif not affected_services and len(candidates) < 2:
                    eligible = False
                    ineligible_reason = "Requires at least one downstream affected service or alternative candidate to compare timestamps."

            elif act_id == "compare_hypotheses":
                if len(candidates) < 2:
                    eligible = False
                    ineligible_reason = f"Requires at least 2 distinct root cause candidates (found {len(candidates)})."

            elif act_id == "reevaluate_root_causes":
                if not incident_id:
                    eligible = False
                    ineligible_reason = "Requires an active RCA incident ID to re-evaluate."

            elif act_id == "inspect_saved_simulation":
                if not scenario_id:
                    eligible = False
                    ineligible_reason = "No Module 3 saved simulation scenario ID linked to this session."

            # Calculate utility
            if eligible:
                utility, factors, exp = AgentPolicy.calculate_utility(action_def, context, config)
            else:
                utility = 0.0
                factors = {"information_gain": 0.0, "relevance": 0.0, "discrimination": 0.0, "cost": action_def.estimated_cost, "risk": 0.0, "repeat_penalty": 0.0}
                exp = f"Ineligible: {ineligible_reason}"

            recommendations.append(
                ActionRecommendation(
                    action_id=act_id,
                    action_name=action_def.action_name,
                    target_service_id=resolved_target,
                    utility_score=utility,
                    information_gain=factors["information_gain"],
                    relevance_score=factors["relevance"],
                    discrimination_score=factors["discrimination"],
                    cost=factors["cost"],
                    risk=factors["risk"],
                    repeat_penalty=factors["repeat_penalty"],
                    eligible=eligible,
                    ineligibility_reason=ineligible_reason,
                    selection_reason=exp
                )
            )

        # Deterministic sorting:
        # 1. Eligible first (True before False)
        # 2. Utility score descending
        # 3. Action ID ascending (tie-breaker)
        recommendations.sort(
            key=lambda r: (not r.eligible, -r.utility_score, r.action_id)
        )
        return recommendations

    @classmethod
    def select_best_action(
        cls, 
        context: Dict[str, Any], 
        config: AgentConfigSchema
    ) -> Optional[ActionRecommendation]:
        recommendations = cls.rank_actions(context, config)
        for rec in recommendations:
            if rec.eligible and rec.utility_score >= config.min_utility_threshold:
                return rec
        return None
