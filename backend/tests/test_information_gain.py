import pytest
import math
from app.services.information_gain import InformationGainService

def test_entropy_edge_cases():
    # Empty list
    assert InformationGainService.calculate_entropy([]) == 0.0
    # Single element
    assert InformationGainService.calculate_entropy([1.0]) == 0.0
    # Zeros
    assert InformationGainService.calculate_entropy([0.0, 0.0]) == 0.0
    # Uniform 2 candidates -> 1 bit
    assert round(InformationGainService.calculate_entropy([0.5, 0.5]), 4) == 1.0
    # Uniform 4 candidates -> 2 bits
    assert round(InformationGainService.calculate_entropy([0.25, 0.25, 0.25, 0.25]), 4) == 2.0

def test_scores_to_probabilities():
    assert InformationGainService.scores_to_probabilities([]) == []
    assert InformationGainService.scores_to_probabilities([80.0]) == [1.0]
    
    probs = InformationGainService.scores_to_probabilities([80.0, 40.0])
    assert len(probs) == 2
    assert probs[0] > probs[1]
    assert round(sum(probs), 4) == 1.0

def test_estimate_information_gain_scenarios():
    # 0 candidates
    gain_0, method_0 = InformationGainService.estimate_information_gain([], "inspect_health", 0.75, True)
    assert 0.0 <= gain_0 <= 1.0
    assert method_0 == "heuristic_unobserved_cluster"

    # 1 candidate
    gain_1, method_1 = InformationGainService.estimate_information_gain([70.0], "inspect_health", 0.75, True)
    assert 0.0 <= gain_1 <= 1.0
    assert method_1 == "heuristic_single_candidate_verification"

    # Multiple candidates with competing scores
    gain_multi, method_multi = InformationGainService.estimate_information_gain([75.0, 70.0, 40.0], "compare_timestamps", 0.90, True)
    assert 0.0 <= gain_multi <= 1.0
    assert method_multi == "shannon_entropy_reduction"
