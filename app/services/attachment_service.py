"""Poster and PDF handling. Owner: Nayeem.

Files are stored in UPLOAD_FOLDER (outside static/) under a random name, and are only
served through the notices routes, which check that the announcement is published.
"""
import os
import uuid

from flask import current_app
from werkzeug.utils import secure_filename

from ..constants import PDF_EXTENSIONS, PDF_MAX_BYTES, POSTER_EXTENSIONS, POSTER_MAX_BYTES
from ..errors import ValidationError
from ..extensions import db
from ..models import Announcement, Attachment

KINDS = ("poster", "pdf")

_RULES = {
    "poster": {"extensions": POSTER_EXTENSIONS, "max_bytes": POSTER_MAX_BYTES, "label": "Poster"},
    "pdf": {"extensions": PDF_EXTENSIONS, "max_bytes": PDF_MAX_BYTES, "label": "PDF"},
}

MIME_TYPES = {
    "png": "image/png",
    "jpg": "image/jpeg",
    "jpeg": "image/jpeg",
    "webp": "image/webp",
    "pdf": "application/pdf",
}


def upload_folder():
    return current_app.config["UPLOAD_FOLDER"]


def _signature_matches(ext, head):
    """Check the first bytes of the file really match the claimed type."""
    if ext == "png":
        return head.startswith(b"\x89PNG\r\n\x1a\n")
    if ext in ("jpg", "jpeg"):
        return head.startswith(b"\xff\xd8\xff")
    if ext == "webp":
        return head[:4] == b"RIFF" and head[8:12] == b"WEBP"
    if ext == "pdf":
        return head.startswith(b"%PDF-")
    return False


def check_file(kind, file_storage):
    """Validate an uploaded file. Returns (extension, bytes) or raises ValidationError."""
    if kind not in _RULES:
        raise ValidationError({"attachment": "Unknown attachment type."})
    rules = _RULES[kind]
    label = rules["label"]

    filename = (getattr(file_storage, "filename", "") or "").strip()
    if not filename:
        raise ValidationError({kind: f"Choose a {label.lower()} file to upload."})

    ext = filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
    if ext not in rules["extensions"]:
        allowed = ", ".join(rules["extensions"])
        raise ValidationError({kind: f"{label} must be one of these types: {allowed}."})

    limit = rules["max_bytes"]
    data = file_storage.read(limit + 1)
    file_storage.stream.seek(0)  # so the file can be read again later
    if not data:
        raise ValidationError({kind: f"The {label.lower()} file is empty."})
    if len(data) > limit:
        raise ValidationError({kind: f"{label} must be {limit // (1024 * 1024)} MB or smaller."})
    if not _signature_matches(ext, data[:16]):
        raise ValidationError({kind: f"That file is not a valid {ext.upper()}."})
    return ext, data


def _remove_file(stored_filename):
    try:
        os.remove(os.path.join(upload_folder(), stored_filename))
    except FileNotFoundError:
        pass


def get_attachment(announcement_id, kind):
    return Attachment.query.filter_by(announcement_id=announcement_id, kind=kind).first()


def file_exists(attachment):
    return attachment is not None and os.path.isfile(
        os.path.join(upload_folder(), attachment.stored_filename)
    )


def save_attachment(announcement_id, kind, file_storage):
    """Validate and store a file. Replaces the existing attachment of the same kind."""
    ext, data = check_file(kind, file_storage)
    if db.session.get(Announcement, announcement_id) is None:
        raise ValidationError({"attachment": "That announcement does not exist."})

    stored = f"{uuid.uuid4().hex}.{ext}"
    os.makedirs(upload_folder(), exist_ok=True)
    with open(os.path.join(upload_folder(), stored), "wb") as handle:
        handle.write(data)

    original = secure_filename(file_storage.filename) or f"{kind}.{ext}"
    attachment = get_attachment(announcement_id, kind)
    old_file = attachment.stored_filename if attachment else None
    if attachment is None:
        attachment = Attachment(announcement_id=announcement_id, kind=kind)
        db.session.add(attachment)
    attachment.stored_filename = stored
    attachment.original_filename = original
    attachment.mime_type = MIME_TYPES[ext]
    attachment.size_bytes = len(data)

    try:
        db.session.commit()
    except Exception:
        db.session.rollback()
        _remove_file(stored)
        raise
    if old_file:
        _remove_file(old_file)
    return attachment


def delete_attachment(announcement_id, kind):
    attachment = get_attachment(announcement_id, kind)
    if attachment is None:
        return
    stored = attachment.stored_filename
    db.session.delete(attachment)
    db.session.commit()
    _remove_file(stored)


def delete_all_for(announcement_id):
    for attachment in Attachment.query.filter_by(announcement_id=announcement_id).all():
        stored = attachment.stored_filename
        db.session.delete(attachment)
        _remove_file(stored)
    db.session.commit()
