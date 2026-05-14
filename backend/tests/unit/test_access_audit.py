"""Тесты audit log: append-only инвариант, SHA-256 hash, read_recent_entries.

Ключевой инвариант: write_audit_entry только добавляет строки — никогда
не редактирует и не перезаписывает существующие.
"""

from __future__ import annotations

import hashlib
import json
import time
from pathlib import Path

import pytest

from arena_coach.access.audit import _payload_hash, read_recent_entries, write_audit_entry


@pytest.fixture()
def audit_dir(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    """Временная директория для audit-файлов с подменённым settings.audit_log_dir."""
    import arena_coach.shared.settings as _settings_module
    from arena_coach.shared.settings import Settings

    cfg = Settings(
        audit_log_dir=tmp_path,
        arena_coach_fernet_key="",
        discord_bot_token="",
        discord_guild_id=0,
    )
    monkeypatch.setattr(_settings_module, "settings", cfg)
    return tmp_path


def test_payload_hash_deterministic() -> None:
    """SHA-256 hash одного и того же payload всегда одинаковый."""
    payload = {"role": "viewer", "character": "Stabby", "realm": "Gorefiend"}
    h1 = _payload_hash(payload)
    h2 = _payload_hash(payload)
    assert h1 == h2
    assert len(h1) == 64  # hex SHA-256


def test_payload_hash_is_sha256() -> None:
    """Проверяем что hash совпадает с прямым вычислением SHA-256."""
    payload = {"action": "test"}
    canonical = json.dumps(payload, sort_keys=True, ensure_ascii=False, default=str)
    expected = hashlib.sha256(canonical.encode("utf-8")).hexdigest()
    assert _payload_hash(payload) == expected


def test_write_creates_file(audit_dir: Path) -> None:
    """write_audit_entry создаёт JSONL-файл."""
    write_audit_entry(
        actor_discord_id="111",
        action="whitelist.add",
        target="222",
        payload={"role": "viewer"},
        result="ok",
    )
    files = list(audit_dir.glob("audit-*.jsonl"))
    assert len(files) == 1


def test_write_appends(audit_dir: Path) -> None:
    """Несколько вызовов append-only: N записей → N строк."""
    for i in range(5):
        write_audit_entry(
            actor_discord_id="111",
            action=f"action.{i}",
            target=None,
            payload={"i": i},
            result="ok",
        )

    files = list(audit_dir.glob("audit-*.jsonl"))
    assert len(files) == 1
    lines = files[0].read_text(encoding="utf-8").strip().splitlines()
    assert len(lines) == 5


def test_append_only_invariant(audit_dir: Path) -> None:
    """После записи N строк, предыдущие строки не изменяются."""
    # Записываем первую строку
    write_audit_entry(
        actor_discord_id="aaa",
        action="whitelist.add",
        target="bbb",
        payload={"role": "admin"},
        result="ok",
    )

    log_file = list(audit_dir.glob("audit-*.jsonl"))[0]
    first_line = log_file.read_text(encoding="utf-8").splitlines()[0]

    # Записываем ещё несколько строк
    for _ in range(3):
        write_audit_entry(
            actor_discord_id="ccc",
            action="whitelist.remove",
            target="ddd",
            payload={},
            result="ok",
        )

    # Первая строка не изменилась
    lines = log_file.read_text(encoding="utf-8").splitlines()
    assert lines[0] == first_line
    assert len(lines) == 4  # 1 + 3


def test_each_entry_valid_json(audit_dir: Path) -> None:
    """Каждая строка в файле — валидный JSON с обязательными полями."""
    write_audit_entry(
        actor_discord_id="x",
        action="command.denied",
        target="matchup",
        payload={"role_required": "viewer"},
        result="denied",
    )
    log_file = list(audit_dir.glob("audit-*.jsonl"))[0]
    for line in log_file.read_text(encoding="utf-8").splitlines():
        entry = json.loads(line)
        assert "ts" in entry
        assert "actor" in entry
        assert "action" in entry
        assert "payload_hash" in entry
        assert "result" in entry


def test_read_recent_entries(audit_dir: Path) -> None:
    """read_recent_entries возвращает записи за нужный период."""
    write_audit_entry(
        actor_discord_id="u1",
        action="whitelist.add",
        target="u2",
        payload={"role": "player"},
        result="ok",
    )

    entries = read_recent_entries(days=1, audit_dir=audit_dir)
    assert len(entries) == 1
    assert entries[0]["actor"] == "u1"
    assert entries[0]["action"] == "whitelist.add"


def test_read_recent_empty_dir(tmp_path: Path) -> None:
    """read_recent_entries не падает на пустой директории."""
    entries = read_recent_entries(days=7, audit_dir=tmp_path)
    assert entries == []
