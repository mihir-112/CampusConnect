"""Notification endpoints. Owner: Mridul.

GET   /api/notifications               latest notifications and this browser's unread count
PATCH /api/notifications/{id}/read     mark one as read
PATCH /api/notifications/read-all      mark all as read
The browser identifies itself with an X-Client-Id header (a random id kept in localStorage).
"""
from fastapi import APIRouter, Depends, Header, Query
from sqlalchemy.orm import Session

from backend.database import get_db
from features.search_notifications.backend.schemas.notification import NotificationList, NotificationOut, ReadResult
from features.search_notifications.backend.services import notification_service as service

router = APIRouter(prefix="/api/notifications", tags=["Notifications"])


@router.get("", response_model=NotificationList)
def list_notifications(
    limit: int = Query(10, ge=1, le=50),
    x_client_id: str | None = Header(default=None),
    db: Session = Depends(get_db),
):
    items, read, unread = service.list_recent(db, x_client_id, limit)
    return NotificationList(
        unread=unread,
        items=[
            NotificationOut(id=n.id, announcement_id=n.announcement_id, message=n.message, created_at=n.created_at, is_read=n.id in read)
            for n in items
        ],
    )


@router.patch("/read-all", response_model=ReadResult)
def mark_all_read(x_client_id: str | None = Header(default=None), db: Session = Depends(get_db)):
    return ReadResult(unread=service.mark_all_read(db, x_client_id))


@router.patch("/{notification_id}/read", response_model=ReadResult)
def mark_read(notification_id: int, x_client_id: str | None = Header(default=None), db: Session = Depends(get_db)):
    return ReadResult(unread=service.mark_read(db, x_client_id, notification_id))
