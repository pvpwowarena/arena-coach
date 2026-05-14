"""Тесты AccessService: deny/allow paths, role hierarchy, add/remove (Phase 2).

Использует SQLite in-memory через aiosqlite + pytest-asyncio (asyncio_mode="auto").
"""

from __future__ import annotations

from pathlib import Path

import pytest
from cryptography.fernet import Fernet
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from arena_coach.access.models import Base, Role
from arena_coach.access.service import AccessService

# ── Fixtures ──────────────────────────────────────────────────────────────────


@pytest.fixture()
def fernet_key() -> str:
    return Fernet.generate_key().decode()


@pytest.fixture()
def patched_settings(
    fernet_key: str,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Подменяем settings на тестовые значения."""
    import arena_coach.shared.settings as _sm
    from arena_coach.shared.settings import Settings

    cfg = Settings(
        arena_coach_fernet_key=fernet_key,
        arena_coach_owner_discord_ids=["owner-999"],
        discord_bot_token="test",
        discord_guild_id=0,
        audit_log_dir=str(tmp_path / "audit"),
    )
    monkeypatch.setattr(_sm, "settings", cfg)


@pytest.fixture()
async def service(patched_settings: None) -> AccessService:
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    factory: async_sessionmaker[AsyncSession] = async_sessionmaker(
        engine, expire_on_commit=False
    )
    return AccessService(factory)


# ── Tests ─────────────────────────────────────────────────────────────────────


async def test_default_deny(service: AccessService) -> None:
    """Пользователь без записи → access denied."""
    assert not await service.check_access(discord_id="no-one", required_role=Role.VIEWER)


async def test_owner_always_passes(service: AccessService) -> None:
    """Владелец имеет доступ без записи в БД."""
    assert await service.check_access(discord_id="owner-999", required_role=Role.ADMIN)


async def test_add_and_allow_viewer(service: AccessService) -> None:
    await service.add_entry(
        discord_id="u1",
        character="Stabby",
        realm="Gorefiend",
        role=Role.VIEWER,
        added_by="owner-999",
    )
    assert await service.check_access(discord_id="u1", required_role=Role.VIEWER)


async def test_viewer_denied_player_commands(service: AccessService) -> None:
    await service.add_entry(
        discord_id="u2",
        character="Bob",
        realm="Gorefiend",
        role=Role.VIEWER,
        added_by="owner-999",
    )
    assert not await service.check_access(discord_id="u2", required_role=Role.PLAYER)


async def test_player_allows_lower_roles(service: AccessService) -> None:
    await service.add_entry(
        discord_id="u3",
        character="Alice",
        realm="Gorefiend",
        role=Role.PLAYER,
        added_by="owner-999",
    )
    assert await service.check_access(discord_id="u3", required_role=Role.VIEWER)
    assert await service.check_access(discord_id="u3", required_role=Role.PLAYER)
    assert not await service.check_access(discord_id="u3", required_role=Role.ADMIN)


async def test_admin_allows_all(service: AccessService) -> None:
    await service.add_entry(
        discord_id="u4",
        character="God",
        realm="Gorefiend",
        role=Role.ADMIN,
        added_by="owner-999",
    )
    for role in Role:
        assert await service.check_access(discord_id="u4", required_role=role)


async def test_remove_revokes_access(service: AccessService) -> None:
    await service.add_entry(
        discord_id="u5",
        character="Temp",
        realm="Gorefiend",
        role=Role.VIEWER,
        added_by="owner-999",
    )
    assert await service.check_access(discord_id="u5", required_role=Role.VIEWER)

    assert await service.remove_entry(discord_id="u5", actor="owner-999")
    assert not await service.check_access(discord_id="u5", required_role=Role.VIEWER)


async def test_remove_nonexistent_returns_false(service: AccessService) -> None:
    assert not await service.remove_entry(discord_id="ghost", actor="owner-999")


async def test_decrypt_roundtrip(service: AccessService) -> None:
    await service.add_entry(
        discord_id="u6",
        character="Stabby",
        realm="Gorefiend",
        role=Role.PLAYER,
        added_by="owner-999",
    )
    entry = await service.get_entry("u6")
    assert entry is not None
    assert service.decrypt_character(entry) == "Stabby"
    assert service.decrypt_realm(entry) == "Gorefiend"


async def test_list_entries_active_only(service: AccessService) -> None:
    for i in range(3):
        await service.add_entry(
            discord_id=f"u{i}",
            character=f"C{i}",
            realm="GF",
            role=Role.VIEWER,
            added_by="owner-999",
        )
    await service.remove_entry(discord_id="u0", actor="owner-999")
    entries = await service.list_entries()
    ids = {e.discord_id for e in entries}
    assert "u0" not in ids
    assert {"u1", "u2"} <= ids


async def test_readd_reactivates(service: AccessService) -> None:
    await service.add_entry(
        discord_id="u7", character="Old", realm="GF", role=Role.VIEWER, added_by="owner-999"
    )
    await service.remove_entry(discord_id="u7", actor="owner-999")
    assert not await service.check_access(discord_id="u7", required_role=Role.VIEWER)

    await service.add_entry(
        discord_id="u7", character="New", realm="GF", role=Role.PLAYER, added_by="owner-999"
    )
    assert await service.check_access(discord_id="u7", required_role=Role.PLAYER)
    entry = await service.get_entry("u7")
    assert entry is not None
    assert service.decrypt_character(entry) == "New"


async def test_owner_cannot_be_removed(service: AccessService) -> None:
    """Владельца нельзя удалить даже через remove_entry."""
    result = await service.remove_entry(discord_id="owner-999", actor="owner-999")
    assert result is False
