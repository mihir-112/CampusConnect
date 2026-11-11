"""The shared dependencies every route may use. Owner: core-announcement-engine.

    get_db                  one database session per request           (core-announcement-engine)
    get_settings            the running app's settings                 (core-announcement-engine)
    get_current_publisher   401 unless a valid publisher token         (publisher-auth)
    get_optional_publisher  the publisher if logged in, else None      (publisher-auth)
"""
from backend.core.config import get_settings
from backend.database import get_db
from features.publisher_auth.backend.security.dependencies import get_current_publisher, get_optional_publisher

__all__ = ["get_db", "get_settings", "get_current_publisher", "get_optional_publisher"]
