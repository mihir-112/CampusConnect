"""Student homepage. Owner: Moksh."""
from flask import Blueprint, current_app, render_template, request
from sqlalchemy.exc import SQLAlchemyError

from ..constants import CATEGORIES
from ..services import search_service

bp = Blueprint("dashboard", __name__)


@bp.get("/")
def index():
    q = request.args.get("q", "").strip()
    category = request.args.get("category", "").strip()
    if category not in CATEGORIES:
        category = ""
    page = request.args.get("page", 1, type=int)

    try:
        pagination = search_service.search_announcements(
            q, category or None, page=page, per_page=current_app.config["ANNOUNCEMENTS_PER_PAGE"]
        )
    except SQLAlchemyError:
        current_app.logger.exception("Could not load announcements")
        return render_template("dashboard.html", load_error=True, announcements=[], pagination=None,
                               q=q, active_category=category), 500

    return render_template(
        "dashboard.html",
        load_error=False,
        announcements=pagination.items,
        pagination=pagination,
        q=q,
        active_category=category,
    )
