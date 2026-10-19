from datetime import datetime, timezone
import json
from typing import List, Optional, Tuple, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import desc

from app.models.agent_model import (
    AgentSessionModel,
    AgentActionHistoryModel,
    AgentSessionResultModel
)

class AgentRepository:
    @staticmethod
    def create_session(db: Session, session_data: Dict[str, Any]) -> AgentSessionModel:
        config_json = json.dumps(session_data.get("configuration", {}))
        session = AgentSessionModel(
            incident_id=session_data.get("incident_id"),
            scenario_id=session_data.get("scenario_id"),
            target_service_id=session_data.get("target_service_id"),
            status=session_data.get("status", "IDLE"),
            policy_version=session_data.get("policy_version", "1.0.0"),
            configuration_json=config_json,
            stopping_reason=None,
            total_steps=0,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc)
        )
        db.add(session)
        db.commit()
        db.refresh(session)
        return session

    @staticmethod
    def get_session(db: Session, session_id: str) -> Optional[AgentSessionModel]:
        return db.query(AgentSessionModel).filter(AgentSessionModel.id == session_id).first()

    @staticmethod
    def list_sessions(
        db: Session, 
        skip: int = 0, 
        limit: int = 50, 
        incident_id: Optional[str] = None
    ) -> Tuple[List[AgentSessionModel], int]:
        query = db.query(AgentSessionModel)
        if incident_id:
            query = query.filter(AgentSessionModel.incident_id == incident_id)
        total = query.count()
        sessions = query.order_by(desc(AgentSessionModel.created_at)).offset(skip).limit(limit).all()
        return sessions, total

    @staticmethod
    def update_session(
        db: Session, 
        session_id: str, 
        status: Optional[str] = None, 
        stopping_reason: Optional[str] = None,
        total_steps: Optional[int] = None
    ) -> Optional[AgentSessionModel]:
        session = db.query(AgentSessionModel).filter(AgentSessionModel.id == session_id).first()
        if not session:
            return None
        if status:
            session.status = status
            if status in ["COMPLETED", "STOPPED", "FAILED"]:
                session.completed_at = datetime.now(timezone.utc)
        if stopping_reason is not None:
            session.stopping_reason = stopping_reason
        if total_steps is not None:
            session.total_steps = total_steps
        session.updated_at = datetime.now(timezone.utc)
        db.commit()
        db.refresh(session)
        return session

    @staticmethod
    def record_action_step(db: Session, step_data: Dict[str, Any]) -> AgentActionHistoryModel:
        record = AgentActionHistoryModel(
            session_id=step_data["session_id"],
            step_number=step_data["step_number"],
            action_id=step_data["action_id"],
            parameters_json=json.dumps(step_data.get("parameters", {})),
            selection_score=step_data.get("selection_score", 0.0),
            selection_reason=step_data.get("selection_reason", ""),
            execution_status=step_data.get("execution_status", "SUCCESS"),
            result_summary=step_data.get("result_summary", ""),
            raw_result_json=json.dumps(step_data.get("raw_result", {})),
            evidence_ids_json=json.dumps(step_data.get("evidence_ids", [])),
            started_at=step_data.get("started_at", datetime.now(timezone.utc)),
            completed_at=step_data.get("completed_at", datetime.now(timezone.utc)),
            duration_ms=step_data.get("duration_ms", 0.0)
        )
        db.add(record)
        db.commit()
        db.refresh(record)
        return record

    @staticmethod
    def get_action_history(db: Session, session_id: str) -> List[AgentActionHistoryModel]:
        return db.query(AgentActionHistoryModel).filter(
            AgentActionHistoryModel.session_id == session_id
        ).order_by(AgentActionHistoryModel.step_number).all()

    @staticmethod
    def save_session_result(
        db: Session, 
        session_id: str, 
        result_json: str, 
        final_ranking_json: str, 
        unresolved_questions_json: str, 
        evidence_completeness: float = 0.0,
        completeness: Optional[float] = None
    ) -> AgentSessionResultModel:
        comp_val = completeness if completeness is not None else evidence_completeness
        existing = db.query(AgentSessionResultModel).filter(AgentSessionResultModel.session_id == session_id).first()
        if existing:
            existing.result_json = result_json
            existing.final_ranking_json = final_ranking_json
            existing.unresolved_questions_json = unresolved_questions_json
            existing.evidence_completeness = comp_val
            db.commit()
            db.refresh(existing)
            return existing

        res = AgentSessionResultModel(
            session_id=session_id,
            result_json=result_json,
            final_ranking_json=final_ranking_json,
            unresolved_questions_json=unresolved_questions_json,
            evidence_completeness=comp_val,
            created_at=datetime.now(timezone.utc)
        )
        db.add(res)
        db.commit()
        db.refresh(res)
        return res

    @staticmethod
    def get_session_result(db: Session, session_id: str) -> Optional[AgentSessionResultModel]:
        return db.query(AgentSessionResultModel).filter(AgentSessionResultModel.session_id == session_id).first()

    @staticmethod
    def delete_session(db: Session, session_id: str) -> bool:
        session = db.query(AgentSessionModel).filter(AgentSessionModel.id == session_id).first()
        if not session:
            return False
        db.delete(session)
        db.commit()
        return True
