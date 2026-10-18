import json
import uuid
from datetime import datetime, timezone
from typing import List, Optional, Tuple, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import desc
from app.models.cascade_model import CascadeScenarioModel

class CascadeRepository:
    @staticmethod
    def create_scenario(
        db: Session,
        scenario_name: str,
        initial_service_id: str,
        failure_type: str,
        failure_severity: str,
        input_parameters: Dict[str, Any],
        result_summary: Dict[str, Any],
        data_source: str = "simulated"
    ) -> CascadeScenarioModel:
        """
        Saves a simulation scenario and its prediction results into SQLite.
        """
        scenario_id = f"scen-{uuid.uuid4().hex[:10]}"
        scenario = CascadeScenarioModel(
            id=scenario_id,
            scenario_name=scenario_name.strip(),
            initial_service_id=initial_service_id,
            failure_type=failure_type,
            failure_severity=failure_severity,
            input_parameters=json.dumps(input_parameters),
            result_summary=json.dumps(result_summary),
            data_source=data_source,
            created_at=datetime.now(timezone.utc)
        )
        db.add(scenario)
        db.commit()
        db.refresh(scenario)
        return scenario

    @staticmethod
    def get_scenario_by_id(db: Session, scenario_id: str) -> Optional[CascadeScenarioModel]:
        return db.query(CascadeScenarioModel).filter(CascadeScenarioModel.id == scenario_id).first()

    @staticmethod
    def list_scenarios(
        db: Session,
        page: int = 1,
        limit: int = 20
    ) -> Tuple[List[CascadeScenarioModel], int]:
        query = db.query(CascadeScenarioModel)
        total = query.count()
        offset = (page - 1) * limit
        scenarios = query.order_by(desc(CascadeScenarioModel.created_at)).offset(offset).limit(limit).all()
        return scenarios, total

    @staticmethod
    def delete_scenario(db: Session, scenario_id: str) -> bool:
        scenario = db.query(CascadeScenarioModel).filter(CascadeScenarioModel.id == scenario_id).first()
        if not scenario:
            return False
        db.delete(scenario)
        db.commit()
        return True

    @staticmethod
    def get_latest_scenario(db: Session) -> Optional[CascadeScenarioModel]:
        return db.query(CascadeScenarioModel).order_by(desc(CascadeScenarioModel.created_at)).first()
