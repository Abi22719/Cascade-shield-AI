from typing import List, Dict, Any, Optional, Tuple, Set
import networkx as nx
from datetime import datetime

from app.models.service import ServiceModel
from app.schemas.rca_schema import (
    EvidenceItemSchema,
    CandidateRootCauseSchema
)
from app.services.temporal_analyzer import TemporalAnalyzer
from app.services.dependency_analyzer import DependencyAnalyzer

DEFAULT_RANKING_WEIGHTS = {
    "temporal": 0.30,
    "dependency": 0.25,
    "metric": 0.20,
    "alert": 0.15,
    "cascade": 0.10
}

class CandidateRanker:
    @staticmethod
    def rank_candidates(
        services: List[ServiceModel],
        affected_service_ids: List[str],
        evidence_items: List[EvidenceItemSchema],
        G_impact: nx.DiGraph,
        custom_weights: Optional[Dict[str, float]] = None
    ) -> List[CandidateRootCauseSchema]:
        """
        Ranks plausible root cause candidates using deterministic multi-factor scoring.
        Balances temporal precedence, graph reachability, metric severity, and anomaly evidence,
        while strictly applying penalties for contradictory evidence.
        """
        weights = {**DEFAULT_RANKING_WEIGHTS, **(custom_weights or {})}
        service_map = {s.id: s for s in services}
        
        # 1. Identify Candidate Pool
        candidate_ids: Set[str] = set(affected_service_ids)
        for ev in evidence_items:
            if not ev.is_contradictory and ev.service_id in service_map:
                candidate_ids.add(ev.service_id)

        # If pool is empty, consider all degraded services in digital twin
        if not candidate_ids:
            for s in services:
                if s.health_status in ["critical", "warning"]:
                    candidate_ids.add(s.id)

        if not candidate_ids:
            return []

        # 2. Pre-calculate earliest timestamps
        earliest_map = TemporalAnalyzer.extract_service_earliest_timestamps(evidence_items)

        candidates: List[CandidateRootCauseSchema] = []

        for cand_id in candidate_ids:
            cand_svc = service_map.get(cand_id)
            if not cand_svc:
                continue

            cand_evidence = [e for e in evidence_items if e.service_id == cand_id]
            supporting: List[str] = []
            contradictory: List[str] = []
            missing: List[str] = []

            # Feature A: Temporal Precedence Score (0.0 to 1.0)
            s_temp, temp_sup, temp_contra = TemporalAnalyzer.evaluate_temporal_precedence(
                cand_id, affected_service_ids, earliest_map
            )
            supporting.extend(temp_sup)
            contradictory.extend(temp_contra)

            # Feature B: Dependency Reachability Score (0.0 to 1.0)
            s_dep, paths, reachable, unreachable = DependencyAnalyzer.analyze_candidate_dependencies(
                cand_id, affected_service_ids, G_impact
            )
            if s_dep > 0:
                supporting.append(
                    f"Dependency graph confirms direct/indirect reachability to {len(reachable)} affected services."
                )
            if unreachable:
                contradictory.append(
                    f"{len(unreachable)} affected services ({', '.join(unreachable[:3])}) have no dependency path to '{cand_svc.name}'."
                )

            # Feature C: Metric Degradation Severity (0.0 to 1.0)
            err = float(cand_svc.error_rate)
            lat = float(cand_svc.latency_ms)
            cpu = float(cand_svc.cpu_usage)
            mem = float(cand_svc.memory_usage)

            s_metric = 0.0
            if err >= 2.0:
                s_metric += 0.45
                supporting.append(f"Severe error rate spike observed ({err:.1f}%).")
            elif err >= 0.5:
                s_metric += 0.20

            if lat >= 300.0:
                s_metric += 0.35
                supporting.append(f"Extreme response latency observed ({lat:.0f}ms).")
            elif lat >= 100.0:
                s_metric += 0.15

            if cpu >= 75.0 or mem >= 80.0:
                s_metric += 0.20
                supporting.append(f"Resource saturation detected (CPU {cpu:.0f}%, Mem {mem:.0f}%).")

            s_metric = min(1.0, s_metric)

            # Feature D: Anomaly Alert Evidence (0.0 to 1.0)
            cand_alerts = [e for e in cand_evidence if e.evidence_type == "anomaly_alert"]
            s_alert = 0.0
            if any("CRITICAL" in a.evidence_summary.upper() for a in cand_alerts):
                s_alert = 1.0
                supporting.append(f"Confirmed by {len(cand_alerts)} Module 2 Critical Anomaly Alert(s).")
            elif cand_alerts:
                s_alert = 0.60
                supporting.append(f"Supported by {len(cand_alerts)} Module 2 Warning Alert(s).")
            else:
                missing.append("No active Module 2 anomaly alerts registered for this service.")

            # Feature E: Module 3 Cascade Risk Alignment (0.0 to 1.0)
            cand_cascade = [e for e in cand_evidence if e.evidence_type == "cascade_risk"]
            s_cascade = 0.85 if cand_cascade else 0.40
            if cand_cascade:
                supporting.append("Consistent with Module 3 simulated failure blast radius.")

            # Contradictory Evidence Penalties
            contra_penalty = 0.0
            if cand_svc.health_status == "healthy":
                contra_penalty += 30.0
                contradictory.append("Service reports HEALTHY state in digital twin baseline.")
            if temp_contra:
                contra_penalty += 15.0 * len(temp_contra)
            if len(unreachable) > len(reachable) and len(unreachable) > 0:
                contra_penalty += 20.0

            # Calculate Raw Weighted Score
            raw_score = 100.0 * (
                weights["temporal"] * s_temp +
                weights["dependency"] * s_dep +
                weights["metric"] * s_metric +
                weights["alert"] * s_alert +
                weights["cascade"] * s_cascade
            ) - contra_penalty

            final_score = round(min(100.0, max(0.0, raw_score)), 1)

            # Confidence Labeling & Calibration
            if final_score >= 75.0 and len(contradictory) == 0:
                conf_label = "Strong supporting evidence"
                conf_score = round(min(0.96, 0.75 + (final_score - 75.0) * 0.008), 2)
            elif final_score >= 50.0:
                conf_label = "Moderate supporting evidence"
                conf_score = round(0.55 + (final_score - 50.0) * 0.008, 2)
            elif final_score >= 25.0:
                conf_label = "Weak supporting evidence"
                conf_score = round(0.30 + (final_score - 25.0) * 0.008, 2)
            else:
                conf_label = "Insufficient evidence"
                conf_score = round(max(0.05, final_score * 0.01), 2)

            # Structured Explanation
            if final_score >= 50.0:
                explanation = (
                    f"Service '{cand_svc.name}' is a plausible upstream root cause with a ranking score of {final_score}/100. "
                    f"It exhibits temporal precedence across {len(temp_sup)} dependent callers and reachable propagation paths to {len(reachable)} affected services."
                )
            elif final_score >= 25.0:
                explanation = (
                    f"Service '{cand_svc.name}' shows partial correlation ({final_score}/100), but evidence is diluted by {len(contradictory)} contradictory factor(s) or weak metric degradation."
                )
            else:
                explanation = (
                    f"Service '{cand_svc.name}' has insufficient evidence ({final_score}/100) to support causality. Available telemetry does not support it as the incident root cause."
                )

            # Data Gaps Identification
            if "error_rate" not in [e.metric_name for e in cand_evidence if e.metric_name]:
                missing.append("Detailed error payload categorization or stack traces.")
            if "latency_ms" not in [e.metric_name for e in cand_evidence if e.metric_name]:
                missing.append("P99 tail latency distribution across downstream endpoints.")

            candidates.append(
                CandidateRootCauseSchema(
                    service_id=cand_id,
                    service_name=cand_svc.name,
                    rank=0,  # assigned after sorting
                    ranking_score=final_score,
                    confidence_label=conf_label,
                    confidence_score=conf_score,
                    evidence_for=supporting,
                    evidence_against=contradictory,
                    affected_services=reachable,
                    supporting_paths=paths,
                    missing_evidence=missing,
                    explanation=explanation
                )
            )

        # Sort candidates descending by ranking score
        candidates.sort(key=lambda c: -c.ranking_score)

        # Assign ranks
        for idx, c in enumerate(candidates):
            c.rank = idx + 1

        return candidates
