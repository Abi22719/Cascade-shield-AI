from typing import Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.schemas.search_schemas import SearchResponse, SearchSuggestionsResponse
from app.services.search_service import SearchService

router = APIRouter(prefix="/search", tags=["Module 10: Global Search"])

@router.get("", response_model=SearchResponse)
def global_search(
    q: str = Query("", description="Search term for services, alerts, incidents, plans, benchmarks"),
    module: Optional[str] = Query(None, description="Optional module filter (e.g. module_1, module_2)"),
    severity: Optional[str] = Query(None, description="Optional severity filter (CRITICAL, WARNING, INFO)"),
    service_id: Optional[str] = Query(None, description="Optional target service ID"),
    status: Optional[str] = Query(None, description="Optional status filter"),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """
    Search across services, anomaly alerts, RCA incidents, what-if scenarios, recovery plans, and benchmarks.
    """
    return SearchService.search(
        db=db,
        query=q,
        module_filter=module,
        severity_filter=severity,
        service_filter=service_id,
        status_filter=status,
        skip=skip,
        limit=limit
    )

@router.get("/suggestions", response_model=SearchSuggestionsResponse)
def get_search_suggestions(
    limit: int = Query(8, ge=1, le=20),
    db: Session = Depends(get_db)
):
    """
    Quick auto-complete search suggestions.
    """
    return SearchService.get_suggestions(db, limit=limit)
