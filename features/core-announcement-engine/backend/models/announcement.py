"""The central Announcement table. Owner: core-announcement-engine.

Other members' tables (Publisher, Attachment, Notification) are linked by name so this file
never imports their code. backend/shared/models.py loads them all together.
"""
from datetime import date, datetime, time

from sqlalchemy import CheckConstraint, ForeignKey, Index, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.core.constants import CATEGORIES
from backend.database import Base
from backend.shared.time import utcnow

_CATEGORY_SQL = ", ".join(f"'{c}'" for c in CATEGORIES)


class Announcement(Base):
    __tablename__ = "announcements"
    __table_args__ = (
        CheckConstraint(f"category IN ({_CATEGORY_SQL})", name="ck_announcement_category"),
        Index("ix_announcement_published", "is_published", "published_at"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(150))
    description: Mapped[str] = mapped_column(Text)
    category: Mapped[str] = mapped_column(String(20))
    author_id: Mapped[int] = mapped_column(ForeignKey("publishers.id"))
    created_at: Mapped[datetime] = mapped_column(default=utcnow)
    updated_at: Mapped[datetime] = mapped_column(default=utcnow, onupdate=utcnow)
    published_at: Mapped[datetime | None]  # set the first time it is published
    event_date: Mapped[date | None]
    event_time: Mapped[time | None]
    venue: Mapped[str | None] = mapped_column(String(150))
    registration_link: Mapped[str | None] = mapped_column(String(500))
    is_published: Mapped[bool] = mapped_column(default=False)

    author = relationship("Publisher", back_populates="announcements")
    attachments = relationship(
        "Attachment", back_populates="announcement", cascade="all, delete-orphan", lazy="selectin", order_by="Attachment.kind"
    )
    notifications = relationship("Notification", back_populates="announcement", cascade="all, delete-orphan")
