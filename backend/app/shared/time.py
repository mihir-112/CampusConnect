"""Time helpers. Owner: core-announcement-engine."""
from datetime import datetime, timezone


def utcnow() -> datetime:
    """Current UTC time without a timezone label (SQLite stores it that way)."""
    return datetime.now(timezone.utc).replace(tzinfo=None)
