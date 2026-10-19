from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field

class WorkflowStepSchema(BaseModel):
    step_number: int
    step_name: str
    module: str
    status: str  # COMPLETED, IN_PROGRESS, PENDING, BLOCKED
    record_id: Optional[str] = None
    summary: str
    can_proceed: bool
    missing_prerequisites: List[str] = Field(default_factory=list)

class IncidentWorkflowResponse(BaseModel):
    incident_id: str
    service_id: str
    status: str
    created_at: datetime
    steps: List[WorkflowStepSchema] = Field(default_factory=list)
    current_step: int
    recommendations: List[str] = Field(default_factory=list)
