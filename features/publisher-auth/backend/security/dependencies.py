"""Authentication dependencies other members attach to their routes. Owner: publisher-auth.

    publisher: Publisher = Depends(get_current_publisher)           # login required (401 otherwise)
    publisher: Publisher | None = Depends(get_optional_publisher)   # works for students and publishers
"""
from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from backend.core.config import Settings, get_settings
from backend.core.errors import AppError
from backend.database import get_db
from features.publisher_auth.backend.models.publisher import Publisher
from features.publisher_auth.backend.security.tokens import decode_access_token
from features.publisher_auth.backend.services import auth_service

bearer_scheme = HTTPBearer(auto_error=False)


def read_claims(credentials: HTTPAuthorizationCredentials | None, settings: Settings) -> dict | None:
    if credentials is None:
        return None
    return decode_access_token(credentials.credentials, settings.secret_key)


def _publisher_for(db: Session, claims: dict | None) -> Publisher | None:
    if claims is None or auth_service.is_revoked(db, claims["jti"]):
        return None
    return db.get(Publisher, int(claims["sub"]))


def get_optional_publisher(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    db: Session = Depends(get_db),
    settings: Settings = Depends(get_settings),
) -> Publisher | None:
    return _publisher_for(db, read_claims(credentials, settings))


def get_current_publisher(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    db: Session = Depends(get_db),
    settings: Settings = Depends(get_settings),
) -> Publisher:
    publisher = _publisher_for(db, read_claims(credentials, settings))
    if publisher is None:
        raise AppError.unauthorized("Your session has ended. Please log in again.")
    return publisher
