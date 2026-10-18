from typing import Optional, List
from pydantic import BaseModel, Field, model_validator, ConfigDict

class DependencyBase(BaseModel):
    source_service_id: str = Field(..., min_length=1, max_length=64, description="Caller / dependent service ID")
    target_service_id: str = Field(..., min_length=1, max_length=64, description="Callee / dependency service ID")
    dependency_type: str = Field("sync_http", max_length=64, description="sync_http, async_message, db_query, cache_lookup")
    description: Optional[str] = Field(None, description="Context regarding why this dependency exists")

    @model_validator(mode="after")
    def check_self_dependency(self):
        if self.source_service_id.strip() == self.target_service_id.strip():
            raise ValueError("Self-dependencies are not allowed. Source and Target must be different services.")
        return self

class DependencyCreate(DependencyBase):
    pass

class DependencyResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    source_service_id: str
    target_service_id: str
    dependency_type: str
    description: Optional[str] = None
    has_cycle: bool = False
    cycle_warning: Optional[str] = None
    cycle_path: Optional[List[str]] = None

class DependencyValidationResult(BaseModel):
    valid: bool
    message: str
    is_cycle: bool = False
    cycle_path: Optional[List[str]] = None
