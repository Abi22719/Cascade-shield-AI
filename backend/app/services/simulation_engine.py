import copy
import json
import time
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional, Set
from sqlalchemy.orm import Session
import networkx as nx

from app.schemas.simulation_schema import (
    ScenarioConfigSchema,
    SimulationRunResponse,
    SimulationSummary,
    SimulationStepState,
    SimulatedServiceState
)
from app.services.simulation_state import SimulationState
from app.services.failure_model import FailureModel
from app.services.propagation_model import PropagationModel
from app.services.recovery_model import RecoveryModel
from app.services.metric_evolution import MetricEvolutionService
from app.database.simulation_repository import SimulationRepository

class SimulationEngine:
    """
    Core discrete time-step simulation engine for what-if cloud failure scenarios.
    Executes failure injection, multi-hop dependency propagation, metric evolution,
    and recovery tracking in complete isolation from production data.
    """

    @classmethod
    def run_simulation(
        cls,
        db: Session,
        scenario_id: str,
        scenario_name: str,
        config: ScenarioConfigSchema,
        random_seed: Optional[int] = None,
        max_steps_override: Optional[int] = None
    ) -> SimulationRunResponse:
        t_start = time.perf_counter()

        # Create Run record in SQLite
        seed = random_seed if random_seed is not None else config.random_seed
        run_record = SimulationRepository.create_run(db, {
            "scenario_id": scenario_id,
            "status": "RUNNING",
            "random_seed": seed,
            "model_version": "1.0.0",
            "total_steps": 0
        })

        try:
            # 1. Initialize isolated in-memory state
            sim_state = SimulationState.initialize_from_db(
                db=db,
                scenario_id=scenario_id,
                config=config,
                random_seed=seed
            )

            max_steps = max_steps_override or config.propagation.max_steps
            time_to_first_downstream = None
            time_to_recovery = None
            peak_impact = 0

            # 2. Discrete time-step execution loop
            for step in range(1, max_steps + 1):
                sim_state.current_step = step
                step_events = []
                newly_impacted_in_step = []
                recovered_in_step = []

                # A. Apply Scheduled Initial Failures
                for failure_cfg in config.failures:
                    # Check if failure is active during this step
                    if failure_cfg.start_step <= step < (failure_cfg.start_step + failure_cfg.duration_steps):
                        for target_id in failure_cfg.target_service_ids:
                            target_service = sim_state.services.get(target_id)
                            if target_service:
                                sim_state.active_failure_services.add(target_id)
                                sim_state.initial_failure_services.add(target_id)
                                sim_state.impacted_services.add(target_id)

                                fail_res = FailureModel.apply_initial_failure(target_service, failure_cfg)

                                # Record failure injection event on first step of injection
                                if step == failure_cfg.start_step:
                                    step_events.append({
                                        "step_number": step,
                                        "event_type": "FAILURE_INJECTION",
                                        "service_id": target_id,
                                        "description": fail_res["description"],
                                        "data": fail_res
                                    })
                    else:
                        # Past failure injection duration
                        for target_id in failure_cfg.target_service_ids:
                            sim_state.active_failure_services.discard(target_id)

                # B. Propagate Failure Waves to Dependent Callers
                if sim_state.active_failure_services:
                    newly_impacted, prop_events = PropagationModel.propagate_step(
                        G_prop=sim_state.G_prop,
                        services=sim_state.services,
                        active_failing_services=sim_state.active_failure_services,
                        params=config.propagation,
                        current_step=step
                    )
                    newly_impacted_in_step.extend(newly_impacted)
                    step_events.extend(prop_events)

                    for imp_id in newly_impacted:
                        sim_state.impacted_services.add(imp_id)
                        if time_to_first_downstream is None:
                            time_to_first_downstream = step

                # C. Apply Scheduled Recovery Logic
                recovered_ids, rec_events = RecoveryModel.apply_recovery_step(
                    services=sim_state.services,
                    baseline_services=sim_state.baseline_services,
                    params=config.recovery,
                    current_step=step
                )
                recovered_in_step.extend(recovered_ids)
                step_events.extend(rec_events)

                for rec_id in recovered_ids:
                    sim_state.recovered_services.add(rec_id)
                    sim_state.active_failure_services.discard(rec_id)
                    if time_to_recovery is None:
                        time_to_recovery = step

                # D. Apply Metric Fluctuations & Bounding
                for s in sim_state.services.values():
                    MetricEvolutionService.apply_step_fluctuation(s, step, seed)

                # Track peak simultaneous impact count
                current_active_degraded = sum(
                    1 for s in sim_state.services.values() 
                    if s.health_status in ["DEGRADED", "CRITICAL"]
                )
                peak_impact = max(peak_impact, current_active_degraded)

                # E. Record Step Snapshot in SimulationState
                sim_state.record_step_snapshot(
                    newly_impacted=newly_impacted_in_step,
                    recovered_in_step=recovered_in_step,
                    step_events=step_events
                )

                # F. Persist Events & Service States for this Step into SQLite
                for ev in step_events:
                    SimulationRepository.record_event(
                        db=db,
                        run_id=run_record.id,
                        step_number=step,
                        event_type=ev["event_type"],
                        service_id=ev["service_id"],
                        event_data=ev
                    )

                for sid, sstate in sim_state.services.items():
                    SimulationRepository.record_service_state(
                        db=db,
                        run_id=run_record.id,
                        step_number=step,
                        service_id=sid,
                        health_status=sstate.health_status,
                        state_dict=sstate.model_dump()
                    )

            # 3. Compute Final Summary Metrics
            all_risks = [s.risk_score for s in sim_state.services.values()]
            max_risk = max(all_risks, default=0.0)
            avg_risk = sum(all_risks) / len(all_risks) if all_risks else 0.0

            residual_services = [
                s.service_id for s in sim_state.services.values() 
                if s.health_status in ["DEGRADED", "CRITICAL"]
            ]

            # Aggregate impact score (0 to 100): combines peak breadth, average risk, and residual duration
            breadth_ratio = len(sim_state.impacted_services) / max(1, len(sim_state.services))
            residual_penalty = len(residual_services) / max(1, len(sim_state.services))
            agg_impact = (breadth_ratio * 40.0) + (avg_risk * 0.40) + (residual_penalty * 20.0)

            summary = SimulationSummary(
                total_impacted_services=len(sim_state.impacted_services),
                peak_simultaneous_impact=peak_impact,
                time_to_first_downstream_impact=time_to_first_downstream,
                time_to_recovery=time_to_recovery,
                max_risk_score=round(max_risk, 1),
                avg_risk_score=round(avg_risk, 1),
                aggregate_impact_score=round(min(100.0, agg_impact), 1),
                propagation_events_count=len([e for e in sim_state.all_events if e.get("event_type") == "PROPAGATION_WAVE"]),
                residual_impacted_services=residual_services
            )

            # Extract propagation paths using NetworkX
            propagation_paths = []
            for initial_id in sim_state.initial_failure_services:
                if initial_id in sim_state.G_prop:
                    for target_id in sim_state.impacted_services:
                        if target_id != initial_id and nx.has_path(sim_state.G_prop, initial_id, target_id):
                            try:
                                for p in nx.all_simple_paths(sim_state.G_prop, initial_id, target_id, cutoff=4):
                                    propagation_paths.append(p)
                                    if len(propagation_paths) >= 10:
                                        break
                            except Exception:
                                pass

            # Update Run in Database
            SimulationRepository.update_run(
                db=db,
                run_id=run_record.id,
                status="COMPLETED",
                total_steps=max_steps,
                summary_json=summary.model_dump_json(),
                error_summary=None
            )

            return SimulationRunResponse(
                id=run_record.id,
                scenario_id=scenario_id,
                scenario_name=scenario_name,
                status="COMPLETED",
                random_seed=seed,
                model_version="1.0.0",
                total_steps=max_steps,
                started_at=run_record.started_at,
                completed_at=datetime.now(timezone.utc),
                summary=summary,
                error_summary=None,
                timeline_steps=sim_state.step_history,
                impacted_services=list(sim_state.impacted_services),
                propagation_paths=propagation_paths
            )

        except Exception as ex:
            SimulationRepository.update_run(
                db=db,
                run_id=run_record.id,
                status="FAILED",
                total_steps=0,
                summary_json=None,
                error_summary=str(ex)
            )
            raise
