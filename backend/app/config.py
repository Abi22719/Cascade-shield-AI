import os
from pydantic import BaseModel

class Settings(BaseModel):
    DATABASE_PATH: str = os.getenv("DATABASE_PATH", "./cascadeshield.db")
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    
    # Anomaly Detection Parameters
    DEFAULT_CONTAMINATION: float = float(os.getenv("ISOLATION_FOREST_CONTAMINATION", "0.08"))
    DEFAULT_RANDOM_STATE: int = int(os.getenv("ISOLATION_FOREST_RANDOM_STATE", "42"))
    
    # Demonstration Default Thresholds
    DEFAULT_CPU_WARNING: float = 75.0
    DEFAULT_CPU_CRITICAL: float = 90.0
    DEFAULT_MEMORY_WARNING: float = 80.0
    DEFAULT_MEMORY_CRITICAL: float = 95.0
    DEFAULT_LATENCY_WARNING: float = 500.0
    DEFAULT_LATENCY_CRITICAL: float = 1000.0
    DEFAULT_ERROR_RATE_WARNING: float = 5.0
    DEFAULT_ERROR_RATE_CRITICAL: float = 10.0

settings = Settings()
