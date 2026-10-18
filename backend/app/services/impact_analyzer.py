from typing import List, Dict, Any, Set, Tuple, Optional
import networkx as nx
from app.models.service import ServiceModel
from app.models.dependency import DependencyModel
from app.schemas.cascade_schema import CascadePathInfo

class ImpactAnalyzer:
    @staticmethod
    def build_propagation_graph(
        services: List[ServiceModel],
        dependencies: List[DependencyModel]
    ) -> nx.DiGraph:
        """
        Builds the failure propagation graph.
        In the digital twin, a dependency edge (u -> v) means u depends on v (u is caller, v is callee).
        When callee v fails, failure propagates to caller u (v -> u in propagation flow).
        Thus, the failure propagation graph reverses dependency edges:
        Payment Service -> Order Service -> API Gateway.
        """
        G = nx.DiGraph()

        # Add all service nodes
        for s in services:
            G.add_node(
                s.id,
                id=s.id,
                name=s.name,
                service_type=s.service_type,
                health_status=s.health_status,
                cpu_usage=float(s.cpu_usage),
                memory_usage=float(s.memory_usage),
                latency_ms=float(s.latency_ms),
                error_rate=float(s.error_rate),
                request_volume=int(s.request_volume)
            )

        # In failure propagation, failure flows from the dependency (target) to dependent callers (source)
        for d in dependencies:
            if G.has_node(d.source_service_id) and G.has_node(d.target_service_id):
                # Edge in propagation flow: target_service_id -> source_service_id
                G.add_edge(
                    d.target_service_id,
                    d.source_service_id,
                    id=d.id,
                    dependency_type=d.dependency_type,
                    description=d.description or ""
                )

        return G

    @staticmethod
    def find_affected_services_and_paths(
        G_prop: nx.DiGraph,
        root_service_id: str,
        max_hops: int = 5
    ) -> Tuple[Dict[str, Dict[str, Any]], List[CascadePathInfo]]:
        """
        Cycle-safe traversal finding all services impacted by root_service_id failure,
        computing direct vs indirect classification, hop distances, and non-cyclic failure paths.
        """
        if not G_prop.has_node(root_service_id):
            return {}, []

        service_names = {node: data.get("name", node) for node, data in G_prop.nodes(data=True)}
        affected_services: Dict[str, Dict[str, Any]] = {}
        all_paths_info: List[CascadePathInfo] = []

        # BFS for shortest hop distances and direct/indirect classification
        visited_nodes: Set[str] = {root_service_id}
        queue = [(root_service_id, 0)]  # (service_id, hop_distance)

        while queue:
            current_id, dist = queue.pop(0)

            if dist >= max_hops:
                continue

            for neighbor in G_prop.successors(current_id):
                next_dist = dist + 1
                if neighbor not in affected_services:
                    affected_services[neighbor] = {
                        "service_id": neighbor,
                        "service_name": service_names.get(neighbor, neighbor),
                        "hop_distance": next_dist,
                        "impact_type": "Direct" if next_dist == 1 else "Indirect",
                        "impacted_by": [current_id]
                    }
                else:
                    # Record multiple incoming propagation parents
                    if current_id not in affected_services[neighbor]["impacted_by"]:
                        affected_services[neighbor]["impacted_by"].append(current_id)

                if neighbor not in visited_nodes:
                    visited_nodes.add(neighbor)
                    queue.append((neighbor, next_dist))

        # Cycle-safe path extraction for each affected service
        for target_id in affected_services:
            try:
                # Find all simple paths up to max_hops
                simple_paths = list(nx.all_simple_paths(G_prop, root_service_id, target_id, cutoff=max_hops))
                # Take up to 3 primary paths
                for p in simple_paths[:3]:
                    hop_count = len(p) - 1
                    dep_types = []
                    for i in range(len(p) - 1):
                        edge_data = G_prop.get_edge_data(p[i], p[i+1]) or {}
                        dep_types.append(edge_data.get("dependency_type", "sync_http"))

                    path_names = [service_names.get(node_id, node_id) for node_id in p]
                    readable_flow = " -> ".join(path_names)

                    path_info = CascadePathInfo(
                        path=p,
                        path_names=path_names,
                        hop_count=hop_count,
                        dependency_types=dep_types,
                        risk_contribution=0.0,  # Will be populated by risk scorer
                        evidence=f"Failure propagates along call dependency path: {readable_flow}"
                    )
                    all_paths_info.append(path_info)
            except Exception:
                continue

        return affected_services, all_paths_info
