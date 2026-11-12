"""POST /api/auth/login, POST /api/auth/logout, GET /api/auth/me. Owner: publisher-auth."""
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, Request
from fastapi.security import HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from backend.core.config import Settings, get_settings
from backend.core.errors import AppError
from backend.database import get_db
from features.publisher_auth.backend.models.publisher import Publisher
from features.publisher_auth.backend.schemas.auth import LoginRequest, PublisherOut, TokenOut
from features.publisher_auth.backend.security.dependencies import bearer_scheme, get_current_publisher, read_claims
from features.publisher_auth.backend.security.tokens import create_access_token
from features.publisher_auth.backend.services import auth_service

router = APIRouter(prefix="/api/auth", tags=["Authentication"])


@router.post("/login", response_model=TokenOut)
def login(payload: LoginRequest, request: Request, db: Session = Depends(get_db), settings: Settings = Depends(get_settings)):
    throttle = request.app.state.login_throttle
    key = payload.username.lower()
    if throttle.is_locked(key):
        raise AppError(429, "Too many failed attempts. Please wait a few minutes and try again.")

    publisher = auth_service.authenticate(db, payload.username, payload.password)
    if publisher is None:
        throttle.record_failure(key)
        # The same message for an unknown user and a wrong password, so usernames cannot be probed.
        raise AppError(401, "Invalid username or password.", headers={"WWW-Authenticate": "Bearer"})

    throttle.reset(key)
    token, _expires = create_access_token(publisher.id, settings.secret_key, settings.access_token_minutes)
    return TokenOut(access_token=token, expires_in=settings.access_token_minutes * 60, publisher=PublisherOut.model_validate(publisher))


@router.post("/logout")
def logout(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    _publisher: Publisher = Depends(get_current_publisher),
    db: Session = Depends(get_db),
    settings: Settings = Depends(get_settings),
):
    claims = read_claims(credentials, settings)
    auth_service.revoke_token(db, claims["jti"], datetime.fromtimestamp(claims["exp"], tz=timezone.utc))
    return {"ok": True}


@router.get("/me", response_model=PublisherOut)
def me(publisher: Publisher = Depends(get_current_publisher)):
    return publisher
