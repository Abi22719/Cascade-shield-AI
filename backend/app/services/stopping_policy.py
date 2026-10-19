from typing import Dict, Any, List, Optional, Tuple
from app.schemas.agent_schema import AgentConfigSchema, ActionRecommendation

class StoppingPolicy:
    """
    Evaluates whether the diagnostic loop should stop or continue.
    Returns: (should_stop: bool, stopping_reason: Optional[str], manual_investigation_recommended: bool)
    """

    @classmethod
    def evaluate(
        cls,
        step_number: int,
        elapsed_seconds: float,
        current_candidates: List[Dict[str, Any]],
        next_best_action: Optional[ActionRecommendation],
        config: AgentConfigSchema,
        unresolved_questions: List[str],
        user_stop_requested: bool = False
    ) -> Tuple[bool, Optional[str], bool]:
        # 1. User manual stop requested
        if user_stop_requested:
            return True, "USER_STOP_REQUESTED: Operator requested session termination.", True

        # 2. Maximum step budget reached
        if step_number >= config.max_actions:
            return (
                True, 
                f"MAX_ACTIONS_REACHED: Reached configured diagnostic action budget of {config.max_actions} steps.",
                len(unresolved_questions) > 0 or not cls._is_confident(current_candidates, config)
            )

        # 3. Maximum execution time reached
        if elapsed_seconds >= config.max_execution_time_seconds:
            return (
                True,
                f"MAX_EXECUTION_TIME_REACHED: Elapsed time ({elapsed_seconds:.1f}s) exceeded limit ({config.max_execution_time_seconds:.1f}s).",
                True
            )

        # 4. Sufficient evidence collected (high confidence top candidate with clear margin)
        if cls._has_sufficient_evidence(current_candidates, config):
            top = current_candidates[0]
            return (
                True,
                f"SUFFICIENT_EVIDENCE: Top candidate '{top.get('service_id')}' achieved {top.get('score', 0):.1f}/100 "
                f"with clear score margin exceeding threshold.",
                False
            )

        # 5. No useful eligible action remains
        if not next_best_action or next_best_action.utility_score < config.min_utility_threshold:
            highest_score = next_best_action.utility_score if next_best_action else 0.0
            return (
                True,
                f"NO_USEFUL_ACTIONS_REMAIN: All eligible actions fall below minimum utility threshold "
                f"({config.min_utility_threshold:.2f}, highest was {highest_score:.2f}).",
                True
            )

        # Otherwise continue
        return False, None, False

    @staticmethod
    def _is_confident(candidates: List[Dict[str, Any]], config: AgentConfigSchema) -> bool:
        if not candidates:
            return False
        top = candidates[0]
        score = top.get("score", 0.0)
        return score >= (config.sufficient_confidence_threshold * 100.0)

    @classmethod
    def _has_sufficient_evidence(cls, candidates: List[Dict[str, Any]], config: AgentConfigSchema) -> bool:
        if not candidates:
            return False
        top = candidates[0]
        top_score = top.get("score", 0.0)

        # Must meet sufficient confidence score
        if top_score < (config.sufficient_confidence_threshold * 100.0):
            return False

        # If multiple candidates, top must beat runner-up by margin
        if len(candidates) >= 2:
            runner_up_score = candidates[1].get("score", 0.0)
            margin = top_score - runner_up_score
            return margin >= config.confidence_margin_threshold

        return True
