import copy
from typing import Dict, Any, List, Optional
import networkx as nx
from sqlalchemy.orm import Session

from app.models.service import ServiceModel
from app.models.dependency import DependencyModel
from app.schemas.simulation_schema import (
    SimulatedServiceState,
    SimulationStepState,
    ScenarioConfigSchema
)

class SimulationState:
    """
    Completely isolated in-memory simulation state.
    Clones baseline digital twin services and dependency topologies into an immutable snapshot.
    Ensures ZERO mutation of database models or live metrics.
    """

    def __init__(self, scenario_id: str, config: ScenarioConfigSchema, random_seed: Optional[int] = None):
        self.scenario_id = scenario_id
        self.config = config
        self.random_seed = random_seed
        self.current_step = 0
        
        # In-memory service state: {service_id: SimulatedServiceState}
        self.services: Dict[str, SimulatedServiceState] = {}
        # Baseline snapshot for recovery comparison
        self.baseline_services: Dict[str, SimulatedServiceState] = {}
        
        # Directed propagation graph: callee -> caller (G_prop = G_rev)
        self.G_prop = nx.DiGraph()
        # Architectural dependency graph: caller -> callee
        self.G_dep = nx.DiGraph()

        # Tracking sets
        self.initial_failure_services: set = set()
        self.active_failure_services: set = set()
        self.impacted_services: set = set()
        self.recovered_services: set = set()

        # Step-by-step history: List[SimulationStepState]
        self.step_history: List[SimulationStepState] = []
        # All events: List[Dict[str, Any]]
        self.all_events: List[Dict[str, Any]] = []

    @classmethod
    def initialize_from_db(
        cls, 
        db: Session, 
        scenario_id: str, 
        config: ScenarioConfigSchema, 
        random_seed: Optional[int] = None
    ) -> "SimulationState":
        instance = cls(scenario_id=scenario_id, config=config, random_seed=random_seed)

        # 1. Read real digital twin services (Read-Only)
        services = db.query(ServiceModel).all()
        for s in services:
            state = SimulatedServiceState(
                service_id=s.id,
                service_name=s.name,
                health_status=s.health_status or "HEALTHY",
                cpu_usage=float(getattr(s, "cpu_usage", 25.0)),
                memory_usage=float(getattr(s, "memory_usage", 35.0)),
                latency_ms=float(getattr(s, "latency_ms", 45.0)),
                error_rate=float(getattr(s, "error_rate", 0.05)),
                request_volume=int(getattr(s, "request_volume", 150)),
                risk_score=0.0,
                is_initial_failure=False,
                is_impacted=False,
                is_recovered=False
            )
            instance.services[s.id] = state
            instance.baseline_services[s.id] = copy.deepcopy(state)
            instance.G_dep.add_node(s.id, name=s.name, type=s.service_type)
            instance.G_prop.add_node(s.id, name=s.name, type=s.service_type)

        # 2. Read real dependencies
        deps = db.query(DependencyModel).all()
        for d in deps:
            # Caller -> Callee
            instance.G_dep.add_edge(d.source_service_id, d.target_service_id, protocol=d.dependency_type)
            # Callee -> Caller (Propagation)
            instance.G_prop.add_edge(d.target_service_id, d.source_service_id, protocol=d.dependency_type)

        return instance

    def record_step_snapshot(self, newly_impacted: List[str], recovered_in_step: List[str], step_events: List[Dict[str, Any]]):
        step_state = SimulationStepState(
            step_number=self.current_step,
            active_failures=list(self.active_failure_services),
            newly_impacted=newly_impacted,
            recovered=recovered_in_step,
            services={sid: copy.deepcopy(st) for sid, st in self.services.items()},
            events=step_events
        )
        self.step_history.append(step_state)
        self.all_events.extend(step_events)
