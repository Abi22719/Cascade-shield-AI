import json
import random
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from app.database.benchmark_repository import BenchmarkRepository
from app.models.benchmark_models import BenchmarkDatasetModel, BenchmarkScenarioModel
from app.schemas.benchmark_schemas import BenchmarkDatasetGenerateRequest

CANONICAL_BENCHMARK_SCENARIOS: List[Dict[str, Any]] = [
    {
        "id": "scn-01-payment-down",
        "name": "Single Service Unavailable (Payment Gateway)",
        "scenario_type": "single_service_unavailable",
        "input_config": {
            "target_service_ids": ["srv-payment"],
            "failure_type": "service_unavailable",
            "severity": "severe",
            "start_step": 1,
            "duration_steps": 4,
            "parameters": {"error_rate": 100.0, "latency_ms": 3000.0}
        },
        "ground_truth": {
            "expected_anomalies": ["srv-payment", "srv-order", "srv-gateway"],
            "expected_affected_services": ["srv-payment", "srv-order", "srv-gateway"],
            "expected_failure_paths": [["srv-payment", "srv-order", "srv-gateway"]],
            "expected_root_cause": "srv-payment",
            "expected_diagnostic_actions": ["inspect_service_health", "retrieve_anomaly_alerts", "reevaluate_root_causes"],
            "expected_recovery_strategy": "balanced",
            "expected_validation_outcome": "VERIFIED_SUCCESS"
        }
    },
    {
        "id": "scn-02-db-latency",
        "name": "Database High Latency Storm",
        "scenario_type": "database_latency_storm",
        "input_config": {
            "target_service_ids": ["srv-database"],
            "failure_type": "high_latency",
            "severity": "severe",
            "start_step": 1,
            "duration_steps": 5,
            "parameters": {"latency_ms": 2800.0, "connection_pool_used": 100}
        },
        "ground_truth": {
            "expected_anomalies": ["srv-database", "srv-payment", "srv-product", "srv-order", "srv-gateway"],
            "expected_affected_services": ["srv-database", "srv-product", "srv-order", "srv-gateway"],
            "expected_failure_paths": [
                ["srv-database", "srv-product", "srv-gateway"],
                ["srv-database", "srv-order", "srv-gateway"]
            ],
            "expected_root_cause": "srv-database",
            "expected_diagnostic_actions": ["inspect_service_health", "inspect_dependency", "reevaluate_root_causes"],
            "expected_recovery_strategy": "balanced",
            "expected_validation_outcome": "VERIFIED_SUCCESS"
        }
    },
    {
        "id": "scn-03-auth-failure",
        "name": "Authentication Token Verification Crash",
        "scenario_type": "auth_failure",
        "input_config": {
            "target_service_ids": ["srv-auth"],
            "failure_type": "error_rate_surge",
            "severity": "severe",
            "start_step": 1,
            "duration_steps": 3,
            "parameters": {"error_rate": 88.0, "status_code": 500}
        },
        "ground_truth": {
            "expected_anomalies": ["srv-auth", "srv-gateway"],
            "expected_affected_services": ["srv-auth", "srv-gateway"],
            "expected_failure_paths": [["srv-auth", "srv-gateway"]],
            "expected_root_cause": "srv-auth",
            "expected_diagnostic_actions": ["inspect_service_health", "compare_metrics_baseline"],
            "expected_recovery_strategy": "fastest_recovery",
            "expected_validation_outcome": "VERIFIED_SUCCESS"
        }
    },
    {
        "id": "scn-04-product-cascade",
        "name": "Catalog Dependency Failure Propagation",
        "scenario_type": "dependency_cascade",
        "input_config": {
            "target_service_ids": ["srv-product"],
            "failure_type": "service_unavailable",
            "severity": "moderate",
            "start_step": 1,
            "duration_steps": 4,
            "parameters": {"error_rate": 75.0}
        },
        "ground_truth": {
            "expected_anomalies": ["srv-product", "srv-gateway"],
            "expected_affected_services": ["srv-product", "srv-gateway"],
            "expected_failure_paths": [["srv-product", "srv-gateway"]],
            "expected_root_cause": "srv-product",
            "expected_diagnostic_actions": ["trace_failure_paths", "inspect_cascade_prediction"],
            "expected_recovery_strategy": "balanced",
            "expected_validation_outcome": "VERIFIED_SUCCESS"
        }
    },
    {
        "id": "scn-05-cpu-saturation",
        "name": "Order Service Thread Saturation (CPU 98%)",
        "scenario_type": "cpu_saturation",
        "input_config": {
            "target_service_ids": ["srv-order"],
            "failure_type": "cpu_saturation",
            "severity": "severe",
            "start_step": 1,
            "duration_steps": 4,
            "parameters": {"cpu_usage": 98.5}
        },
        "ground_truth": {
            "expected_anomalies": ["srv-order", "srv-gateway"],
            "expected_affected_services": ["srv-order", "srv-gateway"],
            "expected_failure_paths": [["srv-order", "srv-gateway"]],
            "expected_root_cause": "srv-order",
            "expected_diagnostic_actions": ["retrieve_service_metrics", "compare_metrics_baseline"],
            "expected_recovery_strategy": "fastest_recovery",
            "expected_validation_outcome": "VERIFIED_SUCCESS"
        }
    },
    {
        "id": "scn-06-memory-leak",
        "name": "Cache Service Heap Exhaustion & Eviction Collapse",
        "scenario_type": "memory_leak",
        "input_config": {
            "target_service_ids": ["srv-cache"],
            "failure_type": "memory_exhaustion",
            "severity": "severe",
            "start_step": 1,
            "duration_steps": 5,
            "parameters": {"memory_usage": 96.0}
        },
        "ground_truth": {
            "expected_anomalies": ["srv-cache", "srv-product"],
            "expected_affected_services": ["srv-cache", "srv-product", "srv-gateway"],
            "expected_failure_paths": [["srv-cache", "srv-product", "srv-gateway"]],
            "expected_root_cause": "srv-cache",
            "expected_diagnostic_actions": ["inspect_service_health", "retrieve_service_metrics"],
            "expected_recovery_strategy": "lowest_risk",
            "expected_validation_outcome": "VERIFIED_SUCCESS"
        }
    },
    {
        "id": "scn-07-gateway-error-surge",
        "name": "Edge Gateway 5xx Spike & Connection Storm",
        "scenario_type": "error_rate_surge",
        "input_config": {
            "target_service_ids": ["srv-gateway"],
            "failure_type": "error_rate_surge",
            "severity": "severe",
            "start_step": 1,
            "duration_steps": 3,
            "parameters": {"error_rate": 65.0}
        },
        "ground_truth": {
            "expected_anomalies": ["srv-gateway"],
            "expected_affected_services": ["srv-gateway"],
            "expected_failure_paths": [["srv-gateway"]],
            "expected_root_cause": "srv-gateway",
            "expected_diagnostic_actions": ["inspect_service_health", "retrieve_anomaly_alerts"],
            "expected_recovery_strategy": "fastest_recovery",
            "expected_validation_outcome": "VERIFIED_SUCCESS"
        }
    },
    {
        "id": "scn-08-multi-failure",
        "name": "Concurrent Payment Gateway and Cache Cluster Outage",
        "scenario_type": "multi_service_failure",
        "input_config": {
            "target_service_ids": ["srv-payment", "srv-cache"],
            "failure_type": "service_unavailable",
            "severity": "severe",
            "start_step": 1,
            "duration_steps": 4,
            "parameters": {"concurrent_nodes": 2}
        },
        "ground_truth": {
            "expected_anomalies": ["srv-payment", "srv-cache", "srv-order", "srv-product", "srv-gateway"],
            "expected_affected_services": ["srv-payment", "srv-cache", "srv-order", "srv-product", "srv-gateway"],
            "expected_failure_paths": [
                ["srv-payment", "srv-order", "srv-gateway"],
                ["srv-cache", "srv-product", "srv-gateway"]
            ],
            "expected_root_cause": "srv-payment",
            "expected_diagnostic_actions": ["trace_failure_paths", "compare_hypotheses", "reevaluate_root_causes"],
            "expected_recovery_strategy": "balanced",
            "expected_validation_outcome": "VERIFIED_SUCCESS"
        }
    },
    {
        "id": "scn-09-flapping-instability",
        "name": "Service Flapping and Post-Recovery Instability",
        "scenario_type": "flapping_instability",
        "input_config": {
            "target_service_ids": ["srv-user"],
            "failure_type": "high_latency",
            "severity": "moderate",
            "start_step": 1,
            "duration_steps": 5,
            "parameters": {"flapping_cycle": True}
        },
        "ground_truth": {
            "expected_anomalies": ["srv-user", "srv-auth"],
            "expected_affected_services": ["srv-user", "srv-auth", "srv-gateway"],
            "expected_failure_paths": [["srv-user", "srv-auth", "srv-gateway"]],
            "expected_root_cause": "srv-user",
            "expected_diagnostic_actions": ["retrieve_service_metrics", "compare_timestamps"],
            "expected_recovery_strategy": "lowest_risk",
            "expected_validation_outcome": "PARTIAL_SUCCESS"
        }
    },
    {
        "id": "scn-10-partial-recovery",
        "name": "Database Deadlock with Rollback Contingency",
        "scenario_type": "partial_recovery",
        "input_config": {
            "target_service_ids": ["srv-database"],
            "failure_type": "database_starvation",
            "severity": "severe",
            "start_step": 1,
            "duration_steps": 4,
            "parameters": {"deadlock_lock": True}
        },
        "ground_truth": {
            "expected_anomalies": ["srv-database", "srv-order", "srv-payment"],
            "expected_affected_services": ["srv-database", "srv-order", "srv-gateway"],
            "expected_failure_paths": [["srv-database", "srv-order", "srv-gateway"]],
            "expected_root_cause": "srv-database",
            "expected_diagnostic_actions": ["inspect_service_health", "identify_missing_evidence"],
            "expected_recovery_strategy": "fastest_recovery",
            "expected_validation_outcome": "FAILED"
        }
    }
]

class BenchmarkDatasetService:
    """
    Manages benchmark datasets, scenario generators, and ground-truth specifications.
    Ensures ground-truth labels remain strictly isolated from algorithm outputs.
    """

    @classmethod
    def generate_standard_dataset(
        cls,
        db: Session,
        req: Optional[BenchmarkDatasetGenerateRequest] = None
    ) -> BenchmarkDatasetModel:
        name = req.name if req else "Standard 10-Scenario Cloud Failure Benchmark"
        desc = req.description if req else "Standard synthetic suite across 10 reproducible cloud resilience failure archetypes."
        seed = req.seed if req else 42
        dtype = req.dataset_type if req else "synthetic"

        dataset = BenchmarkRepository.create_dataset(db, {
            "name": name,
            "description": desc,
            "dataset_type": dtype,
            "seed": seed,
            "scenario_count": len(CANONICAL_BENCHMARK_SCENARIOS),
            "schema_version": "1.0.0",
            "metadata": {
                "generated_at": str(random.Random(seed).randint(1000, 9999)),
                "synthetic_ground_truth_isolated": True,
                "scenarios": [s["id"] for s in CANONICAL_BENCHMARK_SCENARIOS]
            }
        })

        for scn in CANONICAL_BENCHMARK_SCENARIOS:
            BenchmarkRepository.create_scenario(db, {
                "id": f"{dataset.id[:8]}-{scn['id']}",
                "dataset_id": dataset.id,
                "name": scn["name"],
                "scenario_type": scn["scenario_type"],
                "input_config": scn["input_config"],
                "ground_truth": scn["ground_truth"],
                "data_source": "synthetic"
            })

        db.commit()
        db.refresh(dataset)
        return dataset

    generate_canonical_dataset = generate_standard_dataset

    @classmethod
    def get_or_create_default_dataset(cls, db: Session) -> BenchmarkDatasetModel:
        datasets, total = BenchmarkRepository.list_datasets(db, skip=0, limit=1)
        if total > 0 and len(datasets) > 0:
            return datasets[0]
        return cls.generate_standard_dataset(db)
