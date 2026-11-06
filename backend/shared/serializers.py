"""Turns database rows into API responses. Owner: Mihir.

Adds the one thing the database cannot know: whether each attached file is still on disk.
"""
import os

from backend.core.config import Settings
from features.core_announcement_engine.backend.models.announcement import Announcement
from features.core_announcement_engine.backend.schemas.announcement import AnnouncementOut


def announcement_out(announcement: Announcement, settings: Settings) -> AnnouncementOut:
    out = AnnouncementOut.model_validate(announcement)
    stored = {a.id: a.stored_filename for a in announcement.attachments}
    for summary in out.attachments:
        summary.available = os.path.isfile(os.path.join(settings.upload_dir, stored[summary.id]))
    return out
