import pytest
from app.services.agent_evaluation import AgentEvaluationService

def test_agent_evaluation_benchmark_metrics():
    res = AgentEvaluationService.run_benchmark_evaluation()
    assert res.benchmark_scenarios_count == 5

    # Strategy 1: Fixed Order
    fixed = res.baseline_fixed_order
    assert fixed.strategy_name == "Fixed-Order Sequence"
    assert fixed.avg_actions_required == 5.0
    assert fixed.accuracy_top1 < 1.0  # fails on ambiguous

    # Strategy 2: Relevance First
    rel = res.baseline_relevance_first
    assert rel.strategy_name == "Highest-Relevance First"
    assert rel.repeated_action_rate > 0.0  # high repetition

    # Strategy 3: Adaptive Utility Agent
    agent = res.adaptive_utility_agent
    assert agent.strategy_name == "Adaptive Utility Agent (Module 5)"
    assert agent.accuracy_top1 == 1.0
    assert agent.accuracy_top3 == 1.0
    assert agent.avg_actions_required < fixed.avg_actions_required
    assert agent.repeated_action_rate == 0.0
    assert agent.avg_cost < fixed.avg_cost
    assert len(res.summary_findings) > 0
