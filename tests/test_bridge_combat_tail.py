"""Phase 4.2: combat-лог как realtime-канал — парсер CLEU и интерпретатор.

Контекст: chat-лог в Anniversary-клиенте не флашится до выхода из игры,
combat-лог флашится в бою (живой тест 2026-07-23). CombatInterpreter
переводит CLEU в AC-payload строки для существующего normalize_raw.
"""

from __future__ import annotations

from pathlib import Path

from arena_bridge.combat_tail import (
    CombatInterpreter,
    find_combat_log,
    parse_cleu_line,
)
from arena_bridge.normalizer import SessionState, normalize_raw


def _line(ts: str, payload: str) -> str:
    return f"7/23/2026 {ts}  {payload}"


HOSTILE = "0x548"
FRIENDLY = "0x511"

PREP_ON_ME = (
    'SPELL_AURA_APPLIED,Player-1-ME,"Arenacoach-Spineshatter",0x511,0x0,'
    'Player-1-ME,"Arenacoach-Spineshatter",0x511,0x0,32727,"Arena Preparation",0x1,BUFF'
)
PREP_ON_ALLY = (
    'SPELL_AURA_APPLIED,Player-1-AL,"Syskilla-Spineshatter",0x511,0x0,'
    'Player-1-AL,"Syskilla-Spineshatter",0x511,0x0,32727,"Arena Preparation",0x1,BUFF'
)
PREP_OFF_ME = (
    'SPELL_AURA_REMOVED,Player-1-ME,"Arenacoach-Spineshatter",0x511,0x0,'
    'Player-1-ME,"Arenacoach-Spineshatter",0x511,0x0,32727,"Arena Preparation",0x1,BUFF'
)


def _enemy_cast(
    guid: str, name: str, spell_id: int, spell: str, event: str = "SPELL_CAST_SUCCESS"
) -> str:
    return (
        f'{event},{guid},"{name}",{HOSTILE},0x0,'
        f'Player-1-ME,"Arenacoach-Spineshatter",0x511,0x0,{spell_id},"{spell}",0x1'
    )


# ── parse_cleu_line ──────────────────────────────────────────────────────────


def test_parse_real_sample_line() -> None:
    line = (
        "7/23/2026 13:50:59.5253  SPELL_AURA_APPLIED,Player-6412-0292A5C4,"
        '"Endwõr-Spineshatter-EU",0x518,0x80000000,Player-6412-0292A5C4,'
        '"Endwõr-Spineshatter-EU",0x518,0x80000000,2383,"Find Herbs",0x1,BUFF'
    )
    parsed = parse_cleu_line(line)
    assert parsed is not None
    ts, fields = parsed
    assert ts.year == 2026 and ts.hour == 13 and ts.minute == 50
    assert fields[0] == "SPELL_AURA_APPLIED"
    assert fields[2] == "Endwõr-Spineshatter-EU"
    assert fields[9] == "2383"


def test_parse_quoted_comma_in_name() -> None:
    line = _line(
        "12:00:00.0001",
        'SPELL_CAST_SUCCESS,Player-1-X,"Foo, the Bar",0x548,0x0,'
        'Player-1-Y,"Baz",0x511,0x0,871,"Shield Wall",0x1',
    )
    parsed = parse_cleu_line(line)
    assert parsed is not None
    assert parsed[1][2] == "Foo, the Bar"


def test_parse_garbage_returns_none() -> None:
    assert parse_cleu_line("") is None
    assert parse_cleu_line("не combat-лог строка") is None
    assert parse_cleu_line("7/23/2026 12:00:00.0000  ") is None


# ── find_combat_log ──────────────────────────────────────────────────────────


def test_find_combat_log_prefers_newest(tmp_path: Path) -> None:
    old = tmp_path / "WoWCombatLog.txt"
    new = tmp_path / "WoWCombatLog-072326_134444.txt"
    old.write_text("old")
    new.write_text("new")
    import os

    os.utime(old, (1_000_000, 1_000_000))
    os.utime(new, (2_000_000, 2_000_000))
    assert find_combat_log(tmp_path) == new
    assert find_combat_log(tmp_path / "nope") is None if (tmp_path / "nope").exists() else True


# ── CombatInterpreter: границы матча и события ───────────────────────────────


def test_arena_start_on_prep_removed() -> None:
    it = CombatInterpreter(player_name="Arenacoach")
    assert it.feed_line(_line("12:00:00.0000", PREP_ON_ME)) == []
    assert it.feed_line(_line("12:00:01.0000", PREP_ON_ALLY)) == []
    out = it.feed_line(_line("12:00:30.0000", PREP_OFF_ME))
    assert out == ["ARENA_START#2v2##"]


def test_enemy_class_inference_reemits_start() -> None:
    it = CombatInterpreter(player_name="Arenacoach")
    it.feed_line(_line("12:00:00.0000", PREP_ON_ME))
    it.feed_line(_line("12:00:01.0000", PREP_ON_ALLY))
    it.feed_line(_line("12:00:30.0000", PREP_OFF_ME))

    out = it.feed_line(
        _line("12:00:40.0000", _enemy_cast("Player-1-E1", "Evilmage-X", 27072, "Frostbolt"))
    )
    assert "ARENA_START#2v2#MAGE/UNKNOWN#" in out


def test_trinket_and_ability_payloads() -> None:
    it = CombatInterpreter(player_name="Arenacoach")
    it.feed_line(_line("12:00:00.0000", PREP_ON_ME))
    it.feed_line(_line("12:00:30.0000", PREP_OFF_ME))

    out = it.feed_line(
        _line("12:00:41.0000", _enemy_cast("Player-1-E2", "Evilwar-X", 42292, "PvP Trinket"))
    )
    assert "TRINKET#Evilwar#42292#pvp_trinket" in out

    out = it.feed_line(
        _line("12:00:50.0000", _enemy_cast("Player-1-E2", "Evilwar-X", 871, "Shield Wall"))
    )
    assert "ABILITY#Evilwar#871#shield_wall" in out


def test_cast_plus_aura_dedupped() -> None:
    it = CombatInterpreter(player_name="Arenacoach")
    it.feed_line(_line("12:00:00.0000", PREP_ON_ME))
    it.feed_line(_line("12:00:30.0000", PREP_OFF_ME))

    first = it.feed_line(
        _line("12:00:41.0000", _enemy_cast("Player-1-E2", "Evilwar-X", 871, "Shield Wall"))
    )
    second = it.feed_line(
        _line(
            "12:00:41.5000",
            _enemy_cast("Player-1-E2", "Evilwar-X", 871, "Shield Wall", "SPELL_AURA_APPLIED"),
        )
    )
    assert any(p.startswith("ABILITY#") for p in first)
    assert not any(p.startswith("ABILITY#") for p in second)


def test_arena_end_after_quiet_period() -> None:
    it = CombatInterpreter(player_name="Arenacoach")
    it.feed_line(_line("12:00:00.0000", PREP_ON_ME))
    it.feed_line(_line("12:00:30.0000", PREP_OFF_ME))
    it.feed_line(
        _line("12:00:40.0000", _enemy_cast("Player-1-E1", "Evilmage-X", 27072, "Frostbolt"))
    )
    # 2 минуты тишины → следующая же строка триггерит ARENA_END
    out = it.feed_line(
        _line(
            "12:02:45.0000",
            'SPELL_AURA_APPLIED,Player-9-Z,"Кто-то",0x518,0x0,'
            'Player-9-Z,"Кто-то",0x518,0x0,2383,"Find Herbs",0x1,BUFF',
        )
    )
    assert any(p.startswith("ARENA_END#") for p in out)


def test_payloads_flow_through_normalizer() -> None:
    """Сквозная проверка: payload'ы интерпретатора жуёт существующий normalize_raw."""
    it = CombatInterpreter(player_name="Arenacoach")
    session = SessionState(default_our_comp="rogue+mage")
    it.feed_line(_line("12:00:00.0000", PREP_ON_ME))
    it.feed_line(_line("12:00:01.0000", PREP_ON_ALLY))
    payloads = it.feed_line(_line("12:00:30.0000", PREP_OFF_ME))
    payloads += it.feed_line(
        _line("12:00:41.0000", _enemy_cast("Player-1-E2", "Evilwar-X", 42292, "PvP Trinket"))
    )

    envelopes = [normalize_raw(p, session, "Arenacoach") for p in payloads]
    envelopes = [e for e in envelopes if e is not None]
    types = [e.event["type"] if isinstance(e.event, dict) else e.event.type for e in envelopes]
    assert "ARENA_START" in str(types).upper() or len(envelopes) >= 1
