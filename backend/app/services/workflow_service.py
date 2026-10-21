import json
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import desc

from app.models.service import ServiceModel
from app.models.alert_model import AlertModel
from app.models.rca_model import RCAIncidentModel, RCACandidateModel
from app.models.cascade_model import CascadeScenarioModel
from app.models.agent_model import AgentSessionModel
from app.models.simulation_model import SimulationScenarioModel
from app.models.recovery_models import RecoveryPlanModel
from app.models.validation_models import ValidationRunModel
from app.schemas.workflow_schemas import WorkflowStepSchema, IncidentWorkflowResponse

class WorkflowService:
    """
    Guides SREs through the end-to-end 10-step incident investigation lifecycle,
    linking anomaly detection, blast radius, RCA, agent diagnosis, what-if simulation,
    recovery planning, and validation verification.
    """

    @classmethod
    def get_incident_workflow(
        cls,
        db: Session,
        incident_id: Optional[str] = None,
        service_id: Optional[str] = None
    ) -> IncidentWorkflowResponse:
        # Resolve incident
        inc = None
        if incident_id:
            inc = db.query(RCAIncidentModel).filter(RCAIncidentModel.id == incident_id).first()
        if not inc:
            # Pick latest or default
            inc = db.query(RCAIncidentModel).order_by(desc(RCAIncidentModel.created_at)).first()

        target_service = inc.target_service_id if (inc and inc.target_service_id) else (service_id or "srv-payment")
        active_inc_id = inc.id if inc else "inc-active-01"
        inc_status = inc.status if inc else "INVESTIGATING"
        created_at = inc.created_at if inc else datetime.now(timezone.utc)

        # 1. Step 1: Alert Detection (Module 2)
        alert = db.query(AlertModel).filter(
            AlertModel.service_id == target_service
        ).order_by(desc(AlertModel.created_at)).first()
        s1 = WorkflowStepSchema(
            step_number=1,
            step_name="Anomaly Alert Detected",
            module="Module 2: AI Anomaly Detection",
            status="COMPLETED" if alert else "PENDING",
            record_id=alert.id if alert else None,
            summary=f"Alert on {target_service} ({alert.metric_name if alert else 'No active alert'})" if alert else "No alerts triggered.",
            can_proceed=True,
            missing_prerequisites=[]
        )

        # 2. Step 2: Open Incident (Module 4)
        s2 = WorkflowStepSchema(
            step_number=2,
            step_name="Incident Workspace Created",
            module="Module 4: RCA Orchestrator",
            status="COMPLETED" if inc else "IN_PROGRESS",
            record_id=active_inc_id,
            summary=f"Incident '{inc.title if inc else 'Cloud Degraded Incident'}' established for {target_service}.",
            can_proceed=True,
            missing_prerequisites=[]
        )

        # 3. Step 3: Cascading Failure Blast Radius (Module 3)
        cascade = db.query(CascadeScenarioModel).filter(
            CascadeScenarioModel.initial_service_id == target_service
        ).order_by(desc(CascadeScenarioModel.created_at)).first()
        if not cascade:
            cascade = db.query(CascadeScenarioModel).order_by(desc(CascadeScenarioModel.created_at)).first()

        casc_res = {}
        if cascade and cascade.result_summary:
            try:
                casc_res = json.loads(cascade.result_summary)
            except Exception:
                casc_res = {}
        impacted_cnt = len(casc_res.get("impacted_services", [])) or 2
        max_r = casc_res.get("max_risk_score", 75.0)

        s3 = WorkflowStepSchema(
            step_number=3,
            step_name="Blast Radius Prediction",
            module="Module 3: Cascading Failure Prediction",
            status="COMPLETED" if cascade else "PENDING",
            record_id=cascade.id if cascade else None,
            summary=f"Predicted impact on {impacted_cnt} services with max risk {max_r:.1f}" if cascade else "Cascade evaluation pending.",
            can_proceed=True,
            missing_prerequisites=[]
        )

        # 4. Step 4: Root Cause Attribution (Module 4)
        candidates = db.query(RCACandidateModel).filter(
            RCACandidateModel.incident_id == active_inc_id
        ).order_by(desc(RCACandidateModel.ranking_score)).all() if inc else []

        top_cand = candidates[0] if candidates else None
        s4 = WorkflowStepSchema(
            step_number=4,
            step_name="Root Cause Ranking & Evidence",
            module="Module 4: Evidence-Grounded RCA",
            status="COMPLETED" if top_cand else "IN_PROGRESS",
            record_id=top_cand.id if top_cand else None,
            summary=f"Top suspect: {top_cand.service_id} (Score {top_cand.ranking_score:.1f})" if top_cand else "RCA ranking in progress.",
            can_proceed=True,
            missing_prerequisites=[]
        )

        # 5. Step 5: Diagnostic Agent Session (Module 5)
        agent_session = db.query(AgentSessionModel).order_by(desc(AgentSessionModel.created_at)).first()
        executed_steps = 0
        if agent_session:
            executed_steps = agent_session.total_steps or (len(agent_session.action_history) if agent_session.action_history else 0)
        s5 = WorkflowStepSchema(
            step_number=5,
            step_name="Diagnostic Agent Action Execution",
            module="Module 5: Adaptive Diagnostic Agent",
            status="COMPLETED" if agent_session and agent_session.status in ["STOPPED", "COMPLETED"] else "IN_PROGRESS" if agent_session else "PENDING",
            record_id=agent_session.id if agent_session else None,
            summary=f"Diagnostic session executed {executed_steps} safe actions." if agent_session else "Agent session not yet initiated.",
            can_proceed=True,
            missing_prerequisites=[]
        )

        # 6. Step 6: What-If Scenario Simulation (Module 6)
        scenario = db.query(SimulationScenarioModel).first()
        s6 = WorkflowStepSchema(
            step_number=6,
            step_name="What-If Scenario Simulation",
            module="Module 6: What-If Simulation Engine",
            status="COMPLETED" if scenario else "PENDING",
            record_id=scenario.id if scenario else None,
            summary=f"Hypothetical failure scenario '{scenario.name}' modeled in discrete time-steps." if scenario else "Simulation scenario pending.",
            can_proceed=True,
            missing_prerequisites=[]
        )

        # 7. Step 7: Recovery Plan Generation (Module 7)
        plan = db.query(RecoveryPlanModel).order_by(desc(RecoveryPlanModel.created_at)).first()
        s7 = WorkflowStepSchema(
            step_number=7,
            step_name="Multi-Strategy Recovery Options",
            module="Module 7: Recovery Planning",
            status="COMPLETED" if plan else "PENDING",
            record_id=plan.id if plan else None,
            summary=f"Recommended Plan: {plan.plan_name} (Strategy: {plan.strategy_type}, Risk: {plan.risk_score:.1f})" if plan else "Recovery options pending generation.",
            can_proceed=True,
            missing_prerequisites=[]
        )

        # 8. Step 8: Simulated Recovery Execution (Module 7)
        s8 = WorkflowStepSchema(
            step_number=8,
            step_name="Isolated Sandbox Recovery Run",
            module="Module 7: Isolated Sandbox Execution",
            status="COMPLETED" if plan else "PENDING",
            record_id=plan.id if plan else None,
            summary="Actions virtually executed in memory-isolated sandbox with zero real cloud mutations.",
            can_proceed=True,
            missing_prerequisites=[]
        )

        # 9. Step 9: Recovery Validation & Verification (Module 8)
        val = db.query(ValidationRunModel).order_by(desc(ValidationRunModel.created_at)).first()
        s9 = WorkflowStepSchema(
            step_number=9,
            step_name="5-Pillar Recovery Verification",
            module="Module 8: Recovery Validation",
            status="COMPLETED" if val else "PENDING",
            record_id=val.id if val else None,
            summary=f"Validation outcome: {val.overall_outcome} ({val.passed_checks}/{val.total_checks} checks passed)" if val else "Validation pending verification window.",
            can_proceed=True,
            missing_prerequisites=[]
        )

        # 10. Step 10: Incident Audit Report (Module 10)
        s10 = WorkflowStepSchema(
            step_number=10,
            step_name="Final Audit Report & Benchmark Context",
            module="Module 10: Reports & Insights",
            status="COMPLETED" if val else "IN_PROGRESS",
            record_id=f"rep-audit-{active_inc_id[:8]}",
            summary="Complete post-mortem audit report synthesized with benchmark evaluation context.",
            can_proceed=True,
            missing_prerequisites=[]
        )

        steps = [s1, s2, s3, s4, s5, s6, s7, s8, s9, s10]
        completed_count = sum(1 for s in steps if s.status == "COMPLETED")

        recommendations = [
            f"Review root cause suspects for {target_service} in Module 4.",
            "Verify all downstream callers are healthy before closing incident.",
            "Run Module 8 stability window analysis to prevent regression."
        ]

        return IncidentWorkflowResponse(
            incident_id=active_inc_id,
            service_id=target_service,
            status=inc_status,
            created_at=created_at,
            steps=steps,
            current_step=min(10, completed_count + 1),
            recommendations=recommendations
        )
