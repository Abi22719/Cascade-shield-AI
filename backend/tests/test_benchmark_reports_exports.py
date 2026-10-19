import json
import pytest
from sqlalchemy.orm import Session
from app.schemas.benchmark_schemas import BenchmarkExperimentCreateRequest
from app.services.benchmark_dataset_service import BenchmarkDatasetService
from app.services.benchmark_experiment_service import BenchmarkExperimentService
from app.services.benchmark_report_service import BenchmarkReportService
from app.services.benchmark_export_service import BenchmarkExportService

def test_generate_reports_and_exports(db_session: Session):
    ds = BenchmarkDatasetService.generate_canonical_dataset(db_session)
    req = BenchmarkExperimentCreateRequest(
        name="Reporting Test Run",
        dataset_id=ds.id,
        selected_modules=["module_2", "module_8"]
    )
    exp = BenchmarkExperimentService.create_experiment(db_session, req)
    BenchmarkExperimentService.run_experiment(db_session, exp.id)

    # 1. Markdown report
    md_report = BenchmarkReportService.generate_report(db_session, exp.id, report_format="markdown")
    assert md_report.id is not None
    assert "# 🛡️ CascadeShield AI Resilience Benchmark Report" in md_report.content
    assert "Overall Resilience Score" in md_report.content

    # 2. JSON report
    json_report = BenchmarkReportService.generate_report(db_session, exp.id, report_format="json")
    parsed = json.loads(json_report.content)
    assert parsed["experiment_id"] == exp.id

    # 3. Export JSON
    exported_json = BenchmarkExportService.export_json(db_session, exp.id)
    assert exported_json["experiment_id"] == exp.id
    assert len(exported_json["results"]) > 0

    # 4. Export CSV
    exported_csv = BenchmarkExportService.export_csv(db_session, exp.id)
    assert "Experiment ID" in exported_csv
    assert "Module,Method,Metric Name" in exported_csv
