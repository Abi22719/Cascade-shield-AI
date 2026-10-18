import re
from datetime import datetime, timezone
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from app.database.database import get_db
from app.models.service import ServiceModel
from app.models.dependency import DependencyModel
from app.schemas.service import (
    ServiceCreate,
    ServiceUpdate,
    ServiceResponse,
    ServiceDetailResponse,
    DependencyItem
)
from app.services.health_evaluator import evaluate_service_health

router = APIRouter(prefix="/services", tags=["Services"])

def generate_service_id(name: str) -> str:
    slug = re.sub(r"[^a-zA-Z0-9]+", "-", name.strip().lower()).strip("-")
    if not slug:
        slug = "service"
    return f"srv-{slug}"

@router.get("", response_model=List[ServiceResponse])
def get_services(
    service_type: Optional[str] = Query(None, description="Filter by service type"),
    health_status: Optional[str] = Query(None, description="Filter by health status (HEALTHY, WARNING, CRITICAL)"),
    search: Optional[str] = Query(None, description="Search term for name or ID"),
    db: Session = Depends(get_db)
):
    """
    List all services with optional filtering by type, health status, or search query.
    """
    query = db.query(ServiceModel)

    if service_type:
        query = query.filter(ServiceModel.service_type == service_type.strip().lower())
    if health_status:
        query = query.filter(ServiceModel.health_status == health_status.strip().upper())
    if search:
        search_pattern = f"%{search.strip()}%"
        query = query.filter(
            (ServiceModel.name.ilike(search_pattern)) | 
            (ServiceModel.id.ilike(search_pattern)) |
            (ServiceModel.description.ilike(search_pattern))
        )

    return query.order_by(ServiceModel.name.asc()).all()

@router.get("/{service_id}", response_model=ServiceDetailResponse)
def get_service_detail(service_id: str, db: Session = Depends(get_db)):
    """
    Retrieve specific service details including incoming and outgoing dependencies,
    health calculation explanation, and degree centrality.
    """
    service = db.query(ServiceModel).filter(ServiceModel.id == service_id).first()
    if not service:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Service with ID '{service_id}' was not found."
        )

    # Fetch incoming dependencies (where service is target)
    incoming_deps = db.query(DependencyModel).filter(DependencyModel.target_service_id == service_id).all()
    # Fetch outgoing dependencies (where service is source)
    outgoing_deps = db.query(DependencyModel).filter(DependencyModel.source_service_id == service_id).all()

    # Map target/source names
    all_service_names = {s.id: s.name for s in db.query(ServiceModel.id, ServiceModel.name).all()}

    incoming_items = [
        DependencyItem(
            id=d.id,
            source_service_id=d.source_service_id,
            target_service_id=d.target_service_id,
            dependency_type=d.dependency_type,
            description=d.description,
            service_name=all_service_names.get(d.source_service_id, d.source_service_id)
        )
        for d in incoming_deps
    ]

    outgoing_items = [
        DependencyItem(
            id=d.id,
            source_service_id=d.source_service_id,
            target_service_id=d.target_service_id,
            dependency_type=d.dependency_type,
            description=d.description,
            service_name=all_service_names.get(d.target_service_id, d.target_service_id)
        )
        for d in outgoing_deps
    ]

    # Evaluate health explanation
    _, reasons = evaluate_service_health(
        cpu_usage=service.cpu_usage,
        memory_usage=service.memory_usage,
        latency_ms=service.latency_ms,
        error_rate=service.error_rate
    )

    return ServiceDetailResponse(
        id=service.id,
        name=service.name,
        service_type=service.service_type,
        description=service.description,
        health_status=service.health_status,
        cpu_usage=service.cpu_usage,
        memory_usage=service.memory_usage,
        latency_ms=service.latency_ms,
        error_rate=service.error_rate,
        request_volume=service.request_volume,
        updated_at=service.updated_at,
        health_reasons=reasons,
        incoming_dependencies=incoming_items,
        outgoing_dependencies=outgoing_items,
        in_degree=len(incoming_items),
        out_degree=len(outgoing_items)
    )

@router.post("", response_model=ServiceResponse, status_code=status.HTTP_201_CREATED)
def create_service(payload: ServiceCreate, db: Session = Depends(get_db)):
    """
    Create a new cloud service in the digital twin.
    """
    srv_id = payload.id
    if not srv_id:
        srv_id = generate_service_id(payload.name)
        # Avoid duplicate slug collision
        counter = 1
        base_id = srv_id
        while db.query(ServiceModel).filter(ServiceModel.id == srv_id).first():
            srv_id = f"{base_id}-{counter}"
            counter += 1
    else:
        # Check if ID already exists
        if db.query(ServiceModel).filter(ServiceModel.id == srv_id).first():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Service with ID '{srv_id}' already exists."
            )

    health_status, _ = evaluate_service_health(
        cpu_usage=payload.cpu_usage,
        memory_usage=payload.memory_usage,
        latency_ms=payload.latency_ms,
        error_rate=payload.error_rate
    )

    new_service = ServiceModel(
        id=srv_id,
        name=payload.name.strip(),
        service_type=payload.service_type.strip().lower(),
        description=payload.description.strip() if payload.description else "",
        health_status=health_status,
        cpu_usage=payload.cpu_usage,
        memory_usage=payload.memory_usage,
        latency_ms=payload.latency_ms,
        error_rate=payload.error_rate,
        request_volume=payload.request_volume,
        updated_at=datetime.now(timezone.utc)
    )

    db.add(new_service)
    db.commit()
    db.refresh(new_service)
    return new_service

@router.put("/{service_id}", response_model=ServiceResponse)
def update_service(service_id: str, payload: ServiceUpdate, db: Session = Depends(get_db)):
    """
    Update service metadata or simulated telemetry metrics.
    Automatically recalculates health status based on rule engine.
    """
    service = db.query(ServiceModel).filter(ServiceModel.id == service_id).first()
    if not service:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Service with ID '{service_id}' was not found."
        )

    if payload.name is not None:
        service.name = payload.name.strip()
    if payload.service_type is not None:
        service.service_type = payload.service_type.strip().lower()
    if payload.description is not None:
        service.description = payload.description.strip()
    if payload.cpu_usage is not None:
        service.cpu_usage = payload.cpu_usage
    if payload.memory_usage is not None:
        service.memory_usage = payload.memory_usage
    if payload.latency_ms is not None:
        service.latency_ms = payload.latency_ms
    if payload.error_rate is not None:
        service.error_rate = payload.error_rate
    if payload.request_volume is not None:
        service.request_volume = payload.request_volume

    # Recalculate health based on current metrics
    new_health, _ = evaluate_service_health(
        cpu_usage=service.cpu_usage,
        memory_usage=service.memory_usage,
        latency_ms=service.latency_ms,
        error_rate=service.error_rate
    )
    service.health_status = new_health
    service.updated_at = datetime.now(timezone.utc)

    db.commit()
    db.refresh(service)
    return service

@router.delete("/{service_id}", status_code=status.HTTP_200_OK)
def delete_service(service_id: str, db: Session = Depends(get_db)):
    """
    Delete a service and cascade delete any associated incoming/outgoing dependencies.
    """
    service = db.query(ServiceModel).filter(ServiceModel.id == service_id).first()
    if not service:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Service with ID '{service_id}' was not found."
        )

    # Count affected dependencies before delete
    affected_incoming = db.query(DependencyModel).filter(DependencyModel.target_service_id == service_id).count()
    affected_outgoing = db.query(DependencyModel).filter(DependencyModel.source_service_id == service_id).count()

    db.delete(service)
    db.commit()

    return {
        "success": True,
        "message": f"Service '{service.name}' ({service_id}) and its {affected_incoming + affected_outgoing} dependencies have been deleted.",
        "deleted_service_id": service_id,
        "removed_dependencies_count": affected_incoming + affected_outgoing
    }
