from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, ConfigDict

class BenchmarkConfigSchema(BaseModel):
    timeout_seconds: int = Field(60, ge=10, le=600, description="Experiment timeout in seconds")
    max_scenarios_per_run: int = Field(20, ge=1, le=100, description="Max scenarios per experiment run")
    default_random_seed: int = Field(42, description="Default seed for reproducibility")
    default_repetitions: int = Field(1, ge=1, le=10, description="Repetitions for statistical stability")
    component_weights: Dict[str, float] = Field(
        default_factory=lambda: {
            "detection": 0.15,
            "prediction": 0.15,
            "rca": 0.15,
            "diagnostic": 0.15,
            "simulation": 0.15,
            "recovery": 0.15,
            "validation": 0.10
        },
        description="Weights for the 0-100 overall resilience score"
    )
    export_formats: List[str] = Field(
        default_factory=lambda: ["json", "csv", "markdown"],
        description="Supported report export formats"
    )

class BenchmarkScenarioSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    dataset_id: str
    name: str
    scenario_type: str
    input_config: Dict[str, Any]
    ground_truth: Dict[str, Any]
    data_source: str = "synthetic"
    created_at: datetime

class BenchmarkDatasetSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    name: str
    description: Optional[str] = None
    dataset_type: str = "synthetic"
    seed: int = 42
    scenario_count: int = 0
    schema_version: str = "1.0.0"
    metadata: Optional[Dict[str, Any]] = None
    scenarios: Optional[List[BenchmarkScenarioSchema]] = None
    created_at: datetime

class BenchmarkDatasetGenerateRequest(BaseModel):
    name: str = Field("Standard 10-Scenario Cloud Failure Benchmark", min_length=2, max_length=128)
    description: Optional[str] = Field(
        "Standard synthetic suite across 10 reproducible cloud resilience failure archetypes.",
        max_length=512
    )
    seed: int = Field(42, description="Random seed for reproducible scenario generation")
    dataset_type: str = Field("synthetic", description="synthetic, hybrid, curated")

class BenchmarkExperimentCreateRequest(BaseModel):
    name: str = Field(..., min_length=2, max_length=128)
    description: Optional[str] = Field(None, max_length=512)
    dataset_id: Optional[str] = Field(None, description="Optional target dataset ID. If omitted, default dataset is used or generated")
    selected_modules: List[str] = Field(
        default_factory=lambda: ["module_2", "module_3", "module_4", "module_5", "module_6", "module_7", "module_8"],
        description="List of modules to benchmark: module_2, module_3, module_4, module_5, module_6, module_7, module_8, end_to_end"
    )
    selected_methods: Optional[Dict[str, List[str]]] = Field(
        default=None,
        description="Dictionary mapping module name to list of methods to test (e.g. {'module_2': ['threshold', 'isolation_forest', 'combined']})"
    )
    random_seed: int = Field(42, description="Seed for reproducible execution")
    repetitions: int = Field(1, ge=1, le=10, description="Number of execution repetitions")
    configuration: Optional[Dict[str, Any]] = Field(default=None, description="Optional overrides for weights, timeouts, etc.")

class BenchmarkResultSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    experiment_id: str
    scenario_id: Optional[str] = None
    module_name: str
    method_name: str
    metric_name: str
    metric_value: float
    metric_unit: str = "ratio"
    sample_count: int = 1
    metadata: Optional[Dict[str, Any]] = None
    created_at: datetime

class BenchmarkComparisonSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    experiment_id: str
    comparison_name: str
    baseline_name: str
    candidate_name: str
    comparison_metrics: Dict[str, Any]
    interpretation: Optional[str] = None
    created_at: datetime

class BenchmarkExperimentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    name: str
    description: Optional[str] = None
    dataset_id: Optional[str] = None
    selected_modules: List[str]
    selected_methods: Optional[Dict[str, List[str]]] = None
    random_seed: int
    repetitions: int
    status: str  # CREATED, RUNNING, COMPLETED, FAILED, CANCELLED
    progress: float = 0.0
    overall_resilience_score: Optional[float] = None
    summary: Optional[Dict[str, Any]] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    error_message: Optional[str] = None
    created_at: datetime
    results: List[BenchmarkResultSchema] = Field(default_factory=list)
    comparisons: List[BenchmarkComparisonSchema] = Field(default_factory=list)

class BenchmarkCompareRequest(BaseModel):
    experiment_ids: List[str] = Field(..., min_length=2, max_length=10)

class BenchmarkCompareResponse(BaseModel):
    experiments: List[Dict[str, Any]]
    best_experiment_id: Optional[str] = None
    resilience_score_comparison: Dict[str, float]
    summary_verdict: str

class BenchmarkEvaluationSummaryResponse(BaseModel):
    total_experiments: int
    completed_experiments: int
    failed_experiments: int
    available_datasets: int
    evaluated_modules_count: int
    average_resilience_score: float
    latest_experiment: Optional[Dict[str, Any]] = None
