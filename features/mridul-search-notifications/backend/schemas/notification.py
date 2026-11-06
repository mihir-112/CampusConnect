"""Search and notification responses. Owner: Mridul."""
from pydantic import BaseModel

from backend.shared.schemas import Page, UtcDateTime
from features.core_announcement_engine.backend.schemas.announcement import AnnouncementOut


class NotificationOut(BaseModel):
    id: int
    announcement_id: int
    message: str
    created_at: UtcDateTime
    is_read: bool


class NotificationList(BaseModel):
    unread: int
    items: list[NotificationOut]


class ReadResult(BaseModel):
    ok: bool = True
    unread: int


class SearchResults(Page[AnnouncementOut]):
    q: str = ""
    category: str | None = None
