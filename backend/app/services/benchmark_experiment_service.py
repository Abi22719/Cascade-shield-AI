import json
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session

from app.database.benchmark_repository import BenchmarkRepository
from app.models.benchmark_models import BenchmarkExperimentModel, BenchmarkDatasetModel, BenchmarkScenarioModel
from app.schemas.benchmark_schemas import BenchmarkExperimentCreateRequest
from app.services.benchmark_baseline_service import BenchmarkBaselineService
from app.services.benchmark_comparison_service import BenchmarkComparisonService
from app.services.benchmark_dataset_service import BenchmarkDatasetService
from app.services.benchmark_metrics_service import BenchmarkMetricsService

class BenchmarkExperimentService:
    """
    Orchestrates automated resilience benchmarking experiments across Modules 1 to 8.
    Evaluates candidate and baseline methods against canonical synthetic failure datasets,
    records detailed results and side-by-side comparisons, and computes overall resilience scores.
    """

    @classmethod
    def create_experiment(cls, db: Session, req: BenchmarkExperimentCreateRequest) -> BenchmarkExperimentModel:
        # Resolve dataset if not provided
        dataset_id = req.dataset_id
        if not dataset_id:
            datasets, count = BenchmarkRepository.list_datasets(db, limit=1)
            if datasets:
                dataset_id = datasets[0].id
            else:
                default_ds = BenchmarkDatasetService.generate_canonical_dataset(db)
                dataset_id = default_ds.id

        data = {
            "name": req.name,
            "description": req.description,
            "dataset_id": dataset_id,
            "selected_modules": req.selected_modules,
            "selected_methods": req.selected_methods,
            "configuration": req.configuration,
            "random_seed": req.random_seed,
            "repetitions": req.repetitions,
            "status": "CREATED"
        }
        return BenchmarkRepository.create_experiment(db, data)

    @classmethod
    def run_experiment(cls, db: Session, experiment_id: str) -> Optional[BenchmarkExperimentModel]:
        exp = BenchmarkRepository.get_experiment(db, experiment_id)
        if not exp:
            return None

        # Resolve dataset
        dataset_id = exp.dataset_id
        if not dataset_id:
            datasets, count = BenchmarkRepository.list_datasets(db, limit=1)
            if datasets:
                dataset_id = datasets[0].id
                exp.dataset_id = dataset_id
            else:
                default_ds = BenchmarkDatasetService.generate_canonical_dataset(db)
                dataset_id = default_ds.id
                exp.dataset_id = dataset_id

        scenarios = BenchmarkRepository.list_scenarios_for_dataset(db, dataset_id)
        if not scenarios:
            # Re-generate canonical dataset scenarios if dataset was empty
            BenchmarkDatasetService.generate_canonical_dataset(db)
            scenarios = BenchmarkRepository.list_scenarios_for_dataset(db, dataset_id)

        # Mark as RUNNING
        BenchmarkRepository.update_experiment_status(db, experiment_id, status="RUNNING", progress=5.0)

        selected_modules = json.loads(exp.selected_modules_json) if exp.selected_modules_json else []
        if not selected_modules:
            selected_modules = ["module_2", "module_3", "module_4", "module_5", "module_6", "module_7", "module_8"]

        supported_baselines = BenchmarkBaselineService.get_supported_baselines()
        total_steps = len(scenarios) * len(selected_modules)
        completed_steps = 0

        # Accumulator for module aggregate scores
        module_aggregates: Dict[str, List[float]] = {
            "detection": [],
            "prediction": [],
            "rca": [],
            "diagnostic": [],
            "simulation": [],
            "recovery": [],
            "validation": []
        }

        try:
            for scn in scenarios:
                # Check for cancellation
                current_exp = BenchmarkRepository.get_experiment(db, experiment_id)
                if current_exp and current_exp.status == "CANCELLED":
                    return current_exp

                input_config = json.loads(scn.input_json) if scn.input_json else {}
                ground_truth = json.loads(scn.ground_truth_json) if scn.ground_truth_json else {}

                for mod in selected_modules:
                    if mod not in supported_baselines:
                        completed_steps += 1
                        continue

                    mod_info = supported_baselines[mod]
                    cand_method = mod_info["candidate"]
                    baseline_methods = mod_info["baselines"]

                    # 1. Evaluate candidate method
                    cand_metrics = cls._evaluate_method_for_module(mod, cand_method, input_config, ground_truth)
                    for k, v in cand_metrics.items():
                        BenchmarkRepository.record_result(db, {
                            "experiment_id": experiment_id,
                            "scenario_id": scn.id,
                            "module_name": mod,
                            "method_name": cand_method,
                            "metric_name": k,
                            "metric_value": v,
                            "metric_unit": "ms" if "ms" in k or "time" in k or "delay" in k else "ratio",
                            "sample_count": 1
                        })

                    # Track primary metric for resilience score
                    cls._accumulate_module_score(mod, cand_metrics, module_aggregates)

                    # 2. Evaluate each baseline and record comparison
                    for base_method in baseline_methods:
                        base_metrics = cls._evaluate_method_for_module(mod, base_method, input_config, ground_truth)
                        for k, v in base_metrics.items():
                            BenchmarkRepository.record_result(db, {
                                "experiment_id": experiment_id,
                                "scenario_id": scn.id,
                                "module_name": mod,
                                "method_name": base_method,
                                "metric_name": k,
                                "metric_value": v,
                                "metric_unit": "ms" if "ms" in k or "time" in k or "delay" in k else "ratio",
                                "sample_count": 1
                            })

                        # Compare candidate vs baseline
                        comp = BenchmarkComparisonService.compare_module_methods(
                            module_name=mod,
                            baseline_name=base_method,
                            baseline_metrics=base_metrics,
                            candidate_name=cand_method,
                            candidate_metrics=cand_metrics
                        )
                        BenchmarkRepository.record_comparison(db, {
                            "experiment_id": experiment_id,
                            "comparison_name": comp["comparison_name"],
                            "baseline_name": base_method,
                            "candidate_name": cand_method,
                            "comparison_metrics": comp["comparison_metrics"],
                            "interpretation": comp["interpretation"]
                        })

                    completed_steps += 1
                    pct = round(5.0 + (completed_steps / max(1, total_steps)) * 90.0, 1)
                    exp.progress = min(95.0, pct)
                    db.flush()

            # Compute module average scores (0-100)
            module_scores: Dict[str, float] = {}
            for mod_key, vals in module_aggregates.items():
                if vals:
                    module_scores[mod_key] = round((sum(vals) / len(vals)) * 100.0, 2)

            # Overall Resilience Score
            config_dict = json.loads(exp.configuration_json) if exp.configuration_json else {}
            weights = config_dict.get("component_weights")
            overall_score, breakdown = BenchmarkMetricsService.compute_overall_resilience_score(module_scores, weights)

            summary = {
                "overall_resilience_score": overall_score,
                "module_scores": module_scores,
                "score_breakdown": breakdown,
                "scenarios_evaluated_count": len(scenarios),
                "modules_evaluated_count": len(selected_modules),
                "total_steps": total_steps
            }

            BenchmarkRepository.update_experiment_status(
                db=db,
                experiment_id=experiment_id,
                status="COMPLETED",
                progress=100.0,
                summary=summary,
                overall_score=overall_score
            )

        except Exception as e:
            BenchmarkRepository.update_experiment_status(
                db=db,
                experiment_id=experiment_id,
                status="FAILED",
                progress=100.0,
                error_message=str(e)
            )
            raise e

        return BenchmarkRepository.get_experiment(db, experiment_id)

    @classmethod
    def cancel_experiment(cls, db: Session, experiment_id: str) -> Optional[BenchmarkExperimentModel]:
        return BenchmarkRepository.update_experiment_status(
            db, experiment_id, status="CANCELLED", progress=100.0
        )

    @classmethod
    def _evaluate_method_for_module(
        cls,
        module_name: str,
        method_name: str,
        input_config: Dict[str, Any],
        ground_truth: Dict[str, Any]
    ) -> Dict[str, float]:
        if module_name == "module_2":
            return BenchmarkBaselineService.evaluate_module_2(ground_truth, method_name)
        elif module_name == "module_3":
            return BenchmarkBaselineService.evaluate_module_3(ground_truth, method_name)
        elif module_name == "module_4":
            return BenchmarkBaselineService.evaluate_module_4(ground_truth, method_name)
        elif module_name == "module_5":
            return BenchmarkBaselineService.evaluate_module_5(ground_truth, method_name)
        elif module_name == "module_6":
            return BenchmarkBaselineService.evaluate_module_6(input_config, ground_truth, method_name)
        elif module_name == "module_7":
            return BenchmarkBaselineService.evaluate_module_7(ground_truth, method_name)
        elif module_name == "module_8":
            return BenchmarkBaselineService.evaluate_module_8(ground_truth, method_name)
        return {}

    @classmethod
    def _accumulate_module_score(
        cls,
        module_name: str,
        metrics: Dict[str, float],
        aggregates: Dict[str, List[float]]
    ) -> None:
        if module_name == "module_2" and "f1_score" in metrics:
            aggregates["detection"].append(metrics["f1_score"])
        elif module_name == "module_3" and "cascade_f1" in metrics:
            aggregates["prediction"].append(metrics["cascade_f1"])
        elif module_name == "module_4" and "top1_accuracy" in metrics:
            aggregates["rca"].append(metrics["top1_accuracy"])
        elif module_name == "module_5" and "useful_ratio" in metrics:
            aggregates["diagnostic"].append(metrics["useful_ratio"])
        elif module_name == "module_6" and "reproducibility_rate" in metrics:
            aggregates["simulation"].append(metrics["reproducibility_rate"])
        elif module_name == "module_7" and "recovery_success" in metrics:
            aggregates["recovery"].append(metrics["recovery_success"])
        elif module_name == "module_8" and "validation_accuracy" in metrics:
            aggregates["validation"].append(metrics["validation_accuracy"])
