from typing import List, Dict, Any, Optional, Tuple
import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest
from app.config import settings
from app.schemas.metric_schema import MetricPoint

FEATURE_COLUMNS = ["cpu_usage", "memory_usage", "latency_ms", "error_rate", "request_volume"]

class IsolationForestDetector:
    def __init__(
        self,
        contamination: Optional[float] = None,
        random_state: Optional[int] = None,
        n_estimators: int = 100
    ):
        self.contamination = contamination if contamination is not None else settings.DEFAULT_CONTAMINATION
        self.random_state = random_state if random_state is not None else settings.DEFAULT_RANDOM_STATE
        self.n_estimators = n_estimators
        self.model: Optional[IsolationForest] = None
        self.is_fitted = False
        self.training_sample_count = 0
        self.feature_means = np.zeros(len(FEATURE_COLUMNS))
        self.feature_stds = np.ones(len(FEATURE_COLUMNS))

    def _extract_feature_matrix(self, metrics: List[MetricPoint]) -> np.ndarray:
        """
        Converts MetricPoint objects into a 2D NumPy feature array.
        Preprocesses and handles missing or non-finite numbers safely.
        """
        rows = []
        for m in metrics:
            row = [
                m.cpu_usage,
                m.memory_usage,
                m.latency_ms,
                m.error_rate,
                float(m.request_volume)
            ]
            rows.append(row)

        X = np.array(rows, dtype=np.float64)
        # Clean any possible NaNs or Infs
        X = np.nan_to_num(X, nan=0.0, posinf=1e6, neginf=0.0)
        return X

    def fit(self, reference_metrics: List[MetricPoint]) -> bool:
        """
        Fits the Isolation Forest on a reference dataset.
        Prevents fitting on fewer than 2 observations.
        If reference metrics are insufficient, augments with baseline cluster.
        """
        if not reference_metrics or len(reference_metrics) < 2:
            # Insufficient reference data: generate baseline cluster
            X = self._generate_baseline_reference_data(count=80)
        else:
            X = self._extract_feature_matrix(reference_metrics)
            if len(X) < 10:
                # Augment sparse data with baseline variations
                baseline = self._generate_baseline_reference_data(count=60)
                X = np.vstack([X, baseline])

        self.feature_means = np.mean(X, axis=0)
        self.feature_stds = np.std(X, axis=0)
        self.feature_stds[self.feature_stds == 0] = 1.0

        self.model = IsolationForest(
            contamination=self.contamination,
            random_state=self.random_state,
            n_estimators=self.n_estimators
        )
        self.model.fit(X)
        self.is_fitted = True
        self.training_sample_count = len(X)
        return True

    def _generate_baseline_reference_data(self, count: int = 100) -> np.ndarray:
        """
        Synthesizes a reproducible normal operating baseline cluster
        to ensure model stability when cold-starting with no prior history.
        """
        rng = np.random.RandomState(self.random_state)
        # Normal ranges:
        # CPU: 20 - 45%
        # Memory: 30 - 55%
        # Latency: 20 - 70ms
        # Error Rate: 0.01 - 0.4%
        # Request Volume: 800 - 3500 req/s
        cpu = rng.normal(loc=32.0, scale=8.0, size=count).clip(5.0, 65.0)
        mem = rng.normal(loc=42.0, scale=10.0, size=count).clip(15.0, 70.0)
        lat = rng.normal(loc=45.0, scale=18.0, size=count).clip(5.0, 250.0)
        err = rng.normal(loc=0.15, scale=0.10, size=count).clip(0.0, 1.5)
        req = rng.normal(loc=2000, scale=600, size=count).clip(200, 6000)

        return np.column_stack([cpu, mem, lat, err, req])

    def detect_batch(
        self,
        metrics: List[MetricPoint]
    ) -> List[Dict[str, Any]]:
        """
        Evaluates a batch of metric points using the Isolation Forest.
        Returns prediction details for each metric point.
        """
        if not metrics:
            return []

        if not self.is_fitted or self.model is None:
            # Auto-fit with baseline prior to first detection
            self.fit([])

        X = self._extract_feature_matrix(metrics)
        
        # Isolation Forest:
        # decision_function: positive for inliers, negative for outliers.
        # anomaly_score = -decision_function (higher score = more anomalous)
        decision_scores = self.model.decision_function(X)
        predictions = self.model.predict(X)  # -1 for anomaly, 1 for inlier

        results = []
        for i, m in enumerate(metrics):
            is_anomaly = bool(predictions[i] == -1)
            raw_score = float(-decision_scores[i])  # higher = more anomalous
            
            # Identify most contributing deviating feature
            z_scores = np.abs((X[i] - self.feature_means) / self.feature_stds)
            max_dev_idx = int(np.argmax(z_scores))
            top_deviating_feature = FEATURE_COLUMNS[max_dev_idx]
            top_feature_value = float(X[i][max_dev_idx])

            evidence = (
                f"Multivariate pattern anomaly detected via Isolation Forest (score: {raw_score:.3f}). "
                f"Primary deviating metric: {top_deviating_feature} = {top_feature_value:.2f}."
                if is_anomaly else
                f"Metric cluster aligned with normal operating multidimensional baseline (score: {raw_score:.3f})."
            )

            results.append({
                "service_id": m.service_id,
                "service_name": m.service_name or m.service_id,
                "is_anomaly": is_anomaly,
                "anomaly_score": round(raw_score, 4),
                "top_deviating_feature": top_deviating_feature if is_anomaly else None,
                "top_feature_value": top_feature_value if is_anomaly else None,
                "evidence_summary": evidence,
                "timestamp": m.timestamp,
                "raw_metrics": {
                    "cpu_usage": m.cpu_usage,
                    "memory_usage": m.memory_usage,
                    "latency_ms": m.latency_ms,
                    "error_rate": m.error_rate,
                    "request_volume": m.request_volume
                }
            })

        return results

    def detect_single(self, metric: MetricPoint) -> Dict[str, Any]:
        """
        Evaluates a single metric observation.
        """
        return self.detect_batch([metric])[0]

# Shared singleton instance
anomaly_detector = IsolationForestDetector()
