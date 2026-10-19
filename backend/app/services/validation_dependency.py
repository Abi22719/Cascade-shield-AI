from typing import Dict, Any, List, Set, Tuple
import networkx as nx
from sqlalchemy.orm import Session
from app.services.graph_service import GraphService

class ValidationDependencyEngine:
    """
    Performs cycle-safe graph traversal to validate downstream caller recovery
    and detect secondary dependency failures.
    """

    @classmethod
    def analyze_downstream_recovery(
        cls,
        db: Session,
        target_service_ids: List[str],
        simulated_healths: Dict[str, str],
        baseline_healths: Dict[str, str]
    ) -> Dict[str, Any]:
        """
        Analyzes downstream dependencies for all recovered target services.
        Uses cycle-safe BFS traversal on the reverse propagation graph.
        """
        G = GraphService.get_dependency_graph(db)
        # Invert graph to get propagation direction: callee -> caller
        G_prop = G.reverse()

        expected_recovered_callers: Set[str] = set()
        still_unhealthy_callers: List[Dict[str, str]] = []
        fully_recovered_callers: List[str] = []
        newly_affected_services: List[str] = []

        # 1. Identify all reachable downstream callers from target services
        for target_id in target_service_ids:
            if target_id in G_prop:
                reachable = nx.descendants(G_prop, target_id)
                expected_recovered_callers.update(reachable)

        # 2. Check each expected caller's simulated health
        for caller_id in expected_recovered_callers:
            current_health = simulated_healths.get(caller_id, "UNKNOWN")
            if current_health in ["DEGRADED", "CRITICAL"]:
                still_unhealthy_callers.append({
                    "service_id": caller_id,
                    "health_status": current_health
                })
            elif current_health == "HEALTHY":
                fully_recovered_callers.append(caller_id)

        # 3. Detect newly affected services that were HEALTHY in baseline but now UNHEALTHY
        for sid, health in simulated_healths.items():
            if sid not in target_service_ids and sid not in expected_recovered_callers:
                base_h = baseline_healths.get(sid, "HEALTHY")
                if base_h == "HEALTHY" and health in ["DEGRADED", "CRITICAL"]:
                    newly_affected_services.append(sid)

        # 4. Check cycle safety
        has_cycles = False
        try:
            cycles = list(nx.simple_cycles(G))
            has_cycles = len(cycles) > 0
        except Exception:
            has_cycles = False

        return {
            "expected_callers_count": len(expected_recovered_callers),
            "fully_recovered_callers": fully_recovered_callers,
            "still_unhealthy_callers": still_unhealthy_callers,
            "newly_affected_services": newly_affected_services,
            "graph_has_cycles": has_cycles,
            "all_downstream_recovered": len(still_unhealthy_callers) == 0 and len(newly_affected_services) == 0
        }
