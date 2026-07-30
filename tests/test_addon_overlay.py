"""Phase 4.18: логика визуального слоя аддона — проверяется без клиента WoW.

Аддон гоняется в обычном lua5.1 поверх заглушки клиентского API
(`tests/fixtures/addon_stub.lua`). Так проверяются ровно те решения, ради
которых слой и делался: килл-таргет из скомпилированной KB, фолбэк-эвристика
для незнакомого сетапа и разрешение ДУБЛЕЙ класса по потраченному тринкету.

Без lua5.1 в системе тесты скипаются (в CI ставится пакетом).
"""

from __future__ import annotations

import json
import shutil
import subprocess
import textwrap
from pathlib import Path

import pytest

LUA = shutil.which("lua5.1") or shutil.which("lua")

#: Сценарные тесты требуют интерпретатора; проверки генератора и .toc — нет.
needs_lua = pytest.mark.skipif(LUA is None, reason="lua5.1 не установлен")

REPO = Path(__file__).resolve().parent.parent
ADDON = REPO / "addon" / "ArenaCoach"
STUB = Path(__file__).resolve().parent / "fixtures" / "addon_stub.lua"

#: Порядок загрузки — как в ArenaCoach.toc.
FILES = ("Core.lua", "Tracker.lua", "KillTargets.lua", "Overlay.lua", "UI.lua")


def _run(scenario_lua: str, probe_lua: str) -> dict[str, object]:
    """Загрузить аддон в lua5.1, применить сценарий, вернуть результат probe как dict."""
    script = textwrap.dedent(
        """
        dofile("{stub}")
        ArenaCoachDB = {{ sessions = {{}} }}
        {loads}
        local S = SCENARIO
        local O = ArenaCoach.Overlay
        {scenario}
        {probe}
        """
    ).format(
        stub=STUB,
        loads="\n".join(f'dofile("{ADDON / f}")' for f in FILES),
        scenario=scenario_lua,
        probe=probe_lua,
    )
    proc = subprocess.run(
        [LUA or "lua", "-"], input=script, capture_output=True, text=True, timeout=30
    )
    assert proc.returncode == 0, proc.stderr
    return json.loads(proc.stdout.strip().splitlines()[-1])


#: Простейший сериализатор результата: печатаем одну JSON-строку.
_EMIT = """
local function q(v)
    if v == nil then return "null" end
    if type(v) == "boolean" then return tostring(v) end
    if type(v) == "number" then return tostring(v) end
    return '"' .. tostring(v) .. '"'
end
print("{" ..
    '"target":' .. q(O.targetUnit) .. "," ..
    '"sure":' .. q(O.targetSure) .. "," ..
    '"source":' .. q(O.source) .. "," ..
    '"units":' .. q(#O.units) .. "," ..
    '"marks":' .. q(#S.marks) ..
"}")
"""


def _scenario(party: dict[str, str], enemies: list[dict[str, object]], bracket: str) -> str:
    """Сгенерировать lua-настройку сценария: наш состав + враги + брекет."""
    lines = []
    for unit, cls in party.items():
        lines.append(f'S.party["{unit}"] = {{ class = "{cls}" }}')
    for i, e in enumerate(enemies, start=1):
        hp = e.get("hp", 100)
        lines.append(
            f'S.units["arena{i}"] = {{ class = "{e["class"]}", '
            f'name = "Enemy{i}", guid = "GUID-arena{i}", hp = {hp} }}'
        )
    lines.append(f'ArenaCoach.currentSession = {{ bracket = "{bracket}" }}')
    return "\n".join(lines)


@needs_lua
class TestKillTargetFromKB:
    def test_known_matchup_uses_kb(self) -> None:
        # 2v2|rogue+warlock|druid+rogue → друид (есть в KillTargets.lua).
        res = _run(
            _scenario(
                {"player": "ROGUE", "party1": "WARLOCK"},
                [{"class": "DRUID"}, {"class": "ROGUE"}],
                "2v2",
            )
            + "\nO:StartMatch()",
            _EMIT,
        )
        assert res["source"] == "KB"
        assert res["target"] == "arena1"  # друид
        assert res["sure"] is True
        assert res["marks"] >= 1  # череп на цель поставлен

    def test_unknown_matchup_falls_back_to_heuristic(self) -> None:
        res = _run(
            _scenario(
                {"player": "ROGUE", "party1": "MAGE", "party2": "PRIEST"},
                [{"class": "SHAMAN"}, {"class": "SHAMAN"}, {"class": "SHAMAN"}],
                "3v3",
            )
            + "\nO:StartMatch()",
            _EMIT,
        )
        assert res["source"] == "эвристика"
        assert res["sure"] is False  # эвристика всегда провизорна
        assert res["target"] is not None

    def test_healer_class_is_deprioritised(self) -> None:
        # Пала (вероятный хилер) против мага: цель — маг, даже если пала первый.
        res = _run(
            _scenario(
                {"player": "ROGUE", "party1": "SHAMAN"},
                [{"class": "PALADIN"}, {"class": "MAGE"}],
                "2v2",
            )
            + "\nO:StartMatch()",
            _EMIT,
        )
        assert res["target"] == "arena2"


@needs_lua
class TestDuplicateClasses:
    def test_target_switches_to_the_one_who_burned_trinket(self) -> None:
        """Дубль класса: бьём ту рогу, что уже потратила тринкет."""
        setup = (
            _scenario(
                {"player": "ROGUE", "party1": "WARLOCK"},
                [{"class": "ROGUE"}, {"class": "ROGUE"}],
                "2v2",
            )
            + "\nO:StartMatch()"
        )
        before = _run(setup, _EMIT)
        assert before["target"] == "arena1"  # при равенстве — первый

        after = _run(setup + '\nO:NoteTrinket("GUID-arena2")', _EMIT)
        assert after["target"] == "arena2"

    def test_lower_hp_wins_when_trinkets_equal(self) -> None:
        res = _run(
            _scenario(
                {"player": "ROGUE", "party1": "WARLOCK"},
                [{"class": "ROGUE", "hp": 90}, {"class": "ROGUE", "hp": 30}],
                "2v2",
            )
            + "\nO:StartMatch()",
            _EMIT,
        )
        assert res["target"] == "arena2"


@needs_lua
class TestRosterLifecycle:
    def test_stealth_roster_is_empty_then_fills(self) -> None:
        empty = _run(
            _scenario({"player": "ROGUE", "party1": "WARLOCK"}, [], "2v2") + "\nO:StartMatch()",
            _EMIT,
        )
        assert empty["units"] == 0
        assert empty["target"] is None

        revealed = _run(
            _scenario({"player": "ROGUE", "party1": "WARLOCK"}, [], "2v2")
            + "\nO:StartMatch()"
            + '\nS.units["arena1"] = { class = "MAGE", name = "E", guid = "G1", hp = 100 }'
            + "\nO:ScanRoster()",
            _EMIT,
        )
        assert revealed["units"] == 1
        assert revealed["target"] == "arena1"

    def test_end_match_clears_everything(self) -> None:
        res = _run(
            _scenario(
                {"player": "ROGUE", "party1": "WARLOCK"},
                [{"class": "DRUID"}, {"class": "ROGUE"}],
                "2v2",
            )
            + "\nO:StartMatch()\nO:EndMatch()",
            _EMIT,
        )
        assert res["units"] == 0
        assert res["target"] is None


class TestGeneratedTable:
    def test_killtargets_lua_is_in_sync_with_kb(self) -> None:
        """Сгенерированный файл обязан совпадать с текущим KB."""
        proc = subprocess.run(
            ["python3", str(REPO / "tools" / "gen_addon_killtargets.py"), "--check"],
            capture_output=True,
            text=True,
            cwd=REPO,
        )
        assert proc.returncode == 0, proc.stdout + proc.stderr

    def test_toc_lists_every_lua_file(self) -> None:
        toc = (ADDON / "ArenaCoach.toc").read_text(encoding="utf-8")
        for path in sorted(ADDON.glob("*.lua")):
            assert path.name in toc, f"{path.name} не подключён в .toc"
