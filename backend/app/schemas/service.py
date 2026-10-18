from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, field_validator, ConfigDict

class ServiceBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=128, description="Human-readable service name")
    service_type: str = Field(..., min_length=1, max_length=64, description="Type: gateway, auth, compute, database, cache, etc.")
    description: Optional[str] = Field(None, description="Detailed description of the service role")
    cpu_usage: float = Field(20.0, ge=0.0, le=100.0, description="Simulated CPU utilization percentage")
    memory_usage: float = Field(30.0, ge=0.0, le=100.0, description="Simulated Memory utilization percentage")
    latency_ms: float = Field(45.0, ge=0.0, description="Simulated response latency in milliseconds")
    error_rate: float = Field(0.1, ge=0.0, le=100.0, description="Simulated error rate percentage")
    request_volume: int = Field(150, ge=0, description="Simulated requests per second")

class ServiceCreate(ServiceBase):
    id: Optional[str] = Field(None, max_length=64, description="Unique service ID. If omitted, will be generated from name.")

    @field_validator("id")
    def validate_id(cls, v):
        if v is not None:
            v = v.strip().lower()
            if not v:
                raise ValueError("Service ID cannot be empty whitespace")
        return v

class ServiceUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=128)
    service_type: Optional[str] = Field(None, min_length=1, max_length=64)
    description: Optional[str] = None
    cpu_usage: Optional[float] = Field(None, ge=0.0, le=100.0)
    memory_usage: Optional[float] = Field(None, ge=0.0, le=100.0)
    latency_ms: Optional[float] = Field(None, ge=0.0)
    error_rate: Optional[float] = Field(None, ge=0.0, le=100.0)
    request_volume: Optional[int] = Field(None, ge=0)

class ServiceSimulationUpdate(BaseModel):
    cpu_usage: float = Field(..., ge=0.0, le=100.0)
    memory_usage: float = Field(..., ge=0.0, le=100.0)
    latency_ms: float = Field(..., ge=0.0)
    error_rate: float = Field(..., ge=0.0, le=100.0)
    request_volume: int = Field(..., ge=0)

class DependencyItem(BaseModel):
    id: str
    source_service_id: str
    target_service_id: str
    dependency_type: str
    description: Optional[str] = None
    service_name: Optional[str] = None

class ServiceResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    name: str
    service_type: str
    description: Optional[str] = None
    health_status: str
    cpu_usage: float
    memory_usage: float
    latency_ms: float
    error_rate: float
    request_volume: int
    updated_at: Optional[datetime] = None

class ServiceDetailResponse(ServiceResponse):
    health_reasons: List[str] = []
    incoming_dependencies: List[DependencyItem] = []
    outgoing_dependencies: List[DependencyItem] = []
    in_degree: int = 0
    out_degree: int = 0
