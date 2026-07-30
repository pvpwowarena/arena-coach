"""Phase 4.18: класс ИГРОКА больше не подменяется классом напарника.

Дефект из живого теста 30.07 (память: measured-26s-blind-window): Влад играл
рогой, а бэкенд весь матч считал `player_class=HUNTER` — опенер, килл-таргет и
угрозы шли под класс напарника. Механика была такая: в строку allies попадали
только юниты с известным классом, класс роги за 26 секунд ворот так и не
раскрылся, и напарник-хант оказался первым.

Проверяем три ремонта:
  1) свой класс запоминается НАВСЕГДА и с любого каста (хоть до арены);
  2) при неизвестном классе первым идёт явный UNKNOWN, а не напарник;
  3) класс распознаётся по ИМЕНИ спелла, когда id ранга нет в таблице
     (реальный промах: Arcane Intellect ранга 1459).
"""

from __future__ import annotations

from arena_bridge.combat_tail import CombatInterpreter, class_of_spell
from arena_bridge.normalizer import SessionState, normalize_raw

ME = "Arenacoach"
FRIENDLY = "0x511"
HOSTILE = "0x548"


def _line(ts: str, payload: str) -> str:
    return f"7/30/2026 {ts}  {payload}"


def _prep(event: str, guid: str, name: str) -> str:
    return (
        f'{event},{guid},"{name}-Spineshatter",{FRIENDLY},0x0,'
        f'{guid},"{name}-Spineshatter",{FRIENDLY},0x0,32727,"Arena Preparation",0x1,BUFF'
    )


def _cast(guid: str, name: str, spell_id: int, spell: str, flags: str = FRIENDLY) -> str:
    return (
        f'SPELL_CAST_SUCCESS,{guid},"{name}-Spineshatter",{flags},0x0,'
        f'{guid},"{name}-Spineshatter",{flags},0x0,{spell_id},"{spell}",0x1'
    )


def _prep_start(it: CombatInterpreter) -> None:
    """Аура Arena Preparation на меня и напарника — начало prep-фазы."""
    it.feed_line(_line("13:49:40.000", _prep("SPELL_AURA_APPLIED", "Player-ME", ME)))
    it.feed_line(_line("13:49:40.100", _prep("SPELL_AURA_APPLIED", "Player-AL", "Halfling")))


def _open_gates(it: CombatInterpreter) -> list[str]:
    """Снятие ауры = ворота открылись."""
    return it.feed_line(_line("13:49:45.260", _prep("SPELL_AURA_REMOVED", "Player-ME", ME)))


def _gates(it: CombatInterpreter) -> list[str]:
    _prep_start(it)
    return _open_gates(it)


class TestSelfClassMemory:
    def test_class_learned_before_arena_survives_gates(self) -> None:
        it = CombatInterpreter(player_name=ME)
        # Каст ДО арены (в городе): раньше он не учитывался вовсе.
        it.feed_line(_line("13:00:00.000", _cast("Player-ME", ME, 1856, "Vanish")))
        out = _gates(it)
        assert out == ["ARENA_START#2v2##ROGUE/UNKNOWN"]

    def test_partner_never_takes_the_player_slot(self) -> None:
        it = CombatInterpreter(player_name=ME)
        _prep_start(it)
        # Хант успел скастовать, рога — нет: ровно ситуация живого теста.
        it.feed_line(_line("13:49:41.000", _cast("Player-AL", "Halfling", 27044, "Aspect")))
        out = _open_gates(it)
        assert out == ["ARENA_START#2v2##UNKNOWN/UNKNOWN,HUNTER/UNKNOWN"]

        # И бэкенд из этого payload берёт «класс неизвестен», а не «HUNTER».
        session = SessionState()
        env = normalize_raw(out[0], session, ME)
        assert env is not None
        assert session.match.player_class is None
        assert session.match.our_comp_hint == "hunter"

    def test_known_class_lands_in_first_slot(self) -> None:
        it = CombatInterpreter(player_name=ME)
        _prep_start(it)
        it.feed_line(_line("13:49:41.000", _cast("Player-AL", "Halfling", 27044, "Aspect")))
        it.feed_line(_line("13:49:42.000", _cast("Player-ME", ME, 1856, "Vanish")))
        out = _open_gates(it)
        assert out == ["ARENA_START#2v2##ROGUE/UNKNOWN,HUNTER/UNKNOWN"]

        session = SessionState()
        normalize_raw(out[0], session, ME)
        assert session.match.player_class == "ROGUE"
        assert session.match.our_comp_hint == "hunter+rogue"

    def test_next_match_reuses_remembered_class(self) -> None:
        """Второй матч подряд: ростер чистится, память о классах — нет."""
        it = CombatInterpreter(player_name=ME)
        # Оба скастовали ДО арены (баффы в городе) — память переживёт очистку ростера.
        it.feed_line(_line("13:40:00.000", _cast("Player-ME", ME, 1856, "Vanish")))
        it.feed_line(_line("13:40:01.000", _cast("Player-AL", "Halfling", 27044, "Aspect")))
        _gates(it)
        out = _gates(it)  # новая prep-фаза = новый матч
        assert out == ["ARENA_START#2v2##ROGUE/UNKNOWN,HUNTER/UNKNOWN"]


class TestClassBySpellName:
    def test_arcane_intellect_rank_without_id_is_still_a_mage(self) -> None:
        # id 1459 (ранг 1) в таблице id нет — именно он не сработал 30.07.
        assert class_of_spell(1459) is None
        assert class_of_spell(1459, "Arcane Intellect") == "MAGE"

    def test_id_wins_over_name(self) -> None:
        assert class_of_spell(1856, "Arcane Intellect") == "ROGUE"

    def test_unknown_stays_unknown(self) -> None:
        assert class_of_spell(999999, "Find Herbs") is None

    def test_enemy_revealed_by_gate_buff_name(self) -> None:
        it = CombatInterpreter(player_name=ME)
        _gates(it)
        out = it.feed_line(
            _line(
                "13:49:45.300",
                _cast("Player-EN", "Malodos", 1459, "Arcane Intellect", flags=HOSTILE),
            )
        )
        assert any(o.startswith("ARENA_START#2v2#MAGE/UNKNOWN#") for o in out)
