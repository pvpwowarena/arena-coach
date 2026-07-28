"""Phase 4.9: pet/totem-инференс — класс (и спек) хозяина по касту пета/саммона.

Два механизма:
  • саммоны/тотемы кастует САМ хозяин (Summon Water Elemental, Grounding…) —
    новые id в _CLASS_SPELLS/_SPELL_TO_SPEC_* работают через существующий путь;
  • каст ПЕТА (Waterbolt элементаля) — хозяин ещё не кастовал: в ростер идёт
    proxy-юнит с классом/спеком хозяина, уступающий место реальному игроку.
"""

from __future__ import annotations

from arena_bridge.combat_tail import CombatInterpreter

HOSTILE = "0x548"
HOSTILE_PET = "0x1148"  # пет/страж: TYPE_PET + hostile, НЕ player


def _line(ts: str, payload: str) -> str:
    return f"7/23/2026 {ts}  {payload}"


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


def _cast(guid: str, name: str, spell_id: int, spell: str, flags: str = HOSTILE) -> str:
    return (
        f'SPELL_CAST_SUCCESS,{guid},"{name}",{flags},0x0,'
        f'Player-1-ME,"Arenacoach-Spineshatter",0x511,0x0,{spell_id},"{spell}",0x1'
    )


def _start_2v2(interp: CombatInterpreter) -> None:
    interp.feed_line(_line("22:00:00.000", PREP_ON_ME))
    interp.feed_line(_line("22:00:01.000", PREP_ON_ALLY))
    interp.feed_line(_line("22:00:30.000", PREP_OFF_ME))


def _payloads(interp: CombatInterpreter, ts: str, cast: str) -> list[str]:
    return [p for p in interp.feed_line(_line(ts, cast)) if p.startswith("ARENA_START")]


class TestOwnerCastIds:
    def test_water_elemental_summon_marks_frost_mage(self) -> None:
        it = CombatInterpreter(player_name="Arenacoach")
        _start_2v2(it)
        out = _payloads(
            it, "22:00:31.000", _cast("Player-1-EN1", "Frosty", 31687, "Summon Water Elemental")
        )
        assert out and "MAGE/UNKNOWN/frost-mage" in out[0]

    def test_tremor_totem_marks_shaman(self) -> None:
        it = CombatInterpreter(player_name="Arenacoach")
        _start_2v2(it)
        out = _payloads(it, "22:00:32.000", _cast("Player-1-EN1", "Totemus", 8143, "Tremor Totem"))
        assert out and "SHAMAN/UNKNOWN" in out[0]

    def test_pain_suppression_marks_disc(self) -> None:
        it = CombatInterpreter(player_name="Arenacoach")
        _start_2v2(it)
        out = _payloads(
            it, "22:00:33.000", _cast("Player-1-EN1", "Discus", 33206, "Pain Suppression")
        )
        assert out and "PRIEST/UNKNOWN/discipline-priest" in out[0]

    def test_crusader_strike_marks_ret(self) -> None:
        it = CombatInterpreter(player_name="Arenacoach")
        _start_2v2(it)
        out = _payloads(
            it, "22:00:34.000", _cast("Player-1-EN1", "Retus", 35395, "Crusader Strike")
        )
        assert out and "PALADIN/UNKNOWN/ret-paladin" in out[0]

    def test_felhunter_summon_marks_warlock(self) -> None:
        it = CombatInterpreter(player_name="Arenacoach")
        _start_2v2(it)
        out = _payloads(it, "22:00:35.000", _cast("Player-1-EN1", "Locky", 691, "Summon Felhunter"))
        assert out and "WARLOCK/UNKNOWN" in out[0]


class TestPetProxy:
    def test_waterbolt_from_pet_adds_frost_mage_proxy(self) -> None:
        it = CombatInterpreter(player_name="Arenacoach")
        _start_2v2(it)
        out = _payloads(
            it,
            "22:00:31.000",
            _cast("Pet-1-ELE", "Water Elemental", 31707, "Waterbolt", HOSTILE_PET),
        )
        assert out and "MAGE/UNKNOWN/frost-mage" in out[0]

    def test_repeated_pet_casts_do_not_duplicate(self) -> None:
        it = CombatInterpreter(player_name="Arenacoach")
        _start_2v2(it)
        _payloads(
            it,
            "22:00:31.000",
            _cast("Pet-1-ELE", "Water Elemental", 31707, "Waterbolt", HOSTILE_PET),
        )
        out = _payloads(
            it,
            "22:00:40.000",
            _cast("Pet-1-ELE", "Water Elemental", 31707, "Waterbolt", HOSTILE_PET),
        )
        assert out == []  # состав не изменился — re-emit нет

    def test_real_mage_displaces_proxy(self) -> None:
        it = CombatInterpreter(player_name="Arenacoach")
        _start_2v2(it)
        _payloads(
            it,
            "22:00:31.000",
            _cast("Pet-1-ELE", "Water Elemental", 31707, "Waterbolt", HOSTILE_PET),
        )
        # второй враг занял оставшийся слот (2v2 → кап 2)
        _payloads(it, "22:00:32.000", _cast("Player-1-EN2", "Locky", 691, "Summon Felhunter"))
        # реальный маг кастует при ПОЛНОМ ростере: прокси уступает место
        out = _payloads(it, "22:00:33.000", _cast("Player-1-EN1", "Frosty", 27072, "Frostbolt"))
        assert out, "прокси должен уступить место реальному магу"
        enemies_field = out[0].split("#")[2]
        assert enemies_field.count("MAGE") == 1  # без фантомного дубля
        assert "WARLOCK" in enemies_field

    def test_no_proxy_when_mage_already_known(self) -> None:
        it = CombatInterpreter(player_name="Arenacoach")
        _start_2v2(it)
        _payloads(it, "22:00:31.000", _cast("Player-1-EN1", "Frosty", 27072, "Frostbolt"))
        out = _payloads(
            it,
            "22:00:32.000",
            _cast("Pet-1-ELE", "Water Elemental", 31707, "Waterbolt", HOSTILE_PET),
        )
        assert out == []  # класс уже в ростере — прокси не добавляется

    def test_unknown_pet_spell_ignored(self) -> None:
        it = CombatInterpreter(player_name="Arenacoach")
        _start_2v2(it)
        out = _payloads(
            it, "22:00:31.000", _cast("Pet-1-DOG", "Wolf", 99999, "Mystery Bite", HOSTILE_PET)
        )
        assert out == []
