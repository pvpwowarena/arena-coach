"""Тесты arena_bridge.env_loader — минимальный dotenv-парсер."""

from __future__ import annotations

import os
from pathlib import Path

import pytest

from arena_bridge.env_loader import apply_env_file, load_env_file

# ── load_env_file ─────────────────────────────────────────────────────────────


def test_load_basic_key_value(tmp_path: Path) -> None:
    """Простые KEY=VALUE парсятся корректно."""
    f = tmp_path / "test.env"
    f.write_text("FOO=bar\nBAZ=qux\n", encoding="utf-8")
    result = load_env_file(f)
    assert result == {"FOO": "bar", "BAZ": "qux"}


def test_load_ignores_comments(tmp_path: Path) -> None:
    """Строки с # игнорируются."""
    f = tmp_path / "test.env"
    f.write_text("# это комментарий\nKEY=value\n", encoding="utf-8")
    result = load_env_file(f)
    assert result == {"KEY": "value"}
    assert len(result) == 1


def test_load_ignores_empty_lines(tmp_path: Path) -> None:
    """Пустые строки и строки только из пробелов пропускаются."""
    f = tmp_path / "test.env"
    f.write_text("\n   \nKEY=value\n\n", encoding="utf-8")
    result = load_env_file(f)
    assert result == {"KEY": "value"}


def test_load_double_quoted_value(tmp_path: Path) -> None:
    """Значение в двойных кавычках — кавычки снимаются."""
    f = tmp_path / "test.env"
    f.write_text('KEY="hello world"\n', encoding="utf-8")
    result = load_env_file(f)
    assert result["KEY"] == "hello world"


def test_load_single_quoted_value(tmp_path: Path) -> None:
    """Значение в одинарных кавычках — кавычки снимаются."""
    f = tmp_path / "test.env"
    f.write_text("KEY='hello world'\n", encoding="utf-8")
    result = load_env_file(f)
    assert result["KEY"] == "hello world"


def test_load_inline_comment_stripped(tmp_path: Path) -> None:
    """Inline-комментарий ( #) после значения убирается (только без кавычек)."""
    f = tmp_path / "test.env"
    f.write_text("KEY=value # inline comment\n", encoding="utf-8")
    result = load_env_file(f)
    assert result["KEY"] == "value"


def test_load_value_with_url(tmp_path: Path) -> None:
    """URL со слешами и https парсятся без потерь."""
    f = tmp_path / "test.env"
    f.write_text("BACKEND_URL=https://coach.example.com\n", encoding="utf-8")
    result = load_env_file(f)
    assert result["BACKEND_URL"] == "https://coach.example.com"


def test_load_windows_path(tmp_path: Path) -> None:
    """Windows-путь с обратными слешами (без кавычек) читается as-is."""
    f = tmp_path / "test.env"
    f.write_text(
        r"WOW_INSTALL_PATH=C:\Program Files\World of Warcraft\_classic_era_" + "\n",
        encoding="utf-8",
    )
    result = load_env_file(f)
    assert result["WOW_INSTALL_PATH"] == r"C:\Program Files\World of Warcraft\_classic_era_"


def test_load_missing_file_returns_empty(tmp_path: Path) -> None:
    """Несуществующий файл → пустой словарь, без исключений."""
    result = load_env_file(tmp_path / "nonexistent.env")
    assert result == {}


def test_load_no_equals_skipped(tmp_path: Path) -> None:
    """Строки без '=' пропускаются (не выбрасывают исключение)."""
    f = tmp_path / "test.env"
    f.write_text("BROKEN_LINE\nKEY=value\n", encoding="utf-8")
    result = load_env_file(f)
    assert "BROKEN_LINE" not in result
    assert result["KEY"] == "value"


# ── apply_env_file ────────────────────────────────────────────────────────────


def test_apply_sets_env_vars(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """apply_env_file устанавливает переменные в os.environ."""
    monkeypatch.delenv("TEST_BRIDGE_FOO", raising=False)
    f = tmp_path / "test.env"
    f.write_text("TEST_BRIDGE_FOO=hello\n", encoding="utf-8")
    applied = apply_env_file(f)
    assert os.environ.get("TEST_BRIDGE_FOO") == "hello"
    assert "TEST_BRIDGE_FOO" in applied


def test_apply_no_override_by_default(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """По умолчанию существующие переменные среды имеют приоритет над файлом."""
    monkeypatch.setenv("TEST_BRIDGE_BAR", "system_value")
    f = tmp_path / "test.env"
    f.write_text("TEST_BRIDGE_BAR=file_value\n", encoding="utf-8")
    apply_env_file(f, override=False)
    assert os.environ["TEST_BRIDGE_BAR"] == "system_value"


def test_apply_override_replaces_env(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """override=True перезаписывает уже установленные переменные."""
    monkeypatch.setenv("TEST_BRIDGE_BAZ", "old_value")
    f = tmp_path / "test.env"
    f.write_text("TEST_BRIDGE_BAZ=new_value\n", encoding="utf-8")
    apply_env_file(f, override=True)
    assert os.environ["TEST_BRIDGE_BAZ"] == "new_value"
