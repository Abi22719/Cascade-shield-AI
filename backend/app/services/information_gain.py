import math
from typing import List, Tuple, Dict, Any, Optional

class InformationGainService:
    """
    Computes information gain and uncertainty reduction over root cause candidate distributions.
    Handles defensible Shannon entropy when probability distributions are available,
    and cleanly falls back to heuristic uncertainty reduction for uncalibrated / single / empty candidate lists.
    """

    @staticmethod
    def calculate_entropy(probabilities: List[float]) -> float:
        """
        Calculates Shannon entropy in bits: H(C) = - sum(p * log2(p)).
        Safely handles empty lists, single candidates, zero probabilities, and normalization.
        """
        if not probabilities or len(probabilities) <= 1:
            return 0.0

        total = sum(probabilities)
        if total <= 0.0:
            return 0.0

        # Normalize
        normalized = [p / total for p in probabilities if p > 0.0]
        if len(normalized) <= 1:
            return 0.0

        entropy = 0.0
        for p in normalized:
            if p > 0.0:
                entropy -= p * math.log2(p)

        return max(0.0, entropy)

    @staticmethod
    def scores_to_probabilities(candidate_scores: List[float], temperature: float = 25.0) -> List[float]:
        """
        Converts heuristic 0-100 candidate ranking scores into a normalized distribution via temperature-scaled softmax.
        Returns empty list if no valid scores.
        """
        if not candidate_scores:
            return []

        if len(candidate_scores) == 1:
            return [1.0]

        max_score = max(candidate_scores)
        # Numerical stability shift
        exp_scores = [math.exp((s - max_score) / max(1.0, temperature)) for s in candidate_scores]
        total_exp = sum(exp_scores)
        if total_exp <= 0.0:
            return [1.0 / len(candidate_scores)] * len(candidate_scores)

        return [e / total_exp for e in exp_scores]

    @staticmethod
    def estimate_information_gain(
        candidate_scores: List[float], 
        action_id: str, 
        action_intrinsic_value: float = 0.7, 
        has_missing_evidence: bool = True
    ) -> Tuple[float, str]:
        """
        Estimates expected uncertainty reduction for a diagnostic action.
        Returns: (normalized_information_gain: float, method_used: str)
        """
        # Case 1: Empty candidate list
        if not candidate_scores:
            gain = action_intrinsic_value * (0.8 if has_missing_evidence else 0.4)
            return round(min(1.0, max(0.0, gain)), 3), "heuristic_unobserved_cluster"

        # Case 2: Single candidate (no distribution entropy)
        if len(candidate_scores) == 1:
            # Uncertainty is about whether the sole candidate is truly the root or a false positive
            single_score = candidate_scores[0]
            # If score is near 50 (ambiguous), information gain of verifying is high
            uncertainty = 1.0 - abs(single_score - 50.0) / 50.0
            gain = action_intrinsic_value * (0.6 + 0.4 * uncertainty)
            return round(min(1.0, max(0.0, gain)), 3), "heuristic_single_candidate_verification"

        # Case 3: Multiple candidates (>= 2)
        probs = InformationGainService.scores_to_probabilities(candidate_scores)
        prior_entropy = InformationGainService.calculate_entropy(probs)
        max_possible_entropy = math.log2(len(candidate_scores)) if len(candidate_scores) > 1 else 1.0

        if prior_entropy <= 0.001 or max_possible_entropy <= 0.0:
            # Deterministic/converged: gain is minimal
            gain = action_intrinsic_value * 0.2
            return round(min(1.0, max(0.0, gain)), 3), "heuristic_converged_candidates"

        # Expected entropy reduction based on action discrimination power
        # High value actions (e.g. timestamp comparison, RCA re-evaluation) reduce more entropy
        expected_posterior_entropy = prior_entropy * (1.0 - (action_intrinsic_value * 0.65))
        delta_entropy = max(0.0, prior_entropy - expected_posterior_entropy)

        # Normalize relative to max entropy
        normalized_gain = delta_entropy / max_possible_entropy
        return round(min(1.0, max(0.0, normalized_gain)), 3), "shannon_entropy_reduction"
