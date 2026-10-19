from typing import Dict, Any, List
from sqlalchemy.orm import Session
from app.database.validation_repository import ValidationRepository
from app.models.validation_models import ValidationRecommendationModel

class ValidationRecommendationEngine:
    """
    Generates actionable, non-destructive diagnostic and remediation recommendations
    when recovery validation indicates partial success, failure, instability, or inconclusive evidence.
    """

    @classmethod
    def generate_recommendations(
        cls,
        db: Session,
        validation_id: str,
        overall_outcome: str,
        unhealthy_services: List[str],
        newly_affected_services: List[str],
        metric_failures: List[Dict[str, Any]],
        is_stable: bool,
        evidence_gap_count: int,
        failed_preconditions: List[str]
    ) -> List[ValidationRecommendationModel]:
        recs_data: List[Dict[str, Any]] = []

        if overall_outcome == "FAILED":
            if failed_preconditions:
                recs_data.append({
                    "recommendation_type": "review_preconditions",
                    "priority": "CRITICAL",
                    "description": f"Precondition violations detected ({', '.join(failed_preconditions)}). Re-verify system assumptions before simulating recovery actions.",
                    "related_service_id": None,
                    "supporting_evidence": {"failed_preconditions": failed_preconditions}
                })

            if unhealthy_services:
                for sid in unhealthy_services:
                    recs_data.append({
                        "recommendation_type": "investigate_service",
                        "priority": "CRITICAL",
                        "description": f"Service '{sid}' remained UNHEALTHY despite simulated plan execution. Investigate internal error logs and resource constraints.",
                        "related_service_id": sid,
                        "supporting_evidence": {"unhealthy_services": unhealthy_services}
                    })

            recs_data.append({
                "recommendation_type": "test_alternative_plan",
                "priority": "HIGH",
                "description": "The current recovery strategy failed in simulation. Test an alternative candidate strategy (e.g. Risk-Aware Balanced or Fastest-Recovery) in an isolated sandbox.",
                "related_service_id": None,
                "supporting_evidence": {"outcome": overall_outcome}
            })

        elif overall_outcome == "PARTIAL_SUCCESS":
            if unhealthy_services:
                for sid in unhealthy_services:
                    recs_data.append({
                        "recommendation_type": "investigate_service",
                        "priority": "HIGH",
                        "description": f"Target service '{sid}' did not fully recover to HEALTHY. Consider scaling compute capacity or verifying database replica lag.",
                        "related_service_id": sid,
                        "supporting_evidence": {"unhealthy_services": unhealthy_services}
                    })

            if metric_failures:
                for mf in metric_failures:
                    recs_data.append({
                        "recommendation_type": "collect_metrics",
                        "priority": "MEDIUM",
                        "description": f"Metric '{mf.get('metric')}' on '{mf.get('service_id')}' exceeded acceptable threshold ({mf.get('value')} vs max {mf.get('threshold')}). Audit query performance.",
                        "related_service_id": mf.get("service_id"),
                        "supporting_evidence": mf
                    })

        elif overall_outcome == "INCONCLUSIVE":
            recs_data.append({
                "recommendation_type": "collect_metrics",
                "priority": "HIGH",
                "description": "Validation evidence is incomplete or unverified. Ensure all affected services publish telemetry metrics across the entire simulation window.",
                "related_service_id": None,
                "supporting_evidence": {"evidence_gaps": evidence_gap_count}
            })

        if not is_stable:
            recs_data.append({
                "recommendation_type": "extend_verification_window",
                "priority": "HIGH",
                "description": "Service metrics exhibited post-recovery instability or secondary regression. Extend the verification window steps from 3 to 5+ steps.",
                "related_service_id": None,
                "supporting_evidence": {"is_stable": False}
            })

        if newly_affected_services:
            for sid in newly_affected_services:
                recs_data.append({
                    "recommendation_type": "review_downstream",
                    "priority": "HIGH",
                    "description": f"Service '{sid}' degraded unexpectedly following recovery action. Verify traffic routing rules and coupling isolation.",
                    "related_service_id": sid,
                    "supporting_evidence": {"newly_affected": newly_affected_services}
                })

        # If VERIFIED_SUCCESS and no warnings, add a positive maintenance note
        if overall_outcome == "VERIFIED_SUCCESS" and not recs_data:
            recs_data.append({
                "recommendation_type": "extend_verification_window",
                "priority": "LOW",
                "description": "All validation criteria passed with zero residual cascades. Plan is eligible for staging deployment review under SRE supervision.",
                "related_service_id": None,
                "supporting_evidence": {"status": "ALL_CHECKS_PASSED"}
            })

        records = []
        for r in recs_data:
            rec_model = ValidationRepository.record_recommendation(db, {
                "validation_id": validation_id,
                "recommendation_type": r["recommendation_type"],
                "priority": r["priority"],
                "description": r["description"],
                "related_service_id": r.get("related_service_id"),
                "supporting_evidence": r.get("supporting_evidence")
            })
            records.append(rec_model)

        return records
