"""Login, logout and publisher accounts. Owner: publisher-auth."""
from datetime import datetime

from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from backend.core.errors import AppError
from backend.shared.time import utcnow
from features.publisher_auth.backend.models.publisher import Publisher
from features.publisher_auth.backend.models.revoked_token import RevokedToken
from features.publisher_auth.backend.security.passwords import hash_password, is_legacy_hash, verify_password

MIN_PASSWORD = 8


def authenticate(db: Session, username: str, password: str) -> Publisher | None:
    publisher = db.scalar(select(Publisher).where(Publisher.username == username))
    if publisher is None or not verify_password(publisher.password_hash, password):
        return None
    if is_legacy_hash(publisher.password_hash):  # upgrade old Flask hashes
        publisher.password_hash = hash_password(password)
        db.commit()
    return publisher


def create_publisher(db: Session, username: str, email: str, password: str) -> Publisher:
    username, email = username.strip(), email.strip().lower()
    errors = {}
    if not username:
        errors["username"] = "Username is required."
    if "@" not in email:
        errors["email"] = "Enter a valid email address."
    if len(password) < MIN_PASSWORD:
        errors["password"] = f"Password must be at least {MIN_PASSWORD} characters."
    if errors:
        raise AppError.validation(errors)
    taken = db.scalar(select(Publisher).where((Publisher.username == username) | (Publisher.email == email)))
    if taken is not None:
        raise AppError(409, "A publisher with that username or email already exists.")
    publisher = Publisher(username=username, email=email, password_hash=hash_password(password))
    db.add(publisher)
    db.commit()
    return publisher


def revoke_token(db: Session, jti: str, expires_at: datetime) -> None:
    db.execute(delete(RevokedToken).where(RevokedToken.expires_at < utcnow()))  # tidy up old rows
    if db.get(RevokedToken, jti) is None:
        db.add(RevokedToken(jti=jti, expires_at=expires_at.replace(tzinfo=None)))
    db.commit()


def is_revoked(db: Session, jti: str) -> bool:
    return db.get(RevokedToken, jti) is not None
