import uuid
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database.database import get_db
from app.models.service import ServiceModel
from app.models.dependency import DependencyModel
from app.schemas.dependency import DependencyCreate, DependencyResponse
from app.services.graph_service import GraphService

router = APIRouter(prefix="/dependencies", tags=["Dependencies"])

@router.get("", response_model=List[DependencyResponse])
def get_dependencies(
    source_id: Optional[str] = None,
    target_id: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    List all dependencies with optional filtering by source or target service.
    """
    query = db.query(DependencyModel)
    if source_id:
        query = query.filter(DependencyModel.source_service_id == source_id)
    if target_id:
        query = query.filter(DependencyModel.target_service_id == target_id)
    return query.all()

@router.post("", response_model=DependencyResponse, status_code=status.HTTP_201_CREATED)
def create_dependency(payload: DependencyCreate, db: Session = Depends(get_db)):
    """
    Create a new directed dependency edge between two services.
    Validates endpoint existence, prevents self-loops and duplicate edges,
    and detects circular dependencies with explicit warning details.
    """
    src_id = payload.source_service_id.strip()
    tgt_id = payload.target_service_id.strip()

    # 1. Prevent self-dependencies
    if src_id == tgt_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Self-dependencies are not allowed. Source and Target must be different services."
        )

    # 2. Validate source service exists
    source_service = db.query(ServiceModel).filter(ServiceModel.id == src_id).first()
    if not source_service:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Source service '{src_id}' does not exist."
        )

    # 3. Validate target service exists
    target_service = db.query(ServiceModel).filter(ServiceModel.id == tgt_id).first()
    if not target_service:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Target service '{tgt_id}' does not exist."
        )

    # 4. Check for duplicate dependency
    existing = db.query(DependencyModel).filter(
        DependencyModel.source_service_id == src_id,
        DependencyModel.target_service_id == tgt_id
    ).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Dependency already exists between '{source_service.name}' and '{target_service.name}'."
        )

    # 5. Build current graph and detect cycle addition
    services = db.query(ServiceModel).all()
    dependencies = db.query(DependencyModel).all()
    G = GraphService.build_networkx_graph(services, dependencies)

    has_cycle, cycle_path = GraphService.will_form_cycle(G, src_id, tgt_id)
    cycle_warning = None
    if has_cycle and cycle_path:
        cycle_warning = f"Circular dependency detected: {' -> '.join(cycle_path)}"

    # Generate edge id
    dep_id = f"dep-{src_id}-{tgt_id}"
    if db.query(DependencyModel).filter(DependencyModel.id == dep_id).first():
        dep_id = f"dep-{src_id}-{tgt_id}-{uuid.uuid4().hex[:6]}"

    new_dep = DependencyModel(
        id=dep_id,
        source_service_id=src_id,
        target_service_id=tgt_id,
        dependency_type=payload.dependency_type,
        description=payload.description.strip() if payload.description else None
    )

    db.add(new_dep)
    db.commit()
    db.refresh(new_dep)

    return DependencyResponse(
        id=new_dep.id,
        source_service_id=new_dep.source_service_id,
        target_service_id=new_dep.target_service_id,
        dependency_type=new_dep.dependency_type,
        description=new_dep.description,
        has_cycle=has_cycle,
        cycle_warning=cycle_warning,
        cycle_path=cycle_path
    )

@router.delete("/{dependency_id}", status_code=status.HTTP_200_OK)
def delete_dependency(dependency_id: str, db: Session = Depends(get_db)):
    """
    Remove an existing directed dependency edge.
    """
    dep = db.query(DependencyModel).filter(DependencyModel.id == dependency_id).first()
    if not dep:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Dependency with ID '{dependency_id}' was not found."
        )

    src_id = dep.source_service_id
    tgt_id = dep.target_service_id
    db.delete(dep)
    db.commit()

    return {
        "success": True,
        "message": f"Dependency between '{src_id}' and '{tgt_id}' ({dependency_id}) successfully removed.",
        "deleted_dependency_id": dependency_id
    }
