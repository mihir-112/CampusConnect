"""Poster and PDF handling. Owner: notice-details.

Files are stored in the upload folder (never a public static folder) under a random name and are
only served through /api/attachments/..., which checks that the announcement is published.
"""
import os
import re
import uuid
from typing import BinaryIO

from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.core.config import Settings
from backend.core.constants import PDF_EXTENSIONS, PDF_MAX_BYTES, POSTER_EXTENSIONS, POSTER_MAX_BYTES
from backend.core.errors import AppError
from backend.shared import events
from features.core_announcement_engine.backend.models.announcement import Announcement
from features.notice_details.backend.models.attachment import Attachment

KINDS = ("poster", "pdf")

_RULES = {
    "poster": {"extensions": POSTER_EXTENSIONS, "max_bytes": POSTER_MAX_BYTES, "label": "Poster"},
    "pdf": {"extensions": PDF_EXTENSIONS, "max_bytes": PDF_MAX_BYTES, "label": "PDF"},
}

MIME_TYPES = {"png": "image/png", "jpg": "image/jpeg", "jpeg": "image/jpeg", "webp": "image/webp", "pdf": "application/pdf"}


def _signature_matches(ext: str, head: bytes) -> bool:
    """Check that the first bytes of the file really match the claimed type."""
    if ext == "png":
        return head.startswith(b"\x89PNG\r\n\x1a\n")
    if ext in ("jpg", "jpeg"):
        return head.startswith(b"\xff\xd8\xff")
    if ext == "webp":
        return head[:4] == b"RIFF" and head[8:12] == b"WEBP"
    if ext == "pdf":
        return head.startswith(b"%PDF-")
    return False


def check_file(kind: str, filename: str | None, stream: BinaryIO) -> tuple[str, bytes]:
    """Validate an upload. Returns (extension, file bytes) or raises a validation error."""
    if kind not in _RULES:
        raise AppError.validation({"kind": "Attachment type must be poster or pdf."})
    rules = _RULES[kind]
    label = rules["label"]

    filename = (filename or "").strip()
    if not filename:
        raise AppError.validation({"file": f"Choose a {label.lower()} file to upload."})
    ext = filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
    if ext not in rules["extensions"]:
        raise AppError.validation({"file": f"{label} must be one of these types: {', '.join(rules['extensions'])}."})

    limit = rules["max_bytes"]
    data = stream.read(limit + 1)
    if not data:
        raise AppError.validation({"file": f"The {label.lower()} file is empty."})
    if len(data) > limit:
        raise AppError(413, f"{label} must be {limit // (1024 * 1024)} MB or smaller.", "file_too_large", {"file": f"{label} is too large."})
    if not _signature_matches(ext, data[:16]):
        raise AppError.validation({"file": f"That file is not a valid {ext.upper()}."})
    return ext, data


def safe_display_name(filename: str, fallback: str) -> str:
    """Keep only the file's own name (no folders) with harmless characters."""
    base = re.split(r"[\\/]", filename)[-1]
    base = re.sub(r"[^A-Za-z0-9._ -]", "_", base).strip(" .")
    return base[:200] or fallback


def file_path(settings: Settings, attachment: Attachment) -> str:
    return os.path.join(settings.upload_dir, attachment.stored_filename)


def file_exists(settings: Settings, attachment: Attachment) -> bool:
    return os.path.isfile(file_path(settings, attachment))


def _remove_file(settings: Settings, stored_filename: str) -> None:
    try:
        os.remove(os.path.join(settings.upload_dir, stored_filename))
    except FileNotFoundError:
        pass


def get_or_404(db: Session, attachment_id: int) -> Attachment:
    attachment = db.get(Attachment, attachment_id)
    if attachment is None:
        raise AppError.not_found("That file could not be found.")
    return attachment


def save_attachment(db: Session, settings: Settings, announcement: Announcement, kind: str, filename: str | None, stream: BinaryIO) -> Attachment:
    """Validate and store a file. Replaces the existing attachment of the same kind."""
    ext, data = check_file(kind, filename, stream)

    stored = f"{uuid.uuid4().hex}.{ext}"
    os.makedirs(settings.upload_dir, exist_ok=True)
    with open(os.path.join(settings.upload_dir, stored), "wb") as handle:
        handle.write(data)

    attachment = db.scalar(select(Attachment).where(Attachment.announcement_id == announcement.id, Attachment.kind == kind))
    old_file = attachment.stored_filename if attachment else None
    if attachment is None:
        attachment = Attachment(announcement_id=announcement.id, kind=kind)
        db.add(attachment)
    attachment.stored_filename = stored
    attachment.original_filename = safe_display_name(filename or "", f"{kind}.{ext}")
    attachment.mime_type = MIME_TYPES[ext]
    attachment.size_bytes = len(data)

    try:
        db.commit()
    except Exception:
        db.rollback()
        _remove_file(settings, stored)
        raise
    if old_file:
        _remove_file(settings, old_file)
    return attachment


def delete_attachment(db: Session, settings: Settings, attachment: Attachment) -> None:
    stored = attachment.stored_filename
    db.delete(attachment)
    db.commit()
    _remove_file(settings, stored)


def remove_files_after_delete(settings: Settings, stored_files: list[str], **_ignored) -> None:
    """Event handler: when an announcement is deleted, delete its files from disk too."""
    for stored in stored_files:
        _remove_file(settings, stored)


events.subscribe(events.DELETED, remove_files_after_delete)
