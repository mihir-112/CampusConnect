"""Notification tables. Owner: Mridul.

`notifications` is shared by everyone. There are no student accounts, so "read" is remembered per
browser: the React app creates a random browser id and `notification_reads` stores
(browser id, notification). Clearing browser data makes everything unread again.
"""
from datetime import datetime

from sqlalchemy import ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.database import Base
from backend.shared.time import utcnow


class Notification(Base):
    __tablename__ = "notifications"

    id: Mapped[int] = mapped_column(primary_key=True)
    announcement_id: Mapped[int] = mapped_column(ForeignKey("announcements.id", ondelete="CASCADE"))
    message: Mapped[str] = mapped_column(String(200))
    created_at: Mapped[datetime] = mapped_column(default=utcnow)

    announcement = relationship("Announcement", back_populates="notifications")
    reads = relationship("NotificationRead", cascade="all, delete-orphan", passive_deletes=True)


class NotificationRead(Base):
    __tablename__ = "notification_reads"
    __table_args__ = (UniqueConstraint("client_id", "notification_id", name="uq_read_client_notification"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    client_id: Mapped[str] = mapped_column(String(64), index=True)
    notification_id: Mapped[int] = mapped_column(ForeignKey("notifications.id", ondelete="CASCADE"))
    read_at: Mapped[datetime] = mapped_column(default=utcnow)
