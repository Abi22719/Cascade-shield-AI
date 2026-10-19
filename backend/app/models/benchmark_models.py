import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Integer, Float, Text, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from app.database.database import Base

def generate_uuid() -> str:
    return str(uuid.uuid4())

class BenchmarkDatasetModel(Base):
    __tablename__ = "benchmark_datasets"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    name = Column(String(128), nullable=False, index=True)
    description = Column(Text, nullable=True)
    dataset_type = Column(String(32), nullable=False, default="synthetic")  # synthetic, hybrid, curated
    seed = Column(Integer, nullable=False, default=42)
    scenario_count = Column(Integer, nullable=False, default=0)
    schema_version = Column(String(16), nullable=False, default="1.0.0")
    metadata_json = Column(Text, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    # Relationships
    scenarios = relationship("BenchmarkScenarioModel", back_populates="dataset", cascade="all, delete-orphan", order_by="BenchmarkScenarioModel.created_at")
    experiments = relationship("BenchmarkExperimentModel", back_populates="dataset")

class BenchmarkScenarioModel(Base):
    __tablename__ = "benchmark_scenarios"

    id = Column(String(64), primary_key=True)
    dataset_id = Column(String(36), ForeignKey("benchmark_datasets.id", ondelete="CASCADE"), nullable=False, index=True)
    name = Column(String(128), nullable=False)
    scenario_type = Column(String(64), nullable=False)
    input_json = Column(Text, nullable=False)
    ground_truth_json = Column(Text, nullable=False)
    data_source = Column(String(32), nullable=False, default="synthetic")
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    # Relationships
    dataset = relationship("BenchmarkDatasetModel", back_populates="scenarios")

class BenchmarkExperimentModel(Base):
    __tablename__ = "benchmark_experiments"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    name = Column(String(128), nullable=False, index=True)
    description = Column(Text, nullable=True)
    dataset_id = Column(String(36), ForeignKey("benchmark_datasets.id", ondelete="SET NULL"), nullable=True, index=True)
    selected_modules_json = Column(Text, nullable=False)
    selected_methods_json = Column(Text, nullable=True)
    configuration_json = Column(Text, nullable=True)
    random_seed = Column(Integer, nullable=False, default=42)
    repetitions = Column(Integer, nullable=False, default=1)
    status = Column(String(32), nullable=False, default="CREATED", index=True)  # CREATED, RUNNING, COMPLETED, FAILED, CANCELLED
    progress = Column(Float, nullable=False, default=0.0)  # 0.0 to 100.0
    overall_resilience_score = Column(Float, nullable=True)
    summary_json = Column(Text, nullable=True)
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    # Relationships
    dataset = relationship("BenchmarkDatasetModel", back_populates="experiments")
    results = relationship("BenchmarkResultModel", back_populates="experiment", cascade="all, delete-orphan", order_by="BenchmarkResultModel.created_at")
    comparisons = relationship("BenchmarkComparisonModel", back_populates="experiment", cascade="all, delete-orphan", order_by="BenchmarkComparisonModel.created_at")
    reports = relationship("BenchmarkReportModel", back_populates="experiment", cascade="all, delete-orphan", order_by="desc(BenchmarkReportModel.created_at)")

class BenchmarkResultModel(Base):
    __tablename__ = "benchmark_results"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    experiment_id = Column(String(36), ForeignKey("benchmark_experiments.id", ondelete="CASCADE"), nullable=False, index=True)
    scenario_id = Column(String(64), nullable=True, index=True)
    module_name = Column(String(32), nullable=False, index=True)
    method_name = Column(String(64), nullable=False)
    metric_name = Column(String(64), nullable=False, index=True)
    metric_value = Column(Float, nullable=False)
    metric_unit = Column(String(16), nullable=False, default="ratio")
    sample_count = Column(Integer, nullable=False, default=1)
    metadata_json = Column(Text, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    # Relationships
    experiment = relationship("BenchmarkExperimentModel", back_populates="results")

class BenchmarkComparisonModel(Base):
    __tablename__ = "benchmark_comparisons"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    experiment_id = Column(String(36), ForeignKey("benchmark_experiments.id", ondelete="CASCADE"), nullable=False, index=True)
    comparison_name = Column(String(128), nullable=False)
    baseline_name = Column(String(64), nullable=False)
    candidate_name = Column(String(64), nullable=False)
    comparison_metrics_json = Column(Text, nullable=False)
    interpretation = Column(Text, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    # Relationships
    experiment = relationship("BenchmarkExperimentModel", back_populates="comparisons")

class BenchmarkReportModel(Base):
    __tablename__ = "benchmark_reports"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    experiment_id = Column(String(36), ForeignKey("benchmark_experiments.id", ondelete="CASCADE"), nullable=False, index=True)
    report_format = Column(String(16), nullable=False, default="json")  # json, csv, markdown
    report_metadata_json = Column(Text, nullable=True)
    content = Column(Text, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    # Relationships
    experiment = relationship("BenchmarkExperimentModel", back_populates="reports")

class BenchmarkConfigModel(Base):
    __tablename__ = "benchmark_config"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    config_key = Column(String(64), unique=True, index=True, nullable=False)
    config_value = Column(Text, nullable=False)
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)
