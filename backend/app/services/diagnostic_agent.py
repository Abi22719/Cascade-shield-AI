import json
import time
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session

from app.schemas.agent_schema import (
    CreateSessionRequest,
    AgentConfigSchema,
    AgentSessionResponse,
    AgentStepResponse,
    ActionExecutionResult,
    ActionRecommendation
)
from app.database.agent_repository import AgentRepository
from app.models.agent_model import AgentSessionModel
from app.models.service import ServiceModel
from app.models.alert_model import AlertModel
from app.models.rca_model import RCAIncidentModel
from app.services.action_selector import ActionSelector
from app.services.diagnostic_executor import DiagnosticExecutor
from app.services.observation_analyzer import ObservationAnalyzer
from app.services.stopping_policy import StoppingPolicy
from app.services.agent_explanation import AgentExplanationService

class DiagnosticAgent:
    """
    Master orchestrator for the Adaptive AI Diagnostic Agent.
    Manages session lifecycle, iterative hypothesis refinement,
    safe read-only step execution, and auditable persistence.
    """

    @classmethod
    def create_session(cls, db: Session, req: CreateSessionRequest) -> AgentSessionModel:
        config = req.custom_config or AgentConfigSchema()
        
        # Determine target service if not explicitly passed
        target_service = req.target_service_id
        if not target_service and req.incident_id:
            inc = db.query(RCAIncidentModel).filter(RCAIncidentModel.id == req.incident_id).first()
            if inc and inc.target_service_id:
                target_service = inc.target_service_id

        # If still none, pick service with highest active alert count
        if not target_service:
            top_alert = db.query(AlertModel).filter(AlertModel.acknowledged == False).first()
            target_service = top_alert.service_id if top_alert else "srv-payment"

        session_data = {
            "incident_id": req.incident_id,
            "scenario_id": req.scenario_id,
            "target_service_id": target_service,
            "status": "IDLE",
            "policy_version": config.policy_version,
            "configuration": config.model_dump()
        }
        session = AgentRepository.create_session(db, session_data)

        # Initialize initial candidates & unresolved questions
        initial_candidates = cls._build_initial_candidates(db, session.incident_id, session.target_service_id)
        initial_questions = cls._build_initial_questions(session.target_service_id)

        AgentRepository.save_session_result(
            db=db,
            session_id=session.id,
            result_json=json.dumps({"summary": "Session initialized. Awaiting diagnostic steps."}),
            final_ranking_json=json.dumps(initial_candidates),
            unresolved_questions_json=json.dumps(initial_questions),
            completeness=0.0
        )
        return session

    @classmethod
    def step(cls, db: Session, session_id: str) -> AgentStepResponse:
        session = AgentRepository.get_session(db, session_id)
        if not session:
            raise ValueError(f"Agent session '{session_id}' not found.")

        if session.status in ["COMPLETED", "STOPPED", "FAILED"]:
            res_record = AgentRepository.get_session_result(db, session_id)
            candidates = json.loads(res_record.final_ranking_json) if res_record and res_record.final_ranking_json else []
            questions = json.loads(res_record.unresolved_questions_json) if res_record and res_record.unresolved_questions_json else []
            return AgentStepResponse(
                session_id=session.id,
                step_number=session.total_steps,
                session_status=session.status,
                stopping_reason=session.stopping_reason,
                executed_action=None,
                next_recommendations=[],
                latest_ranking=candidates,
                unresolved_questions=questions,
                evidence_completeness=res_record.evidence_completeness if res_record else 1.0
            )

        # Transition to RUNNING
        if session.status == "IDLE":
            AgentRepository.update_session(db, session.id, status="RUNNING")

        config_dict = json.loads(session.configuration_json or "{}")
        config = AgentConfigSchema(**config_dict)

        # Load session history & result
        history = AgentRepository.get_action_history(db, session.id)
        res_record = AgentRepository.get_session_result(db, session.id)
        candidates = json.loads(res_record.final_ranking_json) if res_record and res_record.final_ranking_json else []
        questions = json.loads(res_record.unresolved_questions_json) if res_record and res_record.unresolved_questions_json else []
        executed_ids = [h.action_id for h in history]

        # Build context
        context = {
            "session_id": session.id,
            "incident_id": session.incident_id,
            "scenario_id": session.scenario_id,
            "target_service_id": session.target_service_id,
            "affected_service_ids": cls._get_affected_services(db, session.target_service_id),
            "candidates": candidates,
            "unresolved_questions": questions,
            "executed_action_ids": executed_ids,
            "alerts_count": db.query(AlertModel).filter(AlertModel.service_id == session.target_service_id).count(),
            "has_missing_evidence": len(questions) > 0,
            "new_evidence_since_reeval": True
        }

        # Rank actions and select next best
        recommendations = ActionSelector.rank_actions(context, config)
        best_rec = ActionSelector.select_best_action(context, config)

        # Compute elapsed time
        elapsed_seconds = (datetime.now(timezone.utc) - session.created_at.replace(tzinfo=timezone.utc)).total_seconds()

        # Check stopping condition before execution
        should_stop, stop_reason, manual_needed = StoppingPolicy.evaluate(
            step_number=session.total_steps,
            elapsed_seconds=elapsed_seconds,
            current_candidates=candidates,
            next_best_action=best_rec,
            config=config,
            unresolved_questions=questions
        )

        if should_stop:
            AgentRepository.update_session(db, session.id, status="COMPLETED", stopping_reason=stop_reason)
            return AgentStepResponse(
                session_id=session.id,
                step_number=session.total_steps,
                session_status="COMPLETED",
                stopping_reason=stop_reason,
                executed_action=None,
                next_recommendations=recommendations,
                latest_ranking=candidates,
                unresolved_questions=questions,
                evidence_completeness=res_record.evidence_completeness if res_record else 1.0
            )

        # Prepare parameters for selected action
        params = cls._build_action_parameters(best_rec.action_id, context)

        # Execute safe read-only action
        exec_result = DiagnosticExecutor.execute_action(best_rec.action_id, params, db)

        # Analyze observation and update candidates & questions
        analysis = ObservationAnalyzer.analyze_observation(best_rec.action_id, exec_result, context)
        updated_candidates = analysis["updated_candidates"]
        updated_questions = analysis["unresolved_questions"]
        completeness = analysis["evidence_completeness"]

        # Explain ranking shift
        explanation = AgentExplanationService.explain_ranking_shift(candidates, updated_candidates, best_rec.action_name)

        # Record step in database
        step_number = session.total_steps + 1
        history_record = AgentRepository.record_action_step(db, {
            "session_id": session.id,
            "step_number": step_number,
            "action_id": best_rec.action_id,
            "parameters": params,
            "selection_score": best_rec.utility_score,
            "selection_reason": best_rec.selection_reason,
            "execution_status": exec_result["execution_status"],
            "result_summary": exec_result["result_summary"],
            "raw_result": exec_result["raw_result"],
            "evidence_ids": [e.get("service_id", "") for e in exec_result.get("evidence_created", [])],
            "started_at": exec_result["started_at"],
            "completed_at": exec_result["completed_at"],
            "duration_ms": exec_result["duration_ms"]
        })

        # Check stopping condition again post-execution
        post_stop, post_reason, post_manual = StoppingPolicy.evaluate(
            step_number=step_number,
            elapsed_seconds=elapsed_seconds,
            current_candidates=updated_candidates,
            next_best_action=None if completeness >= 1.0 else best_rec,
            config=config,
            unresolved_questions=updated_questions
        )

        new_status = "COMPLETED" if post_stop else "RUNNING"
        AgentRepository.update_session(
            db, 
            session.id, 
            status=new_status, 
            stopping_reason=post_reason if post_stop else None,
            total_steps=step_number
        )

        # Update session result record
        AgentRepository.save_session_result(
            db=db,
            session_id=session.id,
            result_json=json.dumps({"latest_explanation": explanation, "analysis": analysis}),
            final_ranking_json=json.dumps(updated_candidates),
            unresolved_questions_json=json.dumps(updated_questions),
            completeness=completeness
        )

        executed_action_dto = ActionExecutionResult(
            step_number=step_number,
            action_id=best_rec.action_id,
            action_name=best_rec.action_name,
            parameters=params,
            selection_score=best_rec.utility_score,
            selection_reason=best_rec.selection_reason,
            execution_status=exec_result["execution_status"],
            duration_ms=exec_result["duration_ms"],
            result_summary=exec_result["result_summary"],
            raw_result=exec_result["raw_result"],
            evidence_created=exec_result.get("evidence_created", []),
            started_at=exec_result["started_at"],
            completed_at=exec_result["completed_at"]
        )

        # Re-compute recommendations for next step
        context["candidates"] = updated_candidates
        context["unresolved_questions"] = updated_questions
        context["executed_action_ids"].append(best_rec.action_id)
        next_recs = ActionSelector.rank_actions(context, config)

        return AgentStepResponse(
            session_id=session.id,
            step_number=step_number,
            session_status=new_status,
            stopping_reason=post_reason if post_stop else None,
            executed_action=executed_action_dto,
            next_recommendations=next_recs,
            latest_ranking=updated_candidates,
            unresolved_questions=updated_questions,
            evidence_completeness=completeness
        )

    @classmethod
    def run(cls, db: Session, session_id: str, max_steps: Optional[int] = None) -> AgentSessionResponse:
        session = AgentRepository.get_session(db, session_id)
        if not session:
            raise ValueError(f"Agent session '{session_id}' not found.")

        config_dict = json.loads(session.configuration_json or "{}")
        config = AgentConfigSchema(**config_dict)
        steps_limit = max_steps or config.max_actions

        current_step = session.total_steps
        while current_step < steps_limit and session.status in ["IDLE", "RUNNING"]:
            step_res = cls.step(db, session_id)
            current_step = step_res.step_number
            session = AgentRepository.get_session(db, session_id)
            if step_res.session_status in ["COMPLETED", "STOPPED", "FAILED"]:
                break

        return cls.get_session_details(db, session_id)

    @classmethod
    def stop(cls, db: Session, session_id: str) -> AgentSessionResponse:
        session = AgentRepository.get_session(db, session_id)
        if not session:
            raise ValueError(f"Agent session '{session_id}' not found.")

        AgentRepository.update_session(
            db, 
            session.id, 
            status="STOPPED", 
            stopping_reason="USER_STOP_REQUESTED: Operator requested session termination."
        )
        return cls.get_session_details(db, session_id)

    @classmethod
    def get_session_details(cls, db: Session, session_id: str) -> AgentSessionResponse:
        session = AgentRepository.get_session(db, session_id)
        if not session:
            raise ValueError(f"Agent session '{session_id}' not found.")

        history_models = AgentRepository.get_action_history(db, session.id)
        history_dtos = []
        for h in history_models:
            history_dtos.append(
                ActionExecutionResult(
                    step_number=h.step_number,
                    action_id=h.action_id,
                    action_name=h.action_id.replace("_", " ").title(),
                    parameters=json.loads(h.parameters_json or "{}"),
                    selection_score=h.selection_score or 0.0,
                    selection_reason=h.selection_reason or "",
                    execution_status=h.execution_status,
                    duration_ms=h.duration_ms or 0.0,
                    result_summary=h.result_summary or "",
                    raw_result=json.loads(h.raw_result_json or "{}"),
                    evidence_created=[],
                    started_at=h.started_at,
                    completed_at=h.completed_at
                )
            )

        res_record = AgentRepository.get_session_result(db, session.id)
        candidates = json.loads(res_record.final_ranking_json) if res_record and res_record.final_ranking_json else []
        questions = json.loads(res_record.unresolved_questions_json) if res_record and res_record.unresolved_questions_json else []
        completeness = res_record.evidence_completeness if res_record else 0.0
        config_dict = json.loads(session.configuration_json or "{}")

        return AgentSessionResponse(
            id=session.id,
            incident_id=session.incident_id,
            scenario_id=session.scenario_id,
            target_service_id=session.target_service_id,
            status=session.status,
            policy_version=session.policy_version,
            total_steps=session.total_steps,
            stopping_reason=session.stopping_reason,
            configuration=AgentConfigSchema(**config_dict),
            created_at=session.created_at,
            updated_at=session.updated_at,
            completed_at=session.completed_at,
            action_history=history_dtos,
            latest_ranking=candidates,
            unresolved_questions=questions,
            evidence_completeness=completeness
        )

    # ================= HELPER UTILITIES ================= #

    @classmethod
    def _build_initial_candidates(cls, db: Session, incident_id: Optional[str], target_service_id: Optional[str]) -> List[Dict[str, Any]]:
        candidates = []
        if incident_id:
            inc = db.query(RCAIncidentModel).filter(RCAIncidentModel.id == incident_id).first()
            if inc and inc.candidates:
                for c in inc.candidates:
                    candidates.append({
                        "service_id": c.service_id,
                        "service_name": c.service_name,
                        "rank": c.rank,
                        "score": c.ranking_score,
                        "confidence_label": c.confidence_label
                    })
                return candidates

        if target_service_id:
            srv = db.query(ServiceModel).filter(ServiceModel.id == target_service_id).first()
            name = srv.name if srv else target_service_id
            candidates.append({
                "service_id": target_service_id,
                "service_name": name,
                "rank": 1,
                "score": 60.0,
                "confidence_label": "Moderate supporting evidence"
            })

            # Add caller as competitor if exists
            deps = cls._get_affected_services(db, target_service_id)
            if deps:
                caller = deps[0]
                candidates.append({
                    "service_id": caller,
                    "service_name": caller,
                    "rank": 2,
                    "score": 40.0,
                    "confidence_label": "Weak supporting evidence"
                })

        return candidates

    @staticmethod
    def _build_initial_questions(target_service_id: Optional[str]) -> List[str]:
        target = target_service_id or "target service"
        return [
            f"What is the current health status and error rate of {target}?",
            f"Are there active anomaly alerts recorded for {target}?",
            f"Did {target} degrade prior to downstream callers?",
            f"Are there valid dependency call paths from {target} to affected callers?"
        ]

    @staticmethod
    def _get_affected_services(db: Session, service_id: Optional[str]) -> List[str]:
        if not service_id:
            return []
        from app.models.dependency import DependencyModel
        deps = db.query(DependencyModel).filter(DependencyModel.target_service_id == service_id).all()
        return [d.source_service_id for d in deps]

    @staticmethod
    def _build_action_parameters(action_id: str, context: Dict[str, Any]) -> Dict[str, Any]:
        target = context.get("target_service_id", "srv-payment")
        affected = context.get("affected_service_ids", [])
        candidates = context.get("candidates", [])

        if action_id in ["inspect_service_health", "retrieve_service_metrics", "compare_metrics_baseline", "retrieve_anomaly_alerts", "inspect_dependency", "trace_failure_paths", "inspect_cascade_prediction", "identify_missing_evidence"]:
            return {"service_id": target}
        elif action_id == "compare_timestamps":
            comp = affected[0] if affected else (candidates[1]["service_id"] if len(candidates) >= 2 else "srv-order")
            return {"service_id": target, "comparator_service_id": comp}
        elif action_id == "compare_hypotheses":
            c_a = candidates[0]["service_id"] if len(candidates) >= 1 else target
            c_b = candidates[1]["service_id"] if len(candidates) >= 2 else "srv-database"
            return {"candidate_a": c_a, "candidate_b": c_b}
        elif action_id == "reevaluate_root_causes":
            return {"incident_id": context.get("incident_id") or "inc-auto"}
        elif action_id == "inspect_saved_simulation":
            return {"scenario_id": context.get("scenario_id") or "scen-auto"}
        return {"service_id": target}
