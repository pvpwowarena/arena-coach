"""SQLAlchemy модели: WhitelistEntry, Role. Phase 2 skeleton.

См. docs/phase-0-design.md §5.1 — финальная схема.
"""

from __future__ import annotations

from enum import Enum


class Role(str, Enum):
    VIEWER = "viewer"
    PLAYER = "player"
    ADMIN = "admin"


# TODO(Phase 2): SQLAlchemy 2 declarative модели.
# class Base(DeclarativeBase): ...
# class WhitelistEntry(Base): ...
