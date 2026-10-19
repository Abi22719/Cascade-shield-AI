import csv
import io
import json
from typing import Dict, Any, List
from sqlalchemy.orm import Session
from app.database.benchmark_repository import BenchmarkRepository

class BenchmarkExportService:
    """
    Exports benchmark experiment results, metrics, and comparisons to CSV, JSON, and Markdown formats.
    """

    @classmethod
    def export_json(cls, db: Session, experiment_id: str) -> Dict[str, Any]:
        exp = BenchmarkRepository.get_experiment(db, experiment_id)
        if not exp:
            raise ValueError(f"Experiment '{experiment_id}' not found.")

        results = BenchmarkRepository.get_results_for_experiment(db, experiment_id)
        comparisons = BenchmarkRepository.get_comparisons_for_experiment(db, experiment_id)

        return {
            "experiment_id": exp.id,
            "name": exp.name,
            "description": exp.description,
            "dataset_id": exp.dataset_id,
            "random_seed": exp.random_seed,
            "repetitions": exp.repetitions,
            "status": exp.status,
            "progress": exp.progress,
            "overall_resilience_score": exp.overall_resilience_score,
            "summary": json.loads(exp.summary_json) if exp.summary_json else {},
            "started_at": exp.started_at.isoformat() if exp.started_at else None,
            "completed_at": exp.completed_at.isoformat() if exp.completed_at else None,
            "created_at": exp.created_at.isoformat(),
            "results": [
                {
                    "module_name": r.module_name,
                    "method_name": r.method_name,
                    "metric_name": r.metric_name,
                    "metric_value": r.metric_value,
                    "metric_unit": r.metric_unit,
                    "scenario_id": r.scenario_id
                }
                for r in results
            ],
            "comparisons": [
                {
                    "comparison_name": c.comparison_name,
                    "baseline_name": c.baseline_name,
                    "candidate_name": c.candidate_name,
                    "metrics": json.loads(c.comparison_metrics_json) if c.comparison_metrics_json else {},
                    "interpretation": c.interpretation
                }
                for c in comparisons
            ]
        }

    @classmethod
    def export_csv(cls, db: Session, experiment_id: str) -> str:
        data = cls.export_json(db, experiment_id)
        output = io.StringIO()
        writer = csv.writer(output)

        # Header metadata
        writer.writerow(["Experiment ID", data["experiment_id"]])
        writer.writerow(["Name", data["name"]])
        writer.writerow(["Status", data["status"]])
        writer.writerow(["Overall Resilience Score", data["overall_resilience_score"] or "N/A"])
        writer.writerow(["Seed", data["random_seed"]])
        writer.writerow([])

        # Results table
        writer.writerow(["Module", "Method", "Metric Name", "Metric Value", "Unit", "Scenario ID"])
        for r in data["results"]:
            writer.writerow([
                r["module_name"],
                r["method_name"],
                r["metric_name"],
                r["metric_value"],
                r["metric_unit"],
                r["scenario_id"] or "AGGREGATE"
            ])

        return output.getvalue()
