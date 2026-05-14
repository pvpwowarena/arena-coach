"""SQLAlchemy 2 декларативные модели: WhitelistEntry, Role.

Схема: docs/phase-0-design.md §5.1.
character и realm хранятся зашифрованными (Fernet) — никогда plaintext в БД.
"""

from __future__ import annotations

from datetime import datetime
from enum import Enum

from sqlalchemy import Boolean, DateTime, Integer, LargeBinary, String
from sqlalchemy import Enum as SAEnum
from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Role(str, Enum):
    VIEWER = "viewer"
    PLAYER = "player"
    ADMIN = "admin"

    def rank(self) -> int:
        """Числовой ранг для сравнения ролей: VIEWER=0, PLAYER=1, ADMIN=2."""
        return {"viewer": 0, "player": 1, "admin": 2}[self.value]

    def __ge__(self, other: object) -> bool:
        if not isinstance(other, Role):
            return NotImplemented
        return self.rank() >= other.rank()

    def __gt__(self, other: object) -> bool:
        if not isinstance(other, Role):
            return NotImplemented
        return self.rank() > other.rank()

    def __le__(self, other: object) -> bool:
        if not isinstance(other, Role):
            return NotImplemented
        return self.rank() <= other.rank()

    def __lt__(self, other: object) -> bool:
        if not isinstance(other, Role):
            return NotImplemented
        return self.rank() < other.rank()


class Base(AsyncAttrs, DeclarativeBase):
    pass


class WhitelistEntry(Base):
    """Запись в whitelist.

    character_enc / realm_enc — Fernet-зашифрованные bytes.
    Для чтения: access.service.AccessService.decrypt_character / decrypt_realm.
    Soft-delete: active=False вместо физического удаления (для audit trail).
    """

    __tablename__ = "whitelist_entries"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    # Discord user ID хранится как строка (избегаем потери точности 64-bit int)
    discord_id: Mapped[str] = mapped_column(String(64), unique=True, index=True, nullable=False)

    # Зашифрованные игровые данные
    character_enc: Mapped[bytes] = mapped_column(LargeBinary, nullable=False)
    realm_enc: Mapped[bytes] = mapped_column(LargeBinary, nullable=False)

    role: Mapped[Role] = mapped_column(SAEnum(Role), nullable=False, default=Role.VIEWER)

    # Кто добавил и когда
    added_by: Mapped[str] = mapped_column(String(64), nullable=False)
    added_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)

    # Опциональное время истечения (None = бессрочно)
    expires_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    # Soft-delete: remove не удаляет строку, сохраняет историю для audit
    active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    def __repr__(self) -> str:
        return (
            f"<WhitelistEntry discord_id={self.discord_id!r} "
            f"role={self.role.value!r} active={self.active}>"
        )
