import json
import logging
from typing import List, Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.database.rca_repository import RCARepository
from app.models.rca_model import RCAIncidentModel
from app.schemas.rca_schema import (
    RCAInvestigationRequest,
    RCAReportSchema,
    RCAIncidentListResponse,
    RCAIncidentSummarySchema,
    EvidenceItemSchema,
    CandidateRootCauseSchema,
    TimelineEventSchema,
    DiagnosticRecommendationSchema,
    RCAEvaluationResponse,
    RCACompareRequest,
    RCACompareResponse
)
from app.services.rca_engine import RCAEngine
from app.services.rca_evaluation import RCAEvaluationService

logger = logging.getLogger("cascadeshield.rca_routes")

router = APIRouter(prefix="/rca", tags=["Module 4: Evidence-Grounded Root Cause Analysis"])

@router.get("/health", summary="Module 4 health and source module connectivity status")
def rca_health(db: Session = Depends(get_db)):
    from app.models.service import ServiceModel
    from app.models.alert_model import AlertModel
    from app.models.cascade_model import CascadeScenarioModel

    services_count = db.query(ServiceModel).count()
    alerts_count = db.query(AlertModel).count()
    scenarios_count = db.query(CascadeScenarioModel).count()

    return {
        "status": "healthy",
        "module": "Module 4: Evidence-Grounded Root Cause Analysis",
        "version": "4.0.0",
        "connected_source_modules": {
            "module_1_digital_twin": {
                "available": services_count > 0,
                "services_count": services_count
            },
            "module_2_anomaly_detection": {
                "available": alerts_count >= 0,
                "recorded_alerts_count": alerts_count
            },
            "module_3_cascade_prediction": {
                "available": scenarios_count >= 0,
                "saved_scenarios_count": scenarios_count
            }
        },
        "capabilities": [
            "Multi-source evidence normalization",
            "Temporal precedence and onset detection",
            "NetworkX failure path reachability",
            "Deterministic multi-factor candidate ranking",
            "Contradictory evidence penalties",
            "Alternative hypotheses discovery",
            "Targeted non-destructive diagnostic recommendations",
            "Auditable structured investigation report"
        ]
    }

@router.post("/analyze", response_model=RCAReportSchema, summary="Run Root Cause Analysis on an incident")
def analyze_incident(
    request: RCAInvestigationRequest,
    db: Session = Depends(get_db)
):
    try:
        return RCAEngine.analyze_incident(db, request)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to execute Root Cause Analysis: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Root Cause Analysis failed: {str(e)}"
        )

@router.get("/incidents", response_model=RCAIncidentListResponse, summary="List saved RCA investigations")
def list_incidents(
    status_filter: Optional[str] = Query(None, alias="status"),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    incidents, total = RCARepository.list_incidents(db, status=status_filter, page=page, limit=limit)
    summaries = []

    for inc in incidents:
        # Extract top candidate info from candidates relationship or report
        top_cand = None
        top_conf = None
        if inc.candidates:
            c0 = inc.candidates[0]
            top_cand = f"{c0.service_name} ({c0.ranking_score:.1f} pts)"
            top_conf = c0.confidence_label
        elif inc.report:
            try:
                rep_data = json.loads(inc.report.report_json)
                if rep_data.get("primary_root_cause"):
                    p = rep_data["primary_root_cause"]
                    top_cand = f"{p['service_name']} ({p['ranking_score']:.1f} pts)"
                    top_conf = p["confidence_label"]
            except Exception:
                pass

        aff_count = 0
        try:
            aff_count = len(json.loads(inc.affected_service_ids))
        except Exception:
            pass

        summaries.append(
            RCAIncidentSummarySchema(
                id=inc.id,
                title=inc.title,
                status=inc.status,
                target_service_id=inc.target_service_id,
                affected_services_count=aff_count,
                top_candidate=top_cand,
                top_confidence=top_conf,
                created_at=inc.created_at
            )
        )

    return RCAIncidentListResponse(
        items=summaries,
        total=total,
        page=page,
        limit=limit
    )

@router.get("/incidents/{incident_id}", response_model=RCAReportSchema, summary="Get full incident investigation report")
def get_incident(
    incident_id: str,
    db: Session = Depends(get_db)
):
    report = RCAEngine.get_incident_report(db, incident_id)
    if not report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Investigation report for incident '{incident_id}' not found."
        )
    return report

@router.post("/incidents/{incident_id}/reanalyze", response_model=RCAReportSchema, summary="Re-run RCA on an existing incident")
def reanalyze_incident(
    incident_id: str,
    db: Session = Depends(get_db)
):
    return RCAEngine.reanalyze_incident(db, incident_id)

@router.delete("/incidents/{incident_id}", summary="Delete an incident investigation")
def delete_incident(
    incident_id: str,
    db: Session = Depends(get_db)
):
    success = RCARepository.delete_incident(db, incident_id)
    if not success:
        raise HTTPException(status_code=404, detail=f"Incident '{incident_id}' not found.")
    return {"message": f"Incident '{incident_id}' and all associated evidence deleted.", "deleted": True}

@router.get("/incidents/{incident_id}/evidence", response_model=List[EvidenceItemSchema], summary="Get evidence collected for incident")
def get_incident_evidence(
    incident_id: str,
    db: Session = Depends(get_db)
):
    report = RCAEngine.get_incident_report(db, incident_id)
    if not report:
        raise HTTPException(status_code=404, detail=f"Incident '{incident_id}' not found.")
    return report.evidence_items

@router.get("/incidents/{incident_id}/candidates", response_model=List[CandidateRootCauseSchema], summary="Get ranked root cause candidates")
def get_incident_candidates(
    incident_id: str,
    db: Session = Depends(get_db)
):
    report = RCAEngine.get_incident_report(db, incident_id)
    if not report:
        raise HTTPException(status_code=404, detail=f"Incident '{incident_id}' not found.")
    return report.ranked_candidates

@router.get("/incidents/{incident_id}/timeline", response_model=List[TimelineEventSchema], summary="Get time-ordered event timeline")
def get_incident_timeline(
    incident_id: str,
    db: Session = Depends(get_db)
):
    report = RCAEngine.get_incident_report(db, incident_id)
    if not report:
        raise HTTPException(status_code=404, detail=f"Incident '{incident_id}' not found.")
    return report.evidence_timeline

@router.get("/incidents/{incident_id}/recommendations", response_model=List[DiagnosticRecommendationSchema], summary="Get diagnostic recommendations")
def get_incident_recommendations(
    incident_id: str,
    db: Session = Depends(get_db)
):
    report = RCAEngine.get_incident_report(db, incident_id)
    if not report:
        raise HTTPException(status_code=404, detail=f"Incident '{incident_id}' not found.")
    return report.diagnostic_recommendations

@router.get("/incidents/{incident_id}/report", response_model=RCAReportSchema, summary="Get auditable report for incident")
def get_incident_report_endpoint(
    incident_id: str,
    db: Session = Depends(get_db)
):
    return get_incident(incident_id, db)

@router.get("/evaluation", response_model=RCAEvaluationResponse, summary="Benchmark evaluation across synthetic ground-truth topologies")
def get_rca_evaluation():
    """
    Executes reproducible benchmark evaluation on synthetic cloud topology incidents with known ground-truth.
    Compares Earliest-Anomaly Baseline vs Dependency-Only Baseline vs Evidence-Grounded RCA.
    """
    return RCAEvaluationService.run_benchmark_evaluation()

@router.post("/compare", response_model=RCACompareResponse, summary="Compare multiple incident investigations side-by-side")
def compare_incidents(
    request: RCACompareRequest,
    db: Session = Depends(get_db)
):
    return RCAEngine.compare_incidents(db, request)
