from datetime import datetime, timezone
from typing import List, Dict, Any, Optional
from app.schemas.rca_schema import (
    RCAReportSchema,
    CandidateRootCauseSchema,
    EvidenceItemSchema,
    TimelineEventSchema,
    AlternativeHypothesisSchema,
    DiagnosticRecommendationSchema
)

class ExplanationBuilder:
    @staticmethod
    def build_report(
        incident_id: str,
        title: str,
        status: str,
        affected_service_ids: List[str],
        window_start: Optional[datetime],
        window_end: Optional[datetime],
        candidates: List[CandidateRootCauseSchema],
        evidence_items: List[EvidenceItemSchema],
        timeline_events: List[TimelineEventSchema],
        alternative_hypotheses: List[AlternativeHypothesisSchema],
        diagnostic_recommendations: List[DiagnosticRecommendationSchema],
        algorithm_version: str = "4.0.0"
    ) -> RCAReportSchema:
        """
        Compiles the comprehensive, auditable Root Cause Analysis investigation report.
        Ensures all findings are grounded strictly in collected evidence with source references.
        """
        primary_candidate = candidates[0] if candidates and candidates[0].ranking_score >= 25.0 else None

        # Build Confidence & Uncertainty Explanation
        if primary_candidate:
            conf_text = (
                f"Candidate '{primary_candidate.service_name}' ({primary_candidate.service_id}) is identified as the primary root cause "
                f"with a normalized ranking score of {primary_candidate.ranking_score}/100 ({primary_candidate.confidence_label}, calibrated heuristic confidence: {primary_candidate.confidence_score:.2f}). "
                f"Evaluation is grounded across {len(primary_candidate.evidence_for)} supporting evidence observations, "
                f"temporal precedence analysis, and NetworkX dependency graph traversal. "
                f"Note: Temporal order and graph connectivity represent strong heuristic evidence, not absolute proof of causality. "
                f"Confidence decreases if unobserved downstream bottlenecks or unmodeled third-party dependencies are present."
            )
        else:
            conf_text = (
                "INVESTIGATION INCONCLUSIVE: No evaluated service achieved the minimum confidence threshold (score < 25/100). "
                "Available telemetry shows symptoms across monitored services, but evidence is insufficient or contradictory to isolate "
                "a single ground-zero root cause without risking false attribution."
            )

        # Missing Data Gaps Identification
        missing_gaps: List[str] = [
            "Distributed tracing spans (Jaeger/OpenTelemetry) to measure inter-service network transit times.",
            "Underlying container host noisy neighbor telemetry and Kubernetes pod throttling events.",
            "Detailed SQL transaction query execution profiles and database connection pool queue depths."
        ]
        if not any(e.evidence_type == "anomaly_alert" for e in evidence_items):
            missing_gaps.append("Active Module 2 Anomaly Detection alerts were not present during this investigation window.")

        # Investigation Limitations
        limitations: List[str] = [
            "Simulation & Digital Twin Scope: Telemetry is synthetically simulated for cloud resilience decision support.",
            "Non-Destructive Guarantee: The RCA engine provides decision-support analysis and does not execute automated remediation or alter live infrastructure.",
            "Correlation Boundary: Graph reachability and temporal precedence demonstrate plausibility, not absolute mathematical proof of causality.",
            "Sampling Granularity: Microsecond burst spikes occurring between discrete sampling intervals may not be reflected in aggregate metrics."
        ]

        return RCAReportSchema(
            incident_id=incident_id,
            title=title,
            status=status,
            investigation_window={
                "start": window_start,
                "end": window_end
            },
            affected_services=affected_service_ids,
            primary_root_cause=primary_candidate,
            ranked_candidates=candidates,
            evidence_timeline=timeline_events,
            evidence_count=len(evidence_items),
            evidence_items=evidence_items,
            alternative_hypotheses=alternative_hypotheses,
            diagnostic_recommendations=diagnostic_recommendations,
            confidence_and_uncertainty_explanation=conf_text,
            missing_data_gaps=missing_gaps,
            investigation_limitations=limitations,
            data_sources=["simulated", "digital_twin_telemetry", "isolation_forest_alerts"],
            algorithm_version=algorithm_version,
            analyzed_at=datetime.now(timezone.utc)
        )
