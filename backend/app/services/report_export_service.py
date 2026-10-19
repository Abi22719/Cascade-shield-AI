import csv
import io
import json
from typing import Dict, Any, Optional
from sqlalchemy.orm import Session
from app.database.dashboard_repository import DashboardRepository

class ReportExportService:
    """
    Exports generated reports to CSV, JSON, and plain-text formats.
    """

    @classmethod
    def export_json(cls, db: Session, report_id: str) -> Dict[str, Any]:
        rep = DashboardRepository.get_report(db, report_id)
        if not rep:
            raise ValueError(f"Report '{report_id}' not found.")

        return {
            "report_id": rep.id,
            "report_type": rep.report_type,
            "report_title": rep.report_title,
            "related_record_id": rep.related_record_id,
            "data_source": rep.data_source,
            "report_status": rep.report_status,
            "content": rep.content,
            "metadata": json.loads(rep.metadata_json) if rep.metadata_json else {},
            "created_at": rep.created_at.isoformat(),
            "completed_at": rep.completed_at.isoformat() if rep.completed_at else None
        }

    @classmethod
    def export_csv(cls, db: Session, report_id: str) -> str:
        rep = DashboardRepository.get_report(db, report_id)
        if not rep:
            raise ValueError(f"Report '{report_id}' not found.")

        output = io.StringIO()
        writer = csv.writer(output)

        writer.writerow(["Report ID", rep.id])
        writer.writerow(["Report Title", rep.report_title])
        writer.writerow(["Report Type", rep.report_type])
        writer.writerow(["Data Source", rep.data_source])
        writer.writerow(["Created At", rep.created_at.isoformat()])
        writer.writerow([])
        writer.writerow(["Section", "Content"])

        # Split content lines
        if rep.content:
            for line in rep.content.splitlines():
                if line.strip():
                    writer.writerow(["Line", line.strip()])

        return output.getvalue()
