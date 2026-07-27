"""Мастер первого запуска моста (Phase 4.8, bridge 0.7.0).

Мастер обязан: (1) запускаться только когда конфига нет и консоль живая,
(2) переварить копипаст с кавычками/пробелами, (3) найти WoW сам или принять
путь руками, (4) записать bridge.env, который env_loader читает обратно
один-в-один. Всё без TTY и реального диска — ввод/вывод и корни инъектируются.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from arena_bridge.env_loader import load_env_file
from arena_bridge.setup_wizard import (
    COMP_SHORTCUTS,
    DEFAULT_BACKEND_URL,
    find_wow_installs,
    looks_like_wow_dir,
    normalize_comp,
    render_env,
    run_wizard,
    should_run_wizard,
)


def scripted(*answers: str):
    """input_fn из списка ответов; лишний вопрос = EOF (как закрытая консоль)."""
    queue = list(answers)

    def _input(_prompt: str) -> str:
        if not queue:
            raise EOFError
        return queue.pop(0)

    return _input


def make_wow_dir(tmp_path: Path, name: str = "World of Warcraft") -> Path:
    wow = tmp_path / name
    (wow / "Logs").mkdir(parents=True)
    (wow / "Interface").mkdir()
    return wow


# ── should_run_wizard: когда мастеру можно ───────────────────────────────────


def test_runs_when_no_config_and_interactive() -> None:
    assert should_run_wizard(None, {}, True) is True


def test_skips_when_env_file_exists(tmp_path: Path) -> None:
    assert should_run_wizard(tmp_path / "bridge.env", {}, True) is False


def test_skips_when_token_in_environ() -> None:
    assert should_run_wizard(None, {"BRIDGE_BEARER_TOKEN": "tok"}, True) is False


def test_skips_without_tty() -> None:
    assert should_run_wizard(None, {}, False) is False


def test_skips_for_check_config_even_forced() -> None:
    assert should_run_wizard(None, {}, True, force=True, check_config=True) is False


def test_force_overrides_existing_config(tmp_path: Path) -> None:
    env = tmp_path / "bridge.env"
    assert should_run_wizard(env, {"BRIDGE_BEARER_TOKEN": "tok"}, True, force=True) is True


def test_force_still_requires_tty() -> None:
    assert should_run_wizard(None, {}, False, force=True) is False


# ── normalize_comp ───────────────────────────────────────────────────────────


@pytest.mark.parametrize(("raw", "expected"), sorted(COMP_SHORTCUTS.items()))
def test_comp_shortcuts(raw: str, expected: str) -> None:
    assert normalize_comp(raw) == expected
    assert normalize_comp(raw.upper()) == expected


def test_comp_full_slug_passthrough() -> None:
    assert normalize_comp(" Rogue+Mage ") == "rogue+mage"
    assert normalize_comp("rogue+resto-druid") == "rogue+resto-druid"


def test_comp_empty_and_garbage_mean_auto() -> None:
    assert normalize_comp("") is None
    assert normalize_comp("   ") is None
    assert normalize_comp("не знаю") is None
    assert normalize_comp("rogue+ma ge") is None  # пробел внутри класса


# ── поиск WoW ────────────────────────────────────────────────────────────────


def test_looks_like_wow_dir(tmp_path: Path) -> None:
    assert looks_like_wow_dir(make_wow_dir(tmp_path)) is True
    assert looks_like_wow_dir(tmp_path / "нет-такой") is False
    empty = tmp_path / "пустая"
    empty.mkdir()
    assert looks_like_wow_dir(empty) is False


def test_find_wow_scans_roots_and_children(tmp_path: Path) -> None:
    # корень сам НЕ похож на WoW, но содержит _classic_era_ с Logs/
    root = tmp_path / "World of Warcraft"
    inner = root / "_classic_era_"
    (inner / "Logs").mkdir(parents=True)
    found = find_wow_installs([root, tmp_path / "мимо"])
    assert found == [inner]


# ── run_wizard: сценарии ─────────────────────────────────────────────────────


def test_happy_path_writes_env_readable_by_env_loader(tmp_path: Path) -> None:
    wow = make_wow_dir(tmp_path)
    out: list[str] = []
    path = run_wizard(
        tmp_path,
        input_fn=scripted("  SECRET-1 ", "Готмог", "rl"),
        print_fn=out.append,
        wow_roots=[wow],
    )
    assert path == tmp_path / "bridge.env"
    cfg = load_env_file(path)
    assert cfg["BRIDGE_BEARER_TOKEN"] == "SECRET-1"
    assert cfg["BRIDGE_PLAYER_NAME"] == "Готмог"
    assert cfg["BRIDGE_OUR_COMP"] == "rogue+warlock"
    assert cfg["WOW_INSTALL_PATH"] == str(wow)
    assert cfg["BACKEND_URL"] == DEFAULT_BACKEND_URL
    assert any("Готово" in line for line in out)


def test_quotes_stripped_from_pasted_token(tmp_path: Path) -> None:
    wow = make_wow_dir(tmp_path)
    path = run_wizard(
        tmp_path,
        input_fn=scripted('"токен-в-кавычках"', "Ник", ""),
        print_fn=lambda _s: None,
        wow_roots=[wow],
    )
    assert load_env_file(path)["BRIDGE_BEARER_TOKEN"] == "токен-в-кавычках"


def test_empty_comp_leaves_auto_detection(tmp_path: Path) -> None:
    wow = make_wow_dir(tmp_path)
    path = run_wizard(
        tmp_path,
        input_fn=scripted("t", "N", ""),
        print_fn=lambda _s: None,
        wow_roots=[wow],
    )
    assert "BRIDGE_OUR_COMP" not in load_env_file(path)


def test_unknown_comp_warns_and_falls_back_to_auto(tmp_path: Path) -> None:
    wow = make_wow_dir(tmp_path)
    out: list[str] = []
    path = run_wizard(
        tmp_path,
        input_fn=scripted("t", "N", "васян-стайл"),
        print_fn=out.append,
        wow_roots=[wow],
    )
    assert "BRIDGE_OUR_COMP" not in load_env_file(path)
    assert any("Не узнал состав" in line for line in out)


def test_empty_token_reasked_until_given(tmp_path: Path) -> None:
    wow = make_wow_dir(tmp_path)
    path = run_wizard(
        tmp_path,
        input_fn=scripted("", "   ", "наконец-токен", "Ник", ""),
        print_fn=lambda _s: None,
        wow_roots=[wow],
    )
    assert load_env_file(path)["BRIDGE_BEARER_TOKEN"] == "наконец-токен"


def test_multiple_wow_installs_numbered_choice(tmp_path: Path) -> None:
    wow1 = make_wow_dir(tmp_path, "WoW-старый")
    wow2 = make_wow_dir(tmp_path, "WoW-новый")
    out: list[str] = []
    path = run_wizard(
        tmp_path,
        input_fn=scripted("t", "N", "", "abc", "2"),  # сначала мимо, потом номер
        print_fn=out.append,
        wow_roots=[wow1, wow2],
    )
    assert load_env_file(path)["WOW_INSTALL_PATH"] == str(wow2)
    assert any("несколько установок" in line for line in out)


def test_manual_path_with_quotes_after_failed_autodetect(tmp_path: Path) -> None:
    wow = make_wow_dir(tmp_path, "Игры/World of Warcraft")
    bad = tmp_path / "не-wow"
    bad.mkdir()
    path = run_wizard(
        tmp_path,
        input_fn=scripted("t", "N", "", f'"{bad}"', f'"{wow}"'),
        print_fn=lambda _s: None,
        wow_roots=[tmp_path / "пусто"],  # автопоиск ничего не найдёт
    )
    assert load_env_file(path)["WOW_INSTALL_PATH"] == str(wow)


def test_eof_mid_wizard_aborts_without_file(tmp_path: Path) -> None:
    out: list[str] = []
    result = run_wizard(
        tmp_path,
        input_fn=scripted("токен"),  # дальше EOF
        print_fn=out.append,
        wow_roots=[],
    )
    assert result is None
    assert not (tmp_path / "bridge.env").exists()
    assert any("прервана" in line for line in out)


def test_keyboard_interrupt_aborts_gracefully(tmp_path: Path) -> None:
    def _boom(_prompt: str) -> str:
        raise KeyboardInterrupt

    assert run_wizard(tmp_path, input_fn=_boom, print_fn=lambda _s: None, wow_roots=[]) is None


# ── render_env: пути с пробелами переживают round-trip ──────────────────────


def test_render_env_round_trip_spaces_and_backslashes(tmp_path: Path) -> None:
    wow = tmp_path / "Program Files (x86)" / "World of Warcraft"
    (wow / "Logs").mkdir(parents=True)
    env_text = render_env("tok", "Ник", wow, "rogue+mage")
    f = tmp_path / "bridge.env"
    f.write_text(env_text, encoding="utf-8")
    cfg = load_env_file(f)
    assert cfg["WOW_INSTALL_PATH"] == str(wow)
    assert cfg["BRIDGE_OUR_COMP"] == "rogue+mage"
