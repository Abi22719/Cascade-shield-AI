from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import PlainTextResponse, Response
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.schemas.report_schemas import ReportGenerateRequest, ReportResponse, ReportListResponse
from app.services.report_service import ReportService
from app.services.report_export_service import ReportExportService

router = APIRouter(prefix="/reports", tags=["Module 10: Reports Center"])

@router.get("", response_model=ReportListResponse)
def list_reports(
    report_type: Optional[str] = Query(None, description="Optional filter by report type"),
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """
    List historical and generated reports across Modules 1 to 10.
    """
    return ReportService.list_reports(db, report_type=report_type, limit=limit)

@router.get("/{report_id}", response_model=ReportResponse)
def get_report(report_id: str, db: Session = Depends(get_db)):
    """
    Retrieve full report content and metadata.
    """
    rep = ReportService.get_report(db, report_id)
    if not rep:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Report '{report_id}' not found.")
    return rep

@router.post("/generate", response_model=ReportResponse)
def generate_report(req: ReportGenerateRequest, db: Session = Depends(get_db)):
    """
    Generate a new structured markdown report for a module or incident lifecycle.
    """
    return ReportService.generate_report(db, req)

@router.get("/{report_id}/export/csv")
def export_report_csv(report_id: str, db: Session = Depends(get_db)):
    """
    Export report in CSV format.
    """
    try:
        csv_data = ReportExportService.export_csv(db, report_id)
        return Response(
            content=csv_data,
            media_type="text/csv",
            headers={"Content-Disposition": f"attachment; filename=report_{report_id}.csv"}
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

@router.get("/{report_id}/export/json")
def export_report_json(report_id: str, db: Session = Depends(get_db)):
    """
    Export report in JSON format.
    """
    try:
        return ReportExportService.export_json(db, report_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
