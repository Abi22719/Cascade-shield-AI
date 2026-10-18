import pytest
from app.services.evaluation_service import EvaluationService

def test_benchmark_dataset_generation():
    """Verify labeled benchmark dataset has correct counts and ground truth labels."""
    dataset = EvaluationService.generate_labeled_benchmark_dataset(
        normal_count=100,
        anomaly_count=20,
        random_seed=42
    )
    assert len(dataset) == 120
    normals = [item for item in dataset if not item[1]]
    anomalies = [item for item in dataset if item[1]]
    assert len(normals) == 100
    assert len(anomalies) == 20

def test_metrics_calculation_formulas():
    """Verify confusion matrix and metrics formulas (Precision, Recall, F1, FPR, Accuracy)."""
    # 3 TP, 1 FP, 4 TN, 2 FN
    y_true = [True, True, True, False, False, False, False, True, True]
    y_pred = [True, True, True, True,  False, False, False, False, False]
    # TP: 3, FP: 1, TN: 3, FN: 2
    metrics = EvaluationService._calculate_metrics(y_true, y_pred)
    assert metrics.true_positives == 3
    assert metrics.false_positives == 1
    assert metrics.true_negatives == 3
    assert metrics.false_negatives == 2
    # Precision = 3 / (3 + 1) = 0.75
    assert metrics.precision == 0.75
    # Recall = 3 / (3 + 2) = 0.6
    assert metrics.recall == 0.6
    # F1 = 2 * (0.75 * 0.6) / (0.75 + 0.6) = 2 * 0.45 / 1.35 = 0.6667
    assert 0.66 <= metrics.f1_score <= 0.67

def test_zero_division_safety():
    """Verify handling when there are 0 positive predictions or 0 anomalies."""
    y_true = [False, False, False]
    y_pred = [False, False, False]
    metrics = EvaluationService._calculate_metrics(y_true, y_pred)
    assert metrics.precision == 0.0
    assert metrics.recall == 0.0
    assert metrics.f1_score == 0.0
    assert metrics.accuracy == 1.0

def test_benchmark_evaluation_comparison():
    """Verify full benchmark evaluation comparing Threshold, Isolation Forest, and Combined."""
    comparison = EvaluationService.run_benchmark_evaluation()
    assert comparison.dataset_size == 200
    assert comparison.anomalous_samples_count == 40
    assert comparison.normal_samples_count == 160

    # Verify all detectors produced valid bounded metrics (0.0 to 1.0)
    for model_metrics in [
        comparison.threshold_detector,
        comparison.isolation_forest,
        comparison.combined_detector
    ]:
        assert 0.0 <= model_metrics.precision <= 1.0
        assert 0.0 <= model_metrics.recall <= 1.0
        assert 0.0 <= model_metrics.f1_score <= 1.0
        assert 0.0 <= model_metrics.accuracy <= 1.0
        assert model_metrics.true_positives + model_metrics.false_negatives == 40
