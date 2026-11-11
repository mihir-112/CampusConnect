"""FastAPI entry point. Owner: core-announcement-engine.

Start it with:   py -m uvicorn backend.main:app --reload --port 8000
API documentation (Swagger) is at http://127.0.0.1:8000/docs
"""
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.core.config import Settings, load_settings
from backend.core.errors import register_error_handlers
from backend.database import Database


def create_app(settings: Settings | None = None) -> FastAPI:
    """Build the application. Tests call this with their own temporary settings."""
    settings = settings or load_settings()

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        app.state.db.create_tables()
        yield
        app.state.db.dispose()

    app = FastAPI(
        title="CampusConnect API",
        description="Your campus. One place. College announcements for students, management tools for publishers.",
        version="1.0.0",
        lifespan=lifespan,
    )
    app.state.settings = settings
    app.state.db = Database(settings.database_url)

    from features.publisher_auth.backend.security.throttle import LoginThrottle

    app.state.login_throttle = LoginThrottle(settings.login_max_attempts, settings.login_window_seconds)

    app.add_middleware(
        CORSMiddleware,
        allow_origins=list(settings.cors_origins),
        allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE"],
        allow_headers=["Authorization", "Content-Type", "X-Client-Id"],
    )
    register_error_handlers(app)

    # Each feature's router is registered here. Paths are listed in docs/api-documentation.md.
    from features.publisher_auth.backend.routes import auth
    from features.core_announcement_engine.backend.routes import announcements
    from features.student_dashboard.backend.routes import dashboard
    from features.search_notifications.backend.routes import notifications, search
    from features.notice_details.backend.routes import attachments

    for module in (auth, announcements, attachments, dashboard, search, notifications):
        app.include_router(module.router)

    @app.get("/api/health", tags=["System"])
    def health():
        return {"status": "ok"}

    return app


app = create_app()
