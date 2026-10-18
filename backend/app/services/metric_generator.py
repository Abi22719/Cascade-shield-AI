from datetime import datetime, timezone, timedelta
from typing import List, Dict, Optional
import numpy as np
from sqlalchemy.orm import Session
from app.models.service import ServiceModel
from app.schemas.metric_schema import MetricPoint

class MetricGenerator:
    @staticmethod
    def get_latest_metrics_from_services(db: Session) -> List[MetricPoint]:
        """
        Extracts current simulated metrics for all active services in the digital twin.
        """
        services = db.query(ServiceModel).all()
        now = datetime.now(timezone.utc)
        results = []

        for s in services:
            results.append(
                MetricPoint(
                    timestamp=s.updated_at if s.updated_at else now,
                    service_id=s.id,
                    service_name=s.name,
                    cpu_usage=float(s.cpu_usage),
                    memory_usage=float(s.memory_usage),
                    latency_ms=float(s.latency_ms),
                    error_rate=float(s.error_rate),
                    request_volume=int(s.request_volume),
                    data_source="simulated"
                )
            )
        return results

    @staticmethod
    def generate_service_metric_history(
        service: ServiceModel,
        points_count: int = 40,
        interval_minutes: int = 1,
        condition_type: str = "auto"
    ) -> List[MetricPoint]:
        """
        Generates realistic synthetic time-series history for a cloud service.
        Supports:
        - 'normal': baseline healthy operational variance
        - 'degradation': creeping resource consumption (memory leak / thread pool exhaustion)
        - 'spike': abrupt latency and error rate spikes
        - 'unusual_combination': low CPU with high latency and queue build-up
        - 'auto': automatically infers pattern based on service current health status
        """
        now = datetime.now(timezone.utc)
        # Use deterministic seed based on service ID to maintain reproducible curves
        seed = sum(ord(c) for c in service.id)
        rng = np.random.RandomState(seed)

        base_cpu = float(service.cpu_usage)
        base_mem = float(service.memory_usage)
        base_lat = float(service.latency_ms)
        base_err = float(service.error_rate)
        base_req = int(service.request_volume)

        # Decide condition pattern
        if condition_type == "auto":
            if service.health_status == "CRITICAL":
                condition_type = "spike"
            elif service.health_status == "WARNING":
                condition_type = "degradation"
            else:
                condition_type = "normal"

        history: List[MetricPoint] = []

        for i in range(points_count - 1, -1, -1):
            point_time = now - timedelta(minutes=i * interval_minutes)
            progress = (points_count - 1 - i) / max(1, points_count - 1)

            # Random noise
            cpu_noise = rng.normal(0, 1.8)
            mem_noise = rng.normal(0, 1.2)
            lat_noise = rng.normal(0, 3.5)
            err_noise = rng.normal(0, 0.05)
            req_noise = int(rng.normal(0, 40))

            if condition_type == "degradation":
                # Upward ramp over the last 15 points
                ramp = max(0.0, (progress - 0.5) * 2.0)
                cur_cpu = min(98.0, base_cpu + ramp * 25.0 + cpu_noise)
                cur_mem = min(98.0, base_mem + ramp * 35.0 + mem_noise)
                cur_lat = max(5.0, base_lat + ramp * 450.0 + lat_noise)
                cur_err = max(0.0, base_err + ramp * 4.5 + err_noise)
                cur_req = max(10, base_req + req_noise)
            elif condition_type == "spike":
                # Abrupt spike in the last 6 points
                is_spiking = i <= 6
                spike_factor = 2.8 if is_spiking else 1.0
                cur_cpu = min(99.0, base_cpu * (1.8 if is_spiking else 1.0) + cpu_noise)
                cur_mem = min(98.0, base_mem + mem_noise)
                cur_lat = max(5.0, base_lat * spike_factor + lat_noise)
                cur_err = max(0.0, (base_err + (12.5 if is_spiking else 0.0)) + err_noise)
                cur_req = max(10, int(base_req * (1.6 if is_spiking else 1.0)) + req_noise)
            elif condition_type == "unusual_combination":
                # Low CPU, very high latency (e.g. external blocking call / deadlock)
                is_anom = i <= 8
                cur_cpu = max(5.0, (base_cpu * 0.4 if is_anom else base_cpu) + cpu_noise)
                cur_mem = min(95.0, base_mem + mem_noise)
                cur_lat = max(5.0, (base_lat + 600.0 if is_anom else base_lat) + lat_noise)
                cur_err = max(0.0, (base_err + 3.0 if is_anom else base_err) + err_noise)
                cur_req = max(10, base_req + req_noise)
            else:
                # Normal operating variance
                cur_cpu = max(2.0, min(95.0, base_cpu + cpu_noise))
                cur_mem = max(5.0, min(95.0, base_mem + mem_noise))
                cur_lat = max(3.0, base_lat + lat_noise)
                cur_err = max(0.0, min(100.0, base_err + err_noise))
                cur_req = max(10, base_req + req_noise)

            history.append(
                MetricPoint(
                    timestamp=point_time,
                    service_id=service.id,
                    service_name=service.name,
                    cpu_usage=round(cur_cpu, 1),
                    memory_usage=round(cur_mem, 1),
                    latency_ms=round(cur_lat, 1),
                    error_rate=round(cur_err, 2),
                    request_volume=cur_req,
                    data_source="simulated"
                )
            )

        return history
