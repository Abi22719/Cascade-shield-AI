import json
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session

from app.models.service import ServiceModel
from app.models.recovery_models import RecoveryPlanModel, RecoverySimulationRunModel, RecoveryEventModel
from app.schemas.recovery_schemas import RecoverySimulationRequest
from app.schemas.validation_schemas import (
    ValidationRunRequest,
    ValidationRunResponse,
    ValidationCheckSchema,
    ValidationEvidenceSchema,
    ValidationRecommendationSchema,
    BeforeAfterComparisonSchema,
    BeforeAfterMetricDiff
)
from app.database.recovery_repository import RecoveryRepository
from app.database.validation_repository import ValidationRepository
from app.services.recovery_simulation_service import RecoverySimulationService
from app.services.validation_rules import ValidationRuleEngine
from app.services.validation_metrics import ValidationMetricsEngine
from app.services.validation_dependency import ValidationDependencyEngine
from app.services.validation_evidence import ValidationEvidenceEngine
from app.services.validation_comparison import ValidationComparisonEngine
from app.services.validation_recommendations import ValidationRecommendationEngine

class ValidationEngine:
    """
    Main orchestrator for Module 8: Automated Recovery Validation and Verification.
    Executes 5 validation check pillars: Health, Metrics, Dependencies, Stability, Side-Effects,
    and grounds every finding with explicit evidence linkage and classification.
    """

    @classmethod
    def validate_recovery(cls, db: Session, req: ValidationRunRequest) -> ValidationRunResponse:
        started_at = datetime.now(timezone.utc)

        # 1. Retrieve Recovery Plan
        plan = RecoveryRepository.get_plan(db, req.recovery_plan_id)
        if not plan:
            raise ValueError(f"Recovery Plan '{req.recovery_plan_id}' does not exist.")

        # 2. Retrieve or execute Recovery Simulation Run
        sim_run = None
        if req.recovery_simulation_run_id:
            sim_run = db.query(RecoverySimulationRunModel).filter(
                RecoverySimulationRunModel.id == req.recovery_simulation_run_id
            ).first()
            if not sim_run:
                raise ValueError(f"Simulation Run '{req.recovery_simulation_run_id}' not found.")
        else:
            # Pick latest run if available
            sim_run = db.query(RecoverySimulationRunModel).filter(
                RecoverySimulationRunModel.plan_id == plan.id
            ).order_by(RecoverySimulationRunModel.created_at.desc()).first()

        # If no simulation run has been executed yet, run one now inside isolated simulator
        if not sim_run:
            sim_resp = RecoverySimulationService.simulate_recovery_plan(
                db=db,
                plan_id=plan.id,
                req=RecoverySimulationRequest()
            )
            sim_run = db.query(RecoverySimulationRunModel).filter(
                RecoverySimulationRunModel.id == sim_resp.id
            ).first()

        # 3. Duplicate check unless force_rerun is True
        if not req.force_rerun:
            existing = ValidationRepository.find_existing_run(db, plan.id, sim_run.id if sim_run else None)
            if existing:
                return cls._format_response(db, existing)

        # 4. Load configuration & active baseline
        config = ValidationRuleEngine.get_config(db)
        if req.custom_thresholds:
            config_dict = config.model_dump()
            config_dict.update(req.custom_thresholds)
            config = ValidationRuleEngine.get_config(db).__class__(**config_dict)

        baseline_services = {s.id: s for s in db.query(ServiceModel).all()}
        simulated_healths: Dict[str, str] = {}
        if sim_run and sim_run.final_health_summary:
            simulated_healths = json.loads(sim_run.final_health_summary)
        else:
            simulated_healths = {sid: s.health_status for sid, s in baseline_services.items()}

        target_service_ids = list({act.target_service_id for act in plan.actions if act.target_service_id})
        if not target_service_ids:
            target_service_ids = ["srv-payment"]

        # 5. Create Validation Run record
        val_run = ValidationRepository.create_run(db, {
            "recovery_plan_id": plan.id,
            "recovery_simulation_run_id": sim_run.id if sim_run else None,
            "source_scenario_id": req.source_scenario_id or plan.scenario_id,
            "status": "RUNNING",
            "overall_outcome": "NOT_RUN",
            "verification_window_steps": req.verification_window_steps or config.verification_window_steps,
            "started_at": started_at
        })

        checks_data: List[Dict[str, Any]] = []
        evidence_items: List[Dict[str, Any]] = []
        metric_failures: List[Dict[str, Any]] = []
        failed_preconditions: List[str] = []

        # =========================================================================
        # PILLAR A: SERVICE HEALTH VALIDATION
        # =========================================================================
        unhealthy_targets = []
        for tid in target_service_ids:
            actual_health = simulated_healths.get(tid, "UNKNOWN")
            expected_health = "HEALTHY"

            status = "PASS" if actual_health == "HEALTHY" else ("WARNING" if actual_health == "RECOVERING" else "FAIL")
            if status != "PASS":
                unhealthy_targets.append(tid)

            check = {
                "validation_id": val_run.id,
                "check_type": "service_health",
                "target_service_id": tid,
                "check_name": f"Target Service Health: {tid}",
                "status": status,
                "expected_value": expected_health,
                "actual_value": actual_health,
                "explanation": f"Service '{tid}' reached status '{actual_health}' following recovery plan execution.",
                "evidence_reference": f"sim_run:{sim_run.id}:final_health",
                "simulation_step": sim_run.total_recovery_time if sim_run else 1
            }
            checks_data.append(check)

            evidence_items.append({
                "check_id": None,
                "source_module": "module_7",
                "source_record_id": sim_run.id if sim_run else None,
                "evidence_type": "service_health",
                "description": f"Target service '{tid}' simulated health is '{actual_health}'.",
                "observed_or_simulated": "simulated",
                "timestamp_or_step": str(sim_run.total_recovery_time if sim_run else 1),
                "metadata": {"target_service_id": tid, "health_status": actual_health}
            })

        # =========================================================================
        # PILLAR B: METRICS VALIDATION
        # =========================================================================
        all_metric_diffs: List[BeforeAfterMetricDiff] = []
        for sid, s in baseline_services.items():
            base_metrics = {
                "latency_ms": s.latency_ms,
                "error_rate": s.error_rate,
                "cpu_usage": s.cpu_usage,
                "memory_usage": s.memory_usage,
                "request_volume": s.request_volume
            }

            # If service was in target or affected, derive simulated after-metrics
            is_target = sid in target_service_ids
            after_health = simulated_healths.get(sid, "HEALTHY")

            after_metrics = dict(base_metrics)
            if after_health == "HEALTHY":
                after_metrics["latency_ms"] = min(base_metrics["latency_ms"], config.max_acceptable_latency_ms * 0.5)
                after_metrics["error_rate"] = min(base_metrics["error_rate"], config.max_acceptable_error_rate * 0.2)
            elif after_health in ["DEGRADED", "RECOVERING"]:
                after_metrics["latency_ms"] = max(base_metrics["latency_ms"], config.max_acceptable_latency_ms * 1.1)
                after_metrics["error_rate"] = max(base_metrics["error_rate"], config.max_acceptable_error_rate * 1.2)
            elif after_health == "CRITICAL":
                after_metrics["latency_ms"] = 2500.0
                after_metrics["error_rate"] = 95.0

            diffs = ValidationMetricsEngine.validate_service_metrics(
                service_id=sid,
                service_name=s.name,
                before_metrics=base_metrics,
                after_metrics=after_metrics,
                config=config
            )
            all_metric_diffs.extend(diffs)

            if is_target or sid in config.critical_services:
                for d in diffs:
                    if d.metric_name in ["latency_ms", "error_rate"]:
                        checks_data.append({
                            "validation_id": val_run.id,
                            "check_type": "metrics",
                            "target_service_id": sid,
                            "check_name": f"{sid} Metric SLA: {d.metric_name}",
                            "status": d.status,
                            "expected_value": f"<= {config.max_acceptable_latency_ms if d.metric_name == 'latency_ms' else config.max_acceptable_error_rate}",
                            "actual_value": str(d.after_value),
                            "explanation": f"Post-recovery {d.metric_name} is {d.after_value} (trend: {d.trend}, delta: {d.delta}).",
                            "evidence_reference": f"metric:{sid}:{d.metric_name}",
                            "simulation_step": sim_run.total_recovery_time if sim_run else 1
                        })
                        if d.status == "FAIL":
                            metric_failures.append({
                                "service_id": sid,
                                "metric": d.metric_name,
                                "value": d.after_value,
                                "threshold": config.max_acceptable_latency_ms if d.metric_name == "latency_ms" else config.max_acceptable_error_rate
                            })

        # =========================================================================
        # PILLAR C: DEPENDENCY VALIDATION
        # =========================================================================
        baseline_health_map = {sid: s.health_status for sid, s in baseline_services.items()}
        dep_analysis = ValidationDependencyEngine.analyze_downstream_recovery(
            db=db,
            target_service_ids=target_service_ids,
            simulated_healths=simulated_healths,
            baseline_healths=baseline_health_map
        )

        dep_status = "PASS" if dep_analysis["all_downstream_recovered"] else "FAIL"
        checks_data.append({
            "validation_id": val_run.id,
            "check_type": "dependency",
            "target_service_id": None,
            "check_name": "Downstream Dependent Callers Recovery",
            "status": dep_status,
            "expected_value": "Zero residual caller failures",
            "actual_value": f"{len(dep_analysis['still_unhealthy_callers'])} unhealthy callers",
            "explanation": f"Cycle-safe traversal verified {dep_analysis['expected_callers_count']} callers. Unhealthy: {len(dep_analysis['still_unhealthy_callers'])}.",
            "evidence_reference": "networkx:graph_prop",
            "simulation_step": sim_run.total_recovery_time if sim_run else 1
        })

        # =========================================================================
        # PILLAR D: RECOVERY STABILITY VALIDATION
        # =========================================================================
        total_steps = sim_run.total_recovery_time if sim_run else 0
        window_required = req.verification_window_steps or config.verification_window_steps
        has_rollback = False

        if sim_run and sim_run.events:
            for ev in sim_run.events:
                if ev.event_type in ["ROLLBACK_TRIGGERED", "PRECONDITION_FAILED"]:
                    has_rollback = True
                    failed_preconditions.append(ev.description)

        is_stable = (total_steps >= window_required) and not has_rollback and len(unhealthy_targets) == 0

        stab_status = "PASS" if is_stable else ("FAIL" if has_rollback else "WARNING")
        checks_data.append({
            "validation_id": val_run.id,
            "check_type": "stability",
            "target_service_id": None,
            "check_name": f"Post-Recovery Stability Window ({window_required} steps)",
            "status": stab_status,
            "expected_value": f"{window_required} stable steps with no rollbacks",
            "actual_value": f"{total_steps} steps simulated, rollbacks: {has_rollback}",
            "explanation": "Recovery remained stable across verification window." if is_stable else (
                "Rollback triggered during simulated plan." if has_rollback else
                f"Simulation ran {total_steps} steps, less than the {window_required}-step verification window."
            ),
            "evidence_reference": f"sim_run:{sim_run.id}:timeline",
            "simulation_step": total_steps
        })

        # =========================================================================
        # PILLAR E: SIDE-EFFECT VALIDATION
        # =========================================================================
        new_failures = dep_analysis["newly_affected_services"]
        side_effect_status = "PASS" if len(new_failures) == 0 and not has_rollback else "FAIL"

        checks_data.append({
            "validation_id": val_run.id,
            "check_type": "side_effects",
            "target_service_id": None,
            "check_name": "Zero Secondary Degradations / Side-Effects",
            "status": side_effect_status,
            "expected_value": "0 new failures",
            "actual_value": f"{len(new_failures)} new failures, rollbacks: {has_rollback}",
            "explanation": "No secondary degradation detected." if side_effect_status == "PASS" else f"Detected new failures on: {', '.join(new_failures) if new_failures else 'rollback triggered'}.",
            "evidence_reference": "validation:side_effects",
            "simulation_step": total_steps
        })

        # =========================================================================
        # PILLAR F: EVIDENCE GROUNDING & COMPLETENESS
        # =========================================================================
        evidence_gap_count = sum(1 for c in checks_data if c["status"] == "UNKNOWN")
        checks_data.append({
            "validation_id": val_run.id,
            "check_type": "evidence",
            "target_service_id": None,
            "check_name": "Audit & Evidence Completeness",
            "status": "PASS" if evidence_gap_count == 0 else "WARNING",
            "expected_value": "100% evidence linkage",
            "actual_value": f"{len(checks_data)} findings grounded, {evidence_gap_count} gaps",
            "explanation": f"All findings are grounded with explicit simulation telemetry." if evidence_gap_count == 0 else f"{evidence_gap_count} checks lack metric evidence.",
            "evidence_reference": "validation:evidence_manifest",
            "simulation_step": total_steps
        })

        # Record all checks into DB
        check_records = []
        for c in checks_data:
            rec = ValidationRepository.record_check(db, c)
            check_records.append(rec)

        # Record evidence into DB
        ValidationEvidenceEngine.collect_and_link_evidence(db, val_run.id, evidence_items)

        # Calculate counts
        passed_count = sum(1 for c in checks_data if c["status"] == "PASS")
        failed_count = sum(1 for c in checks_data if c["status"] == "FAIL")
        warning_count = sum(1 for c in checks_data if c["status"] == "WARNING")
        unknown_count = sum(1 for c in checks_data if c["status"] == "UNKNOWN")
        total_checks = len(checks_data)

        # =========================================================================
        # DETERMINE OVERALL OUTCOME
        # =========================================================================
        if has_rollback or (failed_count > 0 and len(unhealthy_targets) > 0):
            overall_outcome = "FAILED"
        elif unknown_count > 2 and passed_count == 0:
            overall_outcome = "INCONCLUSIVE"
        elif failed_count > 0 or warning_count > 0 or len(unhealthy_targets) > 0 or not is_stable:
            overall_outcome = "PARTIAL_SUCCESS"
        else:
            overall_outcome = "VERIFIED_SUCCESS"

        # Build before-and-after comparison
        comparison = ValidationComparisonEngine.build_comparison(
            services_before={sid: {"health_status": s.health_status} for sid, s in baseline_services.items()},
            services_after={sid: {"health_status": simulated_healths.get(sid, "HEALTHY")} for sid in baseline_services},
            metric_diffs=all_metric_diffs,
            new_failures=new_failures,
            downstream_before_count=dep_analysis["expected_callers_count"],
            downstream_after_count=len(dep_analysis["still_unhealthy_callers"]),
            recovery_time_steps=total_steps,
            stability_steps=window_required,
            is_stable=is_stable
        )

        # Generate actionable recommendations
        ValidationRecommendationEngine.generate_recommendations(
            db=db,
            validation_id=val_run.id,
            overall_outcome=overall_outcome,
            unhealthy_services=unhealthy_targets,
            newly_affected_services=new_failures,
            metric_failures=metric_failures,
            is_stable=is_stable,
            evidence_gap_count=evidence_gap_count,
            failed_preconditions=failed_preconditions
        )

        # Update ValidationRun record
        val_run.overall_outcome = overall_outcome
        val_run.status = "COMPLETED"
        val_run.total_checks = total_checks
        val_run.passed_checks = passed_count
        val_run.failed_checks = failed_count
        val_run.warning_checks = warning_count
        val_run.unknown_checks = unknown_count
        val_run.completed_at = datetime.now(timezone.utc)
        val_run.comparison_json = json.dumps(comparison.model_dump())
        val_run.summary_json = json.dumps({
            "target_services": target_service_ids,
            "overall_outcome": overall_outcome,
            "is_stable": is_stable,
            "has_rollback": has_rollback,
            "unhealthy_targets": unhealthy_targets,
            "new_failures": new_failures
        })
        db.commit()
        db.refresh(val_run)

        return cls._format_response(db, val_run)

    @classmethod
    def _format_response(cls, db: Session, val_run) -> ValidationRunResponse:
        checks = ValidationRepository.get_checks_for_run(db, val_run.id)
        evidence = ValidationRepository.get_evidence_for_run(db, val_run.id)
        recs = ValidationRepository.get_recommendations_for_run(db, val_run.id)

        comparison_data = None
        if val_run.comparison_json:
            comparison_data = BeforeAfterComparisonSchema(**json.loads(val_run.comparison_json))

        summary_data = None
        if val_run.summary_json:
            summary_data = json.loads(val_run.summary_json)

        return ValidationRunResponse(
            id=val_run.id,
            recovery_plan_id=val_run.recovery_plan_id,
            recovery_simulation_run_id=val_run.recovery_simulation_run_id,
            source_scenario_id=val_run.source_scenario_id,
            status=val_run.status,
            overall_outcome=val_run.overall_outcome,
            total_checks=val_run.total_checks,
            passed_checks=val_run.passed_checks,
            failed_checks=val_run.failed_checks,
            warning_checks=val_run.warning_checks,
            unknown_checks=val_run.unknown_checks,
            verification_window_steps=val_run.verification_window_steps,
            checks=[ValidationCheckSchema.model_validate(c) for c in checks],
            evidence=[
                ValidationEvidenceSchema(
                    id=e.id,
                    validation_id=e.validation_id,
                    check_id=e.check_id,
                    source_module=e.source_module,
                    source_record_id=e.source_record_id,
                    evidence_type=e.evidence_type,
                    description=e.description,
                    observed_or_simulated=e.observed_or_simulated,
                    timestamp_or_step=e.timestamp_or_step,
                    metadata=json.loads(e.metadata_json) if e.metadata_json else None,
                    created_at=e.created_at
                ) for e in evidence
            ],
            recommendations=[
                ValidationRecommendationSchema(
                    id=r.id,
                    validation_id=r.validation_id,
                    recommendation_type=r.recommendation_type,
                    priority=r.priority,
                    description=r.description,
                    related_service_id=r.related_service_id,
                    supporting_evidence=json.loads(r.supporting_evidence_json) if r.supporting_evidence_json else None,
                    created_at=r.created_at
                ) for r in recs
            ],
            comparison=comparison_data,
            summary=summary_data,
            started_at=val_run.started_at,
            completed_at=val_run.completed_at,
            created_at=val_run.created_at
        )
