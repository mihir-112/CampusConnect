"""Poster / PDF attachment model. Owner: Nayeem."""
from sqlalchemy import CheckConstraint, UniqueConstraint

from ..extensions import db, utcnow


class Attachment(db.Model):
    __tablename__ = "attachments"

    id = db.Column(db.Integer, primary_key=True)
    announcement_id = db.Column(
        db.Integer, db.ForeignKey("announcements.id", ondelete="CASCADE"), nullable=False
    )
    kind = db.Column(db.String(10), nullable=False)  # "poster" or "pdf"
    stored_filename = db.Column(db.String(255), nullable=False)  # random name on disk
    original_filename = db.Column(db.String(255), nullable=False)  # shown to students
    mime_type = db.Column(db.String(100), nullable=False)
    size_bytes = db.Column(db.Integer, nullable=False)
    uploaded_at = db.Column(db.DateTime, default=utcnow, nullable=False)

    announcement = db.relationship("Announcement", back_populates="attachments")

    __table_args__ = (
        UniqueConstraint("announcement_id", "kind", name="uq_attachment_announcement_kind"),
        CheckConstraint("kind IN ('poster', 'pdf')", name="ck_attachment_kind"),
    )
