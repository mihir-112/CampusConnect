"""GET /api/dashboard: the numbers behind the student homepage. Owner: Moksh."""
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from backend.core.constants import CATEGORIES
from backend.database import get_db
from features.core_announcement_engine.backend.models.announcement import Announcement

router = APIRouter(prefix="/api", tags=["Student dashboard"])


class CategoryCount(BaseModel):
    name: str
    count: int


class DashboardOut(BaseModel):
    total: int
    categories: list[CategoryCount]


@router.get("/dashboard", response_model=DashboardOut)
def dashboard(db: Session = Depends(get_db)):
    """How many published announcements exist in total and in each of the four categories."""
    rows = db.execute(
        select(Announcement.category, func.count()).where(Announcement.is_published.is_(True)).group_by(Announcement.category)
    ).all()
    counts = dict(rows)
    return DashboardOut(total=sum(counts.values()), categories=[CategoryCount(name=c, count=counts.get(c, 0)) for c in CATEGORIES])
