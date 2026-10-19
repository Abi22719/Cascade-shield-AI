import json
from datetime import datetime, timezone
from typing import List, Optional, Dict, Any, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import desc

from app.models.benchmark_models import (
    BenchmarkDatasetModel,
    BenchmarkScenarioModel,
    BenchmarkExperimentModel,
    BenchmarkResultModel,
    BenchmarkComparisonModel,
    BenchmarkReportModel,
    BenchmarkConfigModel
)

class BenchmarkRepository:
    """
    CRUD repository for benchmark datasets, scenarios, experiments, results, and reports.
    """

    # --- Datasets ---
    @classmethod
    def create_dataset(cls, db: Session, data: Dict[str, Any]) -> BenchmarkDatasetModel:
        dataset = BenchmarkDatasetModel(
            name=data["name"],
            description=data.get("description"),
            dataset_type=data.get("dataset_type", "synthetic"),
            seed=int(data.get("seed", 42)),
            scenario_count=int(data.get("scenario_count", 0)),
            schema_version=data.get("schema_version", "1.0.0"),
            metadata_json=json.dumps(data.get("metadata", {})) if data.get("metadata") else None
        )
        db.add(dataset)
        db.flush()
        return dataset

    @classmethod
    def get_dataset(cls, db: Session, dataset_id: str) -> Optional[BenchmarkDatasetModel]:
        return db.query(BenchmarkDatasetModel).filter(BenchmarkDatasetModel.id == dataset_id).first()

    @classmethod
    def list_datasets(cls, db: Session, skip: int = 0, limit: int = 50) -> Tuple[List[BenchmarkDatasetModel], int]:
        query = db.query(BenchmarkDatasetModel)
        total = query.count()
        items = query.order_by(desc(BenchmarkDatasetModel.created_at)).offset(skip).limit(limit).all()
        return items, total

    # --- Scenarios ---
    @classmethod
    def create_scenario(cls, db: Session, data: Dict[str, Any]) -> BenchmarkScenarioModel:
        scenario = BenchmarkScenarioModel(
            id=data["id"],
            dataset_id=data["dataset_id"],
            name=data["name"],
            scenario_type=data["scenario_type"],
            input_json=json.dumps(data.get("input_config", {})),
            ground_truth_json=json.dumps(data.get("ground_truth", {})),
            data_source=data.get("data_source", "synthetic")
        )
        db.add(scenario)
        db.flush()
        return scenario

    @classmethod
    def get_scenario(cls, db: Session, scenario_id: str) -> Optional[BenchmarkScenarioModel]:
        return db.query(BenchmarkScenarioModel).filter(BenchmarkScenarioModel.id == scenario_id).first()

    @classmethod
    def list_scenarios_for_dataset(cls, db: Session, dataset_id: str) -> List[BenchmarkScenarioModel]:
        return db.query(BenchmarkScenarioModel).filter(
            BenchmarkScenarioModel.dataset_id == dataset_id
        ).order_by(BenchmarkScenarioModel.created_at).all()

    # --- Experiments ---
    @classmethod
    def create_experiment(cls, db: Session, data: Dict[str, Any]) -> BenchmarkExperimentModel:
        exp = BenchmarkExperimentModel(
            name=data["name"],
            description=data.get("description"),
            dataset_id=data.get("dataset_id"),
            selected_modules_json=json.dumps(data.get("selected_modules", [])),
            selected_methods_json=json.dumps(data.get("selected_methods", {})) if data.get("selected_methods") else None,
            configuration_json=json.dumps(data.get("configuration", {})) if data.get("configuration") else None,
            random_seed=int(data.get("random_seed", 42)),
            repetitions=int(data.get("repetitions", 1)),
            status=data.get("status", "CREATED"),
            progress=0.0
        )
        db.add(exp)
        db.flush()
        return exp

    @classmethod
    def get_experiment(cls, db: Session, experiment_id: str) -> Optional[BenchmarkExperimentModel]:
        return db.query(BenchmarkExperimentModel).filter(BenchmarkExperimentModel.id == experiment_id).first()

    @classmethod
    def list_experiments(
        cls, 
        db: Session, 
        skip: int = 0, 
        limit: int = 50, 
        status: Optional[str] = None
    ) -> Tuple[List[BenchmarkExperimentModel], int]:
        query = db.query(BenchmarkExperimentModel)
        if status:
            query = query.filter(BenchmarkExperimentModel.status == status)
        total = query.count()
        items = query.order_by(desc(BenchmarkExperimentModel.created_at)).offset(skip).limit(limit).all()
        return items, total

    @classmethod
    def update_experiment_status(
        cls,
        db: Session,
        experiment_id: str,
        status: str,
        progress: float = 0.0,
        error_message: Optional[str] = None,
        summary: Optional[Dict[str, Any]] = None,
        overall_score: Optional[float] = None
    ) -> Optional[BenchmarkExperimentModel]:
        exp = cls.get_experiment(db, experiment_id)
        if not exp:
            return None
        exp.status = status
        exp.progress = progress
        if status == "RUNNING" and not exp.started_at:
            exp.started_at = datetime.now(timezone.utc)
        if status in ["COMPLETED", "FAILED", "CANCELLED"]:
            exp.completed_at = datetime.now(timezone.utc)
        if error_message:
            exp.error_message = error_message
        if summary is not None:
            exp.summary_json = json.dumps(summary)
        if overall_score is not None:
            exp.overall_resilience_score = overall_score
        db.commit()
        db.refresh(exp)
        return exp

    # --- Results ---
    @classmethod
    def record_result(cls, db: Session, data: Dict[str, Any]) -> BenchmarkResultModel:
        res = BenchmarkResultModel(
            experiment_id=data["experiment_id"],
            scenario_id=data.get("scenario_id"),
            module_name=data["module_name"],
            method_name=data["method_name"],
            metric_name=data["metric_name"],
            metric_value=float(data["metric_value"]),
            metric_unit=data.get("metric_unit", "ratio"),
            sample_count=int(data.get("sample_count", 1)),
            metadata_json=json.dumps(data.get("metadata", {})) if data.get("metadata") else None
        )
        db.add(res)
        db.flush()
        return res

    @classmethod
    def get_results_for_experiment(
        cls, 
        db: Session, 
        experiment_id: str, 
        module_name: Optional[str] = None
    ) -> List[BenchmarkResultModel]:
        query = db.query(BenchmarkResultModel).filter(
            BenchmarkResultModel.experiment_id == experiment_id
        )
        if module_name:
            query = query.filter(BenchmarkResultModel.module_name == module_name)
        return query.order_by(BenchmarkResultModel.created_at).all()

    # --- Comparisons ---
    @classmethod
    def record_comparison(cls, db: Session, data: Dict[str, Any]) -> BenchmarkComparisonModel:
        comp = BenchmarkComparisonModel(
            experiment_id=data["experiment_id"],
            comparison_name=data["comparison_name"],
            baseline_name=data["baseline_name"],
            candidate_name=data["candidate_name"],
            comparison_metrics_json=json.dumps(data.get("comparison_metrics", {})),
            interpretation=data.get("interpretation")
        )
        db.add(comp)
        db.flush()
        return comp

    @classmethod
    def get_comparisons_for_experiment(cls, db: Session, experiment_id: str) -> List[BenchmarkComparisonModel]:
        return db.query(BenchmarkComparisonModel).filter(
            BenchmarkComparisonModel.experiment_id == experiment_id
        ).order_by(BenchmarkComparisonModel.created_at).all()

    # --- Reports ---
    @classmethod
    def create_report(cls, db: Session, data: Dict[str, Any]) -> BenchmarkReportModel:
        rep = BenchmarkReportModel(
            experiment_id=data["experiment_id"],
            report_format=data.get("report_format", "json"),
            report_metadata_json=json.dumps(data.get("report_metadata", {})),
            content=data.get("content")
        )
        db.add(rep)
        db.commit()
        db.refresh(rep)
        return rep

    @classmethod
    def get_report_for_experiment(cls, db: Session, experiment_id: str, report_format: str = "json") -> Optional[BenchmarkReportModel]:
        return db.query(BenchmarkReportModel).filter(
            BenchmarkReportModel.experiment_id == experiment_id,
            BenchmarkReportModel.report_format == report_format
        ).order_by(desc(BenchmarkReportModel.created_at)).first()

    # --- Config ---
    @classmethod
    def get_config(cls, db: Session, key: str, default: Optional[str] = None) -> Optional[str]:
        cfg = db.query(BenchmarkConfigModel).filter(BenchmarkConfigModel.config_key == key).first()
        return cfg.config_value if cfg else default

    @classmethod
    def set_config(cls, db: Session, key: str, value: str) -> BenchmarkConfigModel:
        cfg = db.query(BenchmarkConfigModel).filter(BenchmarkConfigModel.config_key == key).first()
        if cfg:
            cfg.config_value = value
            cfg.updated_at = datetime.now(timezone.utc)
        else:
            cfg = BenchmarkConfigModel(config_key=key, config_value=value)
            db.add(cfg)
        db.commit()
        db.refresh(cfg)
        return cfg

    @classmethod
    def get_all_configs(cls, db: Session) -> Dict[str, str]:
        cfgs = db.query(BenchmarkConfigModel).all()
        return {c.config_key: c.config_value for c in cfgs}
