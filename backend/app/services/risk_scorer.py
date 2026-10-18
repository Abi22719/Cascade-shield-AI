import math
from typing import Dict, List, Any, Optional, Tuple
from app.models.service import ServiceModel
from app.models.alert_model import AlertModel
from app.schemas.cascade_schema import CascadePathInfo

DEFAULT_PROTOCOL_WEIGHTS = {
    "sync_http": 1.0,
    "database_read_write": 0.95,
    "cache_lookup": 0.40,
    "async_message": 0.45,
    "default": 0.70
}

SEVERITY_BASE_SCORES = {
    "severe": 95.0,
    "moderate": 70.0,
    "mild": 40.0
}

class RiskScorer:
    @staticmethod
    def get_risk_level(score: float) -> str:
        """
        Categorizes score into documented 0-100 risk bands:
        - 0-24: Low
        - 25-49: Moderate
        - 50-74: High
        - 75-100: Critical
        """
        if score >= 75.0:
            return "Critical"
        if score >= 50.0:
            return "High"
        if score >= 25.0:
            return "Moderate"
        return "Low"

    @staticmethod
    def calculate_service_cascade_risk(
        service_node: Dict[str, Any],
        hop_distance: int,
        failure_type: str,
        failure_severity: str,
        paths_to_service: List[CascadePathInfo],
        recent_alerts: List[AlertModel],
        attenuation_factor: float = 0.75,
        custom_weights: Optional[Dict[str, float]] = None
    ) -> Tuple[float, str, float, List[str]]:
        """
        Calculates normalized risk score (0-100), risk level band,
        heuristic propagation probability, and contributing evidence.
        """
        protocol_weights = {**DEFAULT_PROTOCOL_WEIGHTS, **(custom_weights or {})}
        evidence_list: List[str] = []

        # 1. Base Score from Failure Severity
        base_score = SEVERITY_BASE_SCORES.get(failure_severity.lower(), 70.0)
        evidence_list.append(f"Root scenario severity '{failure_severity}' establishes baseline risk of {base_score:.0f} pts.")

        # 2. Path-based Attenuation & Protocol Criticality
        path_scores: List[float] = []

        if not paths_to_service or hop_distance == 0:
            # Root service itself
            path_scores.append(base_score)
        else:
            for p in paths_to_service:
                hop = p.hop_count
                decay = attenuation_factor ** max(0, hop - 1)
                
                # Protocol coupling weight across path edges
                coupling_multiplier = 1.0
                for edge_proto in p.dependency_types:
                    weight = protocol_weights.get(edge_proto, protocol_weights["default"])
                    coupling_multiplier *= weight

                p_score = base_score * decay * coupling_multiplier
                p.risk_contribution = round(p_score, 1)
                path_scores.append(p_score)

        # Multi-path combination: R_comb = 100 * (1 - prod(1 - s/100))
        if len(path_scores) == 1:
            combined_path_score = path_scores[0]
        else:
            prob_inv = 1.0
            for ps in path_scores:
                clamped_ratio = min(0.99, max(0.01, ps / 100.0))
                prob_inv *= (1.0 - clamped_ratio)
            combined_path_score = 100.0 * (1.0 - prob_inv)
            evidence_list.append(
                f"Combined risk amplified across {len(path_scores)} concurrent propagation paths."
            )

        if hop_distance > 0:
            evidence_list.append(
                f"Hop distance {hop_distance} applied {attenuation_factor:.2f} attenuation decay factor."
            )

        # 3. Telemetry & Baseline Resource Saturation Amplification
        telemetry_boost = 0.0
        cpu = service_node.get("cpu_usage", 20.0)
        mem = service_node.get("memory_usage", 30.0)
        lat = service_node.get("latency_ms", 30.0)
        err = service_node.get("error_rate", 0.1)

        if err >= 2.0:
            telemetry_boost += 12.0
            evidence_list.append(f"Elevated baseline error rate ({err:.1f}%) increases service fragility (+12 pts).")
        if lat >= 350.0:
            telemetry_boost += 10.0
            evidence_list.append(f"High baseline latency ({lat:.0f}ms) reduces failover headroom (+10 pts).")
        if cpu >= 75.0 or mem >= 80.0:
            telemetry_boost += 8.0
            evidence_list.append(f"Resource saturation (CPU {cpu:.0f}%, Mem {mem:.0f}%) heightens vulnerability (+8 pts).")

        # 4. Active Module 2 Anomaly Alerts Integration
        active_service_alerts = [
            a for a in recent_alerts
            if (not service_node.get("id") or a.service_id == service_node.get("id"))
            and not getattr(a, "acknowledged", False)
        ]
        alert_boost = 0.0
        if active_service_alerts:
            has_crit = any(a.severity == "Critical" for a in active_service_alerts)
            if has_crit:
                alert_boost = 15.0
                evidence_list.append(f"Active Critical Module 2 Anomaly Alert detected on service (+15 pts).")
            else:
                alert_boost = 8.0
                evidence_list.append(f"Active Warning Module 2 Anomaly Alert detected on service (+8 pts).")

        # Final score summation and clamping (0.0 to 100.0)
        final_score = combined_path_score + telemetry_boost + alert_boost
        final_score = min(100.0, max(5.0, final_score))
        final_score = round(final_score, 1)

        risk_level = RiskScorer.get_risk_level(final_score)

        # Calibrated heuristic propagation probability estimate (0.05 - 0.98)
        prob_estimate = round(min(0.98, max(0.05, (final_score / 100.0) * (0.95 if hop_distance > 0 else 1.0))), 2)

        return final_score, risk_level, prob_estimate, evidence_list
