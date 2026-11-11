"""Announcement request and response shapes. Owner: Mihir.

The validators here are the single place where announcement rules live; the React form repeats
the same limits only to give faster feedback.
"""
from datetime import date, datetime, time

from pydantic import BaseModel, ConfigDict, field_validator

from backend.core.constants import CATEGORIES, LINK_MAX, TITLE_MAX, VENUE_MAX
from backend.shared.schemas import AttachmentSummary, UtcDateTime


def _blank_to_none(value):
    if isinstance(value, str) and not value.strip():
        return None
    return value


class AnnouncementIn(BaseModel):
    title: str
    description: str
    category: str
    venue: str | None = None
    event_date: date | None = None
    event_time: time | None = None
    registration_link: str | None = None

    @field_validator("title", mode="before")
    @classmethod
    def _title(cls, value):
        value = (value or "").strip() if isinstance(value, str) or value is None else value
        if not value:
            raise ValueError("Title is required.")
        if len(value) > TITLE_MAX:
            raise ValueError(f"Title must be {TITLE_MAX} characters or fewer.")
        return value

    @field_validator("description", mode="before")
    @classmethod
    def _description(cls, value):
        value = (value or "").strip() if isinstance(value, str) or value is None else value
        if not value:
            raise ValueError("Description is required.")
        return value

    @field_validator("category", mode="before")
    @classmethod
    def _category(cls, value):
        value = value.strip() if isinstance(value, str) else value
        if value not in CATEGORIES:
            raise ValueError("Category must be one of: " + ", ".join(CATEGORIES) + ".")
        return value

    @field_validator("venue", mode="before")
    @classmethod
    def _venue(cls, value):
        value = _blank_to_none(value)
        if isinstance(value, str):
            value = value.strip()
            if len(value) > VENUE_MAX:
                raise ValueError(f"Venue must be {VENUE_MAX} characters or fewer.")
        return value

    @field_validator("registration_link", mode="before")
    @classmethod
    def _link(cls, value):
        value = _blank_to_none(value)
        if isinstance(value, str):
            value = value.strip()
            if len(value) > LINK_MAX or not value.lower().startswith(("http://", "https://")) or " " in value:
                raise ValueError("Registration link must start with http:// or https://.")
        return value

    @field_validator("event_date", mode="before")
    @classmethod
    def _event_date(cls, value):
        value = _blank_to_none(value)
        if isinstance(value, str):
            try:
                return date.fromisoformat(value.strip())
            except ValueError:
                raise ValueError("Event date must look like 2026-12-31.") from None
        return value

    @field_validator("event_time", mode="before")
    @classmethod
    def _event_time(cls, value):
        value = _blank_to_none(value)
        if isinstance(value, str):
            try:
                return time.fromisoformat(value.strip())
            except ValueError:
                raise ValueError("Event time must look like 14:30.") from None
        return value


class AnnouncementCreate(AnnouncementIn):
    is_published: bool = False  # false saves a draft


class AnnouncementUpdate(AnnouncementIn):
    is_published: bool | None = None  # leave out to keep the current status


class AnnouncementOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    description: str
    category: str
    venue: str | None
    event_date: date | None
    event_time: time | None
    registration_link: str | None
    is_published: bool
    created_at: UtcDateTime
    updated_at: UtcDateTime
    published_at: UtcDateTime | None
    attachments: list[AttachmentSummary] = []

    @field_validator("event_time")
    @classmethod
    def _short_time(cls, value: time | None):
        return value.replace(second=0, microsecond=0) if value else value


class PublisherStats(BaseModel):
    total: int
    published: int
    drafts: int
    by_category: dict[str, int]


class PublisherAnnouncements(BaseModel):
    stats: PublisherStats
    items: list[AnnouncementOut]
