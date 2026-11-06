"""The shared dependencies every route may use. Owner: Mihir.

    get_db                  one database session per request           (Mihir)
    get_settings            the running app's settings                 (Mihir)
    get_current_publisher   401 unless a valid publisher token         (Aariz)
    get_optional_publisher  the publisher if logged in, else None      (Aariz)
"""
from backend.core.config import get_settings
from backend.database import get_db
from features.publisher_auth.backend.security.dependencies import get_current_publisher, get_optional_publisher

__all__ = ["get_db", "get_settings", "get_current_publisher", "get_optional_publisher"]
