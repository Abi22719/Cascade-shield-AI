import json
from datetime import datetime, timezone
from typing import List, Optional, Tuple, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import desc

from app.models.simulation_model import (
    SimulationScenarioModel,
    SimulationRunModel,
    SimulationEventModel,
    SimulationServiceStateModel
)

class SimulationRepository:
    @staticmethod
    def create_scenario(db: Session, data: Dict[str, Any]) -> SimulationScenarioModel:
        config_json = json.dumps(data["config"]) if isinstance(data["config"], dict) else data["config"]
        scenario = SimulationScenarioModel(
            name=data["name"],
            description=data.get("description"),
            category=data.get("category", "failure_propagation"),
            scenario_config_json=config_json,
            source_data_type=data.get("source_data_type", "digital_twin"),
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc)
        )
        db.add(scenario)
        db.commit()
        db.refresh(scenario)
        return scenario

    @staticmethod
    def get_scenario(db: Session, scenario_id: str) -> Optional[SimulationScenarioModel]:
        return db.query(SimulationScenarioModel).filter(SimulationScenarioModel.id == scenario_id).first()

    @staticmethod
    def list_scenarios(
        db: Session, 
        skip: int = 0, 
        limit: int = 50, 
        category: Optional[str] = None
    ) -> Tuple[List[SimulationScenarioModel], int]:
        query = db.query(SimulationScenarioModel)
        if category:
            query = query.filter(SimulationScenarioModel.category == category)
        total = query.count()
        items = query.order_by(desc(SimulationScenarioModel.created_at)).offset(skip).limit(limit).all()
        return items, total

    @staticmethod
    def update_scenario(db: Session, scenario_id: str, data: Dict[str, Any]) -> Optional[SimulationScenarioModel]:
        scenario = db.query(SimulationScenarioModel).filter(SimulationScenarioModel.id == scenario_id).first()
        if not scenario:
            return None

        if "name" in data and data["name"] is not None:
            scenario.name = data["name"]
        if "description" in data:
            scenario.description = data["description"]
        if "category" in data and data["category"] is not None:
            scenario.category = data["category"]
        if "config" in data and data["config"] is not None:
            scenario.scenario_config_json = json.dumps(data["config"]) if isinstance(data["config"], dict) else data["config"]

        scenario.updated_at = datetime.now(timezone.utc)
        db.commit()
        db.refresh(scenario)
        return scenario

    @staticmethod
    def delete_scenario(db: Session, scenario_id: str) -> bool:
        scenario = db.query(SimulationScenarioModel).filter(SimulationScenarioModel.id == scenario_id).first()
        if not scenario:
            return False
        db.delete(scenario)
        db.commit()
        return True

    @staticmethod
    def clone_scenario(db: Session, scenario_id: str, new_name: Optional[str] = None) -> Optional[SimulationScenarioModel]:
        original = db.query(SimulationScenarioModel).filter(SimulationScenarioModel.id == scenario_id).first()
        if not original:
            return None

        clone_name = new_name or f"{original.name} (Clone)"
        cloned = SimulationScenarioModel(
            name=clone_name,
            description=original.description,
            category=original.category,
            scenario_config_json=original.scenario_config_json,
            source_data_type=original.source_data_type,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc)
        )
        db.add(cloned)
        db.commit()
        db.refresh(cloned)
        return cloned

    @staticmethod
    def create_run(db: Session, data: Dict[str, Any]) -> SimulationRunModel:
        run = SimulationRunModel(
            scenario_id=data["scenario_id"],
            status=data.get("status", "RUNNING"),
            random_seed=data.get("random_seed"),
            model_version=data.get("model_version", "1.0.0"),
            total_steps=data.get("total_steps", 0),
            summary_json=None,
            error_summary=None,
            started_at=datetime.now(timezone.utc)
        )
        db.add(run)
        db.commit()
        db.refresh(run)
        return run

    @staticmethod
    def get_run(db: Session, run_id: str) -> Optional[SimulationRunModel]:
        return db.query(SimulationRunModel).filter(SimulationRunModel.id == run_id).first()

    @staticmethod
    def list_runs(
        db: Session, 
        scenario_id: Optional[str] = None, 
        skip: int = 0, 
        limit: int = 50
    ) -> Tuple[List[SimulationRunModel], int]:
        query = db.query(SimulationRunModel)
        if scenario_id:
            query = query.filter(SimulationRunModel.scenario_id == scenario_id)
        total = query.count()
        items = query.order_by(desc(SimulationRunModel.started_at)).offset(skip).limit(limit).all()
        return items, total

    @staticmethod
    def update_run(
        db: Session,
        run_id: str,
        status: Optional[str] = None,
        total_steps: Optional[int] = None,
        summary_json: Optional[str] = None,
        error_summary: Optional[str] = None
    ) -> Optional[SimulationRunModel]:
        run = db.query(SimulationRunModel).filter(SimulationRunModel.id == run_id).first()
        if not run:
            return None

        if status:
            run.status = status
            if status in ["COMPLETED", "FAILED", "CANCELLED"]:
                run.completed_at = datetime.now(timezone.utc)
        if total_steps is not None:
            run.total_steps = total_steps
        if summary_json is not None:
            run.summary_json = summary_json
        if error_summary is not None:
            run.error_summary = error_summary

        db.commit()
        db.refresh(run)
        return run

    @staticmethod
    def record_event(
        db: Session,
        run_id: str,
        step_number: int,
        event_type: str,
        service_id: str,
        event_data: Dict[str, Any]
    ) -> SimulationEventModel:
        ev = SimulationEventModel(
            run_id=run_id,
            step_number=step_number,
            event_type=event_type,
            service_id=service_id,
            event_data_json=json.dumps(event_data),
            created_at=datetime.now(timezone.utc)
        )
        db.add(ev)
        db.commit()
        db.refresh(ev)
        return ev

    @staticmethod
    def record_service_state(
        db: Session,
        run_id: str,
        step_number: int,
        service_id: str,
        health_status: str,
        state_dict: Dict[str, Any]
    ) -> SimulationServiceStateModel:
        st = SimulationServiceStateModel(
            run_id=run_id,
            step_number=step_number,
            service_id=service_id,
            health_status=health_status,
            state_json=json.dumps(state_dict),
            created_at=datetime.now(timezone.utc)
        )
        db.add(st)
        db.commit()
        db.refresh(st)
        return st

    @staticmethod
    def get_run_events(db: Session, run_id: str) -> List[SimulationEventModel]:
        return db.query(SimulationEventModel).filter(
            SimulationEventModel.run_id == run_id
        ).order_by(SimulationEventModel.step_number).all()

    @staticmethod
    def get_run_service_states(
        db: Session, 
        run_id: str, 
        step_number: Optional[int] = None
    ) -> List[SimulationServiceStateModel]:
        query = db.query(SimulationServiceStateModel).filter(SimulationServiceStateModel.run_id == run_id)
        if step_number is not None:
            query = query.filter(SimulationServiceStateModel.step_number == step_number)
        return query.order_by(SimulationServiceStateModel.step_number).all()
