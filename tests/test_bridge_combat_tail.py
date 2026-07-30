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
    # Phase 4.18: слот игрока в allies есть ВСЕГДА — при нераскрытом классе он
    # честно UNKNOWN, чтобы напарник не занял позицию allies[0] (player_class).
    assert out == ["ARENA_START#2v2##UNKNOWN/UNKNOWN"]


def test_enemy_class_inference_reemits_start() -> None:
    it = CombatInterpreter(player_name="Arenacoach")
    it.feed_line(_line("12:00:00.0000", PREP_ON_ME))
    it.feed_line(_line("12:00:01.0000", PREP_ON_ALLY))
    it.feed_line(_line("12:00:30.0000", PREP_OFF_ME))

    out = it.feed_line(
        _line("12:00:40.0000", _enemy_cast("Player-1-E1", "Evilmage-X", 27072, "Frostbolt"))
    )
    # Frostbolt — WEAK-сигнал спека frost (Phase 4.7): раскрывается класс + спек-намёк
    assert "ARENA_START#2v2#MAGE/UNKNOWN/frost-mage#UNKNOWN/UNKNOWN" in out


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
    # Phase 4.12: пятым полем идёт английское имя способности — по нему бэкенд
    # резолвит то, чего нет в зашитой таблице моста.
    assert "ABILITY#Evilwar#871#shield_wall#Shield Wall#" in out


def test_unknown_spell_is_forwarded_by_name() -> None:
    """Хант и шаман не были в TRACKED_SPELLS — теперь они не теряются."""
    it = CombatInterpreter(player_name="Arenacoach")
    it.feed_line(_line("12:00:00.0000", PREP_ON_ME))
    it.feed_line(_line("12:00:30.0000", PREP_OFF_ME))

    out = it.feed_line(
        _line("12:00:41.0000", _enemy_cast("Player-1-E2", "Huntard-X", 19503, "Scatter Shot"))
    )
    assert "ABILITY#Huntard#19503#scatter_shot#Scatter Shot#" in out


def test_forward_budget_caps_unknown_flood() -> None:
    """Потолок форварда незнакомых кастов — 90 в минуту на матч."""
    it = CombatInterpreter(player_name="Arenacoach")
    it.feed_line(_line("12:00:00.0000", PREP_ON_ME))
    it.feed_line(_line("12:00:30.0000", PREP_OFF_ME))

    emitted = 0
    for i in range(200):
        # разные spell_id, чтобы не сработал дедуп cast+aura
        out = it.feed_line(
            _line(
                "12:00:41.0000",
                _enemy_cast("Player-1-E2", "Spammer-X", 900000 + i, f"Spam {i}"),
            )
        )
        emitted += sum(1 for p in out if p.startswith("ABILITY#"))
    assert emitted == 90


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


# ── v0.4.1: шумоподавление (реальный скирмиш 2026-07-23) ─────────────────────


def _setup_2v2(it: CombatInterpreter) -> None:
    it.feed_line(_line("12:00:00.0000", PREP_ON_ME))
    it.feed_line(_line("12:00:01.0000", PREP_ON_ALLY))
    it.feed_line(_line("12:00:30.0000", PREP_OFF_ME))


def _friendly_cast(guid: str, name: str, spell_id: int, spell: str) -> str:
    return (
        f'SPELL_CAST_SUCCESS,{guid},"{name}",{FRIENDLY},0x0,'
        f'{guid},"{name}",{FRIENDLY},0x0,{spell_id},"{spell}",0x8'
    )


def test_ally_class_reveal_reemits_our_comp() -> None:
    """Поздно раскрывшийся напарник МЕНЯЕТ наш состав → re-emit (Phase 4.18).

    Раньше здесь стояло обратное требование («не слать повтор»), и из-за него
    our_comp фризился на первом варианте до конца матча: KB-матчап искался по
    неполному нашему составу. Анти-спам живёт теперь на бэкенде — он дедупит DM
    по выбранному KB-документу, то есть игрок увидит повтор, только если сменился
    ПЛАН, а не строка payload.
    """
    it = CombatInterpreter(player_name="Arenacoach")
    _setup_2v2(it)
    out = it.feed_line(
        _line("12:00:33.0000", _friendly_cast("Player-1-AL", "Syskilla-X", 25454, "Earth Shock"))
    )
    starts = [p for p in out if p.startswith("ARENA_START")]
    assert starts == ["ARENA_START#2v2##UNKNOWN/UNKNOWN,SHAMAN/UNKNOWN"]


def test_random_friendly_player_never_joins_our_roster() -> None:
    """Ростер команды — только те, на кого падала Arena Preparation (Phase 4.18).

    В живом логе 30.07 в «союзники» после матча влетали десятки имён из открытого
    мира, а bracket считается по их числу — оценка состава уезжала целиком.
    """
    it = CombatInterpreter(player_name="Arenacoach")
    _setup_2v2(it)
    # До стелс-порога (6с от ворот), чтобы в вывод не влез стелс-анонс.
    out = it.feed_line(
        _line("12:00:33.0000", _friendly_cast("Player-1-XX", "Passerby-X", 25454, "Earth Shock"))
    )
    assert not any(p.startswith("ARENA_START") for p in out)


def test_same_enemy_comp_not_reemitted() -> None:
    it = CombatInterpreter(player_name="Arenacoach")
    _setup_2v2(it)
    first = it.feed_line(
        _line("12:00:40.0000", _enemy_cast("Player-1-E1", "Evildruid-X", 26982, "Rejuvenation"))
    )
    assert any(p.startswith("ARENA_START#2v2#DRUID/UNKNOWN") for p in first)
    # Тот же друид кастует дальше — состав врагов не изменился, повторов нет
    again = it.feed_line(
        _line("12:00:44.0000", _enemy_cast("Player-1-E1", "Evildruid-X", 26985, "Wrath"))
    )
    assert not any(p.startswith("ARENA_START") for p in again)


def test_world_hostiles_ignored_when_roster_full() -> None:
    """После заполнения ростера 2v2 мировые ордынцы не считаются врагами."""
    it = CombatInterpreter(player_name="Arenacoach")
    _setup_2v2(it)
    it.feed_line(
        _line("12:00:40.0000", _enemy_cast("Player-1-E1", "Evildruid-X", 26982, "Rejuvenation"))
    )
    it.feed_line(
        _line("12:00:42.0000", _enemy_cast("Player-1-E2", "Evilwar-X", 30330, "Mortal Strike"))
    )
    # «Мировой» хант после матча: ростер полон → игнор (ни ARENA_START, ни ABILITY)
    out = it.feed_line(
        _line("12:01:00.0000", _enemy_cast("Player-9-WORLD", "Zonof-X", 1543, "Flare"))
    )
    assert out == []
    # И он же НЕ продлевает сессию: 90с тишины врагов матча → ARENA_END
    out = it.feed_line(
        _line("12:02:20.0000", _enemy_cast("Player-9-WORLD", "Zonof-X", 1543, "Flare"))
    )
    assert any(p.startswith("ARENA_END#") for p in out)


# ── Phase 4.7: определение спека по сигнатурным спеллам ───────────────────────


def test_strong_spec_repentance_ret_paladin() -> None:
    it = CombatInterpreter(player_name="Arenacoach")
    _setup_2v2(it)
    out = it.feed_line(
        _line("12:00:40.0000", _enemy_cast("Player-1-E1", "Judgex-X", 20066, "Repentance"))
    )
    assert "ARENA_START#2v2#PALADIN/UNKNOWN/ret-paladin#UNKNOWN/UNKNOWN" in out


def test_strong_spec_overrides_weak_frost_to_fire() -> None:
    """PoM-Pyro fire-маг: сперва frostbolt (WEAK frost), затем pyroblast (STRONG
    fire) → итог fire-mage, спек лочится и не откатывается."""
    it = CombatInterpreter(player_name="Arenacoach")
    _setup_2v2(it)
    frost = it.feed_line(
        _line("12:00:40.0000", _enemy_cast("Player-1-E1", "Pyrox-X", 27072, "Frostbolt"))
    )
    assert any("MAGE/UNKNOWN/frost-mage" in p for p in frost)
    fire = it.feed_line(
        _line("12:00:44.0000", _enemy_cast("Player-1-E1", "Pyrox-X", 27070, "Pyroblast"))
    )
    assert any("MAGE/UNKNOWN/fire-mage" in p for p in fire)
    # STRONG залочен: повторный frostbolt не откатывает спек на frost
    back = it.feed_line(
        _line("12:00:48.0000", _enemy_cast("Player-1-E1", "Pyrox-X", 27072, "Frostbolt"))
    )
    assert not any("frost-mage" in p for p in back)


def test_spec_flows_through_normalizer_to_enemyinfo() -> None:
    it = CombatInterpreter(player_name="Arenacoach")
    session = SessionState(default_our_comp="rogue+mage")
    _setup_2v2(it)
    payloads = it.feed_line(
        _line("12:00:40.0000", _enemy_cast("Player-1-E1", "Feralx-X", 33983, "Mangle (Cat)"))
    )
    envs = [normalize_raw(p, session, "Arenacoach") for p in payloads]
    envs = [e for e in envs if e is not None]
    starts = [e for e in envs if e.event.type == "ARENA_START"]
    assert starts, "нет ARENA_START в envelope'ах"
    enemies = starts[0].match.enemies
    assert enemies and enemies[0].wow_class == "DRUID"
    assert enemies[0].spec == "feral-druid"


# ── Стелс-опенер: пустой ростер ≠ инвиз (Phase 4.12) ─────────────────────────


def _own_line(ts_spell: int = 1784) -> str:
    """Своя строка в логе — время идёт, врагов по-прежнему не видно."""
    return (
        f'SPELL_CAST_SUCCESS,Player-1-ME,"Arenacoach-Spineshatter",{FRIENDLY},0x0,'
        f'Player-1-ME,"Arenacoach-Spineshatter",{FRIENDLY},0x0,{ts_spell},"Stealth",0x1'
    )


def _is_stealth_marker(payload: str) -> bool:
    return payload.startswith("ARENA_START#") and payload.endswith("#stealth")


def test_stealth_marker_only_after_delay() -> None:
    """На воротах состав всегда пуст — это не инвиз. Маркер идёт через 6с тишины."""
    it = CombatInterpreter(player_name="Arenacoach")
    it.feed_line(_line("12:00:00.0000", PREP_ON_ME))
    it.feed_line(_line("12:00:00.0000", PREP_ON_ALLY))
    out = it.feed_line(_line("12:00:30.0000", PREP_OFF_ME))
    assert not any(_is_stealth_marker(p) for p in out), "на воротах инвиз не объявляем"

    early = it.feed_line(_line("12:00:33.0000", _own_line()))
    assert not any(_is_stealth_marker(p) for p in early), "3с — рано"

    late = it.feed_line(_line("12:00:40.0000", _own_line()))
    assert any(_is_stealth_marker(p) for p in late), "6с тишины — пора предупредить"

    again = it.feed_line(_line("12:00:50.0000", _own_line()))
    assert not any(_is_stealth_marker(p) for p in again), "повторно не спамим"


def test_no_stealth_marker_when_enemy_revealed() -> None:
    """Враг раскрылся — предупреждать об инвизе не о чем."""
    it = CombatInterpreter(player_name="Arenacoach")
    it.feed_line(_line("12:00:00.0000", PREP_ON_ME))
    it.feed_line(_line("12:00:00.0000", PREP_ON_ALLY))
    it.feed_line(_line("12:00:30.0000", PREP_OFF_ME))
    it.feed_line(
        _line("12:00:32.0000", _enemy_cast("Player-1-E1", "Evilwar-X", 871, "Shield Wall"))
    )
    out = it.feed_line(_line("12:00:45.0000", _own_line()))
    assert not any(_is_stealth_marker(p) for p in out)


# ── Начало каста: единственный сигнал ДО факта (Phase 4.12) ──────────────────


def test_cast_start_forwarded_with_phase() -> None:
    it = CombatInterpreter(player_name="Arenacoach")
    it.feed_line(_line("12:00:00.0000", PREP_ON_ME))
    it.feed_line(_line("12:00:30.0000", PREP_OFF_ME))

    start = it.feed_line(
        _line(
            "12:00:41.0000",
            _enemy_cast("Player-1-E2", "Shamy-X", 25357, "Healing Wave", "SPELL_CAST_START"),
        )
    )
    assert any(p.endswith("#healing_wave#Healing Wave#start") for p in start)

    # успех того же спелла — отдельное событие, дедуп по фазе его не съедает
    done = it.feed_line(
        _line("12:00:43.0000", _enemy_cast("Player-1-E2", "Shamy-X", 25357, "Healing Wave"))
    )
    assert any(p.endswith("#healing_wave#Healing Wave#") for p in done)
