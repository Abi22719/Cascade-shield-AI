import json
from typing import Dict, Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.schemas.validation_schemas import (
    ValidationConfigSchema,
    ValidationRunRequest,
    ValidationRunResponse,
    ValidationCheckSchema,
    ValidationEvidenceSchema,
    ValidationRecommendationSchema,
    BeforeAfterComparisonSchema,
    ValidationCompareRequest,
    ValidationCompareResponse,
    ValidationEvaluationResponse
)
from app.database.validation_repository import ValidationRepository
from app.services.validation_rules import ValidationRuleEngine
from app.services.validation_engine import ValidationEngine
from app.services.validation_evaluation_service import ValidationEvaluationService

router = APIRouter(prefix="/validation", tags=["Module 8: Recovery Validation & Verification"])

@router.get("/health")
def validation_health(db: Session = Depends(get_db)):
    """
    Subsystem health and integration status across Modules 1 to 7.
    """
    return {
        "status": "healthy",
        "module": "Module 8: Automated Recovery Validation and Verification",
        "capabilities": [
            "service_health_validation",
            "telemetry_metric_validation",
            "downstream_dependency_cycle_safe_validation",
            "recovery_stability_window_analysis",
            "side_effect_and_rollback_detection",
            "evidence_grounding_and_attribution",
            "multi_run_comparison_matrix",
            "archetype_benchmarking"
        ],
        "safety_mode": "strictly_simulated_isolated_sandbox"
    }

@router.get("/config", response_model=ValidationConfigSchema)
def get_validation_config(db: Session = Depends(get_db)):
    """
    Retrieve current configurable validation rules and operational thresholds.
    """
    return ValidationRuleEngine.get_config(db)

@router.put("/config", response_model=ValidationConfigSchema)
def update_validation_config(updates: Dict[str, Any], db: Session = Depends(get_db)):
    """
    Update validation thresholds (max latency, error rate, stability window, etc.).
    """
    try:
        return ValidationRuleEngine.update_config(db, updates)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.get("/rules")
def get_validation_rules():
    """
    Retrieve itemized documentation of validation rules, categories, and defaults.
    """
    return {
        "rules": ValidationRuleEngine.get_rules_documentation(),
        "disclaimer": "Thresholds are configurable demonstration defaults, not universal production standards."
    }

@router.post("/run", response_model=ValidationRunResponse, status_code=status.HTTP_201_CREATED)
def run_validation(req: ValidationRunRequest, db: Session = Depends(get_db)):
    """
    Executes an automated recovery validation and verification run on a completed simulation.
    """
    try:
        return ValidationEngine.validate_recovery(db, req)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Validation error: {str(e)}")

@router.get("/runs")
def list_validation_runs(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    outcome: Optional[str] = Query(None, description="VERIFIED_SUCCESS, PARTIAL_SUCCESS, FAILED, INCONCLUSIVE, NOT_RUN"),
    plan_id: Optional[str] = Query(None, description="Filter by recovery plan ID"),
    db: Session = Depends(get_db)
):
    """
    List paginated validation runs with optional outcome and recovery plan filters.
    """
    runs, total = ValidationRepository.list_runs(db, skip=skip, limit=limit, outcome=outcome, plan_id=plan_id)
    return {
        "total": total,
        "skip": skip,
        "limit": limit,
        "items": [
            {
                "id": r.id,
                "recovery_plan_id": r.recovery_plan_id,
                "recovery_simulation_run_id": r.recovery_simulation_run_id,
                "source_scenario_id": r.source_scenario_id,
                "status": r.status,
                "overall_outcome": r.overall_outcome,
                "total_checks": r.total_checks,
                "passed_checks": r.passed_checks,
                "failed_checks": r.failed_checks,
                "warning_checks": r.warning_checks,
                "unknown_checks": r.unknown_checks,
                "verification_window_steps": r.verification_window_steps,
                "started_at": r.started_at,
                "completed_at": r.completed_at,
                "created_at": r.created_at
            }
            for r in runs
        ]
    }

@router.get("/runs/{validation_id}", response_model=ValidationRunResponse)
def get_validation_run(validation_id: str, db: Session = Depends(get_db)):
    """
    Retrieve full validation run details, checks, evidence, recommendations, and comparison.
    """
    run = ValidationRepository.get_run(db, validation_id)
    if not run:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Validation run '{validation_id}' not found.")
    return ValidationEngine._format_response(db, run)

@router.get("/runs/{validation_id}/checks", response_model=List[ValidationCheckSchema])
def get_validation_checks(validation_id: str, db: Session = Depends(get_db)):
    """
    Retrieve itemized validation check records for a validation run.
    """
    run = ValidationRepository.get_run(db, validation_id)
    if not run:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Validation run '{validation_id}' not found.")
    checks = ValidationRepository.get_checks_for_run(db, validation_id)
    return [ValidationCheckSchema.model_validate(c) for c in checks]

@router.get("/runs/{validation_id}/evidence", response_model=List[ValidationEvidenceSchema])
def get_validation_evidence(validation_id: str, db: Session = Depends(get_db)):
    """
    Retrieve evidence records supporting a validation run.
    """
    run = ValidationRepository.get_run(db, validation_id)
    if not run:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Validation run '{validation_id}' not found.")
    evidence = ValidationRepository.get_evidence_for_run(db, validation_id)
    return [
        ValidationEvidenceSchema(
            id=e.id,
            validation_id=e.validation_id,
            check_id=e.check_id,
            source_module=e.source_module,
            source_record_id=e.source_record_id,
            evidence_type=e.evidence_type,
            description=e.description,
            observed_or_simulated=e.observed_or_simulated,
            timestamp_or_step=e.timestamp_or_step,
            metadata=json.loads(e.metadata_json) if e.metadata_json else None,
            created_at=e.created_at
        )
        for e in evidence
    ]

@router.get("/runs/{validation_id}/timeline")
def get_validation_timeline(validation_id: str, db: Session = Depends(get_db)):
    """
    Retrieve chronological timeline of validation checks and events.
    """
    run = ValidationRepository.get_run(db, validation_id)
    if not run:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Validation run '{validation_id}' not found.")
    checks = ValidationRepository.get_checks_for_run(db, validation_id)
    evidence = ValidationRepository.get_evidence_for_run(db, validation_id)

    timeline_events = []
    for c in checks:
        timeline_events.append({
            "type": "CHECK",
            "step": c.simulation_step or 0,
            "title": c.check_name,
            "status": c.status,
            "description": c.explanation,
            "created_at": c.created_at
        })

    for e in evidence:
        timeline_events.append({
            "type": "EVIDENCE",
            "step": int(e.timestamp_or_step) if e.timestamp_or_step and e.timestamp_or_step.isdigit() else 0,
            "title": f"Evidence: {e.evidence_type}",
            "status": e.observed_or_simulated,
            "description": e.description,
            "created_at": e.created_at
        })

    timeline_events.sort(key=lambda x: (x["step"], x["created_at"]))
    return {"validation_id": validation_id, "timeline": timeline_events}

@router.get("/runs/{validation_id}/comparison", response_model=Optional[BeforeAfterComparisonSchema])
def get_validation_comparison(validation_id: str, db: Session = Depends(get_db)):
    """
    Retrieve before-and-after recovery comparison for a validation run.
    """
    run = ValidationRepository.get_run(db, validation_id)
    if not run:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Validation run '{validation_id}' not found.")
    if run.comparison_json:
        return BeforeAfterComparisonSchema(**json.loads(run.comparison_json))
    return None

@router.get("/runs/{validation_id}/recommendations", response_model=List[ValidationRecommendationSchema])
def get_validation_recommendations(validation_id: str, db: Session = Depends(get_db)):
    """
    Retrieve actionable recommendations for partial, failed, or inconclusive recoveries.
    """
    run = ValidationRepository.get_run(db, validation_id)
    if not run:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Validation run '{validation_id}' not found.")
    recs = ValidationRepository.get_recommendations_for_run(db, validation_id)
    return [
        ValidationRecommendationSchema(
            id=r.id,
            validation_id=r.validation_id,
            recommendation_type=r.recommendation_type,
            priority=r.priority,
            description=r.description,
            related_service_id=r.related_service_id,
            supporting_evidence=json.loads(r.supporting_evidence_json) if r.supporting_evidence_json else None,
            created_at=r.created_at
        )
        for r in recs
    ]

@router.get("/evaluation", response_model=ValidationEvaluationResponse)
def get_validation_evaluation(db: Session = Depends(get_db)):
    """
    Benchmark comparative accuracy and reliability across 3 validation modes on 10 synthetic archetypes.
    """
    return ValidationEvaluationService.run_benchmark(db)

@router.post("/compare", response_model=ValidationCompareResponse)
def compare_validation_runs(req: ValidationCompareRequest, db: Session = Depends(get_db)):
    """
    Side-by-side comparison matrix across multiple validation runs.
    """
    if len(req.validation_ids) < 2:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="At least 2 validation IDs required for comparison.")

    validations = []
    best_id = None
    best_score = -1.0

    for vid in req.validation_ids:
        r = ValidationRepository.get_run(db, vid)
        if not r:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Validation run '{vid}' not found.")

        # Compute a simple validation quality score: passed / total (penalize failed)
        score = 0.0
        if r.total_checks > 0:
            score = (r.passed_checks / r.total_checks) * 100.0 - (r.failed_checks * 15.0)
            if r.overall_outcome == "VERIFIED_SUCCESS":
                score += 20.0
            elif r.overall_outcome == "FAILED":
                score -= 30.0

        if score > best_score:
            best_score = score
            best_id = r.id

        validations.append({
            "id": r.id,
            "recovery_plan_id": r.recovery_plan_id,
            "overall_outcome": r.overall_outcome,
            "total_checks": r.total_checks,
            "passed_checks": r.passed_checks,
            "failed_checks": r.failed_checks,
            "warning_checks": r.warning_checks,
            "unknown_checks": r.unknown_checks,
            "quality_score": round(max(0.0, score), 1),
            "created_at": r.created_at.isoformat()
        })

    return ValidationCompareResponse(
        validations=validations,
        best_validation_id=best_id,
        summary_verdict=f"Validation run '{best_id}' exhibited the highest recovery fidelity and verification completeness."
    )
