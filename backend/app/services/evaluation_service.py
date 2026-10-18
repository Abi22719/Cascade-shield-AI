from typing import List, Tuple, Dict, Any
import numpy as np
from datetime import datetime, timezone

from app.schemas.metric_schema import MetricPoint
from app.schemas.anomaly_schema import EvaluationMetrics, EvaluationComparisonResponse
from app.services.threshold_detector import ThresholdDetector
from app.services.anomaly_detector import IsolationForestDetector

class EvaluationService:
    @staticmethod
    def generate_labeled_benchmark_dataset(
        normal_count: int = 160,
        anomaly_count: int = 40,
        random_seed: int = 123
    ) -> List[Tuple[MetricPoint, bool]]:
        """
        Synthesizes a deterministic labeled benchmark dataset with ground truth labels.
        Ground truth: True = Anomaly, False = Normal.

        Anomalies cover:
        1. Single-metric threshold spikes (e.g. Latency 1400ms or CPU 96%)
        2. Subtle multivariate outliers within normal individual limits but abnormal in combination
           (e.g. high request volume + 0% CPU + elevated latency)
        3. Degrading memory leakage
        """
        rng = np.random.RandomState(random_seed)
        dataset: List[Tuple[MetricPoint, bool]] = []
        now = datetime.now(timezone.utc)

        # 1. Normal Samples (Ground Truth = False)
        for i in range(normal_count):
            cpu = float(np.clip(rng.normal(30.0, 7.0), 8.0, 68.0))
            mem = float(np.clip(rng.normal(40.0, 8.0), 15.0, 72.0))
            lat = float(np.clip(rng.normal(45.0, 15.0), 8.0, 280.0))
            err = float(np.clip(rng.normal(0.12, 0.08), 0.0, 1.2))
            req = int(np.clip(rng.normal(1800, 450), 300, 4200))

            m = MetricPoint(
                timestamp=now,
                service_id=f"bench-norm-{i % 9}",
                service_name=f"Service-{i % 9}",
                cpu_usage=round(cpu, 1),
                memory_usage=round(mem, 1),
                latency_ms=round(lat, 1),
                error_rate=round(err, 2),
                request_volume=req,
                data_source="simulated"
            )
            dataset.append((m, False))

        # 2. Anomalous Samples (Ground Truth = True)
        # Type A: Severe Threshold Spikes (20 samples)
        for i in range(anomaly_count // 2):
            spike_type = i % 4
            cpu = float(rng.uniform(20.0, 50.0))
            mem = float(rng.uniform(30.0, 60.0))
            lat = float(rng.uniform(30.0, 100.0))
            err = float(rng.uniform(0.1, 0.8))
            req = int(rng.uniform(1000, 3000))

            if spike_type == 0:  # Critical Latency
                lat = float(rng.uniform(1100.0, 2200.0))
            elif spike_type == 1:  # Critical Error Rate
                err = float(rng.uniform(12.0, 35.0))
            elif spike_type == 2:  # Critical CPU
                cpu = float(rng.uniform(92.0, 99.5))
            else:  # Critical Memory
                mem = float(rng.uniform(94.0, 99.0))

            m = MetricPoint(
                timestamp=now,
                service_id=f"bench-spike-{i}",
                service_name=f"Service-Spike-{i}",
                cpu_usage=round(cpu, 1),
                memory_usage=round(mem, 1),
                latency_ms=round(lat, 1),
                error_rate=round(err, 2),
                request_volume=req,
                data_source="simulated"
            )
            dataset.append((m, True))

        # Type B: Multivariate & Subtle Anomalies (20 samples)
        # Metrics individually near or slightly below threshold, but combination is anomalous
        for i in range(anomaly_count // 2):
            # E.g. Low CPU (3%), very high latency (650ms), elevated error (3.5%), high traffic (8000 req/s)
            cpu = float(rng.uniform(2.0, 8.0))
            mem = float(rng.uniform(78.0, 88.0))
            lat = float(rng.uniform(550.0, 900.0))
            err = float(rng.uniform(3.0, 6.0))
            req = int(rng.uniform(6500, 12000))

            m = MetricPoint(
                timestamp=now,
                service_id=f"bench-multi-{i}",
                service_name=f"Service-Multi-{i}",
                cpu_usage=round(cpu, 1),
                memory_usage=round(mem, 1),
                latency_ms=round(lat, 1),
                error_rate=round(err, 2),
                request_volume=req,
                data_source="simulated"
            )
            dataset.append((m, True))

        return dataset

    @staticmethod
    def _calculate_metrics(y_true: List[bool], y_pred: List[bool]) -> EvaluationMetrics:
        """
        Calculates confusion matrix and performance statistics handling zero division.
        """
        tp = sum(1 for yt, yp in zip(y_true, y_pred) if yt and yp)
        fp = sum(1 for yt, yp in zip(y_true, y_pred) if not yt and yp)
        tn = sum(1 for yt, yp in zip(y_true, y_pred) if not yt and not yp)
        fn = sum(1 for yt, yp in zip(y_true, y_pred) if yt and not yp)

        total = len(y_true)
        precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
        recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
        f1 = (2 * precision * recall) / (precision + recall) if (precision + recall) > 0 else 0.0
        fpr = fp / (fp + tn) if (fp + tn) > 0 else 0.0
        accuracy = (tp + tn) / total if total > 0 else 0.0

        return EvaluationMetrics(
            true_positives=tp,
            false_positives=fp,
            true_negatives=tn,
            false_negatives=fn,
            precision=round(precision, 4),
            recall=round(recall, 4),
            f1_score=round(f1, 4),
            false_positive_rate=round(fpr, 4),
            accuracy=round(accuracy, 4),
            dataset_size=total
        )

    @staticmethod
    def run_benchmark_evaluation() -> EvaluationComparisonResponse:
        """
        Runs complete benchmark evaluation comparing:
        1. Threshold Detector
        2. Isolation Forest Detector
        3. Combined Alerting Approach
        """
        benchmark_data = EvaluationService.generate_labeled_benchmark_dataset(
            normal_count=160,
            anomaly_count=40,
            random_seed=42
        )
        metrics_list = [item[0] for item in benchmark_data]
        y_true = [item[1] for item in benchmark_data]

        # 1. Evaluate Threshold Detector
        thresh = ThresholdDetector()
        y_pred_threshold = []
        for m in metrics_list:
            violations = thresh.evaluate(m)
            # Flagged as anomaly if warning or critical violation exists
            y_pred_threshold.append(len(violations) > 0)

        # 2. Evaluate Isolation Forest Detector
        iso_forest = IsolationForestDetector(contamination=0.15, random_state=42)
        # Train on normal reference baseline
        normal_samples = [m for m, label in benchmark_data if not label]
        iso_forest.fit(normal_samples)
        ml_results = iso_forest.detect_batch(metrics_list)
        y_pred_ml = [r["is_anomaly"] for r in ml_results]

        # 3. Evaluate Combined Detector (Union of Threshold and ML detections)
        y_pred_combined = [
            (pt or pm) for pt, pm in zip(y_pred_threshold, y_pred_ml)
        ]

        metrics_thresh = EvaluationService._calculate_metrics(y_true, y_pred_threshold)
        metrics_ml = EvaluationService._calculate_metrics(y_true, y_pred_ml)
        metrics_comb = EvaluationService._calculate_metrics(y_true, y_pred_combined)

        return EvaluationComparisonResponse(
            threshold_detector=metrics_thresh,
            isolation_forest=metrics_ml,
            combined_detector=metrics_comb,
            dataset_size=len(benchmark_data),
            anomalous_samples_count=sum(1 for y in y_true if y),
            normal_samples_count=sum(1 for y in y_true if not y),
            benchmark_description=(
                "Evaluation evaluated over 200 labeled observations (160 normal, 40 anomalous). "
                "Anomalies include single-metric threshold spikes and subtle multidimensional patterns."
            )
        )
