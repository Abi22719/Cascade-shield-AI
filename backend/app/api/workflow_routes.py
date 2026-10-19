from typing import Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.schemas.workflow_schemas import IncidentWorkflowResponse
from app.services.workflow_service import WorkflowService

router = APIRouter(prefix="/workflow", tags=["Module 10: Incident Investigation Workflow"])

@router.get("/incidents/{incident_id}", response_model=IncidentWorkflowResponse)
def get_incident_workflow(
    incident_id: str,
    service_id: Optional[str] = Query(None, description="Optional service ID override"),
    db: Session = Depends(get_db)
):
    """
    Get 10-step incident investigation lifecycle status, steps, and recommendations.
    """
    return WorkflowService.get_incident_workflow(db, incident_id=incident_id, service_id=service_id)

@router.get("/incidents/{incident_id}/timeline")
def get_incident_timeline(
    incident_id: str,
    db: Session = Depends(get_db)
):
    """
    Timeline of investigation steps for a specific incident.
    """
    wf = WorkflowService.get_incident_workflow(db, incident_id=incident_id)
    return {
        "incident_id": wf.incident_id,
        "service_id": wf.service_id,
        "current_step": wf.current_step,
        "steps": wf.steps
    }

@router.get("/incidents/{incident_id}/summary")
def get_incident_summary(
    incident_id: str,
    db: Session = Depends(get_db)
):
    """
    High-level overview of incident status, top suspect, and resolution actions.
    """
    wf = WorkflowService.get_incident_workflow(db, incident_id=incident_id)
    return {
        "incident_id": wf.incident_id,
        "service_id": wf.service_id,
        "status": wf.status,
        "current_step": wf.current_step,
        "recommendations": wf.recommendations
    }
