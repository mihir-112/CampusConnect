"""JWT creation and checking. Owner: publisher-auth."""
import uuid
from datetime import datetime, timedelta, timezone

import jwt

ALGORITHM = "HS256"


def create_access_token(publisher_id: int, secret_key: str, minutes: int) -> tuple[str, datetime]:
    """Return (token, expiry). The token carries the publisher id, a unique id (jti) and an expiry."""
    now = datetime.now(timezone.utc)
    expires = now + timedelta(minutes=minutes)
    claims = {"sub": str(publisher_id), "jti": uuid.uuid4().hex, "iat": now, "exp": expires}
    return jwt.encode(claims, secret_key, algorithm=ALGORITHM), expires


def decode_access_token(token: str, secret_key: str) -> dict | None:
    """Return the claims, or None if the token is forged, expired or malformed."""
    try:
        claims = jwt.decode(token, secret_key, algorithms=[ALGORITHM], options={"require": ["exp", "sub", "jti"]})
        int(claims["sub"])
        return claims
    except (jwt.PyJWTError, ValueError):
        return None
