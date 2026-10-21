"""
CascadeShield AI - Background Telemetry Daemon
Module 1: Cloud Digital Twin Telemetry Refresher

Periodically injects slight operational fluctuation (jitter) into healthy and degraded
services in the virtual digital twin database and updates timestamps, simulating
a continuous live telemetry feed from cloud monitoring agents (e.g. Prometheus / CloudWatch).
"""

import sys
import os
import time
import random
import logging
from datetime import datetime, timezone

# Ensure backend root is on python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.database.database import SessionLocal
from app.models.service import ServiceModel
from app.services.health_evaluator import evaluate_service_health
from app.database.dashboard_repository import DashboardRepository

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [TelemetryDaemon] %(levelname)s - %(message)s"
)
logger = logging.getLogger("telemetry_daemon")

def tick_telemetry(db, apply_jitter: bool = True) -> int:
    """
    Applies a single simulation cycle across all digital twin services.
    """
    services = db.query(ServiceModel).all()
    if not services:
        return 0

    now = datetime.now(timezone.utc)
    updated_count = 0

    for s in services:
        if apply_jitter and s.health_status in ["HEALTHY", "WARNING"]:
            # Minor non-critical operational drift
            s.cpu_usage = round(max(2.0, min(95.0, s.cpu_usage + random.uniform(-1.5, 1.5))), 1)
            s.memory_usage = round(max(5.0, min(95.0, s.memory_usage + random.uniform(-1.0, 1.0))), 1)
            s.latency_ms = round(max(1.0, min(3000.0, s.latency_ms + random.uniform(-2.0, 2.0))), 1)
            if s.error_rate < 5.0:
                s.error_rate = round(max(0.0, min(10.0, s.error_rate + random.uniform(-0.02, 0.02))), 2)
            s.request_volume = max(10, int(s.request_volume + random.randint(-25, 25)))

            # Recalculate health
            new_health, _ = evaluate_service_health(
                cpu_usage=s.cpu_usage,
                memory_usage=s.memory_usage,
                latency_ms=s.latency_ms,
                error_rate=s.error_rate
            )
            s.health_status = new_health
            updated_count += 1

        s.updated_at = now

    db.commit()
    return len(services)

def run_telemetry_loop(interval_seconds: int = 10, max_ticks: int = None):
    """
    Main daemon loop running continuously.
    """
    logger.info(f"Starting Digital Twin Telemetry Daemon (cycle interval: {interval_seconds}s)...")
    ticks = 0

    while True:
        try:
            db = SessionLocal()
            try:
                total = tick_telemetry(db)
                ticks += 1
                logger.info(f"Cycle #{ticks}: Refreshed telemetry across {total} services at {datetime.now(timezone.utc).strftime('%H:%M:%S UTC')}")
            finally:
                db.close()
        except Exception as e:
            logger.error(f"Error during telemetry tick: {e}")

        if max_ticks and ticks >= max_ticks:
            logger.info("Reached maximum cycles, terminating daemon.")
            break

        time.sleep(interval_seconds)

if __name__ == "__main__":
    interval = int(os.environ.get("REFRESH_INTERVAL_SECONDS", 10))
    run_telemetry_loop(interval_seconds=interval)
