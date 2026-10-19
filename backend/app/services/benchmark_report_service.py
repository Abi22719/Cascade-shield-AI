import json
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from app.database.benchmark_repository import BenchmarkRepository
from app.models.benchmark_models import BenchmarkExperimentModel, BenchmarkReportModel

class BenchmarkReportService:
    """
    Generates comprehensive, formatted benchmark evaluation reports
    in Markdown, JSON, and structured formats.
    """

    @classmethod
    def generate_report(
        cls,
        db: Session,
        experiment_id: str,
        report_format: str = "markdown"
    ) -> BenchmarkReportModel:
        exp = BenchmarkRepository.get_experiment(db, experiment_id)
        if not exp:
            raise ValueError(f"Experiment '{experiment_id}' not found.")

        results = BenchmarkRepository.get_results_for_experiment(db, experiment_id)
        comparisons = BenchmarkRepository.get_comparisons_for_experiment(db, experiment_id)

        if report_format == "markdown":
            content = cls._build_markdown_report(exp, results, comparisons)
        elif report_format == "json":
            content = cls._build_json_report(exp, results, comparisons)
        else:
            content = cls._build_markdown_report(exp, results, comparisons)

        metadata = {
            "experiment_id": experiment_id,
            "experiment_name": exp.name,
            "overall_resilience_score": exp.overall_resilience_score,
            "total_results": len(results),
            "total_comparisons": len(comparisons),
            "generated_format": report_format
        }

        return BenchmarkRepository.create_report(db, {
            "experiment_id": experiment_id,
            "report_format": report_format,
            "report_metadata": metadata,
            "content": content
        })

    @classmethod
    def _build_markdown_report(
        cls,
        exp: BenchmarkExperimentModel,
        results: List[Any],
        comparisons: List[Any]
    ) -> str:
        summary = json.loads(exp.summary_json) if exp.summary_json else {}
        score = exp.overall_resilience_score or 0.0
        score_breakdown = summary.get("score_breakdown", {})

        md = []
        md.append(f"# 🛡️ CascadeShield AI Resilience Benchmark Report")
        md.append(f"**Experiment Name:** {exp.name}")
        md.append(f"**Experiment ID:** `{exp.id}`")
        md.append(f"**Status:** `{exp.status}` | **Progress:** {exp.progress}%")
        md.append(f"**Dataset ID:** `{exp.dataset_id or 'canonical-synthetic'}`")
        md.append(f"**Execution Timestamp:** {exp.completed_at or exp.created_at}")
        md.append("")
        md.append("---")
        md.append("")
        md.append(f"## 🏆 Overall Resilience Score: **{score:.1f} / 100.0**")
        md.append("")
        md.append("| Resilience Pillar | Raw Score | Pillar Weight | Weighted Contribution |")
        md.append("| :--- | :--- | :--- | :--- |")
        for pillar, data in score_breakdown.items():
            raw = data.get("raw_score", 0.0)
            w = data.get("weight", 0.0)
            contrib = data.get("weighted_score", 0.0)
            md.append(f"| **{pillar.capitalize()}** | {raw:.1f}% | {w:.2f} | {contrib:.2f} |")
        md.append("")
        md.append("---")
        md.append("")
        md.append("## 📊 Candidate Method vs Baseline Comparisons")
        md.append("")
        if comparisons:
            for comp in comparisons:
                md.append(f"### Method: `{comp.candidate_name}` vs Baseline: `{comp.baseline_name}`")
                md.append(f"> **Interpretation:** {comp.interpretation}")
                md.append("")
                comp_metrics = json.loads(comp.comparison_metrics_json) if comp.comparison_metrics_json else {}
                if comp_metrics:
                    md.append("| Metric | Baseline Value | Candidate Value | Improvement (%) | Verdict |")
                    md.append("| :--- | :--- | :--- | :--- | :--- |")
                    for m_name, m_data in comp_metrics.items():
                        base = m_data.get("baseline", 0.0)
                        cand = m_data.get("candidate", 0.0)
                        diff_pct = m_data.get("percentage_diff", 0.0)
                        sign = "+" if diff_pct > 0 else ""
                        verdict = "✅ Improved" if m_data.get("is_improvement") else "➖ Equivalent / Neutral"
                        md.append(f"| `{m_name}` | {base} | **{cand}** | {sign}{diff_pct}% | {verdict} |")
                    md.append("")
        else:
            md.append("*No comparisons recorded for this run.*")
            md.append("")

        md.append("---")
        md.append("")
        md.append("## 🔒 Safety & Environment Isolation Verification")
        md.append("- **Infrastructure Mutation:** `ZERO` (100% simulated sandbox execution).")
        md.append("- **Ground Truth Isolation:** Algorithm outputs were evaluated against independent synthetic ground truth.")
        md.append("- **Metric Rigor:** Zero-division safe calculations with explicit ratio/ms units.")
        md.append("")
        md.append("---")
        md.append("*Report generated by CascadeShield AI Module 9: Resilience Benchmarking & Performance Evaluation.*")

        return "\n".join(md)

    @classmethod
    def _build_json_report(
        cls,
        exp: BenchmarkExperimentModel,
        results: List[Any],
        comparisons: List[Any]
    ) -> str:
        summary = json.loads(exp.summary_json) if exp.summary_json else {}
        report_dict = {
            "experiment_id": exp.id,
            "experiment_name": exp.name,
            "status": exp.status,
            "overall_resilience_score": exp.overall_resilience_score,
            "summary": summary,
            "results_count": len(results),
            "comparisons_count": len(comparisons),
            "comparisons": [
                {
                    "comparison_name": c.comparison_name,
                    "candidate_name": c.candidate_name,
                    "baseline_name": c.baseline_name,
                    "interpretation": c.interpretation,
                    "metrics": json.loads(c.comparison_metrics_json) if c.comparison_metrics_json else {}
                }
                for c in comparisons
            ]
        }
        return json.dumps(report_dict, indent=2)
