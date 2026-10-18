import json
import logging
from typing import List, Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.models.cascade_model import CascadeScenarioModel
from app.database.cascade_repository import CascadeRepository
from app.schemas.cascade_schema import (
    CascadePredictRequest,
    CascadePredictionResponse,
    CascadePathInfo,
    CascadeScenarioSaveRequest,
    CascadeScenarioResponse,
    CascadeSummaryResponse,
    ScenarioComparisonRequest,
    CascadeEvaluationResponse
)
from app.services.cascade_predictor import CascadePredictor
from app.services.cascade_evaluation import CascadeEvaluationService

logger = logging.getLogger("cascadeshield.cascade_routes")

router = APIRouter(prefix="/cascade", tags=["Module 3: Cascading Failure Prediction Engine"])

def _to_scenario_response(scenario: CascadeScenarioModel) -> CascadeScenarioResponse:
    try:
        input_params = json.loads(scenario.input_parameters) if isinstance(scenario.input_parameters, str) else scenario.input_parameters
    except Exception:
        input_params = {}

    try:
        res_summary = json.loads(scenario.result_summary) if isinstance(scenario.result_summary, str) else scenario.result_summary
    except Exception:
        res_summary = {}

    return CascadeScenarioResponse(
        id=scenario.id,
        scenario_name=scenario.scenario_name,
        initial_service_id=scenario.initial_service_id,
        failure_type=scenario.failure_type,
        failure_severity=scenario.failure_severity,
        input_parameters=input_params,
        result_summary=res_summary,
        created_at=scenario.created_at,
        data_source=scenario.data_source or "simulated"
    )

@router.get("/health", summary="Module 3 health status")
def cascade_health():
    return {
        "status": "healthy",
        "module": "Module 3: Cascading Failure Prediction Engine",
        "version": "3.0.0",
        "capabilities": [
            "Reverse graph failure propagation",
            "Multi-hop caller blast radius analysis",
            "0-100 normalized risk scoring",
            "Protocol-aware coupling decay",
            "Discrete time-step simulation timeline",
            "Benchmarking ground-truth evaluation",
            "Scenario persistence & comparison"
        ]
    }

@router.get("/summary", response_model=CascadeSummaryResponse, summary="Get summary overview of prediction metrics")
def get_cascade_summary(db: Session = Depends(get_db)):
    return CascadePredictor.get_summary(db)

@router.post("/predict", response_model=CascadePredictionResponse, summary="Predict failure propagation across dependent services")
def predict_cascading_failure(
    request: CascadePredictRequest,
    db: Session = Depends(get_db)
):
    try:
        return CascadePredictor.predict_cascade(db, request)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error during cascade prediction: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Cascading failure prediction failed: {str(e)}"
        )

@router.post("/simulate", response_model=CascadePredictionResponse, summary="Execute step-by-step failure simulation")
def simulate_cascading_failure(
    request: CascadePredictRequest,
    db: Session = Depends(get_db)
):
    """
    Simulates discrete time-step failure wave progression across the dependency graph.
    Returns the comprehensive prediction outcome and simulation step timeline.
    """
    return predict_cascading_failure(request, db)

@router.get("/impact/{service_id}", summary="Get downstream impacted callers for a service")
def get_service_impact(
    service_id: str,
    max_hops: int = Query(5, ge=1, le=8),
    db: Session = Depends(get_db)
):
    return CascadePredictor.get_impact_for_service(db, service_id, max_hops)

@router.get("/paths/{service_id}", response_model=List[CascadePathInfo], summary="Get propagation paths originating from service")
def get_service_paths(
    service_id: str,
    max_hops: int = Query(5, ge=1, le=8),
    db: Session = Depends(get_db)
):
    return CascadePredictor.get_paths_for_service(db, service_id, max_hops)

@router.get("/scenarios", summary="List saved simulation scenarios")
def list_scenarios(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    scenarios, total = CascadeRepository.list_scenarios(db, page, limit)
    items = [_to_scenario_response(s) for s in scenarios]
    return {
        "items": items,
        "total": total,
        "page": page,
        "limit": limit,
        "data_source": "simulated"
    }

@router.post("/scenarios", response_model=CascadeScenarioResponse, status_code=status.HTTP_201_CREATED, summary="Save a simulation scenario")
def save_scenario(
    request: CascadeScenarioSaveRequest,
    db: Session = Depends(get_db)
):
    try:
        scenario = CascadeRepository.create_scenario(
            db=db,
            scenario_name=request.scenario_name,
            initial_service_id=request.initial_service_id,
            failure_type=request.failure_type,
            failure_severity=request.failure_severity,
            input_parameters=request.input_parameters,
            result_summary=request.result_summary
        )
        return _to_scenario_response(scenario)
    except Exception as e:
        logger.error(f"Failed to persist cascade scenario: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to save simulation scenario: {str(e)}"
        )

@router.get("/scenarios/{scenario_id}", response_model=CascadeScenarioResponse, summary="Get a saved scenario by ID")
def get_scenario(
    scenario_id: str,
    db: Session = Depends(get_db)
):
    scenario = CascadeRepository.get_scenario_by_id(db, scenario_id)
    if not scenario:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Scenario '{scenario_id}' not found.")
    return _to_scenario_response(scenario)

@router.delete("/scenarios/{scenario_id}", summary="Delete a saved scenario")
def delete_scenario(
    scenario_id: str,
    db: Session = Depends(get_db)
):
    success = CascadeRepository.delete_scenario(db, scenario_id)
    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Scenario '{scenario_id}' not found.")
    return {"message": f"Scenario '{scenario_id}' deleted successfully.", "deleted": True}

@router.get("/evaluation", response_model=CascadeEvaluationResponse, summary="Benchmark comparison against ground truth")
def get_cascade_evaluation():
    """
    Executes benchmark evaluation on synthetic cloud topology scenarios.
    Compares Baseline Simple Traversal vs Static Rule Scoring vs Evidence-Aware Cascade Prediction.
    """
    return CascadeEvaluationService.run_benchmark_evaluation()

@router.post("/compare", summary="Compare multiple scenarios side-by-side")
def compare_scenarios(
    request: ScenarioComparisonRequest,
    db: Session = Depends(get_db)
):
    comparison_results: List[Dict[str, Any]] = []

    # 1. Compare saved scenarios from DB if provided
    if request.scenario_ids:
        for scen_id in request.scenario_ids:
            scen = CascadeRepository.get_scenario_by_id(db, scen_id)
            if scen:
                resp = _to_scenario_response(scen)
                summary = resp.result_summary
                comparison_results.append({
                    "scenario_id": scen.id,
                    "scenario_name": scen.scenario_name,
                    "initial_service_id": scen.initial_service_id,
                    "failure_type": scen.failure_type,
                    "failure_severity": scen.failure_severity,
                    "total_impacted": summary.get("total_impacted_services", 0),
                    "direct_impact": summary.get("direct_impact_count", 0),
                    "indirect_impact": summary.get("indirect_impact_count", 0),
                    "high_risk_count": summary.get("high_risk_count", 0),
                    "critical_risk_count": summary.get("critical_risk_count", 0),
                    "max_risk_score": summary.get("max_risk_score", 0.0),
                    "source": "persisted"
                })

    # 2. Compare live custom scenarios if provided
    if request.custom_scenarios:
        for i, c_req in enumerate(request.custom_scenarios):
            try:
                res = CascadePredictor.predict_cascade(db, c_req)
                comparison_results.append({
                    "scenario_id": f"custom-{i+1}",
                    "scenario_name": f"Simulation: {res.initial_service_name} ({res.failure_type})",
                    "initial_service_id": res.initial_service_id,
                    "failure_type": res.failure_type,
                    "failure_severity": res.failure_severity,
                    "total_impacted": res.total_impacted_services,
                    "direct_impact": res.direct_impact_count,
                    "indirect_impact": res.indirect_impact_count,
                    "high_risk_count": res.high_risk_count,
                    "critical_risk_count": res.critical_risk_count,
                    "max_risk_score": res.max_risk_score,
                    "source": "live"
                })
            except Exception as e:
                logger.warning(f"Could not predict custom scenario {i+1}: {e}")

    # Comparative analysis synthesis
    max_impact_scenario = max(comparison_results, key=lambda x: x["total_impacted"]) if comparison_results else None
    max_risk_scenario = max(comparison_results, key=lambda x: x["max_risk_score"]) if comparison_results else None

    analysis_notes = []
    if max_impact_scenario:
        analysis_notes.append(
            f"Scenario '{max_impact_scenario['scenario_name']}' produces the largest blast radius with {max_impact_scenario['total_impacted']} impacted services."
        )
    if max_risk_scenario and max_risk_scenario != max_impact_scenario:
        analysis_notes.append(
            f"Scenario '{max_risk_scenario['scenario_name']}' exhibits the highest peak risk score ({max_risk_scenario['max_risk_score']} pts)."
        )

    return {
        "compared_count": len(comparison_results),
        "scenarios": comparison_results,
        "highest_blast_radius": max_impact_scenario,
        "highest_risk_scenario": max_risk_scenario,
        "comparative_analysis": analysis_notes,
        "data_source": "simulated"
    }
