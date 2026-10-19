from typing import Dict, Any, List, Optional
from app.schemas.agent_schema import ActionRecommendation, AgentConfigSchema

class AgentExplanationService:
    """
    Generates transparent, mathematical, and evidence-grounded explanations
    for action selection, ranking shifts, and termination decisions.
    """

    @staticmethod
    def explain_action_selection(
        recommendation: ActionRecommendation,
        unresolved_questions: List[str]
    ) -> str:
        act = recommendation.action_name
        score = recommendation.utility_score
        info = recommendation.information_gain
        rel = recommendation.relevance_score
        disc = recommendation.discrimination_score
        cost = recommendation.cost

        addressed_q = unresolved_questions[0] if unresolved_questions else "verifying current service operational bounds"

        return (
            f"Selected '{act}' with utility {score:.3f}. "
            f"Primary rationale: High relevance ({rel:.2f}) and information gain ({info:.2f}) "
            f"aimed at addressing question: '{addressed_q}'. "
            f"Discrimination power between root hypotheses is {disc:.2f} with minimal execution cost ({cost:.2f})."
        )

    @staticmethod
    def explain_ranking_shift(
        old_candidates: List[Dict[str, Any]],
        new_candidates: List[Dict[str, Any]],
        action_name: str
    ) -> str:
        if not old_candidates or not new_candidates:
            return f"Executed '{action_name}'. Initialized candidate ranking with new telemetry evidence."

        old_top = old_candidates[0].get("service_id")
        old_score = old_candidates[0].get("score", 0.0)
        new_top = new_candidates[0].get("service_id")
        new_score = new_candidates[0].get("score", 0.0)

        if old_top == new_top:
            diff = new_score - old_score
            sign = "+" if diff >= 0 else ""
            return (
                f"Executed '{action_name}'. Candidate '{new_top}' remains primary root cause "
                f"with score adjustment of {sign}{diff:.1f} (now {new_score:.1f}/100)."
            )
        else:
            return (
                f"Executed '{action_name}'. Ranking leadership inverted: '{new_top}' ({new_score:.1f}/100) "
                f"displaced previous leader '{old_top}' ({old_score:.1f}/100) based on newly corroborated telemetry."
            )

    @staticmethod
    def explain_stopping_decision(
        stopping_reason: str,
        final_candidates: List[Dict[str, Any]],
        evidence_completeness: float,
        manual_investigation_recommended: bool
    ) -> str:
        top_name = final_candidates[0].get("service_name", "Unknown") if final_candidates else "None"
        top_score = final_candidates[0].get("score", 0.0) if final_candidates else 0.0
        conf = final_candidates[0].get("confidence_label", "Insufficient") if final_candidates else "Insufficient"

        advice = (
            "Further manual SRE investigation is strongly recommended to resolve remaining telemetry ambiguities."
            if manual_investigation_recommended else
            "Telemetry corroboration is sufficient for targeted non-destructive remediation."
        )

        return (
            f"Diagnostic session finalized: {stopping_reason} "
            f"Evidence completeness is {evidence_completeness * 100:.0f}%. "
            f"Leading root cause candidate: {top_name} ({top_score:.1f}/100, {conf}). {advice}"
        )
