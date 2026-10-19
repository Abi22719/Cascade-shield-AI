from typing import List, Dict, Any, Set, Tuple
import networkx as nx

from app.models.service import ServiceModel
from app.models.dependency import DependencyModel

class DependencyAnalyzer:
    @staticmethod
    def build_networkx_graphs(
        services: List[ServiceModel],
        dependencies: List[DependencyModel]
    ) -> Tuple[nx.DiGraph, nx.DiGraph]:
        """
        Builds two graphs:
        1. G_dep: Standard architecture dependency graph (caller -> callee, e.g. Order -> Payment).
        2. G_impact: Failure propagation graph (callee -> caller, e.g. Payment -> Order).
        """
        G_dep = nx.DiGraph()
        G_impact = nx.DiGraph()

        for s in services:
            G_dep.add_node(s.id, name=s.name, service_type=s.service_type)
            G_impact.add_node(s.id, name=s.name, service_type=s.service_type)

        for d in dependencies:
            if G_dep.has_node(d.source_service_id) and G_dep.has_node(d.target_service_id):
                # Standard dependency: caller (source) -> callee (target)
                G_dep.add_edge(d.source_service_id, d.target_service_id, dependency_type=d.dependency_type)
                # Failure propagation: callee (target) -> caller (source)
                G_impact.add_edge(d.target_service_id, d.source_service_id, dependency_type=d.dependency_type)

        return G_dep, G_impact

    @staticmethod
    def analyze_candidate_dependencies(
        candidate_id: str,
        affected_ids: List[str],
        G_impact: nx.DiGraph,
        max_hops: int = 5
    ) -> Tuple[float, List[List[str]], List[str], List[str]]:
        """
        Evaluates graph reachability from candidate_id to affected_ids.
        Returns:
        - dependency_coverage_ratio (0.0 to 1.0)
        - supporting_paths (list of node ID paths)
        - reachable_affected (affected services reachable from candidate)
        - unreachable_affected (affected services with no path from candidate)
        """
        if not G_impact.has_node(candidate_id):
            return 0.0, [], [], affected_ids

        targets_to_check = [a for a in affected_ids if a != candidate_id]
        if not targets_to_check:
            # Candidate is the only affected service
            return 1.0, [], [], []

        reachable: List[str] = []
        unreachable: List[str] = []
        all_paths: List[List[str]] = []

        for target in targets_to_check:
            if not G_impact.has_node(target):
                unreachable.append(target)
                continue

            try:
                paths = list(nx.all_simple_paths(G_impact, candidate_id, target, cutoff=max_hops))
                if paths:
                    reachable.append(target)
                    all_paths.extend(paths[:3])  # top 3 shortest/cleanest paths
                else:
                    unreachable.append(target)
            except Exception:
                unreachable.append(target)

        coverage_ratio = len(reachable) / max(1, len(targets_to_check))
        return round(coverage_ratio, 2), all_paths, reachable, unreachable
