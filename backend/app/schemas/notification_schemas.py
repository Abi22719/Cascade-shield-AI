from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field, ConfigDict

class NotificationSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    event_type: str
    source_module: str
    source_record_id: Optional[str] = None
    title: str
    message: str
    severity: str
    read_status: bool
    created_at: datetime

class NotificationListResponse(BaseModel):
    unread_count: int
    total_count: int
    notifications: List[NotificationSchema] = Field(default_factory=list)
