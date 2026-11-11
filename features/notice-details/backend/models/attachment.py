"""Poster / PDF attachment table. Owner: notice-details."""
from datetime import datetime

from sqlalchemy import CheckConstraint, ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.database import Base
from backend.shared.time import utcnow


class Attachment(Base):
    __tablename__ = "attachments"
    __table_args__ = (
        UniqueConstraint("announcement_id", "kind", name="uq_attachment_announcement_kind"),
        CheckConstraint("kind IN ('poster', 'pdf')", name="ck_attachment_kind"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    announcement_id: Mapped[int] = mapped_column(ForeignKey("announcements.id", ondelete="CASCADE"))
    kind: Mapped[str] = mapped_column(String(10))  # "poster" or "pdf"
    stored_filename: Mapped[str] = mapped_column(String(255))  # random name on disk
    original_filename: Mapped[str] = mapped_column(String(255))  # shown to students
    mime_type: Mapped[str] = mapped_column(String(100))
    size_bytes: Mapped[int]
    uploaded_at: Mapped[datetime] = mapped_column(default=utcnow)

    announcement = relationship("Announcement", back_populates="attachments")
