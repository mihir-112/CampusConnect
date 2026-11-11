"""Logged-out tokens. Owner: publisher-auth.

A JWT cannot be "deleted" once issued, so logout stores the token's id here and every
protected request checks the list. Rows can be removed after the token would have expired anyway.
"""
from datetime import datetime

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from backend.database import Base


class RevokedToken(Base):
    __tablename__ = "revoked_tokens"

    jti: Mapped[str] = mapped_column(String(64), primary_key=True)
    expires_at: Mapped[datetime]
