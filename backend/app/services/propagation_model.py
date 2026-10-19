from typing import Dict, Any, List, Set, Tuple
import networkx as nx
from app.schemas.simulation_schema import (
    SimulatedServiceState,
    PropagationParameters
)

class PropagationModel:
    """
    Simulates discrete time-step failure propagation from failing services to dependent callers.
    Uses reverse propagation graph (callee -> caller), protocol coupling weights,
    distance attenuation, multi-path confluence, and cycle-safe traversal.
    """

    @classmethod
    def propagate_step(
        cls,
        G_prop: nx.DiGraph,
        services: Dict[str, SimulatedServiceState],
        active_failing_services: Set[str],
        params: PropagationParameters,
        current_step: int
    ) -> Tuple[List[str], List[Dict[str, Any]]]:
        """
        Executes one discrete propagation step.
        Returns: (newly_impacted_service_ids, step_propagation_events)
        """
        newly_impacted = []
        events = []
        coupling_weights = params.protocol_coupling_weights or {
            "sync_http": 1.0,
            "database_read_write": 0.95,
            "async_message": 0.45,
            "cache_lookup": 0.40
        }

        # Candidate callers to evaluate: immediate out-edges of actively failing services
        potential_callers: Dict[str, List[Tuple[str, float]]] = {}
        for failing_id in active_failing_services:
            if failing_id not in G_prop:
                continue
            failing_state = services.get(failing_id)
            if not failing_state or failing_state.health_status in ["HEALTHY", "RECOVERED"]:
                continue

            upstream_risk = failing_state.risk_score

            for caller_id in G_prop.successors(failing_id):
                # Don't propagate backwards to the initial failing nodes themselves
                caller_state = services.get(caller_id)
                if not caller_state or caller_state.is_initial_failure:
                    continue

                edge_data = G_prop.get_edge_data(failing_id, caller_id) or {}
                proto = edge_data.get("protocol", "sync_http")
                weight = coupling_weights.get(proto, 0.7)

                # Attenuated incoming risk contribution
                attenuated_risk = upstream_risk * weight * params.attenuation_factor

                if caller_id not in potential_callers:
                    potential_callers[caller_id] = []
                potential_callers[caller_id].append((failing_id, attenuated_risk))

        # Evaluate each potential caller
        for caller_id, incoming_risks in potential_callers.items():
            caller = services[caller_id]
            was_healthy = caller.health_status in ["HEALTHY", "RECOVERED"]

            # Independent multi-path confluence: 1 - prod(1 - r/100)
            product_safe = 1.0
            for upstream_id, r in incoming_risks:
                product_safe *= max(0.0, 1.0 - (min(100.0, r) / 100.0))
            combined_risk = 100.0 * (1.0 - product_safe)

            # Accumulate risk if already degraded or set new
            new_risk = max(caller.risk_score, combined_risk)
            caller.risk_score = round(min(100.0, new_risk), 1)

            # Check if threshold crossed to trigger state degradation
            if caller.risk_score >= params.propagation_threshold:
                if was_healthy:
                    caller.is_impacted = True
                    caller.is_recovered = False
                    newly_impacted.append(caller_id)

                    # Update caller metrics based on propagated degradation
                    if caller.risk_score >= 70.0:
                        caller.health_status = "CRITICAL"
                        caller.latency_ms = max(caller.latency_ms, 850.0 + (caller.risk_score * 8.0))
                        caller.error_rate = min(100.0, max(caller.error_rate, 8.0 + (caller.risk_score * 0.4)))
                    else:
                        caller.health_status = "DEGRADED"
                        caller.latency_ms = max(caller.latency_ms, 220.0 + (caller.risk_score * 4.5))
                        caller.error_rate = min(50.0, max(caller.error_rate, 1.5 + (caller.risk_score * 0.15)))

                    upstream_names = [uid for uid, _ in incoming_risks]
                    desc = (
                        f"Propagation wave reached caller '{caller.service_name}' ({caller_id}) "
                        f"from upstream [{', '.join(upstream_names)}]. "
                        f"Status transitioned to {caller.health_status} (Risk: {caller.risk_score:.1f}/100, Latency: {caller.latency_ms:.0f}ms)."
                    )
                    events.append({
                        "step_number": current_step,
                        "event_type": "PROPAGATION_WAVE",
                        "service_id": caller_id,
                        "description": desc,
                        "data": {
                            "upstream_services": upstream_names,
                            "incoming_risks": [r for _, r in incoming_risks],
                            "combined_risk": caller.risk_score,
                            "new_health": caller.health_status
                        }
                    })

        return newly_impacted, events
