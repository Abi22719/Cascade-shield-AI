from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.schemas.notification_schemas import NotificationSchema, NotificationListResponse
from app.services.notification_service import NotificationService

router = APIRouter(prefix="/notifications", tags=["Module 10: Notifications"])

@router.get("", response_model=NotificationListResponse)
def list_notifications(
    unread_only: bool = Query(False, description="Filter for unread notifications only"),
    severity: Optional[str] = Query(None, description="Optional severity filter (CRITICAL, WARNING, INFO, SUCCESS)"),
    source_module: Optional[str] = Query(None, description="Optional source module filter"),
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """
    List real system notifications derived from stored operational events.
    """
    return NotificationService.get_notifications(
        db=db,
        unread_only=unread_only,
        severity=severity,
        source_module=source_module,
        limit=limit
    )

@router.post("/{notification_id}/read", response_model=NotificationSchema)
def mark_notification_read(notification_id: str, db: Session = Depends(get_db)):
    """
    Mark a specific notification as read.
    """
    notif = NotificationService.mark_as_read(db, notification_id)
    if not notif:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Notification '{notification_id}' not found.")
    return notif

@router.post("/read-all")
def mark_all_notifications_read(db: Session = Depends(get_db)):
    """
    Mark all unread notifications as read.
    """
    count = NotificationService.mark_all_as_read(db)
    return {"marked_read_count": count, "message": "All notifications marked as read."}
