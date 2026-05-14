"""Тесты AccessService: deny/allow paths, add/remove, role hierarchy.

Использует SQLite in-memory через aiosqlite + pytest-asyncio.
"""

from __future__ import annotations

import pytest
import pytest_asyncio
from cryptography.fernet import Fernet
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from arena_coach.access.models import Base, Role, WhitelistEntry
from arena_coach.access.service import AccessService


# ── Fixtures ─────────────────────────────────────────────────────────────────


@pytest.fixture()
def fernet_key() -> str:
    return Fernet.generate_key().decode()


@pytest_asyncio.fixture()
async def service(
    fernet_key: str,
    monkeypatch: pytest.MonkeyPatch,
) -> AccessService:
    """AccessService с in-memory SQLite и тестовыми settings."""
    import arena_coach.shared.settings as _sm
    from arena_coach.shared.settings import Settings

    cfg = Settings(
        arena_coach_fernet_key=fernet_key,
        arena_coach_owner_discord_ids=["owner-id-999"],
        discord_bot_token="test",
        discord_guild_id=0,
        audit_log_dir="/tmp/arena_coach_test_audit",
    )
    monkeypatch.setattr(_sm, "settings", cfg)

    engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    factory = async_sessionmaker(engine, expire_on_commit=False)
    return AccessService(factory)


# ── Tests ────────────────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_default_deny(service: AccessService) -> None:
    """Пользователь без записи в whitelist → access denied."""
    has_access = await service.check_access(
        discord_id="no-such-user", required_role=Role.VIEWER
    )
    assert has_access is False


@pytest.mark.asyncio
async def test_owner_always_passes(service: AccessService) -> None:
    """Владелец (из ARENA_COACH_OWNER_DISCORD_IDS) имеет доступ без записи в БД."""
    has_access = await service.check_access(
        discord_id="owner-id-999", required_role=Role.ADMIN
    )
    assert has_access is True


@pytest.mark.asyncio
async def test_add_and_allow_viewer(service: AccessService) -> None:
    """Добавленный viewer имеет доступ для роли VIEWER."""
    await service.add_entry(
        discord_id="user-111",
        character="Stabby",
        realm="Gorefiend",
        role=Role.VIEWER,
        added_by="owner-id-999",
    )
    assert await service.check_access(discord_id="user-111", required_role=Role.VIEWER)


@pytest.mark.asyncio
async def test_viewer_denied_player_role(service: AccessService) -> None:
    """Viewer не получает доступ к командам с required_role=PLAYER."""
    await service.add_entry(
        discord_id="user-222",
        character="Bob",
        realm="Gorefiend",
        role=Role.VIEWER,
        added_by="owner-id-999",
    )
    has_access = await service.check_access(
        discord_id="user-222", required_role=Role.PLAYER
    )
    assert has_access is False


@pytest.mark.asyncio
async def test_player_allows_viewer_commands(service: AccessService) -> None:
    """PLAYER (rank=1) >= VIEWER (rank=0) → доступ разрешён."""
    await service.add_entry(
        discord_id="user-333",
        character="Alice",
        realm="Gorefiend",
        role=Role.PLAYER,
        added_by="owner-id-999",
    )
    assert await service.check_access(discord_id="user-333", required_role=Role.VIEWER)
    assert await service.check_access(discord_id="user-333", required_role=Role.PLAYER)
    assert not await service.check_access(
        discord_id="user-333", required_role=Role.ADMIN
    )


@pytest.mark.asyncio
async def test_admin_allows_all_roles(service: AccessService) -> None:
    """ADMIN имеет доступ ко всем ролям."""
    await service.add_entry(
        discord_id="user-444",
        character="Godmode",
        realm="Gorefiend",
        role=Role.ADMIN,
        added_by="owner-id-999",
    )
    for role in Role:
        assert await service.check_access(discord_id="user-444", required_role=role)


@pytest.mark.asyncio
async def test_remove_revokes_access(service: AccessService) -> None:
    """После remove_entry доступ должен быть отозван."""
    await service.add_entry(
        discord_id="user-555",
        character="Temp",
        realm="Gorefiend",
        role=Role.VIEWER,
        added_by="owner-id-999",
    )
    assert await service.check_access(discord_id="user-555", required_role=Role.VIEWER)

    removed = await service.remove_entry(discord_id="user-555", actor="owner-id-999")
    assert removed is True

    assert not await service.check_access(
        discord_id="user-555", required_role=Role.VIEWER
    )


@pytest.mark.asyncio
async def test_remove_nonexistent_returns_false(service: AccessService) -> None:
    """remove_entry несуществующего пользователя → False."""
    removed = await service.remove_entry(
        discord_id="ghost-user", actor="owner-id-999"
    )
    assert removed is False


@pytest.mark.asyncio
async def test_decrypt_character_realm(service: AccessService) -> None:
    """decrypt_character и decrypt_realm возвращают исходные значения."""
    await service.add_entry(
        discord_id="user-666",
        character="Stabby",
        realm="Gorefiend",
        role=Role.PLAYER,
        added_by="owner-id-999",
    )
    entry = await service.get_entry("user-666")
    assert entry is not None
    assert service.decrypt_character(entry) == "Stabby"
    assert service.decrypt_realm(entry) == "Gorefiend"


@pytest.mark.asyncio
async def test_list_entries(service: AccessService) -> None:
    """list_entries возвращает только активные записи."""
    for i in range(3):
        await service.add_entry(
            discord_id=f"user-{i}",
            character=f"Char{i}",
            realm="Gorefiend",
            role=Role.VIEWER,
            added_by="owner-id-999",
        )
    await service.remove_entry(discord_id="user-0", actor="owner-id-999")

    entries = await service.list_entries()
    ids = [e.discord_id for e in entries]
    assert "user-0" not in ids
    assert "user-1" in ids
    assert "user-2" in ids


@pytest.mark.asyncio
async def test_readd_reactivates(service: AccessService) -> None:
    """Повторный add_entry для удалённого пользователя реактивирует запись."""
    await service.add_entry(
        discord_id="user-777",
        character="Old",
        realm="Gorefiend",
        role=Role.VIEWER,
        added_by="owner-id-999",
    )
    await service.remove_entry(discord_id="user-777", actor="owner-id-999")
    assert not await service.check_access(discord_id="user-777", required_role=Role.VIEWER)

    await service.add_entry(
        discord_id="user-777",
        character="New",
        realm="Gorefiend",
        role=Role.PLAYER,
        added_by="owner-id-999",
    )
    assert await service.check_access(discord_id="user-777", required_role=Role.PLAYER)
    entry = await service.get_entry("user-777")
    assert entry is not None
    assert service.decrypt_character(entry) == "New"
