"""Тесты для arena_bridge.normalizer — парсинг AC-строк и сборка envelope."""

from __future__ import annotations

from arena_bridge.normalizer import (
    AbilityEvent,
    ArenaEndEvent,
    ArenaStartEvent,
    CanonicalEnvelope,
    EnemyInfo,
    SessionState,
    TrinketEvent,
    _build_slug_hint,
    normalize_raw,
    parse_event,
)

# ── EnemyInfo ────────────────────────────────────────────────────────────────


class TestEnemyInfo:
    def test_from_str_basic(self) -> None:
        e = EnemyInfo.from_str("ROGUE/HUMAN")
        assert e.wow_class == "ROGUE"
        assert e.race == "HUMAN"

    def test_from_str_case_insensitive(self) -> None:
        e = EnemyInfo.from_str("mage/gnome")
        assert e.wow_class == "MAGE"
        assert e.race == "GNOME"

    def test_from_str_no_race(self) -> None:
        e = EnemyInfo.from_str("WARRIOR")
        assert e.wow_class == "WARRIOR"
        assert e.race == "UNKNOWN"


# ── parse_event ───────────────────────────────────────────────────────────────


class TestParseEvent:
    def test_arena_start(self) -> None:
        ev = parse_event("ARENA_START|2v2|ROGUE/HUMAN,MAGE/GNOME")
        assert isinstance(ev, ArenaStartEvent)
        assert ev.bracket == "2v2"
        assert len(ev.enemies) == 2
        assert ev.enemies[0].wow_class == "ROGUE"
        assert ev.enemies[1].wow_class == "MAGE"

    def test_arena_start_3v3(self) -> None:
        ev = parse_event("ARENA_START|3v3|ROGUE/HUMAN,MAGE/GNOME,PRIEST/UNDEAD")
        assert isinstance(ev, ArenaStartEvent)
        assert ev.bracket == "3v3"
        assert len(ev.enemies) == 3

    def test_arena_start_empty_enemies(self) -> None:
        ev = parse_event("ARENA_START|2v2|")
        assert isinstance(ev, ArenaStartEvent)
        assert ev.enemies == []

    def test_trinket(self) -> None:
        ev = parse_event("TRINKET|EnemyPlayer|42292|pvp_trinket")
        assert isinstance(ev, TrinketEvent)
        assert ev.source_name == "EnemyPlayer"
        assert ev.spell_id == 42292
        assert ev.trinket_key == "pvp_trinket"

    def test_ability(self) -> None:
        ev = parse_event("ABILITY|EnemyMage|45438|ice_block")
        assert isinstance(ev, AbilityEvent)
        assert ev.source_name == "EnemyMage"
        assert ev.spell_id == 45438
        assert ev.spell_key == "ice_block"

    def test_arena_end(self) -> None:
        ev = parse_event("ARENA_END|42")
        assert isinstance(ev, ArenaEndEvent)
        assert ev.event_count == 42

    def test_arena_end_zero(self) -> None:
        ev = parse_event("ARENA_END|0")
        assert isinstance(ev, ArenaEndEvent)
        assert ev.event_count == 0

    def test_unknown_type_returns_none(self) -> None:
        assert parse_event("FOOBAR|data") is None

    def test_empty_string_returns_none(self) -> None:
        assert parse_event("") is None

    def test_bad_spell_id_returns_none(self) -> None:
        # spell_id не число → ValueError → None
        result = parse_event("TRINKET|Name|NOTANUMBER|pvp_trinket")
        assert result is None


# ── _build_slug_hint ─────────────────────────────────────────────────────────


class TestBuildSlugHint:
    def test_sorted_classes(self) -> None:
        enemies = [
            EnemyInfo(wow_class="ROGUE", race="HUMAN"),
            EnemyInfo(wow_class="MAGE", race="GNOME"),
        ]
        slug = _build_slug_hint(enemies)
        assert slug == "mage-rogue"  # отсортированы

    def test_single_enemy(self) -> None:
        enemies = [EnemyInfo(wow_class="WARRIOR", race="ORC")]
        slug = _build_slug_hint(enemies)
        assert slug == "warrior"

    def test_empty(self) -> None:
        assert _build_slug_hint([]) is None


# ── SessionState ─────────────────────────────────────────────────────────────


class TestSessionState:
    def test_start_and_end(self) -> None:
        state = SessionState()
        ev = ArenaStartEvent(
            bracket="2v2",
            enemies=[EnemyInfo(wow_class="ROGUE", race="HUMAN")],
        )
        state.start_session(ev)
        assert state.match.bracket == "2v2"
        assert state.match.matchup_slug_hint == "rogue"
        assert state.session_id != ""

        state.end_session()
        assert state.match.bracket == "unknown"

    def test_session_id_changes_on_restart(self) -> None:
        state = SessionState()
        ev = ArenaStartEvent(bracket="2v2", enemies=[])
        state.start_session(ev)
        first_id = state.session_id
        state.end_session()
        state.start_session(ev)
        assert state.session_id != first_id


# ── normalize_raw ─────────────────────────────────────────────────────────────


class TestNormalizeRaw:
    def test_full_pipeline_trinket(self) -> None:
        state = SessionState()
        # Сначала стартуем сессию
        normalize_raw("ARENA_START|2v2|ROGUE/HUMAN,MAGE/GNOME", state, "Vladislav")

        envelope = normalize_raw("TRINKET|Rogueboy|42292|pvp_trinket", state, "Vladislav")
        assert isinstance(envelope, CanonicalEnvelope)
        assert envelope.player_name == "Vladislav"
        assert isinstance(envelope.event, TrinketEvent)
        assert envelope.match.bracket == "2v2"
        assert envelope.match.matchup_slug_hint == "mage-rogue"

    def test_returns_none_on_bad_input(self) -> None:
        state = SessionState()
        assert normalize_raw("UNKNOWN|data", state, "Player") is None

    def test_arena_end_resets_state(self) -> None:
        state = SessionState()
        normalize_raw("ARENA_START|2v2|ROGUE/HUMAN", state, "Player")
        normalize_raw("ARENA_END|10", state, "Player")
        assert state.match.bracket == "unknown"

    def test_bridge_ts_present(self) -> None:
        state = SessionState()
        envelope = normalize_raw("ARENA_START|2v2|MAGE/GNOME", state, "Player")
        assert envelope is not None
        assert envelope.bridge_ts.endswith("Z")

    def test_schema_version(self) -> None:
        state = SessionState()
        envelope = normalize_raw("ARENA_END|5", state, "Player")
        assert envelope is not None
        assert envelope.schema_version == 1
