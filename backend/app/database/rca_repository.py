import json
import uuid
from datetime import datetime, timezone
from typing import List, Optional, Tuple, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import desc

from app.models.rca_model import (
    RCAIncidentModel,
    RCAEvidenceModel,
    RCACandidateModel,
    RCAReportModel
)

class RCARepository:
    @staticmethod
    def create_incident(
        db: Session,
        title: str,
        affected_service_ids: List[str],
        target_service_id: Optional[str] = None,
        investigation_window_start: Optional[datetime] = None,
        investigation_window_end: Optional[datetime] = None,
        scenario_id: Optional[str] = None,
        data_source: str = "simulated"
    ) -> RCAIncidentModel:
        incident_id = f"inc-{uuid.uuid4().hex[:10]}"
        incident = RCAIncidentModel(
            id=incident_id,
            title=title.strip(),
            status="investigating",
            investigation_window_start=investigation_window_start,
            investigation_window_end=investigation_window_end,
            affected_service_ids=json.dumps(affected_service_ids),
            target_service_id=target_service_id,
            scenario_id=scenario_id,
            data_source=data_source,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc)
        )
        db.add(incident)
        db.commit()
        db.refresh(incident)
        return incident

    @staticmethod
    def get_incident_by_id(db: Session, incident_id: str) -> Optional[RCAIncidentModel]:
        return db.query(RCAIncidentModel).filter(RCAIncidentModel.id == incident_id).first()

    @staticmethod
    def list_incidents(
        db: Session,
        status: Optional[str] = None,
        page: int = 1,
        limit: int = 20
    ) -> Tuple[List[RCAIncidentModel], int]:
        query = db.query(RCAIncidentModel)
        if status and status.lower() != "all":
            query = query.filter(RCAIncidentModel.status == status.lower())
        total = query.count()
        offset = (page - 1) * limit
        items = query.order_by(desc(RCAIncidentModel.created_at)).offset(offset).limit(limit).all()
        return items, total

    @staticmethod
    def delete_incident(db: Session, incident_id: str) -> bool:
        incident = db.query(RCAIncidentModel).filter(RCAIncidentModel.id == incident_id).first()
        if not incident:
            return False
        db.delete(incident)
        db.commit()
        return True

    @staticmethod
    def update_incident_status(db: Session, incident_id: str, status: str) -> Optional[RCAIncidentModel]:
        incident = db.query(RCAIncidentModel).filter(RCAIncidentModel.id == incident_id).first()
        if incident:
            incident.status = status
            incident.updated_at = datetime.now(timezone.utc)
            db.commit()
            db.refresh(incident)
        return incident

    @staticmethod
    def save_evidence_items(
        db: Session,
        incident_id: str,
        evidence_list: List[Dict[str, Any]]
    ) -> List[RCAEvidenceModel]:
        # Clear existing evidence for this incident to avoid duplication on reanalysis
        db.query(RCAEvidenceModel).filter(RCAEvidenceModel.incident_id == incident_id).delete()
        db.commit()

        created = []
        for item in evidence_list:
            ev_id = item.get("id") or f"ev-{uuid.uuid4().hex[:10]}"
            ev = RCAEvidenceModel(
                id=ev_id,
                incident_id=incident_id,
                service_id=item["service_id"],
                service_name=item["service_name"],
                evidence_type=item["evidence_type"],
                metric_name=item.get("metric_name"),
                observed_value=item.get("observed_value"),
                expected_or_threshold_value=item.get("expected_or_threshold_value"),
                timestamp=item.get("timestamp") or datetime.now(timezone.utc),
                source_module=item.get("source_module", "Module 4 RCA Engine"),
                source_record_id=item.get("source_record_id"),
                evidence_summary=item["evidence_summary"],
                data_source=item.get("data_source", "simulated"),
                reliability_score=item.get("reliability_score", 0.9),
                is_contradictory=item.get("is_contradictory", False),
                evidence_json=json.dumps(item.get("extra_metadata", {}))
            )
            db.add(ev)
            created.append(ev)

        db.commit()
        return created

    @staticmethod
    def get_evidence_by_incident(db: Session, incident_id: str) -> List[RCAEvidenceModel]:
        return db.query(RCAEvidenceModel).filter(
            RCAEvidenceModel.incident_id == incident_id
        ).order_by(RCAEvidenceModel.timestamp.asc()).all()

    @staticmethod
    def save_candidates(
        db: Session,
        incident_id: str,
        candidate_list: List[Dict[str, Any]]
    ) -> List[RCACandidateModel]:
        # Clear previous candidates on reanalysis
        db.query(RCACandidateModel).filter(RCACandidateModel.incident_id == incident_id).delete()
        db.commit()

        created = []
        for cand in candidate_list:
            cand_id = f"cand-{uuid.uuid4().hex[:10]}"
            model = RCACandidateModel(
                id=cand_id,
                incident_id=incident_id,
                service_id=cand["service_id"],
                service_name=cand["service_name"],
                rank=cand["rank"],
                ranking_score=cand["ranking_score"],
                confidence_label=cand["confidence_label"],
                confidence_score=cand["confidence_score"],
                result_json=json.dumps({
                    "evidence_for": cand.get("evidence_for", []),
                    "evidence_against": cand.get("evidence_against", []),
                    "affected_services": cand.get("affected_services", []),
                    "supporting_paths": cand.get("supporting_paths", []),
                    "missing_evidence": cand.get("missing_evidence", []),
                    "explanation": cand.get("explanation", "")
                })
            )
            db.add(model)
            created.append(model)

        db.commit()
        return created

    @staticmethod
    def get_candidates_by_incident(db: Session, incident_id: str) -> List[RCACandidateModel]:
        return db.query(RCACandidateModel).filter(
            RCACandidateModel.incident_id == incident_id
        ).order_by(RCACandidateModel.rank.asc()).all()

    @staticmethod
    def save_report(
        db: Session,
        incident_id: str,
        report_data: Dict[str, Any],
        algorithm_version: str = "4.0.0"
    ) -> RCAReportModel:
        # Check if report already exists for incident
        existing = db.query(RCAReportModel).filter(RCAReportModel.incident_id == incident_id).first()
        if existing:
            existing.report_json = json.dumps(report_data)
            existing.algorithm_version = algorithm_version
            existing.created_at = datetime.now(timezone.utc)
            db.commit()
            db.refresh(existing)
            return existing

        rep_id = f"rep-{uuid.uuid4().hex[:10]}"
        report = RCAReportModel(
            id=rep_id,
            incident_id=incident_id,
            report_json=json.dumps(report_data),
            algorithm_version=algorithm_version,
            created_at=datetime.now(timezone.utc)
        )
        db.add(report)
        db.commit()
        db.refresh(report)
        return report

    @staticmethod
    def get_report_by_incident(db: Session, incident_id: str) -> Optional[RCAReportModel]:
        return db.query(RCAReportModel).filter(RCAReportModel.incident_id == incident_id).first()
