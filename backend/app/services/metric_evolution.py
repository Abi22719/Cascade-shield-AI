import math
import random
from typing import Dict, Any, List, Optional
from app.schemas.simulation_schema import SimulatedServiceState

class MetricEvolutionService:
    """
    Enforces physical metric boundaries (e.g. CPU/Memory 0-100%, Error Rate 0-100%, Latency >= 0ms)
    and generates synthetic metric time-series progressions.
    """

    @staticmethod
    def clamp_service_metrics(service: SimulatedServiceState):
        service.cpu_usage = round(max(0.0, min(100.0, service.cpu_usage)), 1)
        service.memory_usage = round(max(0.0, min(100.0, service.memory_usage)), 1)
        service.latency_ms = round(max(1.0, min(10000.0, service.latency_ms)), 1)
        service.error_rate = round(max(0.0, min(100.0, service.error_rate)), 2)
        service.request_volume = max(0, min(50000, service.request_volume))
        service.risk_score = round(max(0.0, min(100.0, service.risk_score)), 1)

    @staticmethod
    def apply_step_fluctuation(service: SimulatedServiceState, step: int, seed: Optional[int] = None):
        """
        Adds slight non-critical operational fluctuation to keep simulated metrics realistic.
        Uses reproducible pseudo-randomness if seed is specified.
        """
        rng = random.Random(seed + step if seed is not None else None) if seed is not None else None
        jitter = (rng.uniform(-1.0, 1.0)) if rng else (math.sin(step) * 0.8)

        # Apply minor variation only if not in severe failure
        if service.health_status == "HEALTHY":
            service.cpu_usage = max(10.0, min(60.0, service.cpu_usage + jitter * 1.5))
            service.memory_usage = max(15.0, min(70.0, service.memory_usage + jitter * 0.8))
            service.latency_ms = max(5.0, min(120.0, service.latency_ms + jitter * 3.0))
        
        MetricEvolutionService.clamp_service_metrics(service)
