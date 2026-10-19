import pytest
from sqlalchemy.orm import Session
from app.database.benchmark_repository import BenchmarkRepository
from app.services.benchmark_dataset_service import BenchmarkDatasetService, CANONICAL_BENCHMARK_SCENARIOS
from app.schemas.benchmark_schemas import BenchmarkDatasetGenerateRequest

def test_canonical_scenarios_count():
    assert len(CANONICAL_BENCHMARK_SCENARIOS) == 10
    for scn in CANONICAL_BENCHMARK_SCENARIOS:
        assert "id" in scn
        assert "name" in scn
        assert "scenario_type" in scn
        assert "input_config" in scn
        assert "ground_truth" in scn
        # Verify ground truth fields
        gt = scn["ground_truth"]
        assert "expected_anomalies" in gt
        assert "expected_affected_services" in gt
        assert "expected_root_cause" in gt
        assert "expected_validation_outcome" in gt

def test_generate_canonical_dataset(db_session: Session):
    req = BenchmarkDatasetGenerateRequest(
        name="Test Benchmark Suite",
        description="Dataset for testing",
        seed=100
    )
    dataset = BenchmarkDatasetService.generate_canonical_dataset(db_session, req)
    assert dataset.id is not None
    assert dataset.name == "Test Benchmark Suite"
    assert dataset.scenario_count == 10

    # Verify scenarios stored in DB
    scenarios = BenchmarkRepository.list_scenarios_for_dataset(db_session, dataset.id)
    assert len(scenarios) == 10
    first_scn = scenarios[0]
    assert first_scn.dataset_id == dataset.id
    assert first_scn.scenario_type is not None

def test_dataset_repository_crud(db_session: Session):
    datasets, total = BenchmarkRepository.list_datasets(db_session)
    assert total >= 0

    retrieved = BenchmarkRepository.get_dataset(db_session, "non-existent")
    assert retrieved is None
