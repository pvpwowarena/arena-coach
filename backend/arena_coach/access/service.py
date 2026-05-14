"""Whitelist business-логика: add / remove / check / list.

Принципы:
- Default-deny: check_access возвращает False если нет записи.
- Владельцы (ARENA_COACH_OWNER_DISCORD_IDS) всегда проходят как ADMIN.
- Audit: каждая mutate-операция пишет в JSONL ДО изменения БД.
- Soft-delete: remove ставит active=False, не удаляет строку.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from arena_coach.access.audit import write_audit_entry
from arena_coach.access.crypto import decrypt_field, encrypt_field
from arena_coach.access.models import Role, WhitelistEntry


class AccessService:
    """Сервис управления whitelist'ом. Принимает фабрику async-сессий."""

    def __init__(self, session_factory: async_sessionmaker[AsyncSession]) -> None:
        self._sf = session_factory

    # ── add ──────────────────────────────────────────────────────────────

    async def add_entry(
        self,
        *,
        discord_id: str,
        character: str,
        realm: str,
        role: Role,
        added_by: str,
        expires_at: datetime | None = None,
    ) -> WhitelistEntry:
        """Добавить или обновить запись в whitelist.

        Если пользователь уже есть (active=True или False) — обновляем поля.
        Audit пишется до операции.
        """
        audit_payload: dict[str, Any] = {
            "role": role.value,
            "character": character,
            "realm": realm,
        }
        write_audit_entry(
            actor_discord_id=added_by,
            action="whitelist.add",
            target=discord_id,
            payload=audit_payload,
            result="attempt",
        )

        async with self._sf() as session, session.begin():
            result = await session.execute(
                select(WhitelistEntry).where(WhitelistEntry.discord_id == discord_id)
            )
            existing = result.scalar_one_or_none()

            if existing is not None:
                # Обновляем существующую запись (re-add или изменение роли)
                existing.character_enc = encrypt_field(character)
                existing.realm_enc = encrypt_field(realm)
                existing.role = role
                existing.added_by = added_by
                existing.added_at = datetime.now(tz=timezone.utc)
                existing.expires_at = expires_at
                existing.active = True
                entry = existing
            else:
                entry = WhitelistEntry(
                    discord_id=discord_id,
                    character_enc=encrypt_field(character),
                    realm_enc=encrypt_field(realm),
                    role=role,
                    added_by=added_by,
                    added_at=datetime.now(tz=timezone.utc),
                    expires_at=expires_at,
                    active=True,
                )
                session.add(entry)

        write_audit_entry(
            actor_discord_id=added_by,
            action="whitelist.add",
            target=discord_id,
            payload=audit_payload,
            result="ok",
        )
        return entry

    # ── remove ───────────────────────────────────────────────────────────

    async def remove_entry(self, *, discord_id: str, actor: str) -> bool:
        """Soft-delete записи. Возвращает True если запись была найдена и деактивирована."""
        # Владельца нельзя удалить
        from arena_coach.shared.settings import settings

        if discord_id in settings.owner_ids_set:
            write_audit_entry(
                actor_discord_id=actor,
                action="whitelist.remove",
                target=discord_id,
                payload={"reason": "owner_protected"},
                result="denied",
            )
            return False

        write_audit_entry(
            actor_discord_id=actor,
            action="whitelist.remove",
            target=discord_id,
            payload={},
            result="attempt",
        )

        async with self._sf() as session, session.begin():
            result = await session.execute(
                select(WhitelistEntry).where(
                    WhitelistEntry.discord_id == discord_id,
                    WhitelistEntry.active.is_(True),
                )
            )
            entry = result.scalar_one_or_none()
            if entry is None:
                write_audit_entry(
                    actor_discord_id=actor,
                    action="whitelist.remove",
                    target=discord_id,
                    payload={},
                    result="not_found",
                )
                return False
            entry.active = False

        write_audit_entry(
            actor_discord_id=actor,
            action="whitelist.remove",
            target=discord_id,
            payload={},
            result="ok",
        )
        return True

    # ── check ────────────────────────────────────────────────────────────

    async def check_access(
        self,
        *,
        discord_id: str,
        required_role: Role = Role.VIEWER,
    ) -> bool:
        """Проверить доступ. Default-deny. Владельцы всегда ADMIN.

        Возвращает True только если:
        - discord_id в owner_ids_set (любая required_role), ИЛИ
        - активная запись с role >= required_role и не истёкшим expires_at.
        """
        from arena_coach.shared.settings import settings

        # Владельцы всегда проходят независимо от required_role
        if discord_id in settings.owner_ids_set:
            return True

        async with self._sf() as session:
            result = await session.execute(
                select(WhitelistEntry).where(
                    WhitelistEntry.discord_id == discord_id,
                    WhitelistEntry.active.is_(True),
                )
            )
            entry = result.scalar_one_or_none()

        if entry is None:
            return False

        # Проверяем срок действия
        if entry.expires_at is not None:
            now = datetime.now(tz=timezone.utc)
            # expires_at может быть naive datetime если БД без TZ
            exp = entry.expires_at
            if exp.tzinfo is None:
                from datetime import timezone as _tz

                exp = exp.replace(tzinfo=_tz.utc)
            if now > exp:
                return False

        # Проверяем ранг роли
        return entry.role >= required_role

    # ── list ─────────────────────────────────────────────────────────────

    async def list_entries(self) -> list[WhitelistEntry]:
        """Список всех активных записей."""
        async with self._sf() as session:
            result = await session.execute(
                select(WhitelistEntry).where(WhitelistEntry.active.is_(True))
            )
            return list(result.scalars().all())

    async def get_entry(self, discord_id: str) -> WhitelistEntry | None:
        """Получить активную запись по discord_id."""
        async with self._sf() as session:
            result = await session.execute(
                select(WhitelistEntry).where(
                    WhitelistEntry.discord_id == discord_id,
                    WhitelistEntry.active.is_(True),
                )
            )
            return result.scalar_one_or_none()

    # ── decrypt helpers ──────────────────────────────────────────────────

    def decrypt_character(self, entry: WhitelistEntry) -> str:
        """Расшифровать имя персонажа."""
        return decrypt_field(entry.character_enc)

    def decrypt_realm(self, entry: WhitelistEntry) -> str:
        """Расшифровать реалм."""
        return decrypt_field(entry.realm_enc)


__all__ = ["AccessService"]
