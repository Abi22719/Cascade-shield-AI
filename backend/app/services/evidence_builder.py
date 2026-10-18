from typing import List

class EvidenceBuilder:
    @staticmethod
    def generate_recommendation(
        service_name: str,
        service_type: str,
        risk_level: str,
        hop_distance: int,
        failure_type: str
    ) -> str:
        """
        Generates actionable cloud resilience and monitoring recommendations
        based on service type, risk level, and propagation distance.
        """
        if hop_distance == 0:
            return f"Primary Point of Failure: Isolate {service_name}, inspect root cause telemetry, and fail over to secondary replica."

        if risk_level == "Critical":
            if service_type in ["gateway", "ingress"]:
                return f"CRITICAL HAZARD: Activate rate limiting and shedding at {service_name} to prevent whole-cluster cascading brownout."
            elif service_type in ["database", "storage"]:
                return f"CRITICAL HAZARD: Enforce query timeouts and pool limits on {service_name} to avoid connection starvation."
            else:
                return f"CRITICAL HAZARD: Trip circuit breakers immediately on incoming callers to {service_name} and serve degraded fallbacks."

        if risk_level == "High":
            if "latency" in failure_type:
                return f"Adjust downstream HTTP client timeouts on {service_name} to avoid thread pool and socket exhaustion."
            elif "error" in failure_type:
                return f"Enable exponential backoff and retry jitter on {service_name} to dampen retry storms."
            else:
                return f"Pre-emptively scale out replica count for {service_name} and monitor queue backlog."

        if risk_level == "Moderate":
            return f"Monitor telemetry trends for {service_name}; review health check intervals and cache TTL."

        return f"Observe baseline metrics for {service_name}; risk is currently contained."

    @staticmethod
    def build_executive_summary_recommendations(
        impacted_count: int,
        high_risk_count: int,
        critical_risk_count: int,
        root_service_name: str
    ) -> List[str]:
        recommendations = [
            f"Cascading failure originating at '{root_service_name}' threatens {impacted_count} dependent cloud services.",
            f"Prioritize immediate mitigation on {critical_risk_count} Critical and {high_risk_count} High risk services."
        ]

        if critical_risk_count > 0:
            recommendations.append("Deploy active circuit breakers and request throttling on direct callers to halt propagation.")
        else:
            recommendations.append("Propagated impact remains moderate; observe queue depths and response latencies.")

        recommendations.append("All predictions represent heuristic simulation estimates for resilience decision support.")
        return recommendations
