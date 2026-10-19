from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from app.database.validation_repository import ValidationRepository
from app.models.validation_models import ValidationEvidenceModel

class ValidationEvidenceEngine:
    """
    Evidence grounding service. Links validation findings to explicit simulation logs,
    telemetry snapshots, and multi-module records. Explicitly labels data lineage.
    """

    @classmethod
    def collect_and_link_evidence(
        cls,
        db: Session,
        validation_id: str,
        evidence_items: List[Dict[str, Any]]
    ) -> List[ValidationEvidenceModel]:
        records: List[ValidationEvidenceModel] = []

        for item in evidence_items:
            # Ensure observed_or_simulated is explicitly categorized
            data_type = item.get("observed_or_simulated", "simulated")
            if data_type not in ["observed", "simulated", "synthetic", "inferred"]:
                data_type = "simulated"

            ev = ValidationRepository.record_evidence(db, {
                "validation_id": validation_id,
                "check_id": item.get("check_id"),
                "source_module": item.get("source_module", "module_7"),
                "source_record_id": item.get("source_record_id"),
                "evidence_type": item.get("evidence_type", "metric_observation"),
                "description": item["description"],
                "observed_or_simulated": data_type,
                "timestamp_or_step": item.get("timestamp_or_step"),
                "metadata": item.get("metadata", {})
            })
            records.append(ev)

        return records
