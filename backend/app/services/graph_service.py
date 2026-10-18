from typing import List, Dict, Any, Optional, Tuple
import networkx as nx
from app.models.service import ServiceModel
from app.models.dependency import DependencyModel

class GraphService:
    @staticmethod
    def build_networkx_graph(
        services: List[ServiceModel],
        dependencies: List[DependencyModel]
    ) -> nx.DiGraph:
        """
        Constructs a NetworkX DiGraph from database records.
        """
        G = nx.DiGraph()

        for s in services:
            G.add_node(
                s.id,
                name=s.name,
                service_type=s.service_type,
                description=s.description or "",
                health_status=s.health_status,
                cpu_usage=s.cpu_usage,
                memory_usage=s.memory_usage,
                latency_ms=s.latency_ms,
                error_rate=s.error_rate,
                request_volume=s.request_volume,
                updated_at=s.updated_at.isoformat() if s.updated_at else None
            )

        for d in dependencies:
            # Only add edge if both source and target exist in nodes
            if G.has_node(d.source_service_id) and G.has_node(d.target_service_id):
                G.add_edge(
                    d.source_service_id,
                    d.target_service_id,
                    id=d.id,
                    dependency_type=d.dependency_type,
                    description=d.description or ""
                )

        return G

    @staticmethod
    def detect_all_cycles(G: nx.DiGraph) -> List[List[str]]:
        """
        Detects all simple cycles in the directed graph.
        Returns a list of cycle node id sequences.
        """
        try:
            cycles = list(nx.simple_cycles(G))
            return cycles
        except Exception:
            return []

    @staticmethod
    def will_form_cycle(G: nx.DiGraph, source_id: str, target_id: str) -> Tuple[bool, Optional[List[str]]]:
        """
        Checks if adding directed edge source_id -> target_id creates a cycle.
        If source_id == target_id, it is a self-loop (cycle of length 1).
        If nx.has_path(G, target_id, source_id), adding source_id -> target_id creates a cycle.
        Returns (has_cycle, cycle_path)
        """
        if source_id == target_id:
            return True, [source_id, source_id]

        if not G.has_node(source_id) or not G.has_node(target_id):
            return False, None

        if nx.has_path(G, target_id, source_id):
            try:
                path = nx.shortest_path(G, target_id, source_id)
                # Form cycle: source -> target -> ... -> source
                return True, [source_id] + path
            except Exception:
                return True, [source_id, target_id, source_id]

        return False, None

    @staticmethod
    def to_cytoscape_elements(G: nx.DiGraph) -> Dict[str, Any]:
        """
        Formats graph nodes and edges into Cytoscape.js compatible data structure.
        """
        nodes = []
        for node_id, attrs in G.nodes(data=True):
            in_degree = G.in_degree(node_id)
            out_degree = G.out_degree(node_id)
            nodes.append({
                "data": {
                    "id": node_id,
                    "label": attrs.get("name", node_id),
                    "name": attrs.get("name", node_id),
                    "service_type": attrs.get("service_type", "compute"),
                    "health_status": attrs.get("health_status", "HEALTHY"),
                    "cpu_usage": attrs.get("cpu_usage", 0.0),
                    "memory_usage": attrs.get("memory_usage", 0.0),
                    "latency_ms": attrs.get("latency_ms", 0.0),
                    "error_rate": attrs.get("error_rate", 0.0),
                    "request_volume": attrs.get("request_volume", 0),
                    "description": attrs.get("description", ""),
                    "in_degree": in_degree,
                    "out_degree": out_degree,
                }
            })

        edges = []
        for u, v, attrs in G.edges(data=True):
            edges.append({
                "data": {
                    "id": attrs.get("id", f"dep-{u}-{v}"),
                    "source": u,
                    "target": v,
                    "dependency_type": attrs.get("dependency_type", "sync_http"),
                    "description": attrs.get("description", ""),
                    "label": attrs.get("dependency_type", "sync_http")
                }
            })

        cycles = GraphService.detect_all_cycles(G)

        return {
            "nodes": nodes,
            "edges": edges,
            "summary": {
                "total_services": G.number_of_nodes(),
                "total_dependencies": G.number_of_edges(),
                "has_cycles": len(cycles) > 0,
                "cycles_count": len(cycles),
                "is_dag": nx.is_directed_acyclic_graph(G)
            },
            "cycles": cycles
        }

    @staticmethod
    def get_downstream_impact(G: nx.DiGraph, service_id: str) -> Dict[str, Any]:
        """
        Calculates downstream services reachable from service_id.
        Computes shortest paths, depth tiers, and impact boundary.
        Does not claim to predict actual failures.
        """
        if not G.has_node(service_id):
            return {
                "service_id": service_id,
                "found": False,
                "reachable_count": 0,
                "reachable_services": [],
                "direct_dependents": [],
                "indirect_dependents": [],
                "impact_tiers": {},
                "paths": {}
            }

        # Descendants: all nodes reachable by following directed edges out from service_id
        descendants = nx.descendants(G, service_id)
        
        # Direct outgoing targets (Tier 1)
        direct_dependents = list(G.successors(service_id))
        
        impact_tiers: Dict[str, List[str]] = {}
        paths: Dict[str, List[str]] = {}
        reachable_details = []

        for desc_id in descendants:
            try:
                shortest_path = nx.shortest_path(G, service_id, desc_id)
                depth = len(shortest_path) - 1
                depth_key = str(depth)
                paths[desc_id] = shortest_path
                
                if depth_key not in impact_tiers:
                    impact_tiers[depth_key] = []
                impact_tiers[depth_key].append(desc_id)
                
                node_data = G.nodes[desc_id]
                reachable_details.append({
                    "id": desc_id,
                    "name": node_data.get("name", desc_id),
                    "service_type": node_data.get("service_type", "compute"),
                    "health_status": node_data.get("health_status", "HEALTHY"),
                    "distance_hops": depth,
                    "is_direct": depth == 1,
                    "path_from_source": shortest_path
                })
            except Exception:
                continue

        # Sort reachable_details by distance_hops ascending
        reachable_details.sort(key=lambda x: (x["distance_hops"], x["name"]))
        indirect_dependents = [d["id"] for d in reachable_details if not d["is_direct"]]

        return {
            "service_id": service_id,
            "service_name": G.nodes[service_id].get("name", service_id),
            "found": True,
            "reachable_count": len(descendants),
            "direct_dependents_count": len(direct_dependents),
            "indirect_dependents_count": len(indirect_dependents),
            "direct_dependents": direct_dependents,
            "indirect_dependents": indirect_dependents,
            "reachable_services": reachable_details,
            "impact_tiers": impact_tiers,
            "paths": paths
        }
