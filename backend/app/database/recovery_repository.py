import json
from typing import List, Optional, Dict, Any, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import desc

from app.models.recovery_models import (
    RecoveryPlanModel,
    RecoveryActionModel,
    RecoverySimulationRunModel,
    RecoveryEventModel,
    RecoveryEvaluationModel
)

class RecoveryRepository:
    """
    CRUD repository for recovery plans, actions, simulation runs, and events.
    """

    @classmethod
    def create_plan(cls, db: Session, data: Dict[str, Any]) -> RecoveryPlanModel:
        plan = RecoveryPlanModel(
            incident_id=data.get("incident_id"),
            scenario_id=data.get("scenario_id"),
            plan_name=data["plan_name"],
            description=data.get("description"),
            strategy_type=data.get("strategy_type", "balanced"),
            risk_score=float(data.get("risk_score", 0.0)),
            risk_level=data.get("risk_level", "Low"),
            estimated_recovery_time=int(data.get("estimated_recovery_time", 0)),
            estimated_cost=float(data.get("estimated_cost", 0.0)),
            status=data.get("status", "DRAFT"),
            risk_breakdown_json=json.dumps(data.get("risk_breakdown", []))
        )
        db.add(plan)
        db.flush()

        # Add actions if supplied
        actions_data = data.get("actions", [])
        for act in actions_data:
            action_model = RecoveryActionModel(
                plan_id=plan.id,
                action_type=act["action_type"],
                target_service_id=act.get("target_service_id"),
                action_order=int(act.get("action_order", 1)),
                parameters_json=json.dumps(act.get("parameters", {})),
                preconditions_json=json.dumps(act.get("preconditions", [])),
                estimated_duration=int(act.get("estimated_duration", 1)),
                risk_score=float(act.get("risk_score", 15.0)),
                reversibility=act.get("reversibility", "fully_reversible"),
                status=act.get("status", "PENDING")
            )
            db.add(action_model)

        db.commit()
        db.refresh(plan)
        return plan

    @classmethod
    def get_plan(cls, db: Session, plan_id: str) -> Optional[RecoveryPlanModel]:
        return db.query(RecoveryPlanModel).filter(RecoveryPlanModel.id == plan_id).first()

    @classmethod
    def list_plans(
        cls, 
        db: Session, 
        skip: int = 0, 
        limit: int = 50, 
        incident_id: Optional[str] = None,
        scenario_id: Optional[str] = None
    ) -> Tuple[List[RecoveryPlanModel], int]:
        query = db.query(RecoveryPlanModel)
        if incident_id:
            query = query.filter(RecoveryPlanModel.incident_id == incident_id)
        if scenario_id:
            query = query.filter(RecoveryPlanModel.scenario_id == scenario_id)

        total = query.count()
        plans = query.order_by(desc(RecoveryPlanModel.created_at)).offset(skip).limit(limit).all()
        return plans, total

    @classmethod
    def update_plan(cls, db: Session, plan_id: str, data: Dict[str, Any]) -> Optional[RecoveryPlanModel]:
        plan = cls.get_plan(db, plan_id)
        if not plan:
            return None

        if "plan_name" in data and data["plan_name"]:
            plan.plan_name = data["plan_name"]
        if "description" in data:
            plan.description = data["description"]
        if "strategy_type" in data and data["strategy_type"]:
            plan.strategy_type = data["strategy_type"]
        if "status" in data and data["status"]:
            plan.status = data["status"]
        if "risk_score" in data:
            plan.risk_score = float(data["risk_score"])
        if "risk_level" in data:
            plan.risk_level = data["risk_level"]
        if "estimated_recovery_time" in data:
            plan.estimated_recovery_time = int(data["estimated_recovery_time"])
        if "estimated_cost" in data:
            plan.estimated_cost = float(data["estimated_cost"])
        if "risk_breakdown" in data:
            plan.risk_breakdown_json = json.dumps(data["risk_breakdown"])

        if "actions" in data and data["actions"] is not None:
            # Replace actions
            db.query(RecoveryActionModel).filter(RecoveryActionModel.plan_id == plan_id).delete()
            for act in data["actions"]:
                action_model = RecoveryActionModel(
                    plan_id=plan.id,
                    action_type=act["action_type"],
                    target_service_id=act.get("target_service_id"),
                    action_order=int(act.get("action_order", 1)),
                    parameters_json=json.dumps(act.get("parameters", {})),
                    preconditions_json=json.dumps(act.get("preconditions", [])),
                    estimated_duration=int(act.get("estimated_duration", 1)),
                    risk_score=float(act.get("risk_score", 15.0)),
                    reversibility=act.get("reversibility", "fully_reversible"),
                    status=act.get("status", "PENDING")
                )
                db.add(action_model)

        db.commit()
        db.refresh(plan)
        return plan

    @classmethod
    def delete_plan(cls, db: Session, plan_id: str) -> bool:
        plan = cls.get_plan(db, plan_id)
        if not plan:
            return False
        db.delete(plan)
        db.commit()
        return True

    @classmethod
    def create_run(cls, db: Session, data: Dict[str, Any]) -> RecoverySimulationRunModel:
        run = RecoverySimulationRunModel(
            plan_id=data["plan_id"],
            simulation_run_id=data.get("simulation_run_id"),
            outcome=data.get("outcome", "SUCCESSFUL_RECOVERY"),
            total_recovery_time=int(data.get("total_recovery_time", 0)),
            maximum_risk=float(data.get("maximum_risk", 0.0)),
            final_health_summary=json.dumps(data.get("final_health_summary", {}))
        )
        db.add(run)
        db.commit()
        db.refresh(run)
        return run

    @classmethod
    def get_run(cls, db: Session, run_id: str) -> Optional[RecoverySimulationRunModel]:
        return db.query(RecoverySimulationRunModel).filter(RecoverySimulationRunModel.id == run_id).first()

    @classmethod
    def record_event(
        cls, 
        db: Session, 
        run_id: str, 
        event_type: str, 
        description: str, 
        evidence: Optional[Dict[str, Any]] = None, 
        step: int = 0
    ) -> RecoveryEventModel:
        ev = RecoveryEventModel(
            simulation_run_id=run_id,
            event_type=event_type,
            description=description,
            evidence_json=json.dumps(evidence or {}),
            timestamp_or_step=step
        )
        db.add(ev)
        db.commit()
        db.refresh(ev)
        return ev

    @classmethod
    def get_run_events(cls, db: Session, run_id: str) -> List[RecoveryEventModel]:
        return db.query(RecoveryEventModel).filter(
            RecoveryEventModel.simulation_run_id == run_id
        ).order_by(RecoveryEventModel.timestamp_or_step).all()

    @classmethod
    def create_evaluation(cls, db: Session, data: Dict[str, Any]) -> RecoveryEvaluationModel:
        ev = RecoveryEvaluationModel(
            evaluation_name=data.get("evaluation_name", "Recovery Strategy Benchmark"),
            baseline_name=data.get("baseline_name", "Standard Benchmark Archetypes"),
            metrics_json=json.dumps(data.get("metrics", {}))
        )
        db.add(ev)
        db.commit()
        db.refresh(ev)
        return ev
