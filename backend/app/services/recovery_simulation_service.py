import copy
import json
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session

from app.models.recovery_models import RecoveryPlanModel
from app.models.simulation_model import SimulationScenarioModel
from app.schemas.simulation_schema import ScenarioConfigSchema, FailureInjectionConfig
from app.schemas.recovery_schemas import (
    RecoverySimulationRequest, 
    RecoverySimulationResponse
)
from app.services.simulation_state import SimulationState
from app.services.failure_model import FailureModel
from app.database.recovery_repository import RecoveryRepository

class RecoverySimulationService:
    """
    Executes recovery plans inside an isolated Module 6 simulation canvas.
    Tracks step-by-step action execution, precondition verifications, metric convergence,
    downstream cascade resolution, and rollback events with zero mutation to live records.
    """

    @classmethod
    def simulate_recovery_plan(
        cls,
        db: Session,
        plan_id: str,
        req: RecoverySimulationRequest
    ) -> RecoverySimulationResponse:
        plan = RecoveryRepository.get_plan(db, plan_id)
        if not plan:
            raise ValueError(f"Recovery Plan '{plan_id}' not found.")

        # 1. Determine scenario configuration to run against
        seed = req.random_seed if req.random_seed is not None else 42
        scenario_config = ScenarioConfigSchema()

        if plan.scenario_id:
            scen_record = db.query(SimulationScenarioModel).filter(SimulationScenarioModel.id == plan.scenario_id).first()
            if scen_record and scen_record.scenario_config_json:
                scenario_config = ScenarioConfigSchema(**json.loads(scen_record.scenario_config_json))
        else:
            # Construct scenario config using target services from plan actions
            target_ids = list({act.target_service_id for act in plan.actions if act.target_service_id})
            if not target_ids:
                target_ids = ["srv-payment"]
            scenario_config.failures = [
                FailureInjectionConfig(
                    target_service_ids=target_ids,
                    failure_type="service_unavailable",
                    severity="severe",
                    start_step=1,
                    duration_steps=4
                )
            ]

        # 2. Initialize isolated in-memory simulation state
        sim_state = SimulationState.initialize_from_db(
            db=db,
            scenario_id=plan.scenario_id or "adhoc-sim",
            config=scenario_config,
            random_seed=seed
        )

        # Apply initial failure injection to target services at step 1
        for failure_cfg in scenario_config.failures:
            for tid in failure_cfg.target_service_ids:
                if tid in sim_state.services:
                    FailureModel.apply_initial_failure(sim_state.services[tid], failure_cfg)
                    sim_state.active_failure_services.add(tid)
                    sim_state.impacted_services.add(tid)

        # 3. Create Simulation Run record
        run_record = RecoveryRepository.create_run(db, {
            "plan_id": plan.id,
            "simulation_run_id": None,
            "outcome": "SUCCESSFUL_RECOVERY",
            "total_recovery_time": 0,
            "maximum_risk": plan.risk_score,
            "final_health_summary": {}
        })

        events: List[Dict[str, Any]] = []
        step_comparisons: List[Dict[str, Any]] = []
        actions = sorted(plan.actions, key=lambda a: a.action_order)

        current_step = 1
        failed_steps_count = 0
        total_recovery_time = 0
        max_risk_observed = plan.risk_score

        # Record initial baseline state comparison at Step 0
        step_comparisons.append({
            "step_number": 0,
            "status": "INCIDENT_ACTIVE",
            "services": {sid: s.health_status for sid, s in sim_state.services.items()}
        })

        # 4. Sequentially execute recovery actions
        for act in actions:
            target_id = act.target_service_id or "srv-payment"
            target_svc = sim_state.services.get(target_id)
            base_svc = sim_state.baseline_services.get(target_id)

            action_params = json.loads(act.parameters_json or "{}")
            preconditions = json.loads(act.preconditions_json or "[]")

            # A. Check preconditions
            precondition_failed = False
            for p in preconditions:
                p_status = p.get("status", "satisfied")
                if p_status == "violated":
                    precondition_failed = True
                    desc = f"Action '{act.action_type}' failed: Precondition '{p.get('name')}' was violated."
                    ev = RecoveryRepository.record_event(
                        db=db,
                        run_id=run_record.id,
                        event_type="PRECONDITION_FAILED",
                        description=desc,
                        evidence={"action_id": act.id, "precondition": p},
                        step=current_step
                    )
                    events.append({"event_type": "PRECONDITION_FAILED", "description": desc, "step": current_step})
                    break

            if precondition_failed:
                failed_steps_count += 1
                if req.stop_on_failure:
                    # Rollback triggered
                    desc = f"Rollback triggered: Plan aborted due to violated precondition on action '{act.action_type}'."
                    RecoveryRepository.record_event(
                        db=db,
                        run_id=run_record.id,
                        event_type="ROLLBACK_TRIGGERED",
                        description=desc,
                        evidence={"action_id": act.id},
                        step=current_step
                    )
                    events.append({"event_type": "ROLLBACK_TRIGGERED", "description": desc, "step": current_step})
                    break
                else:
                    current_step += 1
                    continue

            # B. Emit ACTION_STARTED event
            start_desc = f"Executing recovery action: '{act.action_type}' on target '{target_id}'."
            RecoveryRepository.record_event(
                db=db,
                run_id=run_record.id,
                event_type="ACTION_STARTED",
                description=start_desc,
                evidence={"action_id": act.id, "target_service": target_id, "params": action_params},
                step=current_step
            )
            events.append({"event_type": "ACTION_STARTED", "description": start_desc, "step": current_step})

            # C. Apply state changes to target service
            if target_svc and base_svc:
                atype = act.action_type

                if atype in ["restart_service", "rollback_deployment", "restore_database"]:
                    target_svc.health_status = "HEALTHY"
                    target_svc.latency_ms = base_svc.latency_ms
                    target_svc.error_rate = base_svc.error_rate
                    target_svc.cpu_usage = base_svc.cpu_usage
                    target_svc.risk_score = 0.0
                    target_svc.is_recovered = True
                    target_svc.is_initial_failure = False
                    sim_state.active_failure_services.discard(target_id)

                elif atype in ["scale_up", "traffic_reroute"]:
                    target_svc.health_status = "HEALTHY"
                    target_svc.latency_ms = max(base_svc.latency_ms, target_svc.latency_ms * 0.4)
                    target_svc.error_rate = max(base_svc.error_rate, target_svc.error_rate * 0.15)
                    target_svc.cpu_usage = max(base_svc.cpu_usage, target_svc.cpu_usage * 0.5)
                    target_svc.risk_score = max(0.0, target_svc.risk_score * 0.2)
                    target_svc.is_recovered = True
                    sim_state.active_failure_services.discard(target_id)

                elif atype in ["isolate_dependency", "retry_request", "wait_auto_recovery"]:
                    target_svc.health_status = "RECOVERING"
                    target_svc.latency_ms = max(base_svc.latency_ms, target_svc.latency_ms * 0.6)
                    target_svc.error_rate = max(base_svc.error_rate, target_svc.error_rate * 0.4)
                    target_svc.risk_score = max(0.0, target_svc.risk_score * 0.4)

                # D. Resolve downstream caller cascades in propagation graph G_prop
                if target_id in sim_state.G_prop:
                    for caller_id in sim_state.G_prop.successors(target_id):
                        caller_svc = sim_state.services.get(caller_id)
                        caller_base = sim_state.baseline_services.get(caller_id)
                        if caller_svc and caller_base and caller_svc.health_status in ["DEGRADED", "CRITICAL"]:
                            caller_svc.health_status = "HEALTHY"
                            caller_svc.latency_ms = caller_base.latency_ms
                            caller_svc.error_rate = caller_base.error_rate
                            caller_svc.risk_score = 0.0
                            caller_svc.is_recovered = True

                            res_desc = f"Downstream cascade resolved for caller '{caller_id}' following recovery of upstream '{target_id}'."
                            RecoveryRepository.record_event(
                                db=db,
                                run_id=run_record.id,
                                event_type="CASCADE_RESOLVED",
                                description=res_desc,
                                evidence={"recovered_upstream": target_id, "dependent_service": caller_id},
                                step=current_step
                            )
                            events.append({"event_type": "CASCADE_RESOLVED", "description": res_desc, "step": current_step})

            # E. Emit ACTION_COMPLETED event
            comp_desc = f"Action '{act.action_type}' successfully applied to '{target_id}'."
            RecoveryRepository.record_event(
                db=db,
                run_id=run_record.id,
                event_type="ACTION_COMPLETED",
                description=comp_desc,
                evidence={"action_id": act.id, "resulting_health": target_svc.health_status if target_svc else "UNKNOWN"},
                step=current_step
            )
            events.append({"event_type": "ACTION_COMPLETED", "description": comp_desc, "step": current_step})

            # Record step comparison
            step_comparisons.append({
                "step_number": current_step,
                "action_type": act.action_type,
                "target_service_id": target_id,
                "services": {sid: s.health_status for sid, s in sim_state.services.items()}
            })

            current_step += act.estimated_duration
            total_recovery_time += act.estimated_duration

        # 5. Determine final outcome
        all_final_healths = {sid: s.health_status for sid, s in sim_state.services.items()}
        critical_count = sum(1 for h in all_final_healths.values() if h == "CRITICAL")
        degraded_count = sum(1 for h in all_final_healths.values() if h in ["DEGRADED", "RECOVERING"])

        if failed_steps_count > 0 and critical_count > 0:
            final_outcome = "FAILED_RECOVERY"
        elif degraded_count > 0 or critical_count > 0:
            final_outcome = "PARTIAL_RECOVERY"
        else:
            final_outcome = "SUCCESSFUL_RECOVERY"

        # Update Run record in database
        run_record.outcome = final_outcome
        run_record.total_recovery_time = total_recovery_time
        run_record.maximum_risk = max_risk_observed
        run_record.final_health_summary = json.dumps(all_final_healths)
        db.commit()
        db.refresh(run_record)

        # Update Plan status to SIMULATED
        plan.status = "SIMULATED"
        db.commit()

        return RecoverySimulationResponse(
            id=run_record.id,
            plan_id=plan.id,
            simulation_run_id=run_record.simulation_run_id,
            outcome=final_outcome,
            total_recovery_time=total_recovery_time,
            maximum_risk=max_risk_observed,
            final_health_summary=all_final_healths,
            events=events,
            step_comparisons=step_comparisons,
            created_at=run_record.created_at
        )
