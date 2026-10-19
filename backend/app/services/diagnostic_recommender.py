from typing import List, Optional
from app.models.service import ServiceModel
from app.schemas.rca_schema import (
    DiagnosticRecommendationSchema,
    CandidateRootCauseSchema,
    EvidenceItemSchema
)

class DiagnosticRecommender:
    @staticmethod
    def generate_recommendations(
        candidates: List[CandidateRootCauseSchema],
        evidence_items: List[EvidenceItemSchema],
        services: List[ServiceModel]
    ) -> List[DiagnosticRecommendationSchema]:
        """
        Generates targeted, non-destructive diagnostic checks to disambiguate root cause candidates
        and close critical observability gaps.
        """
        recs: List[DiagnosticRecommendationSchema] = []
        rec_counter = 1
        service_map = {s.id: s for s in services}

        # 1. Recommendation for Primary Candidate
        if candidates:
            top_cand = candidates[0]
            svc_model = service_map.get(top_cand.service_id)
            svc_type = svc_model.service_type if svc_model else "compute"

            if svc_type == "database":
                recs.append(
                    DiagnosticRecommendationSchema(
                        recommendation_id=f"rec-{rec_counter}",
                        action_description=f"Inspect '{top_cand.service_name}' active connection pool saturation, deadlocks, and slow query log.",
                        target_service_id=top_cand.service_id,
                        reason=f"Top candidate '{top_cand.service_name}' is the relational data tier; connection pool exhaustion directly chokes all dependent callers.",
                        evidence_gap="Database lock wait times and active connection counts currently unobserved in coarse telemetry.",
                        expected_information_gain="High: Confirms whether caller timeouts stem from database thread starvation.",
                        priority="P1_Immediate",
                        manual_confirmation_required=True
                    )
                )
                rec_counter += 1
            elif svc_type == "security":
                recs.append(
                    DiagnosticRecommendationSchema(
                        recommendation_id=f"rec-{rec_counter}",
                        action_description=f"Verify '{top_cand.service_name}' token validation cache hit rates, JWT verification error rate, and upstream IdP connectivity.",
                        target_service_id=top_cand.service_id,
                        reason=f"Authentication service failure cascades across all authenticated endpoints and orders.",
                        evidence_gap="External Identity Provider (OAuth/OIDC) response status and local token cache expiration rates.",
                        expected_information_gain="High: Disambiguates internal token signing CPU saturation vs upstream IdP outage.",
                        priority="P1_Immediate",
                        manual_confirmation_required=True
                    )
                )
                rec_counter += 1
            elif svc_type == "gateway":
                recs.append(
                    DiagnosticRecommendationSchema(
                        recommendation_id=f"rec-{rec_counter}",
                        action_description=f"Analyze '{top_cand.service_name}' distributed tracing spans to isolate proxy transit time from backend upstream service response duration.",
                        target_service_id=top_cand.service_id,
                        reason="Determines whether Gateway is the origin of errors or merely reflecting downstream backend timeouts.",
                        evidence_gap="Span-level breakdown between gateway edge processing and upstream backend socket wait.",
                        expected_information_gain="High: Proves or disproves Gateway edge misconfiguration vs backend caller degradation.",
                        priority="P1_Immediate",
                        manual_confirmation_required=True
                    )
                )
                rec_counter += 1
            else:
                recs.append(
                    DiagnosticRecommendationSchema(
                        recommendation_id=f"rec-{rec_counter}",
                        action_description=f"Extract recent application stack traces and garbage collection (GC) pause logs for '{top_cand.service_name}'.",
                        target_service_id=top_cand.service_id,
                        reason=f"Identifies whether '{top_cand.service_name}' degradation is driven by thread deadlock, OOM crash, or unhandled 5xx exceptions.",
                        evidence_gap="Application log payloads and GC pause telemetry.",
                        expected_information_gain="High: Pinpoints exact software exception or resource leak.",
                        priority="P1_Immediate",
                        manual_confirmation_required=True
                    )
                )
                rec_counter += 1

        # 2. Recommendation to compare Top 2 candidates if confidence is close
        if len(candidates) >= 2 and (candidates[0].ranking_score - candidates[1].ranking_score < 20):
            c1, c2 = candidates[0], candidates[1]
            recs.append(
                DiagnosticRecommendationSchema(
                    recommendation_id=f"rec-{rec_counter}",
                    action_description=f"Perform cross-service distributed trace comparison between '{c1.service_name}' and '{c2.service_name}'.",
                    target_service_id=None,
                    reason=f"Ranking scores for '{c1.service_name}' ({c1.ranking_score} pts) and '{c2.service_name}' ({c2.ranking_score} pts) are closely matched.",
                    evidence_gap="End-to-end request latency breakdown along the direct call edge between these two services.",
                    expected_information_gain="Medium: Distinguishes primary trigger from secondary propagation victim.",
                    priority="P2_High",
                    manual_confirmation_required=True
                )
            )
            rec_counter += 1

        # 3. Baseline comparison check
        recs.append(
            DiagnosticRecommendationSchema(
                recommendation_id=f"rec-{rec_counter}",
                action_description="Compare pre-incident rolling baseline (24-hour historical window) against the current incident telemetry window.",
                target_service_id=None,
                reason="Verifies whether observed telemetry values exceed normal diurnal traffic peaks.",
                evidence_gap="Historical traffic seasonality and diurnal variance baseline.",
                expected_information_gain="Medium: Validates that incident is a true anomaly rather than expected traffic surge.",
                priority="P3_Medium",
                manual_confirmation_required=True
            )
        )

        return recs
