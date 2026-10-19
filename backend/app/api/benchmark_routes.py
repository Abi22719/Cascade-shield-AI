import json
from typing import Dict, Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import PlainTextResponse, Response
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.database.benchmark_repository import BenchmarkRepository
from app.models.benchmark_models import BenchmarkExperimentModel, BenchmarkDatasetModel, BenchmarkScenarioModel
from app.schemas.benchmark_schemas import (
    BenchmarkConfigSchema,
    BenchmarkDatasetSchema,
    BenchmarkDatasetGenerateRequest,
    BenchmarkScenarioSchema,
    BenchmarkExperimentCreateRequest,
    BenchmarkExperimentResponse,
    BenchmarkResultSchema,
    BenchmarkComparisonSchema,
    BenchmarkCompareRequest,
    BenchmarkCompareResponse,
    BenchmarkEvaluationSummaryResponse
)
from app.services.benchmark_baseline_service import BenchmarkBaselineService
from app.services.benchmark_comparison_service import BenchmarkComparisonService
from app.services.benchmark_dataset_service import BenchmarkDatasetService
from app.services.benchmark_experiment_service import BenchmarkExperimentService
from app.services.benchmark_export_service import BenchmarkExportService
from app.services.benchmark_report_service import BenchmarkReportService

router = APIRouter(prefix="/benchmark", tags=["Module 9: Resilience Benchmarking & Performance Evaluation"])

# Helpers
def _format_scenario(scn: BenchmarkScenarioModel) -> Dict[str, Any]:
    return {
        "id": scn.id,
        "dataset_id": scn.dataset_id,
        "name": scn.name,
        "scenario_type": scn.scenario_type,
        "input_config": json.loads(scn.input_json) if scn.input_json else {},
        "ground_truth": json.loads(scn.ground_truth_json) if scn.ground_truth_json else {},
        "data_source": scn.data_source,
        "created_at": scn.created_at
    }

def _format_dataset(ds: BenchmarkDatasetModel) -> Dict[str, Any]:
    return {
        "id": ds.id,
        "name": ds.name,
        "description": ds.description,
        "dataset_type": ds.dataset_type,
        "seed": ds.seed,
        "scenario_count": ds.scenario_count or len(ds.scenarios or []),
        "schema_version": ds.schema_version,
        "metadata": json.loads(ds.metadata_json) if ds.metadata_json else None,
        "scenarios": [_format_scenario(s) for s in (ds.scenarios or [])],
        "created_at": ds.created_at
    }

def _format_experiment(exp: BenchmarkExperimentModel) -> Dict[str, Any]:
    return {
        "id": exp.id,
        "name": exp.name,
        "description": exp.description,
        "dataset_id": exp.dataset_id,
        "selected_modules": json.loads(exp.selected_modules_json) if exp.selected_modules_json else [],
        "selected_methods": json.loads(exp.selected_methods_json) if exp.selected_methods_json else None,
        "random_seed": exp.random_seed,
        "repetitions": exp.repetitions,
        "status": exp.status,
        "progress": exp.progress,
        "overall_resilience_score": exp.overall_resilience_score,
        "summary": json.loads(exp.summary_json) if exp.summary_json else None,
        "started_at": exp.started_at,
        "completed_at": exp.completed_at,
        "error_message": exp.error_message,
        "created_at": exp.created_at,
        "results": [
            {
                "id": r.id,
                "experiment_id": r.experiment_id,
                "scenario_id": r.scenario_id,
                "module_name": r.module_name,
                "method_name": r.method_name,
                "metric_name": r.metric_name,
                "metric_value": r.metric_value,
                "metric_unit": r.metric_unit,
                "sample_count": r.sample_count,
                "metadata": json.loads(r.metadata_json) if r.metadata_json else None,
                "created_at": r.created_at
            }
            for r in (exp.results or [])
        ],
        "comparisons": [
            {
                "id": c.id,
                "experiment_id": c.experiment_id,
                "comparison_name": c.comparison_name,
                "baseline_name": c.baseline_name,
                "candidate_name": c.candidate_name,
                "comparison_metrics": json.loads(c.comparison_metrics_json) if c.comparison_metrics_json else {},
                "interpretation": c.interpretation,
                "created_at": c.created_at
            }
            for c in (exp.comparisons or [])
        ]
    }


# 1. Health
@router.get("/health")
def benchmark_health():
    """
    Module 9 Resilience Benchmarking subsystem health and integration status across Modules 1 to 8.
    """
    return {
        "status": "healthy",
        "module": "Module 9: Resilience Benchmarking and Performance Evaluation",
        "version": "9.0.0",
        "capabilities": [
            "dataset_management",
            "scenario_catalog_execution",
            "cross_module_evaluations",
            "side_by_side_baseline_comparisons",
            "overall_resilience_scoring",
            "statistical_aggregation",
            "multi_format_reporting",
            "isolated_sandbox_safety"
        ],
        "safety_mode": "strictly_simulated_isolated_sandbox",
        "supported_modules": [
            "module_2", "module_3", "module_4", "module_5", "module_6", "module_7", "module_8", "end_to_end"
        ]
    }


# 2. Config
@router.get("/config", response_model=BenchmarkConfigSchema)
def get_benchmark_config(db: Session = Depends(get_db)):
    """
    Retrieve configurable benchmark parameters, component weights, and thresholds.
    """
    configs = BenchmarkRepository.get_all_configs(db)
    schema = BenchmarkConfigSchema()
    if "timeout_seconds" in configs:
        schema.timeout_seconds = int(configs["timeout_seconds"])
    if "max_scenarios_per_run" in configs:
        schema.max_scenarios_per_run = int(configs["max_scenarios_per_run"])
    if "default_random_seed" in configs:
        schema.default_random_seed = int(configs["default_random_seed"])
    if "default_repetitions" in configs:
        schema.default_repetitions = int(configs["default_repetitions"])
    if "component_weights" in configs:
        schema.component_weights = json.loads(configs["component_weights"])
    if "export_formats" in configs:
        schema.export_formats = json.loads(configs["export_formats"])
    return schema

@router.put("/config", response_model=BenchmarkConfigSchema)
def update_benchmark_config(updates: Dict[str, Any], db: Session = Depends(get_db)):
    """
    Update configurable benchmark settings.
    """
    for k, v in updates.items():
        val_str = json.dumps(v) if isinstance(v, (dict, list)) else str(v)
        BenchmarkRepository.set_config(db, k, val_str)
    return get_benchmark_config(db)


# 3. Datasets
@router.get("/datasets")
def list_datasets(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """
    List registered benchmark datasets with pagination.
    """
    datasets, total = BenchmarkRepository.list_datasets(db, skip=skip, limit=limit)
    if total == 0:
        # Auto-seed canonical dataset
        canonical = BenchmarkDatasetService.generate_canonical_dataset(db)
        datasets = [canonical]
        total = 1

    return {
        "total": total,
        "skip": skip,
        "limit": limit,
        "items": [_format_dataset(d) for d in datasets]
    }

@router.get("/datasets/{dataset_id}")
def get_dataset(dataset_id: str, db: Session = Depends(get_db)):
    """
    Retrieve full dataset specification including all synthetic failure scenarios.
    """
    ds = BenchmarkRepository.get_dataset(db, dataset_id)
    if not ds:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Dataset '{dataset_id}' not found.")
    return _format_dataset(ds)

@router.post("/datasets/generate")
def generate_dataset(req: BenchmarkDatasetGenerateRequest, db: Session = Depends(get_db)):
    """
    Generate standard 10-scenario synthetic failure benchmark suite with isolated ground truth.
    """
    ds = BenchmarkDatasetService.generate_canonical_dataset(db, req)
    return _format_dataset(ds)


# 4. Scenarios
@router.get("/scenarios")
def list_scenarios(dataset_id: Optional[str] = Query(None), db: Session = Depends(get_db)):
    """
    List benchmark failure scenarios, optionally filtered by dataset ID.
    """
    if dataset_id:
        scenarios = BenchmarkRepository.list_scenarios_for_dataset(db, dataset_id)
    else:
        datasets, count = BenchmarkRepository.list_datasets(db, limit=1)
        if not datasets:
            BenchmarkDatasetService.generate_canonical_dataset(db)
            datasets, count = BenchmarkRepository.list_datasets(db, limit=1)
        scenarios = BenchmarkRepository.list_scenarios_for_dataset(db, datasets[0].id)
    return [_format_scenario(s) for s in scenarios]

@router.get("/scenarios/{scenario_id}")
def get_scenario(scenario_id: str, db: Session = Depends(get_db)):
    """
    Retrieve single scenario definition, input parameters, and isolated ground truth labels.
    """
    scn = BenchmarkRepository.get_scenario(db, scenario_id)
    if not scn:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Scenario '{scenario_id}' not found.")
    return _format_scenario(scn)


# 5. Baselines Catalog
@router.get("/baselines")
def get_baselines_catalog():
    """
    Retrieve catalog of supported candidate algorithms and standard baselines for Modules 2 to 8.
    """
    return BenchmarkBaselineService.get_supported_baselines()


# 6. Experiments
@router.post("/experiments", response_model=BenchmarkExperimentResponse)
def create_experiment(
    req: BenchmarkExperimentCreateRequest,
    auto_run: bool = Query(True, description="Immediately execute experiment upon creation"),
    db: Session = Depends(get_db)
):
    """
    Create a new benchmark experiment. If auto_run is True (default), immediately executes
    the run across all selected modules and scenarios.
    """
    exp = BenchmarkExperimentService.create_experiment(db, req)
    if auto_run:
        exp = BenchmarkExperimentService.run_experiment(db, exp.id)
    return _format_experiment(exp)

@router.get("/experiments")
def list_experiments(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    status_filter: Optional[str] = Query(None, alias="status"),
    db: Session = Depends(get_db)
):
    """
    List executed benchmark experiments with pagination and status filtering.
    """
    items, total = BenchmarkRepository.list_experiments(db, skip=skip, limit=limit, status=status_filter)
    return {
        "total": total,
        "skip": skip,
        "limit": limit,
        "items": [_format_experiment(e) for e in items]
    }

@router.get("/experiments/{experiment_id}", response_model=BenchmarkExperimentResponse)
def get_experiment(experiment_id: str, db: Session = Depends(get_db)):
    """
    Retrieve experiment details, execution status, results, and side-by-side baseline comparisons.
    """
    exp = BenchmarkRepository.get_experiment(db, experiment_id)
    if not exp:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Experiment '{experiment_id}' not found.")
    return _format_experiment(exp)

@router.post("/experiments/{experiment_id}/run", response_model=BenchmarkExperimentResponse)
def run_experiment(experiment_id: str, db: Session = Depends(get_db)):
    """
    Trigger execution of a pending or previously created benchmark experiment.
    """
    exp = BenchmarkRepository.get_experiment(db, experiment_id)
    if not exp:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Experiment '{experiment_id}' not found.")
    completed_exp = BenchmarkExperimentService.run_experiment(db, experiment_id)
    return _format_experiment(completed_exp)

@router.post("/experiments/{experiment_id}/cancel")
def cancel_experiment(experiment_id: str, db: Session = Depends(get_db)):
    """
    Cancel an ongoing benchmark experiment run cleanly.
    """
    exp = BenchmarkRepository.get_experiment(db, experiment_id)
    if not exp:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Experiment '{experiment_id}' not found.")
    cancelled = BenchmarkExperimentService.cancel_experiment(db, experiment_id)
    return {
        "id": cancelled.id,
        "status": cancelled.status,
        "progress": cancelled.progress,
        "message": "Experiment run cancelled successfully."
    }

@router.get("/experiments/{experiment_id}/progress")
def get_experiment_progress(experiment_id: str, db: Session = Depends(get_db)):
    """
    Get live progress percentage, status, and current overall resilience score for an experiment.
    """
    exp = BenchmarkRepository.get_experiment(db, experiment_id)
    if not exp:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Experiment '{experiment_id}' not found.")
    return {
        "id": exp.id,
        "status": exp.status,
        "progress": exp.progress,
        "overall_resilience_score": exp.overall_resilience_score,
        "started_at": exp.started_at,
        "completed_at": exp.completed_at
    }

@router.get("/experiments/{experiment_id}/results")
def get_experiment_results(
    experiment_id: str,
    module_name: Optional[str] = Query(None, description="Optional module filter: module_2, module_3, etc."),
    db: Session = Depends(get_db)
):
    """
    Retrieve granular metric results recorded during the experiment.
    """
    exp = BenchmarkRepository.get_experiment(db, experiment_id)
    if not exp:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Experiment '{experiment_id}' not found.")
    results = BenchmarkRepository.get_results_for_experiment(db, experiment_id, module_name=module_name)
    return [
        {
            "id": r.id,
            "experiment_id": r.experiment_id,
            "scenario_id": r.scenario_id,
            "module_name": r.module_name,
            "method_name": r.method_name,
            "metric_name": r.metric_name,
            "metric_value": r.metric_value,
            "metric_unit": r.metric_unit,
            "sample_count": r.sample_count,
            "created_at": r.created_at
        }
        for r in results
    ]


# 7. Experiment Comparison & Summary
@router.post("/compare", response_model=BenchmarkCompareResponse)
def compare_experiments(req: BenchmarkCompareRequest, db: Session = Depends(get_db)):
    """
    Compare multiple benchmark experiment runs side-by-side.
    """
    experiments = []
    resilience_scores = {}
    best_id = None
    highest_score = -1.0

    for exp_id in req.experiment_ids:
        exp = BenchmarkRepository.get_experiment(db, exp_id)
        if exp:
            score = exp.overall_resilience_score or 0.0
            resilience_scores[exp.name] = score
            experiments.append({
                "id": exp.id,
                "name": exp.name,
                "status": exp.status,
                "overall_resilience_score": score,
                "summary": json.loads(exp.summary_json) if exp.summary_json else {},
                "created_at": exp.created_at
            })
            if score > highest_score:
                highest_score = score
                best_id = exp.id

    verdict = f"Experiment '{best_id}' achieved the highest overall resilience score ({highest_score:.1f}/100.0)." if best_id else "No completed experiments compared."

    return BenchmarkCompareResponse(
        experiments=experiments,
        best_experiment_id=best_id,
        resilience_score_comparison=resilience_scores,
        summary_verdict=verdict
    )

@router.get("/summary", response_model=BenchmarkEvaluationSummaryResponse)
def get_benchmark_summary(db: Session = Depends(get_db)):
    """
    High-level aggregate evaluation dashboard metrics across all historical benchmark experiments.
    """
    all_exps, total_count = BenchmarkRepository.list_experiments(db, limit=1000)
    datasets, ds_count = BenchmarkRepository.list_datasets(db, limit=1000)

    completed = [e for e in all_exps if e.status == "COMPLETED"]
    failed = [e for e in all_exps if e.status == "FAILED"]

    avg_score = 0.0
    if completed:
        scores = [e.overall_resilience_score for e in completed if e.overall_resilience_score is not None]
        if scores:
            avg_score = round(sum(scores) / len(scores), 2)

    latest_exp = _format_experiment(all_exps[0]) if all_exps else None

    return BenchmarkEvaluationSummaryResponse(
        total_experiments=total_count,
        completed_experiments=len(completed),
        failed_experiments=len(failed),
        available_datasets=ds_count,
        evaluated_modules_count=7,
        average_resilience_score=avg_score,
        latest_experiment=latest_exp
    )


# 8. Reports & Exports
@router.get("/reports/{experiment_id}")
def get_or_generate_report(
    experiment_id: str,
    format: str = Query("markdown", pattern="^(markdown|json)$"),
    db: Session = Depends(get_db)
):
    """
    Retrieve or generate a full Markdown or JSON benchmark evaluation report.
    """
    report = BenchmarkRepository.get_report_for_experiment(db, experiment_id, report_format=format)
    if not report:
        report = BenchmarkReportService.generate_report(db, experiment_id, report_format=format)

    if format == "markdown":
        return PlainTextResponse(content=report.content, media_type="text/markdown")
    return json.loads(report.content)

@router.get("/export/{experiment_id}/csv")
def export_experiment_csv(experiment_id: str, db: Session = Depends(get_db)):
    """
    Export benchmark experiment results and comparisons as downloadable CSV.
    """
    try:
        csv_data = BenchmarkExportService.export_csv(db, experiment_id)
        return Response(
            content=csv_data,
            media_type="text/csv",
            headers={"Content-Disposition": f"attachment; filename=benchmark_experiment_{experiment_id}.csv"}
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

@router.get("/export/{experiment_id}/json")
def export_experiment_json(experiment_id: str, db: Session = Depends(get_db)):
    """
    Export complete benchmark experiment payload as structured JSON.
    """
    try:
        data = BenchmarkExportService.export_json(db, experiment_id)
        return data
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
