from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database.database import get_db
from app.models.service import ServiceModel
from app.models.dependency import DependencyModel
from app.schemas.graph import GraphResponse, ImpactResponse
from app.services.graph_service import GraphService
from app.database.init_db import init_db

router = APIRouter(prefix="/graph", tags=["Dependency Graph"])

@router.get("", response_model=GraphResponse)
def get_graph(db: Session = Depends(get_db)):
    """
    Retrieve full digital twin topology formatted for Cytoscape.js visualization,
    including node telemetry attributes, edge types, and cycle detection analysis.
    """
    services = db.query(ServiceModel).all()
    dependencies = db.query(DependencyModel).all()

    G = GraphService.build_networkx_graph(services, dependencies)
    cytoscape_data = GraphService.to_cytoscape_elements(G)

    return cytoscape_data

@router.get("/impact/{service_id}", response_model=ImpactResponse)
def get_downstream_impact(service_id: str, db: Session = Depends(get_db)):
    """
    Compute downstream services reachable from the specified service.
    Returns impact tiers, shortest paths, and direct vs indirect dependents.
    Does not predict failure probability (which belongs to Module 3).
    """
    service = db.query(ServiceModel).filter(ServiceModel.id == service_id).first()
    if not service:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Service with ID '{service_id}' was not found."
        )

    services = db.query(ServiceModel).all()
    dependencies = db.query(DependencyModel).all()
    G = GraphService.build_networkx_graph(services, dependencies)

    impact_data = GraphService.get_downstream_impact(G, service_id)
    impact_data["service_name"] = service.name
    return impact_data

@router.post("/reset", status_code=status.HTTP_200_OK)
def reset_graph_topology(db: Session = Depends(get_db)):
    """
    Reset digital twin topology to the default 9-service sample cloud infrastructure.
    """
    init_db(db, force_reset=True)
    services_count = db.query(ServiceModel).count()
    deps_count = db.query(DependencyModel).count()

    return {
        "success": True,
        "message": "Cloud digital twin topology has been reset to default baseline.",
        "services_count": services_count,
        "dependencies_count": deps_count
    }
