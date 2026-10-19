import pytest
from sqlalchemy.orm import Session
from app.database.benchmark_repository import BenchmarkRepository
from app.schemas.benchmark_schemas import BenchmarkExperimentCreateRequest
from app.services.benchmark_dataset_service import BenchmarkDatasetService
from app.services.benchmark_experiment_service import BenchmarkExperimentService

def test_create_and_run_experiment(db_session: Session):
    # Ensure dataset exists
    ds = BenchmarkDatasetService.generate_canonical_dataset(db_session)

    req = BenchmarkExperimentCreateRequest(
        name="Unit Test Resilience Experiment",
        dataset_id=ds.id,
        selected_modules=["module_2", "module_3", "module_4"],
        random_seed=42
    )

    exp = BenchmarkExperimentService.create_experiment(db_session, req)
    assert exp.id is not None
    assert exp.status == "CREATED"

    # Run experiment
    completed = BenchmarkExperimentService.run_experiment(db_session, exp.id)
    assert completed.status == "COMPLETED"
    assert completed.progress == 100.0
    assert completed.overall_resilience_score is not None
    assert completed.overall_resilience_score > 0.0

    # Verify results recorded
    results = BenchmarkRepository.get_results_for_experiment(db_session, exp.id)
    assert len(results) > 0

    # Verify comparisons recorded
    comparisons = BenchmarkRepository.get_comparisons_for_experiment(db_session, exp.id)
    assert len(comparisons) > 0

def test_cancel_experiment(db_session: Session):
    req = BenchmarkExperimentCreateRequest(
        name="Cancellation Test Experiment",
        selected_modules=["module_2"]
    )
    exp = BenchmarkExperimentService.create_experiment(db_session, req)
    cancelled = BenchmarkExperimentService.cancel_experiment(db_session, exp.id)
    assert cancelled.status == "CANCELLED"
