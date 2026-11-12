"""Attachment endpoints. Owner: notice-details.

POST   /api/announcements/{id}/attachments   upload a poster or PDF (owner only)
DELETE /api/attachments/{id}                 remove it (owner only)
GET    /api/attachments/{id}                 view (image or PDF shown inside the page)
GET    /api/attachments/{id}/download        download with the original file name
"""
from typing import Annotated

from fastapi import APIRouter, Depends, File, Form, UploadFile
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from backend.core.config import Settings, get_settings
from backend.core.errors import AppError
from backend.database import get_db
from backend.shared.serializers import announcement_out
from features.publisher_auth.backend.models.publisher import Publisher
from features.publisher_auth.backend.security.dependencies import get_current_publisher, get_optional_publisher
from features.core_announcement_engine.backend.schemas.announcement import AnnouncementOut
from features.core_announcement_engine.backend.services import announcement_service
from features.notice_details.backend.services import attachment_service

router = APIRouter(prefix="/api", tags=["Attachments"])


@router.post("/announcements/{announcement_id}/attachments", response_model=AnnouncementOut, status_code=201)
def upload_attachment(
    announcement_id: int,
    kind: Annotated[str, Form()],
    file: Annotated[UploadFile, File()],
    publisher: Publisher = Depends(get_current_publisher),
    db: Session = Depends(get_db),
    settings: Settings = Depends(get_settings),
):
    announcement = announcement_service.get_owned(db, announcement_id, publisher)
    attachment_service.save_attachment(db, settings, announcement, kind.strip().lower(), file.filename, file.file)
    db.refresh(announcement)
    return announcement_out(announcement, settings)


@router.delete("/attachments/{attachment_id}", status_code=204)
def delete_attachment(
    attachment_id: int,
    publisher: Publisher = Depends(get_current_publisher),
    db: Session = Depends(get_db),
    settings: Settings = Depends(get_settings),
):
    attachment = attachment_service.get_or_404(db, attachment_id)
    announcement_service.get_owned(db, attachment.announcement_id, publisher)
    attachment_service.delete_attachment(db, settings, attachment)


def _serve(attachment_id: int, viewer: Publisher | None, db: Session, settings: Settings, as_download: bool) -> FileResponse:
    attachment = attachment_service.get_or_404(db, attachment_id)
    announcement_service.get_visible(db, attachment.announcement_id, viewer)  # drafts stay private
    if not attachment_service.file_exists(settings, attachment):
        raise AppError.not_found("This file is currently unavailable. Please contact the publisher.")
    return FileResponse(
        attachment_service.file_path(settings, attachment),
        media_type=attachment.mime_type,
        filename=attachment.original_filename,
        content_disposition_type="attachment" if as_download else "inline",
        headers={"X-Content-Type-Options": "nosniff"},
    )


@router.get("/attachments/{attachment_id}")
def view_attachment(
    attachment_id: int,
    viewer: Publisher | None = Depends(get_optional_publisher),
    db: Session = Depends(get_db),
    settings: Settings = Depends(get_settings),
):
    return _serve(attachment_id, viewer, db, settings, as_download=False)


@router.get("/attachments/{attachment_id}/download")
def download_attachment(
    attachment_id: int,
    viewer: Publisher | None = Depends(get_optional_publisher),
    db: Session = Depends(get_db),
    settings: Settings = Depends(get_settings),
):
    return _serve(attachment_id, viewer, db, settings, as_download=True)
