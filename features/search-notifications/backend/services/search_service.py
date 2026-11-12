"""Keyword search and category filtering. Owner: search-notifications."""
from sqlalchemy import or_
from sqlalchemy.orm import Session

from backend.core.constants import CATEGORIES
from backend.core.errors import AppError
from backend.shared.pagination import paginate
from features.core_announcement_engine.backend.models.announcement import Announcement
from features.core_announcement_engine.backend.services.announcement_service import published_query

MAX_KEYWORD = 100


def _escape_like(text: str) -> str:
    """Make %, _ and \\ in the typed text match literally."""
    return text.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")


def search_announcements(db: Session, q: str | None, category: str | None, page: int, per_page: int):
    """Published announcements, newest first, optionally narrowed by keyword and category."""
    category = (category or "").strip() or None
    if category and category not in CATEGORIES:
        raise AppError.validation({"category": "Category must be one of: " + ", ".join(CATEGORIES) + "."})

    statement = published_query()
    if category:
        statement = statement.where(Announcement.category == category)

    keyword = (q or "").strip()[:MAX_KEYWORD]
    if keyword:
        pattern = f"%{_escape_like(keyword)}%"
        statement = statement.where(
            or_(
                Announcement.title.ilike(pattern, escape="\\"),
                Announcement.description.ilike(pattern, escape="\\"),
                Announcement.venue.ilike(pattern, escape="\\"),
            )
        )
    items, total, pages = paginate(db, statement, page, per_page)
    return items, total, pages, keyword, category
