import uuid
from datetime import datetime

from pydantic import BaseModel

from app.models.enums import NotificationCategory


class NotificationCreate(BaseModel):
    user_id: uuid.UUID
    category: NotificationCategory
    title: str
    message: str
    force_send: bool = False


class NotificationRead(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    category: NotificationCategory
    title: str
    message: str
    is_read: bool
    telegram_sent: bool
    created_at: datetime
    model_config = {"from_attributes": True}


class UnreadCountRead(BaseModel):
    count: int
