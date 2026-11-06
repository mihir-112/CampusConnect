"""Notification logic. Owner: Mridul.

Reacts to announcement events: publishing creates one notification, unpublishing removes it.
"""
import re

from sqlalchemy import delete, func, select
from sqlalchemy.orm import Session

from backend.core.constants import NOTIFICATION_LIMIT
from backend.core.errors import AppError
from backend.shared import events
from features.core_announcement_engine.backend.models.announcement import Announcement
from features.search_notifications.backend.models.notification import Notification, NotificationRead

_CLIENT_ID = re.compile(r"^[A-Za-z0-9-]{8,64}$")


def valid_client_id(client_id: str | None) -> str | None:
    return client_id if client_id and _CLIENT_ID.match(client_id) else None


def notify_published(db: Session, announcement: Announcement, **_ignored) -> Notification:
    """Create the notification for a published announcement. Safe to call twice."""
    existing = db.scalar(select(Notification).where(Notification.announcement_id == announcement.id))
    if existing:
        return existing
    notification = Notification(announcement_id=announcement.id, message=f"New in {announcement.category}: {announcement.title}"[:200])
    db.add(notification)
    db.commit()
    return notification


def remove_for_unpublished(db: Session, announcement: Announcement, **_ignored) -> None:
    db.execute(delete(Notification).where(Notification.announcement_id == announcement.id))
    db.commit()


events.subscribe(events.PUBLISHED, notify_published)
events.subscribe(events.UNPUBLISHED, remove_for_unpublished)


def _recent(db: Session, limit: int):
    return db.scalars(
        select(Notification)
        .join(Announcement, Notification.announcement_id == Announcement.id)
        .where(Announcement.is_published.is_(True))
        .order_by(Notification.created_at.desc(), Notification.id.desc())
        .limit(limit)
    ).all()


def _read_ids(db: Session, client_id: str | None, ids: list[int]) -> set[int]:
    if not client_id or not ids:
        return set()
    return set(
        db.scalars(select(NotificationRead.notification_id).where(NotificationRead.client_id == client_id, NotificationRead.notification_id.in_(ids)))
    )


def list_recent(db: Session, client_id: str | None, limit: int = NOTIFICATION_LIMIT):
    """Return (notifications, ids this browser has read, unread count for this browser)."""
    client_id = valid_client_id(client_id)
    items = _recent(db, limit)
    read = _read_ids(db, client_id, [n.id for n in items])
    return items, read, sum(1 for n in items if n.id not in read)


def unread_count(db: Session, client_id: str | None) -> int:
    return list_recent(db, client_id)[2]


def _require_client(client_id: str | None) -> str:
    client_id = valid_client_id(client_id)
    if client_id is None:
        raise AppError(400, "A valid X-Client-Id header is required to track read notifications.", "bad_request")
    return client_id


def mark_read(db: Session, client_id: str | None, notification_id: int) -> int:
    client_id = _require_client(client_id)
    if db.get(Notification, notification_id) is None:
        raise AppError.not_found("That notification could not be found.")
    if not _read_ids(db, client_id, [notification_id]):
        db.add(NotificationRead(client_id=client_id, notification_id=notification_id))
        db.commit()
    return unread_count(db, client_id)


def mark_all_read(db: Session, client_id: str | None) -> int:
    client_id = _require_client(client_id)
    items = _recent(db, 200)
    already = _read_ids(db, client_id, [n.id for n in items])
    db.add_all(NotificationRead(client_id=client_id, notification_id=n.id) for n in items if n.id not in already)
    db.commit()
    return unread_count(db, client_id)


def total_notifications(db: Session) -> int:
    return db.scalar(select(func.count()).select_from(Notification)) or 0
