"""Announcement business rules. Owner: core-announcement-engine.

Routes call these functions; these functions talk to the database and announce events
(see backend/shared/events.py) so notifications and file clean-up can react.
"""
from collections import Counter

from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.core.config import Settings
from backend.core.constants import CATEGORIES
from backend.core.errors import AppError
from backend.shared import events
from backend.shared.pagination import paginate
from backend.shared.time import utcnow
from features.publisher_auth.backend.models.publisher import Publisher
from features.core_announcement_engine.backend.models.announcement import Announcement
from features.core_announcement_engine.backend.schemas.announcement import AnnouncementCreate, AnnouncementUpdate, PublisherStats


def published_query():
    """Everything students are allowed to see, newest first."""
    return (
        select(Announcement)
        .where(Announcement.is_published.is_(True))
        .order_by(Announcement.published_at.desc(), Announcement.id.desc())
    )


def list_published(db: Session, category: str | None, page: int, per_page: int):
    if category and category not in CATEGORIES:
        raise AppError.validation({"category": "Category must be one of: " + ", ".join(CATEGORIES) + "."})
    statement = published_query()
    if category:
        statement = statement.where(Announcement.category == category)
    return paginate(db, statement, page, per_page)


def get_or_404(db: Session, announcement_id: int) -> Announcement:
    announcement = db.get(Announcement, announcement_id)
    if announcement is None:
        raise AppError.not_found()
    return announcement


def get_visible(db: Session, announcement_id: int, viewer: Publisher | None) -> Announcement:
    """Students see published announcements only; a publisher can also open their own drafts."""
    announcement = get_or_404(db, announcement_id)
    if not announcement.is_published and (viewer is None or announcement.author_id != viewer.id):
        raise AppError.not_found()
    return announcement


def get_owned(db: Session, announcement_id: int, publisher: Publisher) -> Announcement:
    announcement = get_or_404(db, announcement_id)
    if announcement.author_id != publisher.id:
        raise AppError.forbidden("You can only change announcements that you created.")
    return announcement


def _apply_publish(announcement: Announcement, published: bool) -> str | None:
    """Switch the status; return the event to announce (or None if nothing changed)."""
    if published and not announcement.is_published:
        announcement.is_published = True
        if announcement.published_at is None:
            announcement.published_at = utcnow()
        return events.PUBLISHED
    if not published and announcement.is_published:
        announcement.is_published = False
        return events.UNPUBLISHED
    return None


def create(db: Session, publisher: Publisher, payload: AnnouncementCreate, settings: Settings) -> Announcement:
    fields = payload.model_dump(exclude={"is_published"})
    announcement = Announcement(author_id=publisher.id, **fields)
    event = _apply_publish(announcement, payload.is_published)
    db.add(announcement)
    db.commit()
    if event:
        events.emit(event, db=db, settings=settings, announcement=announcement)
    return announcement


def update(db: Session, announcement: Announcement, payload: AnnouncementUpdate, settings: Settings) -> Announcement:
    for name, value in payload.model_dump(exclude={"is_published"}).items():
        setattr(announcement, name, value)
    event = _apply_publish(announcement, payload.is_published) if payload.is_published is not None else None
    db.commit()
    if event:
        events.emit(event, db=db, settings=settings, announcement=announcement)
    return announcement


def set_published(db: Session, announcement: Announcement, published: bool, settings: Settings) -> Announcement:
    event = _apply_publish(announcement, published)
    db.commit()
    if event:
        events.emit(event, db=db, settings=settings, announcement=announcement)
    return announcement


def delete(db: Session, announcement: Announcement, settings: Settings) -> None:
    announcement_id = announcement.id
    stored_files = [a.stored_filename for a in announcement.attachments]
    db.delete(announcement)  # attachments and notifications are removed by the cascade
    db.commit()
    events.emit(events.DELETED, db=db, settings=settings, announcement_id=announcement_id, stored_files=stored_files)


def list_for_publisher(db: Session, publisher: Publisher):
    items = db.scalars(
        select(Announcement).where(Announcement.author_id == publisher.id).order_by(Announcement.created_at.desc(), Announcement.id.desc())
    ).all()
    counts = Counter(a.category for a in items)
    published = sum(1 for a in items if a.is_published)
    stats = PublisherStats(
        total=len(items), published=published, drafts=len(items) - published, by_category={c: counts.get(c, 0) for c in CATEGORIES}
    )
    return items, stats
