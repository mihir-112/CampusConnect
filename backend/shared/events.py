"""Tiny event hub. Owner: Mihir.

This is the integration interface between modules. The announcement service announces what
happened ("published", "unpublished", "deleted") and other members' code reacts, so the core
never has to import notification or file code.

    subscribe(PUBLISHED, my_function)      # who listens
    emit(PUBLISHED, db=db, announcement=a) # who announces
"""
from collections import defaultdict

PUBLISHED = "announcement.published"
UNPUBLISHED = "announcement.unpublished"
DELETED = "announcement.deleted"

_listeners: dict = defaultdict(list)


def subscribe(event: str, handler) -> None:
    if handler not in _listeners[event]:  # safe to call more than once
        _listeners[event].append(handler)


def emit(event: str, **context) -> None:
    for handler in list(_listeners[event]):
        handler(**context)
