import json
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.database.simulation_repository import SimulationRepository
from app.schemas.simulation_schema import (
    ScenarioCreateRequest,
    ScenarioUpdateRequest,
    ScenarioResponse,
    SimulationRunRequest,
    SimulationRunResponse,
    SimulationStepState,
    ScenarioComparisonRequest,
    ScenarioComparisonResponse,
    SimulationEvaluationResponse,
    ScenarioConfigSchema
)
from app.services.scenario_builder import ScenarioBuilder
from app.services.simulation_validation import SimulationValidationService
from app.services.simulation_engine import SimulationEngine
from app.services.scenario_comparator import ScenarioComparator
from app.services.simulation_evaluation import SimulationEvaluationService

router = APIRouter(prefix="/simulation", tags=["Module 6: What-If Scenario Simulation Engine"])

# 1. Health
@router.get("/health")
def simulation_health(db: Session = Depends(get_db)):
    return {
        "status": "healthy",
        "module": "Module 6: What-If Scenario Simulation Engine",
        "version": "1.0.0",
        "simulation_mode": "discrete_time_step",
        "isolated_environment": True,
        "capabilities": [
            "multi_failure_injection",
            "multi_hop_propagation",
            "gradual_and_immediate_recovery",
            "scenario_cloning",
            "side_by_side_comparison",
            "ground_truth_benchmarking"
        ]
    }

# 2. Options and Presets
@router.get("/options")
def simulation_options(db: Session = Depends(get_db)):
    return ScenarioBuilder.get_simulation_options(db)

# 3. Create Scenario
@router.post("/scenarios", response_model=ScenarioResponse, status_code=status.HTTP_201_CREATED)
def create_scenario(req: ScenarioCreateRequest, db: Session = Depends(get_db)):
    try:
        SimulationValidationService.validate_scenario_config(db, req.config)
        scenario = SimulationRepository.create_scenario(db, {
            "name": req.name,
            "description": req.description,
            "category": req.category,
            "config": req.config.model_dump(),
            "source_data_type": req.source_data_type
        })
        return ScenarioResponse(
            id=scenario.id,
            name=scenario.name,
            description=scenario.description,
            category=scenario.category,
            config=ScenarioConfigSchema(**json.loads(scenario.scenario_config_json)),
            source_data_type=scenario.source_data_type,
            created_at=scenario.created_at,
            updated_at=scenario.updated_at,
            runs_count=0,
            latest_run_id=None
        )
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))

# 4. List Scenarios
@router.get("/scenarios")
def list_scenarios(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    category: Optional[str] = None,
    db: Session = Depends(get_db)
):
    scenarios, total = SimulationRepository.list_scenarios(db, skip=skip, limit=limit, category=category)
    items = []
    for s in scenarios:
        latest = s.runs[0] if s.runs else None
        items.append({
            "id": s.id,
            "name": s.name,
            "description": s.description,
            "category": s.category,
            "config": json.loads(s.scenario_config_json),
            "source_data_type": s.source_data_type,
            "created_at": s.created_at,
            "updated_at": s.updated_at,
            "runs_count": len(s.runs),
            "latest_run_id": latest.id if latest else None
        })
    return {"total": total, "skip": skip, "limit": limit, "scenarios": items}

# 5. Get Scenario
@router.get("/scenarios/{scenario_id}", response_model=ScenarioResponse)
def get_scenario(scenario_id: str, db: Session = Depends(get_db)):
    scenario = SimulationRepository.get_scenario(db, scenario_id)
    if not scenario:
        raise HTTPException(status_code=404, detail=f"Scenario '{scenario_id}' not found.")
    latest = scenario.runs[0] if scenario.runs else None
    return ScenarioResponse(
        id=scenario.id,
        name=scenario.name,
        description=scenario.description,
        category=scenario.category,
        config=ScenarioConfigSchema(**json.loads(scenario.scenario_config_json)),
        source_data_type=scenario.source_data_type,
        created_at=scenario.created_at,
        updated_at=scenario.updated_at,
        runs_count=len(scenario.runs),
        latest_run_id=latest.id if latest else None
    )

# 6. Update Scenario
@router.put("/scenarios/{scenario_id}", response_model=ScenarioResponse)
def update_scenario(scenario_id: str, req: ScenarioUpdateRequest, db: Session = Depends(get_db)):
    scenario = SimulationRepository.get_scenario(db, scenario_id)
    if not scenario:
        raise HTTPException(status_code=404, detail=f"Scenario '{scenario_id}' not found.")

    if req.config:
        try:
            SimulationValidationService.validate_scenario_config(db, req.config)
        except ValueError as ve:
            raise HTTPException(status_code=400, detail=str(ve))

    updated = SimulationRepository.update_scenario(db, scenario_id, {
        "name": req.name,
        "description": req.description,
        "category": req.category,
        "config": req.config.model_dump() if req.config else None
    })
    latest = updated.runs[0] if updated.runs else None
    return ScenarioResponse(
        id=updated.id,
        name=updated.name,
        description=updated.description,
        category=updated.category,
        config=ScenarioConfigSchema(**json.loads(updated.scenario_config_json)),
        source_data_type=updated.source_data_type,
        created_at=updated.created_at,
        updated_at=updated.updated_at,
        runs_count=len(updated.runs),
        latest_run_id=latest.id if latest else None
    )

# 7. Delete Scenario
@router.delete("/scenarios/{scenario_id}")
def delete_scenario(scenario_id: str, db: Session = Depends(get_db)):
    success = SimulationRepository.delete_scenario(db, scenario_id)
    if not success:
        raise HTTPException(status_code=404, detail=f"Scenario '{scenario_id}' not found.")
    return {"deleted": True, "scenario_id": scenario_id}

# 8. Run Scenario
@router.post("/scenarios/{scenario_id}/run", response_model=SimulationRunResponse)
def run_scenario(
    scenario_id: str, 
    req: Optional[SimulationRunRequest] = None, 
    db: Session = Depends(get_db)
):
    scenario = SimulationRepository.get_scenario(db, scenario_id)
    if not scenario:
        raise HTTPException(status_code=404, detail=f"Scenario '{scenario_id}' not found.")

    config = ScenarioConfigSchema(**json.loads(scenario.scenario_config_json))
    seed = req.random_seed if req else None
    max_steps = req.max_steps_override if req else None

    try:
        return SimulationEngine.run_simulation(
            db=db,
            scenario_id=scenario.id,
            scenario_name=scenario.name,
            config=config,
            random_seed=seed,
            max_steps_override=max_steps
        )
    except Exception as ex:
        raise HTTPException(status_code=500, detail=f"Simulation run failed: {str(ex)}")

# 9. Reset Scenario
@router.post("/scenarios/{scenario_id}/reset")
def reset_scenario(scenario_id: str, db: Session = Depends(get_db)):
    scenario = SimulationRepository.get_scenario(db, scenario_id)
    if not scenario:
        raise HTTPException(status_code=404, detail=f"Scenario '{scenario_id}' not found.")
    return {
        "scenario_id": scenario_id,
        "reset": True,
        "message": "Simulation in-memory canvas reset to clean digital twin baseline. History preserved."
    }

# 10. Get Run Details
@router.get("/runs/{run_id}", response_model=SimulationRunResponse)
def get_run(run_id: str, db: Session = Depends(get_db)):
    run = SimulationRepository.get_run(db, run_id)
    if not run:
        raise HTTPException(status_code=404, detail=f"Run '{run_id}' not found.")

    scenario = SimulationRepository.get_scenario(db, run.scenario_id)
    scen_name = scenario.name if scenario else "Unknown Scenario"
    summary = json.loads(run.summary_json) if run.summary_json else None

    # Load service states to build timeline
    all_states = SimulationRepository.get_run_service_states(db, run_id)
    events = SimulationRepository.get_run_events(db, run_id)

    timeline = []
    # Group by step
    steps_map = {}
    for st in all_states:
        step_num = st.step_number
        if step_num not in steps_map:
            steps_map[step_num] = {}
        steps_map[step_num][st.service_id] = json.loads(st.state_json)

    for step_num in sorted(steps_map.keys()):
        step_evs = [
            {"event_type": e.event_type, "service_id": e.service_id, "data": json.loads(e.event_data_json)}
            for e in events if e.step_number == step_num
        ]
        timeline.append(
            SimulationStepState(
                step_number=step_num,
                services=steps_map[step_num],
                events=step_evs
            )
        )

    impacted = [sid for sid, st in steps_map.get(run.total_steps, {}).items() if st.get("is_impacted")]

    return SimulationRunResponse(
        id=run.id,
        scenario_id=run.scenario_id,
        scenario_name=scen_name,
        status=run.status,
        random_seed=run.random_seed,
        model_version=run.model_version,
        total_steps=run.total_steps,
        started_at=run.started_at,
        completed_at=run.completed_at,
        summary=summary,
        error_summary=run.error_summary,
        timeline_steps=timeline,
        impacted_services=impacted,
        propagation_paths=[]
    )

# 11. Get Run Timeline
@router.get("/runs/{run_id}/timeline")
def get_run_timeline(run_id: str, db: Session = Depends(get_db)):
    run = SimulationRepository.get_run(db, run_id)
    if not run:
        raise HTTPException(status_code=404, detail=f"Run '{run_id}' not found.")
    events = SimulationRepository.get_run_events(db, run_id)
    return [
        {
            "id": e.id,
            "step_number": e.step_number,
            "event_type": e.event_type,
            "service_id": e.service_id,
            "data": json.loads(e.event_data_json),
            "created_at": e.created_at
        }
        for e in events
    ]

# 12. Get Run Metrics History
@router.get("/runs/{run_id}/metrics")
def get_run_metrics(run_id: str, service_id: Optional[str] = None, db: Session = Depends(get_db)):
    states = SimulationRepository.get_run_service_states(db, run_id)
    if service_id:
        states = [s for s in states if s.service_id == service_id]

    sequence = []
    for s in states:
        d = json.loads(s.state_json)
        sequence.append({
            "step_number": s.step_number,
            "service_id": s.service_id,
            "cpu_usage": d.get("cpu_usage"),
            "memory_usage": d.get("memory_usage"),
            "latency_ms": d.get("latency_ms"),
            "error_rate": d.get("error_rate"),
            "risk_score": d.get("risk_score"),
            "health_status": s.health_status
        })
    return sequence

# 13. Get Run Direct & Indirect Impacts
@router.get("/runs/{run_id}/impact")
def get_run_impact(run_id: str, db: Session = Depends(get_db)):
    run = SimulationRepository.get_run(db, run_id)
    if not run or not run.summary_json:
        raise HTTPException(status_code=404, detail=f"Run '{run_id}' not found or incomplete.")
    summary = json.loads(run.summary_json)
    events = SimulationRepository.get_run_events(db, run_id)
    
    initial = [e.service_id for e in events if e.event_type == "FAILURE_INJECTION"]
    propagated = [e.service_id for e in events if e.event_type == "PROPAGATION_WAVE"]

    return {
        "run_id": run_id,
        "initial_failures": list(set(initial)),
        "propagated_impacts": list(set(propagated)),
        "total_impacted_count": summary.get("total_impacted_services", 0),
        "residual_impacted": summary.get("residual_impacted_services", [])
    }

# 14. Compare Scenarios / Runs
@router.post("/compare", response_model=ScenarioComparisonResponse)
def compare_scenarios(req: ScenarioComparisonRequest, db: Session = Depends(get_db)):
    run_ids = list(req.run_ids or [])
    if req.scenario_ids:
        for sc_id in req.scenario_ids:
            sc = SimulationRepository.get_scenario(db, sc_id)
            if sc and sc.runs:
                run_ids.append(sc.runs[0].id)

    # If no specific runs requested, pick latest completed runs
    if not run_ids:
        all_runs, _ = SimulationRepository.list_runs(db, limit=5)
        run_ids = [r.id for r in all_runs if r.status == "COMPLETED"]

    return ScenarioComparator.compare_runs(db, run_ids)

# 15. Benchmark Evaluation
@router.get("/evaluation", response_model=SimulationEvaluationResponse)
def get_evaluation():
    return SimulationEvaluationService.run_benchmark_evaluation()

# 16. Clone Scenario
@router.post("/scenarios/{scenario_id}/clone", response_model=ScenarioResponse)
def clone_scenario(scenario_id: str, new_name: Optional[str] = None, db: Session = Depends(get_db)):
    cloned = SimulationRepository.clone_scenario(db, scenario_id, new_name=new_name)
    if not cloned:
        raise HTTPException(status_code=404, detail=f"Scenario '{scenario_id}' not found.")

    return ScenarioResponse(
        id=cloned.id,
        name=cloned.name,
        description=cloned.description,
        category=cloned.category,
        config=ScenarioConfigSchema(**json.loads(cloned.scenario_config_json)),
        source_data_type=cloned.source_data_type,
        created_at=cloned.created_at,
        updated_at=cloned.updated_at,
        runs_count=0,
        latest_run_id=None
    )
