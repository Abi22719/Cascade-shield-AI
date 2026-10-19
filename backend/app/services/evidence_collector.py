import uuid
import logging
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional, Set
from sqlalchemy.orm import Session

from app.models.service import ServiceModel
from app.models.dependency import DependencyModel
from app.models.alert_model import AlertModel
from app.models.cascade_model import CascadeScenarioModel
from app.schemas.rca_schema import EvidenceItemSchema

logger = logging.getLogger("cascadeshield.evidence_collector")

class EvidenceCollector:
    @staticmethod
    def collect_evidence(
        db: Session,
        affected_service_ids: List[str],
        window_start: Optional[datetime] = None,
        window_end: Optional[datetime] = None,
        scenario_id: Optional[str] = None
    ) -> List[EvidenceItemSchema]:
        """
        Collects and normalizes multi-source evidence across Modules 1, 2, and 3:
        1. Module 1: Service health states, resource metrics, and baseline telemetry.
        2. Module 2: Anomaly alerts, threshold breaches, and detection scores.
        3. Module 3: Failure propagation predictions, scenario parameters, and risk scores.
        """
        evidence_items: List[EvidenceItemSchema] = []
        seen_keys: Set[str] = set()

        services = db.query(ServiceModel).all()
        service_map = {s.id: s for s in services}

        # 1. Module 1 Telemetry & Health Evidence
        for s in services:
            # Check if service is in affected set or directly connected
            is_affected = s.id in affected_service_ids or len(affected_service_ids) == 0
            status_lower = (s.health_status or "healthy").lower()
            svc_timestamp = getattr(s, "updated_at", None) or getattr(s, "last_updated", None) or datetime.now(timezone.utc)

            # 1a. Unhealthy Status Evidence
            if status_lower in ["critical", "warning"]:
                key = f"health_{s.id}_{status_lower}"
                if key not in seen_keys:
                    seen_keys.add(key)
                    evidence_items.append(
                        EvidenceItemSchema(
                            id=f"ev-hlth-{uuid.uuid4().hex[:8]}",
                            service_id=s.id,
                            service_name=s.name,
                            evidence_type="health_degraded",
                            observed_value=1.0 if status_lower == "critical" else 0.5,
                            expected_or_threshold_value=0.0,
                            timestamp=svc_timestamp,
                            source_module="Module 1: Cloud Digital Twin",
                            source_record_id=s.id,
                            evidence_summary=f"Service health status degraded to '{status_lower.upper()}'. Description: {s.description or 'N/A'}",
                            data_source="simulated",
                            reliability_score=0.95,
                            is_contradictory=False
                        )
                    )
            elif is_affected and status_lower == "healthy":
                # Contradictory evidence: service reported healthy despite being marked in incident scope
                key = f"healthy_contra_{s.id}"
                if key not in seen_keys:
                    seen_keys.add(key)
                    evidence_items.append(
                        EvidenceItemSchema(
                            id=f"ev-hlth-ok-{uuid.uuid4().hex[:8]}",
                            service_id=s.id,
                            service_name=s.name,
                            evidence_type="contradictory_evidence",
                            observed_value=0.0,
                            expected_or_threshold_value=1.0,
                            timestamp=svc_timestamp,
                            source_module="Module 1: Cloud Digital Twin",
                            source_record_id=s.id,
                            evidence_summary=f"Service '{s.name}' exhibits HEALTHY state with normal operational indicators, contradicting catastrophic failure hypothesis.",
                            data_source="simulated",
                            reliability_score=0.90,
                            is_contradictory=True
                        )
                    )

            # 1b. Metric Breaches & Saturation
            metrics_to_check = [
                ("error_rate", float(s.error_rate), 2.0, "%", "High error rate surge"),
                ("latency_ms", float(s.latency_ms), 200.0, "ms", "Elevated response latency"),
                ("cpu_usage", float(s.cpu_usage), 75.0, "%", "High CPU exhaustion"),
                ("memory_usage", float(s.memory_usage), 80.0, "%", "Memory saturation pressure")
            ]

            for m_name, val, thresh, unit, desc in metrics_to_check:
                if val >= thresh:
                    key = f"metric_{s.id}_{m_name}"
                    if key not in seen_keys:
                        seen_keys.add(key)
                        evidence_items.append(
                            EvidenceItemSchema(
                                id=f"ev-met-{uuid.uuid4().hex[:8]}",
                                service_id=s.id,
                                service_name=s.name,
                                evidence_type="metric_breach",
                                metric_name=m_name,
                                observed_value=round(val, 2),
                                expected_or_threshold_value=thresh,
                                timestamp=svc_timestamp,
                                source_module="Module 1: Cloud Digital Twin",
                                source_record_id=s.id,
                                evidence_summary=f"{desc} observed: {val:.1f}{unit} (operating baseline threshold: {thresh:.1f}{unit}).",
                                data_source="simulated",
                                reliability_score=0.92,
                                is_contradictory=False
                            )
                        )

        # 2. Module 2 Anomaly Alerts Evidence
        alert_query = db.query(AlertModel)
        if window_start:
            alert_query = alert_query.filter(AlertModel.created_at >= window_start)
        if window_end:
            alert_query = alert_query.filter(AlertModel.created_at <= window_end)

        alerts = alert_query.order_by(AlertModel.created_at.asc()).all()

        for a in alerts:
            key = f"alert_{a.id}"
            if key not in seen_keys:
                seen_keys.add(key)
                is_crit = a.severity == "Critical"
                evidence_items.append(
                    EvidenceItemSchema(
                        id=f"ev-alt-{a.id}",
                        service_id=a.service_id,
                        service_name=a.service_name,
                        evidence_type="anomaly_alert",
                        metric_name=a.metric_name,
                        observed_value=a.observed_value,
                        expected_or_threshold_value=a.threshold_value,
                        timestamp=a.created_at or datetime.now(timezone.utc),
                        source_module="Module 2: AI Anomaly Detection",
                        source_record_id=a.id,
                        evidence_summary=f"[{a.severity.upper()}] Anomaly detected via {a.detection_method}: {a.evidence_summary}",
                        data_source=a.data_source or "simulated",
                        reliability_score=0.95 if is_crit else 0.85,
                        is_contradictory=False
                    )
                )

        # 3. Module 3 Cascading Failure Prediction Scenario Evidence (if linked)
        if scenario_id:
            scenario = db.query(CascadeScenarioModel).filter(CascadeScenarioModel.id == scenario_id).first()
            if scenario and scenario.initial_service_id:
                root_svc = service_map.get(scenario.initial_service_id)
                root_name = root_svc.name if root_svc else scenario.initial_service_id
                key = f"cascade_scen_{scenario.id}"
                if key not in seen_keys:
                    seen_keys.add(key)
                    evidence_items.append(
                        EvidenceItemSchema(
                            id=f"ev-casc-{scenario.id}",
                            service_id=scenario.initial_service_id,
                            service_name=root_name,
                            evidence_type="cascade_risk",
                            observed_value=95.0 if scenario.failure_severity == "severe" else 70.0,
                            expected_or_threshold_value=50.0,
                            timestamp=scenario.created_at,
                            source_module="Module 3: Cascading Failure Prediction",
                            source_record_id=scenario.id,
                            evidence_summary=f"Linked cascade prediction scenario '{scenario.scenario_name}' established {scenario.failure_severity.upper()} {scenario.failure_type} at '{root_name}'.",
                            data_source="simulated",
                            reliability_score=0.88,
                            is_contradictory=False
                        )
                    )

        # Sort evidence chronologically
        evidence_items.sort(key=lambda x: x.timestamp or datetime.min.replace(tzinfo=timezone.utc))

        return evidence_items
