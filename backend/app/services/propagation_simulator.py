from typing import List, Dict, Any, Set, Tuple, Optional
import copy
from app.schemas.cascade_schema import (
    SimulationStepRecord,
    ImpactedServiceResult,
    CascadePredictRequest
)

class PropagationSimulator:
    @staticmethod
    def simulate_propagation_timeline(
        root_service_id: str,
        root_service_name: str,
        failure_type: str,
        failure_severity: str,
        impacted_results: List[ImpactedServiceResult],
        max_steps: int = 5
    ) -> List[SimulationStepRecord]:
        """
        Simulates step-by-step cascade propagation across discrete time intervals.
        Step 0: Initial failure injected at root service.
        Step 1: Failure wave hits Direct dependents (Hop 1).
        Step 2+: Failure wave propagates transitively to Indirect dependents (Hop 2+).
        """
        timeline: List[SimulationStepRecord] = []
        step_interval_seconds = 15  # 15 seconds per simulation step

        # Step 0: Inception at root service
        timeline.append(
            SimulationStepRecord(
                step=0,
                timestamp_offset_seconds=0,
                newly_affected_services=[root_service_name],
                cumulative_affected_count=1,
                average_risk_score=95.0 if failure_severity == "severe" else (70.0 if failure_severity == "moderate" else 40.0),
                step_description=f"Initial {failure_severity} {failure_type.replace('_', ' ')} incident occurs at '{root_service_name}'."
            )
        )

        cumulative_services: Set[str] = {root_service_name}

        # Group impacted services by their hop distance (which corresponds to step onset)
        services_by_hop: Dict[int, List[ImpactedServiceResult]] = {}
        for res in impacted_results:
            if res.hop_distance == 0:
                continue
            hop = res.hop_distance
            if hop not in services_by_hop:
                services_by_hop[hop] = []
            services_by_hop[hop].append(res)

        # Iterate steps 1 to max_steps
        for step in range(1, max_steps + 1):
            offset_sec = step * step_interval_seconds
            new_services_at_step = services_by_hop.get(step, [])
            newly_affected_names = [s.service_name for s in new_services_at_step]
            
            for name in newly_affected_names:
                cumulative_services.add(name)

            # Compute average risk among currently affected services
            relevant_results = [r for r in impacted_results if r.hop_distance <= step]
            avg_risk = round(sum(r.estimated_risk_score for r in relevant_results) / max(1, len(relevant_results)), 1) if relevant_results else 0.0

            if step == 1:
                desc = f"Wave 1 impact: Failure cascades directly to {len(newly_affected_names)} direct caller services ({', '.join(newly_affected_names) if newly_affected_names else 'None'})."
            elif newly_affected_names:
                desc = f"Wave {step} transitive propagation: Latency backlog and connection starvation reach {len(newly_affected_names)} secondary services ({', '.join(newly_affected_names)})."
            else:
                desc = f"Step {step}: Failure propagation stabilizes with no additional downstream services impacted."

            timeline.append(
                SimulationStepRecord(
                    step=step,
                    timestamp_offset_seconds=offset_sec,
                    newly_affected_services=newly_affected_names,
                    cumulative_affected_count=len(cumulative_services),
                    average_risk_score=avg_risk,
                    step_description=desc
                )
            )

        return timeline
