from datetime import datetime, timezone
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session

from app.models.service import ServiceModel
from app.models.alert_model import AlertModel
from app.schemas.metric_schema import MetricPoint
from app.schemas.anomaly_schema import AnomalyDetectionResult
from app.database.alert_repository import AlertRepository
from app.services.threshold_detector import threshold_detector
from app.services.anomaly_detector import anomaly_detector

class AlertService:
    @staticmethod
    def run_detection(
        db: Session,
        metrics: List[MetricPoint],
        method: str = "combined"
    ) -> List[AnomalyDetectionResult]:
        """
        Runs anomaly detection across metric points using the specified method:
        - 'threshold': evaluates threshold rule limits only
        - 'isolation_forest': evaluates multivariate Isolation Forest only
        - 'combined': combines threshold breaches and statistical outlier outputs
        Deduplicates and persists non-Normal alerts to the database.
        """
        results: List[AnomalyDetectionResult] = []
        now = datetime.now(timezone.utc)

        # 1. Run ML batch if needed
        ml_results_map: Dict[str, Dict[str, Any]] = {}
        if method in ["isolation_forest", "combined"] and metrics:
            ml_detections = anomaly_detector.detect_batch(metrics)
            for d in ml_detections:
                ml_results_map[d["service_id"]] = d

        for m in metrics:
            service_id = m.service_id
            service_name = m.service_name or m.service_id

            # A. Threshold detection
            threshold_violations = []
            if method in ["threshold", "combined"]:
                threshold_violations = threshold_detector.evaluate(m)

            # B. ML anomaly detection
            ml_data = ml_results_map.get(service_id, {
                "is_anomaly": False,
                "anomaly_score": 0.0,
                "evidence_summary": "No ML anomaly detected.",
                "top_deviating_feature": None,
                "top_feature_value": None
            })

            # C. Determine alert severity and evidence synthesis
            has_crit_threshold = any(v.severity == "Critical" for v in threshold_violations)
            has_warn_threshold = any(v.severity == "Warning" for v in threshold_violations)
            is_ml_anomaly = ml_data.get("is_anomaly", False)

            severity = "Normal"
            primary_metric = None
            observed_val = None
            threshold_val = None
            evidence_parts = []
            effective_method = method

            if method == "threshold":
                if has_crit_threshold:
                    severity = "Critical"
                elif has_warn_threshold:
                    severity = "Warning"
                
                if threshold_violations:
                    top_v = threshold_violations[0]
                    primary_metric = top_v.metric_name
                    observed_val = top_v.observed_value
                    threshold_val = top_v.threshold_value
                    evidence_parts.append("; ".join(v.message for v in threshold_violations))
                else:
                    evidence_parts.append("All metrics within configured threshold boundaries.")

            elif method == "isolation_forest":
                if is_ml_anomaly:
                    severity = "Warning"  # Statistical outlier requires investigation
                    primary_metric = ml_data.get("top_deviating_feature") or "multivariate"
                    observed_val = ml_data.get("top_feature_value")
                    evidence_parts.append(ml_data["evidence_summary"])
                else:
                    evidence_parts.append("Observation aligned with multidimensional normal cluster.")

            else:  # combined
                if has_crit_threshold:
                    severity = "Critical"
                elif has_warn_threshold:
                    severity = "Warning"
                elif is_ml_anomaly:
                    severity = "Warning"

                if threshold_violations:
                    top_v = threshold_violations[0]
                    primary_metric = top_v.metric_name
                    observed_val = top_v.observed_value
                    threshold_val = top_v.threshold_value
                    evidence_parts.append("[Threshold Breach] " + "; ".join(v.message for v in threshold_violations))

                if is_ml_anomaly:
                    if not primary_metric:
                        primary_metric = ml_data.get("top_deviating_feature") or "multivariate"
                        observed_val = ml_data.get("top_feature_value")
                    evidence_parts.append("[ML Pattern Anomaly] " + ml_data["evidence_summary"])

                if not threshold_violations and not is_ml_anomaly:
                    evidence_parts.append("All metrics within threshold limits and normal cluster.")

            is_anomaly = (severity != "Normal")
            evidence_summary = " ".join(evidence_parts)

            # Deduplication & Persistence
            alert_created = False
            alert_id = None

            if is_anomaly:
                metric_key = primary_metric or "general_telemetry"
                # Check for active duplicate in recent window
                is_duplicate = AlertRepository.is_duplicate_alert(
                    db=db,
                    service_id=service_id,
                    metric_name=metric_key,
                    severity=severity,
                    window_minutes=15
                )

                if not is_duplicate:
                    new_alert = AlertRepository.create_alert(
                        db=db,
                        service_id=service_id,
                        service_name=service_name,
                        metric_name=metric_key,
                        observed_value=observed_val,
                        threshold_value=threshold_val,
                        severity=severity,
                        detection_method=effective_method,
                        anomaly_score=ml_data.get("anomaly_score"),
                        evidence_summary=evidence_summary,
                        data_source=m.data_source
                    )
                    alert_created = True
                    alert_id = new_alert.id

            results.append(
                AnomalyDetectionResult(
                    service_id=service_id,
                    service_name=service_name,
                    is_anomaly=is_anomaly,
                    severity=severity,
                    detection_method=effective_method,
                    anomaly_score=ml_data.get("anomaly_score"),
                    metric_name=primary_metric,
                    observed_value=observed_val,
                    threshold_value=threshold_val,
                    evidence_summary=evidence_summary,
                    timestamp=m.timestamp,
                    alert_created=alert_created,
                    alert_id=alert_id
                )
            )

        return results
