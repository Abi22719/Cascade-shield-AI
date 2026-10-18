from typing import List, Dict, Any, Optional
from pydantic import BaseModel

class CytoscapeNodeData(BaseModel):
    id: str
    label: str
    name: str
    service_type: str
    health_status: str
    cpu_usage: float
    memory_usage: float
    latency_ms: float
    error_rate: float
    request_volume: int
    description: Optional[str] = ""
    in_degree: int = 0
    out_degree: int = 0

class CytoscapeNode(BaseModel):
    data: CytoscapeNodeData

class CytoscapeEdgeData(BaseModel):
    id: str
    source: str
    target: str
    dependency_type: str
    description: Optional[str] = ""
    label: Optional[str] = ""

class CytoscapeEdge(BaseModel):
    data: CytoscapeEdgeData

class GraphSummary(BaseModel):
    total_services: int
    total_dependencies: int
    has_cycles: bool
    cycles_count: int
    is_dag: bool

class GraphResponse(BaseModel):
    nodes: List[CytoscapeNode]
    edges: List[CytoscapeEdge]
    summary: GraphSummary
    cycles: List[List[str]] = []

class ReachableServiceDetail(BaseModel):
    id: str
    name: str
    service_type: str
    health_status: str
    distance_hops: int
    is_direct: bool
    path_from_source: List[str]

class ImpactResponse(BaseModel):
    service_id: str
    service_name: Optional[str] = None
    found: bool
    reachable_count: int
    direct_dependents_count: int
    indirect_dependents_count: int
    direct_dependents: List[str]
    indirect_dependents: List[str]
    reachable_services: List[ReachableServiceDetail]
    impact_tiers: Dict[str, List[str]]
    paths: Dict[str, List[str]]
