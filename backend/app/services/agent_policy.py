from typing import Dict, Any, List, Tuple
from app.schemas.agent_schema import AgentConfigSchema, AgentActionDefinition
from app.services.information_gain import InformationGainService

class AgentPolicy:
    """
    Implements the configurable, multi-factor action utility scoring formula:
    Utility = w_info * InfoGain + w_rel * Relevance + w_disc * Discrimination
              - w_cost * Cost - w_risk * Risk - RepeatPenalty
    """

    @staticmethod
    def calculate_utility(
        action_def: AgentActionDefinition,
        context: Dict[str, Any],
        config: AgentConfigSchema
    ) -> Tuple[float, Dict[str, float], str]:
        """
        Calculates normalized utility score (0.0 to 1.0), component factor breakdown, and explanation string.
        """
        executed_actions = context.get("executed_action_ids", [])
        candidates = context.get("candidates", [])
        candidate_scores = [c.get("score", 50.0) for c in candidates if isinstance(c, dict)]
        target_service = context.get("target_service_id")
        affected_services = context.get("affected_service_ids", [])
        alerts_count = context.get("alerts_count", 0)

        # 1. Information Gain (0.0 to 1.0)
        info_gain, method = InformationGainService.estimate_information_gain(
            candidate_scores=candidate_scores,
            action_id=action_def.action_id,
            action_intrinsic_value=action_def.information_value,
            has_missing_evidence=context.get("has_missing_evidence", True)
        )

        # 2. Incident Relevance (0.0 to 1.0)
        rel = 0.5  # baseline
        act_id = action_def.action_id
        if target_service:
            if act_id in ["inspect_service_health", "retrieve_service_metrics", "compare_metrics_baseline"]:
                rel = 0.95
            elif act_id in ["retrieve_anomaly_alerts", "identify_missing_evidence"]:
                rel = 0.85
            elif act_id in ["inspect_dependency", "trace_failure_paths", "inspect_cascade_prediction"]:
                rel = 0.90 if len(affected_services) > 0 else 0.75
        if act_id == "compare_timestamps" and len(affected_services) >= 1:
            rel = 0.92
        if act_id in ["reevaluate_root_causes", "compare_hypotheses"] and len(candidates) >= 2:
            rel = 0.95

        # 3. Hypothesis Discrimination (0.0 to 1.0)
        # Measures power to differentiate top 2 candidates
        disc = 0.2
        if len(candidates) >= 2:
            top_diff = abs(candidates[0].get("score", 50.0) - candidates[1].get("score", 50.0))
            # If top candidates are close in score, discrimination actions become critically valuable
            closeness_factor = 1.0 - min(1.0, top_diff / 50.0)
            if act_id in ["compare_hypotheses", "compare_timestamps"]:
                disc = min(1.0, 0.7 + 0.3 * closeness_factor)
            elif act_id in ["reevaluate_root_causes", "trace_failure_paths"]:
                disc = min(1.0, 0.6 + 0.3 * closeness_factor)
            elif act_id == "inspect_dependency":
                disc = 0.45
        elif len(candidates) == 1:
            disc = 0.35 if act_id in ["inspect_service_health", "retrieve_anomaly_alerts"] else 0.15

        # 4. Normalized Cost (0.0 to 1.0)
        cost = min(1.0, max(0.0, action_def.estimated_cost))

        # 5. Operational Risk (0.0 to 1.0)
        risk = 0.0 if action_def.risk_level == "READ_ONLY" else (0.05 if action_def.risk_level == "MINIMAL" else 0.10)

        # 6. Repeated Action Penalty (0.0 or penalty)
        repeat_penalty = 0.0
        times_executed = executed_actions.count(act_id)
        if times_executed > 0:
            # Re-evaluation and metric comparison can be repeated once if new evidence appeared, but penalized otherwise
            if act_id == "reevaluate_root_causes" and context.get("new_evidence_since_reeval", False):
                repeat_penalty = config.repeated_action_penalty * 0.4
            else:
                repeat_penalty = config.repeated_action_penalty * (1.0 + 0.5 * (times_executed - 1))

        # Calculate final utility
        raw_utility = (
            config.weight_information_gain * info_gain
            + config.weight_relevance * rel
            + config.weight_hypothesis_discrimination * disc
            - config.weight_cost * cost
            - config.weight_risk * risk
            - repeat_penalty
        )
        final_utility = round(max(0.0, min(1.0, raw_utility)), 3)

        factors = {
            "information_gain": round(info_gain, 3),
            "relevance": round(rel, 3),
            "discrimination": round(disc, 3),
            "cost": round(cost, 3),
            "risk": round(risk, 3),
            "repeat_penalty": round(repeat_penalty, 3)
        }

        explanation = (
            f"Utility {final_utility:.3f} (InfoGain={info_gain:.2f}, Relevance={rel:.2f}, "
            f"Discrimination={disc:.2f}, Cost={cost:.2f}, RepeatPenalty={repeat_penalty:.2f})"
        )
        return final_utility, factors, explanation
