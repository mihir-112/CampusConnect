"""Imports every model so SQLAlchemy knows all tables before they are created. Owner: core-announcement-engine."""


def import_all_models() -> None:
    from features.publisher_auth.backend.models import publisher, revoked_token  # noqa: F401
    from features.core_announcement_engine.backend.models import announcement  # noqa: F401
    from features.search_notifications.backend.models import notification  # noqa: F401
    from features.notice_details.backend.models import attachment  # noqa: F401
