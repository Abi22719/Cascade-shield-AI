import json
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.database.recovery_repository import RecoveryRepository
from app.models.service import ServiceModel
from app.services.graph_service import GraphService
from app.schemas.recovery_schemas import (
    RecoveryPlanCreateRequest,
    RecoveryPlanGenerateRequest,
    RecoveryPlanResponse,
    RecoveryPlanUpdateRequest,
    RecoveryActionSchema,
    RecoverySimulationRequest,
    RecoverySimulationResponse,
    RecoveryComparisonRequest,
    RecoveryComparisonResponse,
    RecoveryConfigSchema,
    RecoveryEvaluationResponse,
    RiskFactorBreakdown
)
from app.services.recovery_risk_service import RecoveryRiskService
from app.services.recovery_validation_service import RecoveryValidationService
from app.services.recovery_plan_service import RecoveryPlanService
from app.services.recovery_simulation_service import RecoverySimulationService
from app.services.recovery_comparison_service import RecoveryComparisonService
from app.services.recovery_evaluation_service import RecoveryEvaluationService

router = APIRouter(prefix="/recovery", tags=["Module 7: Intelligent Recovery Planning and Risk Assessment"])

# Global runtime configuration
_runtime_config = RecoveryConfigSchema()

def _to_plan_response(plan, db: Session) -> RecoveryPlanResponse:
    actions_schemas = []
    for act in plan.actions:
        actions_schemas.append(
            RecoveryActionSchema(
                id=act.id,
                plan_id=act.plan_id,
                action_type=act.action_type,
                target_service_id=act.target_service_id,
                action_order=act.action_order,
                parameters=json.loads(act.parameters_json or "{}"),
                preconditions=json.loads(act.preconditions_json or "[]"),
                estimated_duration=act.estimated_duration,
                risk_score=act.risk_score,
                reversibility=act.reversibility,
                status=act.status,
                created_at=act.created_at
            )
        )

    breakdown_data = json.loads(plan.risk_breakdown_json or "[]")
    breakdown_schemas = [RiskFactorBreakdown(**b) for b in breakdown_data]

    latest = plan.runs[0] if plan.runs else None

    return RecoveryPlanResponse(
        id=plan.id,
        incident_id=plan.incident_id,
        scenario_id=plan.scenario_id,
        plan_name=plan.plan_name,
        description=plan.description,
        strategy_type=plan.strategy_type,
        risk_score=plan.risk_score,
        risk_level=plan.risk_level,
        estimated_recovery_time=plan.estimated_recovery_time,
        estimated_cost=plan.estimated_cost,
        status=plan.status,
        risk_breakdown=breakdown_schemas,
        actions=actions_schemas,
        created_at=plan.created_at,
        updated_at=plan.updated_at,
        runs_count=len(plan.runs),
        latest_run_id=latest.id if latest else None
    )

# 1. Health
@router.get("/health")
def recovery_health():
    return {
        "status": "healthy",
        "module": "Module 7: Intelligent Recovery Planning and Risk Assessment",
        "version": "1.0.0",
        "non_destructive": True,
        "capabilities": [
            "multi_strategy_plan_generation",
            "explainable_risk_scoring",
            "constraint_and_precondition_validation",
            "isolated_what_if_simulation",
            "side_by_side_tradeoff_comparison",
            "standardized_benchmarks"
        ]
    }

# 2. Options
@router.get("/options")
def recovery_options(db: Session = Depends(get_db)):
    services = db.query(ServiceModel).all()
    return {
        "action_types": [
            {"id": "restart_service", "name": "Simulate Service Restart", "desc": "Flushes process memory, clears connection queues, and restarts worker process."},
            {"id": "rollback_deployment", "name": "Simulate Rollback Deployment", "desc": "Reverts container image to previous stable release tag."},
            {"id": "traffic_reroute", "name": "Simulate Traffic Reroute / Shedding", "desc": "Diverts traffic to secondary replica or sheds non-critical endpoints."},
            {"id": "scale_up", "name": "Simulate Elastic Capacity Scale-Up", "desc": "Expands instance replicas to absorb heavy concurrency spikes."},
            {"id": "isolate_dependency", "name": "Simulate Circuit Breaker Isolation", "desc": "Trips circuit breaker to return fallback/mock response, halting cascade."},
            {"id": "restore_database", "name": "Simulate Point-in-Time Database Restore", "desc": "Restores relational connection pool and clears deadlocks."},
            {"id": "retry_request", "name": "Simulate Exponential Backoff Retry", "desc": "Retries transient RPC failures with exponential backoff and jitter."},
            {"id": "wait_auto_recovery", "name": "Simulate Self-Healing Watch", "desc": "Monitors container platform liveness probes without manual intervention."}
        ],
        "strategies": [
            {"id": "lowest_risk", "name": "Lowest-Risk Strategy", "desc": "Minimizes potential blast radius, uses safe circuit breakers, avoids data loss."},
            {"id": "fastest_recovery", "name": "Fastest-Recovery Strategy", "desc": "Aggressively restores service health in minimum steps; higher disruption risk."},
            {"id": "lowest_cost", "name": "Lowest-Cost Strategy", "desc": "Consumes 0 or minimal cloud infrastructure compute resources."},
            {"id": "balanced", "name": "Risk-Aware Balanced Strategy", "desc": "Optimal synthesis: graceful diversion, elastic scaling, and rolling recovery."}
        ],
        "services": [{"id": s.id, "name": s.name, "type": s.service_type, "status": s.health_status} for s in services]
    }

# 3. Config
@router.get("/config", response_model=RecoveryConfigSchema)
def get_config():
    global _runtime_config
    return _runtime_config

@router.put("/config", response_model=RecoveryConfigSchema)
def update_config(cfg: RecoveryConfigSchema):
    global _runtime_config
    _runtime_config = cfg
    return _runtime_config

# 4. Generate Plans (POST /api/recovery/plan)
@router.post("/plan", response_model=List[RecoveryPlanResponse])
def generate_plans(req: RecoveryPlanGenerateRequest, db: Session = Depends(get_db)):
    candidate_requests = RecoveryPlanService.generate_candidate_plans(db, req)
    G_dep = GraphService.get_dependency_graph(db)

    persisted_plans = []
    for c_req in candidate_requests:
        # Calculate risk and factors
        risk_res = RecoveryRiskService.calculate_plan_risk(c_req.actions, G_dep=G_dep, config=_runtime_config)
        
        plan_data = {
            "incident_id": c_req.incident_id,
            "scenario_id": c_req.scenario_id,
            "plan_name": c_req.plan_name,
            "description": c_req.description,
            "strategy_type": c_req.strategy_type,
            "risk_score": risk_res["risk_score"],
            "risk_level": risk_res["risk_level"],
            "estimated_recovery_time": risk_res["estimated_recovery_time"],
            "estimated_cost": risk_res["estimated_cost"],
            "status": "VALIDATED",
            "risk_breakdown": risk_res["breakdown"],
            "actions": [act.model_dump() for act in c_req.actions]
        }
        plan_model = RecoveryRepository.create_plan(db, plan_data)
        persisted_plans.append(_to_plan_response(plan_model, db))

    return persisted_plans

# 5. Create Custom Plan (POST /api/recovery/plans)
@router.post("/plans", response_model=RecoveryPlanResponse, status_code=status.HTTP_201_CREATED)
def create_plan(req: RecoveryPlanCreateRequest, db: Session = Depends(get_db)):
    try:
        RecoveryValidationService.validate_plan_creation(db, req, _runtime_config)
        G_dep = GraphService.get_dependency_graph(db)
        risk_res = RecoveryRiskService.calculate_plan_risk(req.actions, G_dep=G_dep, config=_runtime_config)

        plan_data = {
            "incident_id": req.incident_id,
            "scenario_id": req.scenario_id,
            "plan_name": req.plan_name,
            "description": req.description,
            "strategy_type": req.strategy_type,
            "risk_score": risk_res["risk_score"],
            "risk_level": risk_res["risk_level"],
            "estimated_recovery_time": risk_res["estimated_recovery_time"],
            "estimated_cost": risk_res["estimated_cost"],
            "status": "VALIDATED",
            "risk_breakdown": risk_res["breakdown"],
            "actions": [act.model_dump() for act in req.actions]
        }
        plan = RecoveryRepository.create_plan(db, plan_data)
        return _to_plan_response(plan, db)
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))

# 6. List Plans (GET /api/recovery/plans)
@router.get("/plans")
def list_plans(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    incident_id: Optional[str] = None,
    scenario_id: Optional[str] = None,
    db: Session = Depends(get_db)
):
    plans, total = RecoveryRepository.list_plans(db, skip=skip, limit=limit, incident_id=incident_id, scenario_id=scenario_id)
    return {
        "total": total,
        "skip": skip,
        "limit": limit,
        "plans": [_to_plan_response(p, db) for p in plans]
    }

# 7. Get Plan (GET /api/recovery/plans/{plan_id})
@router.get("/plans/{plan_id}", response_model=RecoveryPlanResponse)
def get_plan(plan_id: str, db: Session = Depends(get_db)):
    plan = RecoveryRepository.get_plan(db, plan_id)
    if not plan:
        raise HTTPException(status_code=404, detail=f"Recovery Plan '{plan_id}' not found.")
    return _to_plan_response(plan, db)

# 8. Update Plan (PUT /api/recovery/plans/{plan_id})
@router.put("/plans/{plan_id}", response_model=RecoveryPlanResponse)
def update_plan(plan_id: str, req: RecoveryPlanUpdateRequest, db: Session = Depends(get_db)):
    plan = RecoveryRepository.get_plan(db, plan_id)
    if not plan:
        raise HTTPException(status_code=404, detail=f"Recovery Plan '{plan_id}' not found.")

    upd_data = {}
    if req.plan_name:
        upd_data["plan_name"] = req.plan_name
    if req.description:
        upd_data["description"] = req.description
    if req.strategy_type:
        upd_data["strategy_type"] = req.strategy_type
    if req.status:
        upd_data["status"] = req.status

    if req.actions is not None:
        try:
            temp_req = RecoveryPlanCreateRequest(
                plan_name=req.plan_name or plan.plan_name,
                actions=req.actions
            )
            RecoveryValidationService.validate_plan_creation(db, temp_req, _runtime_config)
            G_dep = GraphService.get_dependency_graph(db)
            risk_res = RecoveryRiskService.calculate_plan_risk(req.actions, G_dep=G_dep, config=_runtime_config)
            upd_data["actions"] = [act.model_dump() for act in req.actions]
            upd_data["risk_score"] = risk_res["risk_score"]
            upd_data["risk_level"] = risk_res["risk_level"]
            upd_data["estimated_recovery_time"] = risk_res["estimated_recovery_time"]
            upd_data["estimated_cost"] = risk_res["estimated_cost"]
            upd_data["risk_breakdown"] = risk_res["breakdown"]
        except ValueError as ve:
            raise HTTPException(status_code=400, detail=str(ve))

    updated = RecoveryRepository.update_plan(db, plan_id, upd_data)
    return _to_plan_response(updated, db)

# 9. Delete Plan (DELETE /api/recovery/plans/{plan_id})
@router.delete("/plans/{plan_id}")
def delete_plan(plan_id: str, db: Session = Depends(get_db)):
    success = RecoveryRepository.delete_plan(db, plan_id)
    if not success:
        raise HTTPException(status_code=404, detail=f"Recovery Plan '{plan_id}' not found.")
    return {"deleted": True, "plan_id": plan_id}

# 10. Simulate Plan (POST /api/recovery/plans/{plan_id}/simulate)
@router.post("/plans/{plan_id}/simulate", response_model=RecoverySimulationResponse)
def simulate_plan(
    plan_id: str, 
    req: Optional[RecoverySimulationRequest] = None, 
    db: Session = Depends(get_db)
):
    try:
        request_obj = req or RecoverySimulationRequest()
        return RecoverySimulationService.simulate_recovery_plan(db, plan_id, request_obj)
    except ValueError as ve:
        raise HTTPException(status_code=404, detail=str(ve))
    except Exception as ex:
        raise HTTPException(status_code=500, detail=f"Simulation failed: {str(ex)}")

# 11. Get Results (GET /api/recovery/plans/{plan_id}/results)
@router.get("/plans/{plan_id}/results")
def get_plan_results(plan_id: str, db: Session = Depends(get_db)):
    plan = RecoveryRepository.get_plan(db, plan_id)
    if not plan:
        raise HTTPException(status_code=404, detail=f"Recovery Plan '{plan_id}' not found.")
    
    if not plan.runs:
        return {
            "run_id": None,
            "plan_id": plan.id,
            "outcome": None,
            "total_recovery_time": 0,
            "maximum_risk": 0.0,
            "final_health_summary": {},
            "created_at": None
        }

    latest = plan.runs[0]
    return {
        "run_id": latest.id,
        "plan_id": plan.id,
        "outcome": latest.outcome,
        "total_recovery_time": latest.total_recovery_time,
        "maximum_risk": latest.maximum_risk,
        "final_health_summary": json.loads(latest.final_health_summary or "{}"),
        "created_at": latest.created_at
    }

# 12. Get Timeline (GET /api/recovery/plans/{plan_id}/timeline)
@router.get("/plans/{plan_id}/timeline")
def get_plan_timeline(plan_id: str, db: Session = Depends(get_db)):
    plan = RecoveryRepository.get_plan(db, plan_id)
    if not plan:
        raise HTTPException(status_code=404, detail=f"Recovery Plan '{plan_id}' not found.")
    
    if not plan.runs:
        return []

    latest = plan.runs[0]
    events = RecoveryRepository.get_run_events(db, latest.id)
    return [
        {
            "id": ev.id,
            "event_type": ev.event_type,
            "description": ev.description,
            "evidence": json.loads(ev.evidence_json or "{}"),
            "timestamp_or_step": ev.timestamp_or_step,
            "created_at": ev.created_at
        }
        for ev in events
    ]

# 13. Compare Plans (POST /api/recovery/compare)
@router.post("/compare", response_model=RecoveryComparisonResponse)
def compare_plans(req: RecoveryComparisonRequest, db: Session = Depends(get_db)):
    try:
        return RecoveryComparisonService.compare_plans(
            db=db,
            plan_ids=req.plan_ids,
            priority=req.optimization_priority or "balanced"
        )
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))

# 14. Evaluation (GET /api/recovery/evaluation)
@router.get("/evaluation", response_model=RecoveryEvaluationResponse)
def get_evaluation():
    return RecoveryEvaluationService.run_benchmark_evaluation()
