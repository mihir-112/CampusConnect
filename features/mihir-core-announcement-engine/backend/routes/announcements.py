"""Announcement REST endpoints. Owner: Mihir.

Public:     GET /api/announcements, GET /api/announcements/{id}
Publisher:  POST, PUT, PATCH publish/unpublish, DELETE, GET /api/publisher/announcements
"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from backend.core.config import Settings, get_settings
from backend.database import get_db
from backend.shared.schemas import Page
from backend.shared.serializers import announcement_out
from features.publisher_auth.backend.models.publisher import Publisher
from features.publisher_auth.backend.security.dependencies import get_current_publisher, get_optional_publisher
from features.core_announcement_engine.backend.schemas.announcement import (
    AnnouncementCreate,
    AnnouncementOut,
    AnnouncementUpdate,
    PublisherAnnouncements,
)
from features.core_announcement_engine.backend.services import announcement_service as service

router = APIRouter(prefix="/api", tags=["Announcements"])


@router.get("/announcements", response_model=Page[AnnouncementOut])
def list_announcements(
    category: str | None = None,
    page: int = Query(1, ge=1),
    per_page: int = Query(9, ge=1, le=50),
    db: Session = Depends(get_db),
    settings: Settings = Depends(get_settings),
):
    items, total, pages = service.list_published(db, (category or "").strip() or None, page, per_page)
    return Page(items=[announcement_out(a, settings) for a in items], page=page, per_page=per_page, pages=pages, total=total)


@router.get("/announcements/{announcement_id}", response_model=AnnouncementOut)
def get_announcement(
    announcement_id: int,
    viewer: Publisher | None = Depends(get_optional_publisher),
    db: Session = Depends(get_db),
    settings: Settings = Depends(get_settings),
):
    return announcement_out(service.get_visible(db, announcement_id, viewer), settings)


@router.post("/announcements", response_model=AnnouncementOut, status_code=201)
def create_announcement(
    payload: AnnouncementCreate,
    publisher: Publisher = Depends(get_current_publisher),
    db: Session = Depends(get_db),
    settings: Settings = Depends(get_settings),
):
    return announcement_out(service.create(db, publisher, payload, settings), settings)


@router.put("/announcements/{announcement_id}", response_model=AnnouncementOut)
def update_announcement(
    announcement_id: int,
    payload: AnnouncementUpdate,
    publisher: Publisher = Depends(get_current_publisher),
    db: Session = Depends(get_db),
    settings: Settings = Depends(get_settings),
):
    announcement = service.get_owned(db, announcement_id, publisher)
    return announcement_out(service.update(db, announcement, payload, settings), settings)


@router.patch("/announcements/{announcement_id}/publish", response_model=AnnouncementOut)
def publish_announcement(
    announcement_id: int,
    publisher: Publisher = Depends(get_current_publisher),
    db: Session = Depends(get_db),
    settings: Settings = Depends(get_settings),
):
    announcement = service.get_owned(db, announcement_id, publisher)
    return announcement_out(service.set_published(db, announcement, True, settings), settings)


@router.patch("/announcements/{announcement_id}/unpublish", response_model=AnnouncementOut)
def unpublish_announcement(
    announcement_id: int,
    publisher: Publisher = Depends(get_current_publisher),
    db: Session = Depends(get_db),
    settings: Settings = Depends(get_settings),
):
    announcement = service.get_owned(db, announcement_id, publisher)
    return announcement_out(service.set_published(db, announcement, False, settings), settings)


@router.delete("/announcements/{announcement_id}", status_code=204)
def delete_announcement(
    announcement_id: int,
    publisher: Publisher = Depends(get_current_publisher),
    db: Session = Depends(get_db),
    settings: Settings = Depends(get_settings),
):
    service.delete(db, service.get_owned(db, announcement_id, publisher), settings)


@router.get("/publisher/announcements", response_model=PublisherAnnouncements)
def my_announcements(
    publisher: Publisher = Depends(get_current_publisher),
    db: Session = Depends(get_db),
    settings: Settings = Depends(get_settings),
):
    items, stats = service.list_for_publisher(db, publisher)
    return PublisherAnnouncements(stats=stats, items=[announcement_out(a, settings) for a in items])
