"""Simple pagination for SELECT statements. Owner: Mihir."""
import math

from sqlalchemy import func, select
from sqlalchemy.orm import Session


def paginate(db: Session, statement, page: int, per_page: int):
    """Return (items, total, pages) for the requested page of `statement`."""
    page = max(page, 1)
    per_page = max(1, min(per_page, 50))
    total = db.scalar(select(func.count()).select_from(statement.order_by(None).subquery())) or 0
    items = db.scalars(statement.limit(per_page).offset((page - 1) * per_page)).all()
    return items, total, max(math.ceil(total / per_page), 1)
