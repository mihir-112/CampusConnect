"""Application settings. Owner: Mihir.

Every value can be set with an environment variable. Nothing secret is written in the source:
if SECRET_KEY is missing, a random one is created for this run (logins end when the server restarts).
"""
import logging
import os
import secrets
from dataclasses import dataclass, replace
from pathlib import Path

from fastapi import Request

log = logging.getLogger("campusconnect")

ROOT_DIR = Path(__file__).resolve().parents[2]
INSTANCE_DIR = ROOT_DIR / "instance"


@dataclass(frozen=True)
class Settings:
    database_url: str
    upload_dir: str
    secret_key: str
    access_token_minutes: int = 120
    cors_origins: tuple = ("http://localhost:5173", "http://127.0.0.1:5173")
    per_page: int = 9
    login_max_attempts: int = 5
    login_window_seconds: int = 300


def _sqlite_url(path: Path) -> str:
    return "sqlite:///" + path.as_posix()


def load_settings(**overrides) -> Settings:
    secret = os.environ.get("SECRET_KEY")
    if not secret:
        secret = secrets.token_urlsafe(48)
        log.warning("SECRET_KEY is not set. Using a temporary key; publishers must log in again after a restart.")
    origins = os.environ.get("CORS_ORIGINS")
    settings = Settings(
        database_url=os.environ.get("DATABASE_URL", _sqlite_url(INSTANCE_DIR / "campusconnect.db")),
        upload_dir=os.environ.get("UPLOAD_DIR", str(INSTANCE_DIR / "uploads")),
        secret_key=secret,
        access_token_minutes=int(os.environ.get("ACCESS_TOKEN_MINUTES", "120")),
        cors_origins=tuple(o.strip() for o in origins.split(",") if o.strip())
        if origins
        else Settings.__dataclass_fields__["cors_origins"].default,
    )
    return replace(settings, **overrides) if overrides else settings


def get_settings(request: Request) -> Settings:  # FastAPI dependency
    return request.app.state.settings
