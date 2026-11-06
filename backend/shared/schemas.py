"""Schemas used by more than one member. Owner: Mihir (integration contract)."""
from datetime import datetime
from typing import Annotated, Generic, TypeVar

from pydantic import BaseModel, ConfigDict, PlainSerializer, computed_field

# Times are stored as UTC without a label. The API adds "Z" so browsers read them correctly.
UtcDateTime = Annotated[
    datetime, PlainSerializer(lambda value: value.isoformat() + "Z" if value else None, return_type=str | None, when_used="json")
]

T = TypeVar("T")


class Page(BaseModel, Generic[T]):
    items: list[T]
    page: int
    per_page: int
    pages: int
    total: int


class AttachmentSummary(BaseModel):
    """How an attachment appears inside an announcement. Table owner: Nayeem."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    kind: str
    original_filename: str
    mime_type: str
    size_bytes: int
    available: bool = True

    @computed_field
    @property
    def url(self) -> str:
        return f"/api/attachments/{self.id}"

    @computed_field
    @property
    def download_url(self) -> str:
        return f"/api/attachments/{self.id}/download"
