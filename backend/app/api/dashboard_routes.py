from typing import List, Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.schemas.dashboard_schemas import (
    DashboardSummaryResponse,
    DashboardHealthResponse,
    ExplainableInsightSchema
)
from app.services.dashboard_service import DashboardService
from app.services.insight_service import InsightService

router = APIRouter(prefix="/dashboard", tags=["Module 10: Unified Dashboard & Insights"])

@router.get("/summary", response_model=DashboardSummaryResponse)
def get_dashboard_summary(db: Session = Depends(get_db)):
    """
    Unified system summary across Modules 1 to 9 (services, alerts, incidents, plans, benchmarks).
    """
    return DashboardService.get_summary(db)

@router.get("/health", response_model=DashboardHealthResponse)
def get_dashboard_health(db: Session = Depends(get_db)):
    """
    High-level platform and per-module operational health status.
    """
    return DashboardService.get_health(db)

@router.get("/activity")
def get_dashboard_activity(
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db)
):
    """
    Cross-module activity event timeline.
    """
    return DashboardService.get_activity_timeline(db, limit=limit)

@router.get("/insights", response_model=List[ExplainableInsightSchema])
def get_explainable_insights(
    limit: int = Query(10, ge=1, le=50),
    db: Session = Depends(get_db)
):
    """
    Explainable AI insights grounded in actual alerts, incidents, simulations, and recovery plans.
    """
    return InsightService.generate_insights(db, limit=limit)
