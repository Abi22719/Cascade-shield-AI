from typing import Dict, Any, List, Set, Tuple
from app.schemas.simulation_schema import (
    SimulatedServiceState,
    RecoveryParameters
)

class RecoveryModel:
    """
    Simulates recovery events (immediate, gradual, or none) across degraded services.
    Restores metrics towards baseline without modifying database models.
    """

    @classmethod
    def apply_recovery_step(
        cls,
        services: Dict[str, SimulatedServiceState],
        baseline_services: Dict[str, SimulatedServiceState],
        params: RecoveryParameters,
        current_step: int
    ) -> Tuple[List[str], List[Dict[str, Any]]]:
        """
        Executes recovery logic for the current step.
        Returns: (recovered_service_ids_in_step, recovery_events)
        """
        recovered_ids = []
        events = []

        if params.recovery_mode == "none":
            return recovered_ids, events

        rec_step = params.recovery_step or 5
        if current_step < rec_step:
            return recovered_ids, events

        # Target services to restore
        targets = set(params.restored_services) if params.restored_services else set(services.keys())

        for sid, state in services.items():
            if sid not in targets:
                continue
            if state.health_status in ["HEALTHY", "RECOVERED"]:
                continue

            base = baseline_services.get(sid)
            if not base:
                continue

            # First recovery step triggers RECOVERY_START event
            if current_step == rec_step and state.health_status not in ["RECOVERING"]:
                events.append({
                    "step_number": current_step,
                    "event_type": "RECOVERY_START",
                    "service_id": sid,
                    "description": f"Recovery mechanism activated for '{state.service_name}' ({params.recovery_mode}).",
                    "data": {"recovery_mode": params.recovery_mode, "initial_risk": state.risk_score}
                })

            if params.recovery_mode == "immediate":
                state.health_status = "RECOVERED"
                state.is_recovered = True
                state.risk_score = 0.0
                state.latency_ms = base.latency_ms
                state.error_rate = base.error_rate
                state.cpu_usage = base.cpu_usage
                state.memory_usage = base.memory_usage
                recovered_ids.append(sid)

                events.append({
                    "step_number": current_step,
                    "event_type": "RECOVERY_COMPLETE",
                    "service_id": sid,
                    "description": f"Immediate recovery complete: '{state.service_name}' restored to healthy baseline.",
                    "data": {"restored_latency": base.latency_ms, "restored_error_rate": base.error_rate}
                })

            elif params.recovery_mode == "gradual":
                rate = params.recovery_rate
                state.health_status = "RECOVERING"
                
                # Smooth metric convergence: val = val - (val - base) * rate
                state.latency_ms = max(base.latency_ms, state.latency_ms - (state.latency_ms - base.latency_ms) * rate)
                state.error_rate = max(base.error_rate, state.error_rate - (state.error_rate - base.error_rate) * rate)
                state.cpu_usage = max(base.cpu_usage, state.cpu_usage - (state.cpu_usage - base.cpu_usage) * rate)
                state.memory_usage = max(base.memory_usage, state.memory_usage - (state.memory_usage - base.memory_usage) * rate)
                state.risk_score = max(0.0, state.risk_score - (state.risk_score * rate))

                # If within 15% of baseline, complete recovery
                lat_diff = abs(state.latency_ms - base.latency_ms)
                err_diff = abs(state.error_rate - base.error_rate)
                if lat_diff < (base.latency_ms * 0.25) and err_diff < 0.2 and state.risk_score < 15.0:
                    state.health_status = "RECOVERED"
                    state.is_recovered = True
                    state.risk_score = 0.0
                    recovered_ids.append(sid)

                    events.append({
                        "step_number": current_step,
                        "event_type": "RECOVERY_COMPLETE",
                        "service_id": sid,
                        "description": f"Gradual recovery complete: '{state.service_name}' metrics converged back to baseline.",
                        "data": {"final_latency": round(state.latency_ms, 1), "final_error_rate": round(state.error_rate, 2)}
                    })

        return recovered_ids, events
