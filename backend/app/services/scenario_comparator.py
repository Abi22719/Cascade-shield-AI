import json
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session

from app.models.simulation_model import SimulationRunModel, SimulationScenarioModel
from app.schemas.simulation_schema import (
    ScenarioComparisonItem,
    ScenarioComparisonResponse
)

class ScenarioComparator:
    """
    Compares multiple simulation runs side-by-side to evaluate the resilience impact
    of different failure modes, durations, and recovery assumptions.
    """

    @classmethod
    def compare_runs(cls, db: Session, run_ids: List[str]) -> ScenarioComparisonResponse:
        comparisons = []

        for rid in run_ids:
            run = db.query(SimulationRunModel).filter(SimulationRunModel.id == rid).first()
            if not run or run.status != "COMPLETED" or not run.summary_json:
                continue

            scenario = db.query(SimulationScenarioModel).filter(SimulationScenarioModel.id == run.scenario_id).first()
            scen_name = scenario.name if scenario else f"Run {rid[:8]}"
            cat = scenario.category if scenario else "custom"

            config_dict = json.loads(scenario.scenario_config_json) if (scenario and scenario.scenario_config_json) else {}
            initial_targets = []
            for f in config_dict.get("failures", []):
                initial_targets.extend(f.get("target_service_ids", []))

            summary = json.loads(run.summary_json)

            comparisons.append(
                ScenarioComparisonItem(
                    run_id=run.id,
                    scenario_name=scen_name,
                    category=cat,
                    initial_failures=list(set(initial_targets)),
                    total_impacted_services=summary.get("total_impacted_services", 0),
                    peak_simultaneous_impact=summary.get("peak_simultaneous_impact", 0),
                    time_to_first_impact_step=summary.get("time_to_first_downstream_impact"),
                    time_to_recovery_step=summary.get("time_to_recovery"),
                    max_risk_score=summary.get("max_risk_score", 0.0),
                    avg_risk_score=summary.get("avg_risk_score", 0.0),
                    aggregate_impact_score=summary.get("aggregate_impact_score", 0.0),
                    residual_impact_count=len(summary.get("residual_impacted_services", []))
                )
            )

        if not comparisons:
            return ScenarioComparisonResponse(
                comparisons=[],
                summary_insights="No completed simulation runs available for comparison.",
                recommended_scenario=None
            )

        # Sort by aggregate impact score ascending (lowest impact is best)
        comparisons.sort(key=lambda c: c.aggregate_impact_score)
        best = comparisons[0]
        worst = comparisons[-1]

        insights = (
            f"Compared {len(comparisons)} simulation scenarios. "
            f"'{best.scenario_name}' demonstrated the highest cloud resilience with the lowest aggregate impact score "
            f"({best.aggregate_impact_score:.1f}/100 vs {worst.aggregate_impact_score:.1f}/100 for '{worst.scenario_name}'). "
            f"Early recovery reduced peak simultaneous impact from {worst.peak_simultaneous_impact} to {best.peak_simultaneous_impact} services."
        )

        return ScenarioComparisonResponse(
            comparisons=comparisons,
            summary_insights=insights,
            recommended_scenario=best.scenario_name
        )
