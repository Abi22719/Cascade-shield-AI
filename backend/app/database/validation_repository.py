import json
from datetime import datetime, timezone
from typing import List, Optional, Dict, Any, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import desc

from app.models.validation_models import (
    ValidationRunModel,
    ValidationCheckModel,
    ValidationEvidenceModel,
    ValidationRecommendationModel,
    ValidationConfigModel
)

class ValidationRepository:
    """
    CRUD repository for validation runs, checks, evidence, recommendations, and config.
    """

    @classmethod
    def create_run(cls, db: Session, data: Dict[str, Any]) -> ValidationRunModel:
        run = ValidationRunModel(
            recovery_plan_id=data["recovery_plan_id"],
            recovery_simulation_run_id=data.get("recovery_simulation_run_id"),
            source_scenario_id=data.get("source_scenario_id"),
            status=data.get("status", "COMPLETED"),
            overall_outcome=data.get("overall_outcome", "NOT_RUN"),
            total_checks=int(data.get("total_checks", 0)),
            passed_checks=int(data.get("passed_checks", 0)),
            failed_checks=int(data.get("failed_checks", 0)),
            warning_checks=int(data.get("warning_checks", 0)),
            unknown_checks=int(data.get("unknown_checks", 0)),
            verification_window_steps=int(data.get("verification_window_steps", 3)),
            summary_json=json.dumps(data.get("summary", {})) if data.get("summary") else None,
            comparison_json=json.dumps(data.get("comparison", {})) if data.get("comparison") else None,
            started_at=data.get("started_at", datetime.now(timezone.utc)),
            completed_at=data.get("completed_at", datetime.now(timezone.utc))
        )
        db.add(run)
        db.flush()
        return run

    @classmethod
    def get_run(cls, db: Session, validation_id: str) -> Optional[ValidationRunModel]:
        return db.query(ValidationRunModel).filter(ValidationRunModel.id == validation_id).first()

    @classmethod
    def find_existing_run(
        cls, 
        db: Session, 
        recovery_plan_id: str, 
        simulation_run_id: Optional[str]
    ) -> Optional[ValidationRunModel]:
        query = db.query(ValidationRunModel).filter(
            ValidationRunModel.recovery_plan_id == recovery_plan_id
        )
        if simulation_run_id:
            query = query.filter(ValidationRunModel.recovery_simulation_run_id == simulation_run_id)
        return query.order_by(desc(ValidationRunModel.created_at)).first()

    @classmethod
    def list_runs(
        cls,
        db: Session,
        skip: int = 0,
        limit: int = 20,
        outcome: Optional[str] = None,
        plan_id: Optional[str] = None
    ) -> Tuple[List[ValidationRunModel], int]:
        query = db.query(ValidationRunModel)
        if outcome:
            query = query.filter(ValidationRunModel.overall_outcome == outcome)
        if plan_id:
            query = query.filter(ValidationRunModel.recovery_plan_id == plan_id)

        total = query.count()
        items = query.order_by(desc(ValidationRunModel.created_at)).offset(skip).limit(limit).all()
        return items, total

    @classmethod
    def record_check(cls, db: Session, data: Dict[str, Any]) -> ValidationCheckModel:
        check = ValidationCheckModel(
            validation_id=data["validation_id"],
            check_type=data["check_type"],
            target_service_id=data.get("target_service_id"),
            check_name=data["check_name"],
            status=data.get("status", "UNKNOWN"),
            expected_value=str(data.get("expected_value")) if data.get("expected_value") is not None else None,
            actual_value=str(data.get("actual_value")) if data.get("actual_value") is not None else None,
            explanation=data["explanation"],
            evidence_reference=data.get("evidence_reference"),
            simulation_step=data.get("simulation_step")
        )
        db.add(check)
        db.flush()
        return check

    @classmethod
    def record_evidence(cls, db: Session, data: Dict[str, Any]) -> ValidationEvidenceModel:
        ev = ValidationEvidenceModel(
            validation_id=data["validation_id"],
            check_id=data.get("check_id"),
            source_module=data["source_module"],
            source_record_id=data.get("source_record_id"),
            evidence_type=data["evidence_type"],
            description=data["description"],
            observed_or_simulated=data.get("observed_or_simulated", "simulated"),
            timestamp_or_step=str(data.get("timestamp_or_step")) if data.get("timestamp_or_step") is not None else None,
            metadata_json=json.dumps(data.get("metadata", {})) if data.get("metadata") else None
        )
        db.add(ev)
        db.flush()
        return ev

    @classmethod
    def record_recommendation(cls, db: Session, data: Dict[str, Any]) -> ValidationRecommendationModel:
        rec = ValidationRecommendationModel(
            validation_id=data["validation_id"],
            recommendation_type=data["recommendation_type"],
            priority=data.get("priority", "MEDIUM"),
            description=data["description"],
            related_service_id=data.get("related_service_id"),
            supporting_evidence_json=json.dumps(data.get("supporting_evidence", {})) if data.get("supporting_evidence") else None
        )
        db.add(rec)
        db.flush()
        return rec

    @classmethod
    def get_checks_for_run(cls, db: Session, validation_id: str) -> List[ValidationCheckModel]:
        return db.query(ValidationCheckModel).filter(
            ValidationCheckModel.validation_id == validation_id
        ).order_by(ValidationCheckModel.created_at).all()

    @classmethod
    def get_evidence_for_run(cls, db: Session, validation_id: str) -> List[ValidationEvidenceModel]:
        return db.query(ValidationEvidenceModel).filter(
            ValidationEvidenceModel.validation_id == validation_id
        ).order_by(ValidationEvidenceModel.created_at).all()

    @classmethod
    def get_recommendations_for_run(cls, db: Session, validation_id: str) -> List[ValidationRecommendationModel]:
        return db.query(ValidationRecommendationModel).filter(
            ValidationRecommendationModel.validation_id == validation_id
        ).order_by(ValidationRecommendationModel.created_at).all()

    @classmethod
    def get_config(cls, db: Session, key: str, default: Optional[str] = None) -> Optional[str]:
        cfg = db.query(ValidationConfigModel).filter(ValidationConfigModel.config_key == key).first()
        return cfg.config_value if cfg else default

    @classmethod
    def set_config(cls, db: Session, key: str, value: str) -> ValidationConfigModel:
        cfg = db.query(ValidationConfigModel).filter(ValidationConfigModel.config_key == key).first()
        if cfg:
            cfg.config_value = value
            cfg.updated_at = datetime.now(timezone.utc)
        else:
            cfg = ValidationConfigModel(config_key=key, config_value=value)
            db.add(cfg)
        db.commit()
        db.refresh(cfg)
        return cfg

    @classmethod
    def get_all_configs(cls, db: Session) -> Dict[str, str]:
        cfgs = db.query(ValidationConfigModel).all()
        return {c.config_key: c.config_value for c in cfgs}
