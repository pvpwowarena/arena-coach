"""Phase 4.14 в пайплайне: состояние врага в бою + разрешение дублей классов.

Драйвер — аудит 30.07 («бот озвучивает то, что игрок и так видит») и фидбэк
«когда противник с двумя одинаковыми классами — непонятно, как действовать».

Проверяем сквозь `process_event` на РЕАЛЬНОМ каталоге `kb/glossary/realtime_spells.json`
(кулдауны там перенесены из sourced-слоя скриптом `tools/derive_cooldowns.py`) —
чтобы тест ловил и расхождение данных, а не только логику.
"""

from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace
from typing import Any

import pytest

from arena_coach.kb.indexer import KBIndex
from arena_coach.kb.retriever import KBRetriever
from arena_coach.orchestrator import pipeline
from arena_coach.orchestrator.enemy_state import EnemyTracker
from arena_coach.orchestrator.hint_queue import HintQueue
from arena_coach.shared.settings import Settings

DOUBLE_ROGUE = [
    {"wow_class": "ROGUE", "race": "UNKNOWN"},
    {"wow_class": "ROGUE", "race": "UNKNOWN"},
]
ROGUE_MAGE = [
    {"wow_class": "ROGUE", "race": "UNKNOWN"},
    {"wow_class": "MAGE", "race": "UNKNOWN"},
]


class _FakeAccess:
    async def find_by_character(self, character: str) -> SimpleNamespace:
        return SimpleNamespace(discord_id="111")


class _FakeSettingsSvc:
    """player_settings без БД: голос вкл, боевой текст задаётся тестом."""

    def __init__(self, combat_text: str = "on", voice_mode: str = "on") -> None:
        self._combat_text = combat_text
        self._voice_mode = voice_mode

    async def get_voice_mode(self, discord_id: str) -> str:
        return self._voice_mode

    async def get_combat_text(self, discord_id: str) -> str:
        return self._combat_text


class _SpyQueue(HintQueue):
    """Очередь, которая запоминает всё положенное — единственный канал голоса.

    С Phase 4.15 хопа api→bot (`_send_voice_hint`) больше нет: фразы забирает мост
    через `GET /v1/hints`, поэтому «что услышал игрок» = что легло в очередь.
    """

    def __init__(self, spoken: list[str]) -> None:
        super().__init__()
        self.spoken = spoken

    def push(self, player_name: str, phrase: str, ttl_s: float | None = None) -> None:
        self.spoken.append(phrase)
        super().push(player_name, phrase, ttl_s=ttl_s)


def _ctx(
    kb_dir: Path,
    clock: list[float],
    spoken: list[str] | None = None,
    combat_text: str = "on",
) -> pipeline.PipelineContext:
    index = KBIndex()
    index.load(kb_dir)
    return pipeline.PipelineContext(
        access_service=_FakeAccess(),  # type: ignore[arg-type]
        kb_retriever=KBRetriever(index),
        anthropic_client=SimpleNamespace(),
        settings=Settings(discord_bot_token="t", anthropic_api_key=""),
        # Троттлинг в тестах не должен глотать вторую подсказку: интервалы обнулены,
        # проверяем содержание, а бюджет речи покрыт в test_reactions.
        hint_throttle=pipeline.HintThrottle(gap_s=0.0, high_gap_s=0.0, default_repeat_s=0.0),
        enemy_tracker=EnemyTracker(clock=lambda: clock[0]),
        hint_queue=_SpyQueue(spoken if spoken is not None else []),
        # Боевой DM с 4.15 в opt-in; большинству тестов ниже нужен именно текст.
        player_settings=_FakeSettingsSvc(combat_text),  # type: ignore[arg-type]
    )


def _env(
    enemies: list[dict[str, str]],
    event: dict[str, Any],
    *,
    our: str = "rogue+mage",
    bracket: str = "2v2",
    session: str = "s1",
) -> dict[str, Any]:
    return {
        "schema_version": 1,
        "bridge_ts": "2026-07-30T12:00:00Z",
        "session_id": session,
        "player_name": "Arenacoach",
        "event": event,
        "match": {
            "bracket": bracket,
            "enemies": enemies,
            "allies": [],
            "our_comp_hint": our,
            "player_class": "ROGUE",
        },
    }


def _ability(source: str, spell_id: int, key: str, name: str) -> dict[str, Any]:
    return {
        "type": "ABILITY",
        "source_name": source,
        "spell_id": spell_id,
        "spell_key": key,
        "spell_name": name,
    }


def _trinket(source: str) -> dict[str, Any]:
    return {"type": "TRINKET", "source_name": source, "trinket_key": "pvp_trinket"}


@pytest.fixture
def sink(monkeypatch: pytest.MonkeyPatch) -> tuple[list[str], list[str]]:
    """(DM-тексты, озвученные фразы). Список фраз передаётся в `_ctx(..., spoken=)`."""
    dms: list[str] = []
    spoken: list[str] = []

    async def _dm(bot_token: str, discord_id: str, content: str) -> bool:
        dms.append(content)
        return True

    monkeypatch.setattr(pipeline, "_send_discord_dm", _dm)
    return dms, spoken


class TestCatalogCooldowns:
    def test_sourced_cooldowns_reached_the_catalog(self, kb_dir: Path) -> None:
        """Значения переносит tools/derive_cooldowns.py — тест ловит их пропажу."""
        from arena_coach.kb.spells import SpellCatalog

        catalog = SpellCatalog.from_kb_path(kb_dir)
        assert catalog.resolve(spell_key="vanish").cooldown_s == 180.0
        assert catalog.resolve(spell_key="ice_block").cooldown_s == 300.0
        # В abilities.json кулдауна нет → 0.0, и бот говорит без секунд.
        assert catalog.resolve(spell_key="divine_shield").cooldown_s == 0.0


class TestDuplicateClasses:
    async def test_trinket_voice_names_the_rogue_when_two(
        self, kb_dir: Path, sink: tuple[list[str], list[str]]
    ) -> None:
        _, spoken = sink
        clock = [0.0]
        ctx = _ctx(kb_dir, clock, sink[1])
        await pipeline.process_event(ctx, _env(DOUBLE_ROGUE, {"type": "ARENA_START"}))
        # Оба рога раскрылись кастами — только так бэкенд узнаёт ники.
        await pipeline.process_event(
            ctx, _env(DOUBLE_ROGUE, _ability("Cekraj", 1856, "vanish", "Vanish"))
        )
        clock[0] += 5.0
        await pipeline.process_event(
            ctx, _env(DOUBLE_ROGUE, _ability("Shadow", 6770, "sap", "Sap"))
        )
        clock[0] += 5.0
        spoken.clear()

        await pipeline.process_event(ctx, _env(DOUBLE_ROGUE, _trinket("Shadow")))
        assert spoken, "тринкет должен озвучиваться"
        assert "Шадов" in spoken[-1] or "Шэдов" in spoken[-1], spoken[-1]

    async def test_trinket_voice_stays_nameless_without_duplicates(
        self, kb_dir: Path, sink: tuple[list[str], list[str]]
    ) -> None:
        """Ник в голосе — только когда он решает: иначе он лишь удлиняет фразу."""
        _, spoken = sink
        clock = [0.0]
        ctx = _ctx(kb_dir, clock, sink[1])
        await pipeline.process_event(ctx, _env(ROGUE_MAGE, {"type": "ARENA_START"}))
        await pipeline.process_event(
            ctx, _env(ROGUE_MAGE, _ability("Cekraj", 1856, "vanish", "Vanish"))
        )
        clock[0] += 5.0
        spoken.clear()

        await pipeline.process_event(ctx, _env(ROGUE_MAGE, _trinket("Cekraj")))
        # Ваниш + тринкет открыли окно — про него бот говорит первым (это ценнее),
        # а реплика на сам тринкет остаётся безымянной таблично.
        assert spoken[-1] == "Тринкета нет — вешай контроль."

    async def test_trinket_resolves_the_duplicate_immediately(
        self, kb_dir: Path, sink: tuple[list[str], list[str]]
    ) -> None:
        """Первый тринкет — самый ранний момент, когда дубль вообще разрешим."""
        dms, _ = sink
        clock = [0.0]
        ctx = _ctx(kb_dir, clock, sink[1])
        await pipeline.process_event(ctx, _env(DOUBLE_ROGUE, {"type": "ARENA_START"}))
        await pipeline.process_event(
            ctx, _env(DOUBLE_ROGUE, _ability("Cekraj", 1856, "vanish", "Vanish"))
        )
        clock[0] += 5.0
        await pipeline.process_event(
            ctx, _env(DOUBLE_ROGUE, _ability("Shadow", 6770, "sap", "Sap"))
        )
        clock[0] += 5.0
        dms.clear()

        await pipeline.process_event(ctx, _env(DOUBLE_ROGUE, _trinket("Shadow")))
        joined = "\n".join(dms)
        assert "Дубль класса" in joined
        assert "**Shadow**" in joined

    async def test_reemit_arena_start_reannounces_resolved_target(
        self, kb_dir: Path, sink: tuple[list[str], list[str]]
    ) -> None:
        """Дедуп ARENA_START по слагу не должен глотать уточнение цели."""
        dms, spoken = sink
        clock = [0.0]
        ctx = _ctx(kb_dir, clock, sink[1])
        await pipeline.process_event(ctx, _env(DOUBLE_ROGUE, {"type": "ARENA_START"}))
        await pipeline.process_event(
            ctx, _env(DOUBLE_ROGUE, _ability("Cekraj", 1856, "vanish", "Vanish"))
        )
        clock[0] += 5.0
        await pipeline.process_event(
            ctx, _env(DOUBLE_ROGUE, _ability("Shadow", 6770, "sap", "Sap"))
        )
        clock[0] += 5.0
        await pipeline.process_event(ctx, _env(DOUBLE_ROGUE, _trinket("Shadow")))
        clock[0] += 5.0
        dms.clear()
        spoken.clear()

        # Повторный ARENA_START — мост шлёт его при доуточнении состава.
        await pipeline.process_event(ctx, _env(DOUBLE_ROGUE, {"type": "ARENA_START"}, session="s1"))
        joined = "\n".join(dms)
        assert "Дубль рога" in joined, joined
        assert "**Shadow**" in joined
        assert any("Шадов" in s or "Шэдов" in s for s in spoken), spoken


class TestOpenWindowInFight:
    async def test_window_hint_after_trinket_and_defensive(
        self, kb_dir: Path, sink: tuple[list[str], list[str]]
    ) -> None:
        """То, чего игрок видеть не может: у врага не осталось ни тринкета, ни дефа."""
        dms, _ = sink
        clock = [0.0]
        ctx = _ctx(kb_dir, clock, sink[1])
        await pipeline.process_event(ctx, _env(ROGUE_MAGE, {"type": "ARENA_START"}))
        await pipeline.process_event(ctx, _env(ROGUE_MAGE, _trinket("Frosty")))
        clock[0] += 5.0
        dms.clear()

        # Ice Block — категория immunity в каталоге, кулдаун 300с из abilities.json.
        await pipeline.process_event(
            ctx, _env(ROGUE_MAGE, _ability("Frosty", 45438, "ice_block", "Ice Block"))
        )
        joined = "\n".join(dms)
        assert "Окно на Frosty" in joined
        assert "дожимайте" in joined.lower() or "вкладывайте" in joined.lower()

    async def test_window_announced_once(
        self, kb_dir: Path, sink: tuple[list[str], list[str]]
    ) -> None:
        dms, _ = sink
        clock = [0.0]
        ctx = _ctx(kb_dir, clock, sink[1])
        await pipeline.process_event(ctx, _env(ROGUE_MAGE, {"type": "ARENA_START"}))
        await pipeline.process_event(ctx, _env(ROGUE_MAGE, _trinket("Frosty")))
        clock[0] += 5.0
        await pipeline.process_event(
            ctx, _env(ROGUE_MAGE, _ability("Frosty", 45438, "ice_block", "Ice Block"))
        )
        clock[0] += 5.0
        dms.clear()
        await pipeline.process_event(
            ctx, _env(ROGUE_MAGE, _ability("Frosty", 12472, "icy_veins", "Icy Veins"))
        )
        assert "Окно на Frosty" not in "\n".join(dms)

    async def test_cooldown_return_announced(
        self, kb_dir: Path, sink: tuple[list[str], list[str]]
    ) -> None:
        dms, _ = sink
        clock = [0.0]
        ctx = _ctx(kb_dir, clock, sink[1])
        await pipeline.process_event(ctx, _env(ROGUE_MAGE, {"type": "ARENA_START"}))
        await pipeline.process_event(
            ctx, _env(ROGUE_MAGE, _ability("Cekraj", 1856, "vanish", "Vanish"))
        )
        clock[0] += 181.0
        dms.clear()

        await pipeline.process_event(ctx, _env(ROGUE_MAGE, _ability("Cekraj", 6770, "sap", "Sap")))
        assert "откатился" in "\n".join(dms)

    async def test_throttled_event_still_updates_the_ledger(
        self, kb_dir: Path, sink: tuple[list[str], list[str]]
    ) -> None:
        """Подавленная реплика не должна стирать знание: иначе бот «забудет» тринкет."""
        clock = [0.0]
        ctx = _ctx(kb_dir, clock, sink[1])
        # Жёсткий троттлинг: реплики не пройдут, учёт обязан идти всё равно.
        ctx.hint_throttle = pipeline.HintThrottle(gap_s=999.0, high_gap_s=999.0)
        await pipeline.process_event(ctx, _env(ROGUE_MAGE, {"type": "ARENA_START"}))
        await pipeline.process_event(ctx, _env(ROGUE_MAGE, _trinket("Frosty")))
        await pipeline.process_event(
            ctx, _env(ROGUE_MAGE, _ability("Frosty", 45438, "ice_block", "Ice Block"))
        )
        assert ctx.enemy_tracker.without_trinket("Arenacoach") == ["Frosty"]
        assert ctx.enemy_tracker.remaining_s("Arenacoach", "Frosty", "ice_block") == 300.0

    async def test_arena_end_clears_state(
        self, kb_dir: Path, sink: tuple[list[str], list[str]]
    ) -> None:
        clock = [0.0]
        ctx = _ctx(kb_dir, clock, sink[1])
        await pipeline.process_event(ctx, _env(ROGUE_MAGE, {"type": "ARENA_START"}))
        await pipeline.process_event(ctx, _env(ROGUE_MAGE, _trinket("Frosty")))
        await pipeline.process_event(ctx, _env(ROGUE_MAGE, {"type": "ARENA_END"}))
        assert ctx.enemy_tracker.known("Arenacoach") == []


class TestVoiceTranslit:
    async def test_latin_never_reaches_tts(
        self, kb_dir: Path, sink: tuple[list[str], list[str]]
    ) -> None:
        """Ник в голосе обязан быть кириллицей — иначе RU-синтезатор читает кашу."""
        _, spoken = sink
        clock = [0.0]
        ctx = _ctx(kb_dir, clock, sink[1])
        await pipeline.process_event(ctx, _env(DOUBLE_ROGUE, {"type": "ARENA_START"}))
        await pipeline.process_event(
            ctx, _env(DOUBLE_ROGUE, _ability("Cekraj", 1856, "vanish", "Vanish"))
        )
        clock[0] += 5.0
        await pipeline.process_event(
            ctx, _env(DOUBLE_ROGUE, _ability("Shadow", 6770, "sap", "Sap"))
        )
        assert spoken
        for phrase in spoken:
            assert not any("a" <= ch.lower() <= "z" for ch in phrase), phrase
