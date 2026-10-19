from typing import List, Dict, Any, Optional
import networkx as nx

from app.models.service import ServiceModel
from app.schemas.rca_schema import (
    AlternativeHypothesisSchema,
    CandidateRootCauseSchema,
    EvidenceItemSchema
)

class AlternativeHypothesisEngine:
    @staticmethod
    def generate_hypotheses(
        candidates: List[CandidateRootCauseSchema],
        affected_service_ids: List[str],
        services: List[ServiceModel],
        G_dep: nx.DiGraph,
        evidence_items: List[EvidenceItemSchema]
    ) -> List[AlternativeHypothesisSchema]:
        """
        Formulates plausible alternative explanations grounded strictly in data and topology:
        1. Shared Downstream Bottleneck (e.g. Database / Cache starvation).
        2. Downstream Symptom Misidentification (Caller bottleneck vs Callee failure).
        3. Independent Concurrent Anomalies (Disconnected cluster incidents).
        4. Incomplete Telemetry / Observability Blind Spot.
        """
        hypotheses: List[AlternativeHypothesisSchema] = []
        service_map = {s.id: s for s in services}

        # 1. Hypothesis: Shared Downstream Dependency Bottleneck
        # Check if multiple affected services depend on a common callee
        callee_counts: Dict[str, List[str]] = {}
        for aff_id in affected_service_ids:
            if G_dep.has_node(aff_id):
                for callee in G_dep.successors(aff_id):
                    if callee not in callee_counts:
                        callee_counts[callee] = []
                    callee_counts[callee].append(aff_id)

        shared_bottlenecks = [c for c, callers in callee_counts.items() if len(callers) >= 2]
        for sb_id in shared_bottlenecks:
            sb_svc = service_map.get(sb_id)
            sb_name = sb_svc.name if sb_svc else sb_id
            callers_str = ", ".join([service_map.get(c, c).name if isinstance(service_map.get(c), ServiceModel) else c for c in callee_counts[sb_id]])

            hypotheses.append(
                AlternativeHypothesisSchema(
                    hypothesis_id="hyp-shared-dep",
                    hypothesis_title=f"Shared Bottleneck at '{sb_name}'",
                    related_services=[sb_id] + callee_counts[sb_id],
                    supporting_evidence=[
                        f"Common dependency: Multiple affected services ({callers_str}) share '{sb_name}' as their downstream dependency.",
                        f"A localized slow-down or lock contention at '{sb_name}' can manifest as concurrent upstream degradation across all callers."
                    ],
                    contradictory_evidence=[
                        f"Direct metric telemetry on '{sb_name}' shows CPU {sb_svc.cpu_usage if sb_svc else 'N/A'}% and Latency {sb_svc.latency_ms if sb_svc else 'N/A'}ms."
                    ],
                    missing_information=[
                        f"Database connection pool wait queues and transaction lock wait telemetry on '{sb_name}'."
                    ],
                    plausibility_reason=(
                        f"When multiple decoupled microservices degrade simultaneously, shared storage or identity tier saturation "
                        f"is frequently the unobserved root origin."
                    )
                )
            )

        # 2. Hypothesis: Downstream Symptom Misidentification
        if candidates and candidates[0].service_id in ["srv-gateway", "srv-ingress"]:
            top_cand = candidates[0]
            hypotheses.append(
                AlternativeHypothesisSchema(
                    hypothesis_id="hyp-downstream-symptom",
                    hypothesis_title="Gateway Latency as a Downstream Symptom Rather Than Root Cause",
                    related_services=[top_cand.service_id],
                    supporting_evidence=[
                        f"'{top_cand.service_name}' sits at the cluster edge and aggregates all internal API call response times.",
                        "Gateway latencies routinely spike whenever any internal backend service experiences latency or timeout backlog."
                    ],
                    contradictory_evidence=[
                        f"Gateway reports the earliest or most severe metric alert ({top_cand.ranking_score} pts)."
                    ],
                    missing_information=[
                        "Sub-request tracing spans breaking down gateway edge latency vs internal upstream proxy duration."
                    ],
                    plausibility_reason=(
                        "Edge routers often trigger the first alert because customer traffic accumulates there, "
                        "even when the actual root cause is buried deeper in backend microservices."
                    )
                )
            )

        # 3. Hypothesis: Independent Concurrent Degradations
        unreachable_pairs = False
        if len(affected_service_ids) >= 2:
            s1, s2 = affected_service_ids[0], affected_service_ids[1]
            if G_dep.has_node(s1) and G_dep.has_node(s2):
                if not nx.has_path(G_dep, s1, s2) and not nx.has_path(G_dep, s2, s1):
                    unreachable_pairs = True

        if unreachable_pairs:
            hypotheses.append(
                AlternativeHypothesisSchema(
                    hypothesis_id="hyp-independent-failures",
                    hypothesis_title="Independent Coincident Degradation Events",
                    related_services=affected_service_ids[:4],
                    supporting_evidence=[
                        "Affected services reside in disconnected dependency branches with no direct or indirect call paths between them."
                    ],
                    contradictory_evidence=[
                        "Simultaneous occurrence suggests a potential underlying cluster-wide or infrastructure-level trigger."
                    ],
                    missing_information=[
                        "Kubernetes node-level CPU throttling and underlying cloud hypervisor noisy neighbor metrics."
                    ],
                    plausibility_reason=(
                        "Disconnected microservices can degrade at the same time due to shared physical host node saturation "
                        "without any application-level architectural dependency."
                    )
                )
            )

        # 4. Hypothesis: Observability Blind Spot / Incomplete Evidence
        if not candidates or (candidates and candidates[0].ranking_score < 60):
            hypotheses.append(
                AlternativeHypothesisSchema(
                    hypothesis_id="hyp-blind-spot",
                    hypothesis_title="Unmonitored Third-Party or Network Infrastructure Failure",
                    related_services=affected_service_ids,
                    supporting_evidence=[
                        "No single internal service achieved a definitive high-confidence ranking score (peak score < 60 pts).",
                        "Telemetry shows symptom propagation without an obvious ground-zero internal origin."
                    ],
                    contradictory_evidence=[],
                    missing_information=[
                        "External DNS resolution latency, third-party payment vendor webhook health, and VPC NAT gateway egress metrics."
                    ],
                    plausibility_reason=(
                        "External cloud provider dependencies, payment provider gateways, or VPC routing degradation "
                        "can disrupt cloud microservices while leaving internal service metrics looking ambiguous."
                    )
                )
            )

        return hypotheses
