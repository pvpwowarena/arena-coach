"""Phase 4.16 — чтение настроек игрока не должно ронять приём событий.

Прод-инцидент 30.07.2026: миграция 0005 не доехала до боевой БД (баг в
`ops/scripts/vps-deploy.sh` — «тихая» первая попытка alembic без `api.env`, дефолтный
ОТНОСИТЕЛЬНЫЙ путь к sqlite → мигрировался файл рядом с кодом). В итоге
`SELECT player_settings.combat_text` падал с `no such column`, и КАЖДЫЙ
`POST /v1/events` отвечал 500 — необязательная пользовательская настройка выключила
весь коучинг в бою:

    [WARNING] arena_bridge.ws_client: Backend ответил 500, попытка 1/4
    [WARNING] arena_bridge: Событие потеряно: ARENA_START#2v2##MAGE/UNKNOWN

Тесты ниже фиксируют оба вывода из инцидента:
  • геттеры настроек деградируют до дефолта на ЛЮБОЙ ошибке БД;
  • сеттеры ошибку НЕ глушат (пользователь ждёт подтверждения);
  • сквозь `process_event` событие всё равно обрабатывается.
"""

from __future__ import annotations

import sqlite3
from pathlib import Path
from types import SimpleNamespace
from typing import Any

import pytest
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from arena_coach.access.player_settings import (
    DEFAULT_COMBAT_TEXT,
    DEFAULT_VOICE_MODE,
    PlayerSettingsService,
)
from arena_coach.kb.indexer import KBIndex
from arena_coach.kb.retriever import KBRetriever
from arena_coach.orchestrator import pipeline
from arena_coach.shared.settings import Settings


def _legacy_db(tmp_path: Path) -> async_sessionmaker[AsyncSession]:
    """БД в состоянии «до миграции 0005»: колонки `combat_text` нет.

    Ровно то, что было в проде: таблица есть, строка игрока есть, колонки нет.
    """
    path = tmp_path / "coach.db"
    con = sqlite3.connect(path)
    con.execute(
        "CREATE TABLE player_settings ("
        " discord_id TEXT PRIMARY KEY,"
        " voice_mode TEXT NOT NULL,"
        " updated_at TEXT NOT NULL)"
    )
    con.execute(
        "INSERT INTO player_settings (discord_id, voice_mode, updated_at)"
        " VALUES ('111', 'on', '2026-07-30 00:00:00')"
    )
    con.commit()
    con.close()
    engine = create_async_engine(f"sqlite+aiosqlite:///{path}")
    return async_sessionmaker(engine, expire_on_commit=False)


class TestGettersDegrade:
    async def test_combat_text_falls_back_on_missing_column(self, tmp_path: Path) -> None:
        svc = PlayerSettingsService(_legacy_db(tmp_path))
        assert await svc.get_combat_text("111") == DEFAULT_COMBAT_TEXT

    async def test_voice_mode_falls_back_on_missing_column(self, tmp_path: Path) -> None:
        """Голос тоже читается тем же SELECT — значит падал вместе с боевым текстом."""
        svc = PlayerSettingsService(_legacy_db(tmp_path))
        assert await svc.get_voice_mode("111") == DEFAULT_VOICE_MODE

    async def test_missing_table_also_survives(self, tmp_path: Path) -> None:
        engine = create_async_engine(f"sqlite+aiosqlite:///{tmp_path / 'empty.db'}")
        svc = PlayerSettingsService(async_sessionmaker(engine, expire_on_commit=False))
        assert await svc.get_voice_mode("111") == DEFAULT_VOICE_MODE
        assert await svc.get_combat_text("111") == DEFAULT_COMBAT_TEXT


class TestSettersStayLoud:
    async def test_set_raises_when_schema_broken(self, tmp_path: Path) -> None:
        """Молча «сохранить» настройку нельзя — игрок ждёт подтверждения в Discord."""
        svc = PlayerSettingsService(_legacy_db(tmp_path))
        with pytest.raises(Exception):  # noqa: B017 — важен сам факт, не класс
            await svc.set_combat_text("111", "on")


class _FakeAccess:
    async def find_by_character(self, character: str) -> SimpleNamespace:
        return SimpleNamespace(discord_id="111")


def _env(event: dict[str, Any]) -> dict[str, Any]:
    return {
        "schema_version": 1,
        "bridge_ts": "2026-07-30T07:36:00Z",
        "session_id": "s1",
        "player_name": "Arenacoach",
        "event": event,
        "match": {
            "bracket": "2v2",
            "enemies": [
                {"wow_class": "MAGE", "race": "UNKNOWN"},
                {"wow_class": "WARRIOR", "race": "UNKNOWN"},
            ],
            "allies": [],
            "our_comp_hint": "rogue+mage",
            "player_class": "MAGE",
        },
    }


class TestIngestionSurvives:
    async def test_arena_start_still_processed_on_broken_settings_db(
        self, kb_dir: Path, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Тот самый ARENA_START, который в проде терялся после четырёх 500."""
        sent: list[str] = []

        async def _dm(bot_token: str, discord_id: str, content: str) -> bool:
            sent.append(content)
            return True

        monkeypatch.setattr(pipeline, "_send_discord_dm", _dm)

        index = KBIndex()
        index.load(kb_dir)
        ctx = pipeline.PipelineContext(
            access_service=_FakeAccess(),  # type: ignore[arg-type]
            kb_retriever=KBRetriever(index),
            anthropic_client=SimpleNamespace(),
            settings=Settings(discord_bot_token="t", anthropic_api_key=""),
            player_settings=PlayerSettingsService(_legacy_db(tmp_path)),
        )

        assert await pipeline.process_event(ctx, _env({"type": "ARENA_START"})) == "sent"
        await ctx.drain_bg()
        assert sent, "разбор на воротах должен доехать даже со сломанной схемой настроек"


class TestLogNotFlooded:
    async def test_warning_only_once(
        self, tmp_path: Path, caplog: pytest.LogCaptureFixture
    ) -> None:
        """Геттер зовётся на каждое событие — полный трейс в цикле убил бы лог."""
        svc = PlayerSettingsService(_legacy_db(tmp_path))
        with caplog.at_level("WARNING", logger="arena_coach.access.player_settings"):
            for _ in range(5):
                await svc.get_voice_mode("111")
                await svc.get_combat_text("111")
        warnings = [r for r in caplog.records if r.levelname == "WARNING"]
        assert len(warnings) == 1, [r.getMessage() for r in warnings]
        assert "миграция" in warnings[0].getMessage()
