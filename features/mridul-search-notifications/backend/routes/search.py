"""GET /api/search?q=&category=&page= . Owner: Mridul."""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from backend.core.config import Settings, get_settings
from backend.database import get_db
from backend.shared.serializers import announcement_out
from features.search_notifications.backend.schemas.notification import SearchResults
from features.search_notifications.backend.services import search_service

router = APIRouter(prefix="/api", tags=["Search"])


@router.get("/search", response_model=SearchResults)
def search(
    q: str = "",
    category: str | None = None,
    page: int = Query(1, ge=1),
    per_page: int = Query(9, ge=1, le=50),
    db: Session = Depends(get_db),
    settings: Settings = Depends(get_settings),
):
    items, total, pages, keyword, cat = search_service.search_announcements(db, q, category, page, per_page)
    return SearchResults(
        items=[announcement_out(a, settings) for a in items], page=page, per_page=per_page, pages=pages, total=total, q=keyword, category=cat
    )
