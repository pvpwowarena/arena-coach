"""Тесты allies-расширения ARENA_START (addon 0.2.0 / bridge v0.3.0).

Формат: [AC|ARENA_START|2v2|<enemies>|<allies>] — allies опциональны
(обратная совместимость с addon 0.1.x), игрок в allies всегда первый.
"""

from __future__ import annotations

from arena_bridge.normalizer import (
    ArenaStartEvent,
    SessionState,
    normalize_raw,
    parse_event,
)


class TestArenaStartAllies:
    def test_allies_parsed(self) -> None:
        ev = parse_event("ARENA_START|2v2|WARRIOR/ORC,PALADIN/BLOODELF|ROGUE/HUMAN,MAGE/GNOME")
        assert isinstance(ev, ArenaStartEvent)
        assert [e.wow_class for e in ev.enemies] == ["WARRIOR", "PALADIN"]
        assert [a.wow_class for a in ev.allies] == ["ROGUE", "MAGE"]

    def test_old_format_no_allies(self) -> None:
        """Addon 0.1.x шлёт 3 поля — allies пустые, ничего не падает."""
        ev = parse_event("ARENA_START|2v2|WARRIOR/ORC,PALADIN/BLOODELF")
        assert isinstance(ev, ArenaStartEvent)
        assert ev.allies == []

    def test_empty_allies_field(self) -> None:
        ev = parse_event("ARENA_START|2v2|WARRIOR/ORC|")
        assert isinstance(ev, ArenaStartEvent)
        assert ev.allies == []


class TestMatchInfoHints:
    def test_our_comp_and_player_class_from_allies(self) -> None:
        state = SessionState()
        env = normalize_raw(
            "ARENA_START|2v2|WARRIOR/ORC,PALADIN/BLOODELF|ROGUE/HUMAN,MAGE/GNOME",
            state,
            "Vladislav",
        )
        assert env is not None
        assert env.match.our_comp_hint == "mage+rogue"  # sorted, class-level
        assert env.match.player_class == "ROGUE"  # игрок первый в allies
        assert env.match.matchup_slug_hint == "paladin-warrior"

    def test_default_our_comp_fallback(self) -> None:
        """Старый аддон + $BRIDGE_OUR_COMP → hint из конфига."""
        state = SessionState(default_our_comp="rogue+mage")
        env = normalize_raw("ARENA_START|2v2|WARRIOR/ORC", state, "Vladislav")
        assert env is not None
        assert env.match.our_comp_hint == "rogue+mage"
        assert env.match.player_class is None

    def test_no_allies_no_default(self) -> None:
        state = SessionState()
        env = normalize_raw("ARENA_START|2v2|WARRIOR/ORC", state, "Vladislav")
        assert env is not None
        assert env.match.our_comp_hint is None

    def test_reemit_keeps_session_id(self) -> None:
        """Повторный ARENA_START (враг вышел из стелса) — та же сессия."""
        state = SessionState()
        e1 = normalize_raw("ARENA_START|2v2|WARRIOR/ORC", state, "V")
        e2 = normalize_raw("ARENA_START|2v2|WARRIOR/ORC,PALADIN/BLOODELF", state, "V")
        assert e1 is not None and e2 is not None
        assert e1.session_id == e2.session_id
        assert [e.wow_class for e in e2.match.enemies] == ["WARRIOR", "PALADIN"]

    def test_new_session_after_end(self) -> None:
        state = SessionState()
        e1 = normalize_raw("ARENA_START|2v2|WARRIOR/ORC", state, "V")
        normalize_raw("ARENA_END|5", state, "V")
        e2 = normalize_raw("ARENA_START|2v2|MAGE/GNOME", state, "V")
        assert e1 is not None and e2 is not None
        assert e1.session_id != e2.session_id
