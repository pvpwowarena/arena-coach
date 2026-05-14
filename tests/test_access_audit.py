"""Тесты audit log: append-only инвариант, SHA-256 hash, read_recent_entries (Phase 2).

КЛЮЧЕВОЙ ИНВАРИАНТ: write_audit_entry только добавляет строки —
никогда не редактирует и не перезаписывает существующие.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pytest

from arena_coach.access.audit import _payload_hash, read_recent_entries, write_audit_entry


@pytest.fixture()
def audit_dir(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    """Временная директория для audit-файлов с подменённым settings."""
    import arena_coach.shared.settings as _sm
    from arena_coach.shared.settings import Settings

    cfg = Settings(
        audit_log_dir=tmp_path,
        arena_coach_fernet_key="",
        discord_bot_token="",
        discord_guild_id=0,
    )
    monkeypatch.setattr(_sm, "settings", cfg)
    return tmp_path


def test_payload_hash_deterministic() -> None:
    payload = {"role": "viewer", "character": "Stabby"}
    assert _payload_hash(payload) == _payload_hash(payload)
    assert len(_payload_hash(payload)) == 64  # hex SHA-256


def test_payload_hash_is_sha256() -> None:
    payload = {"action": "test"}
    canonical = json.dumps(payload, sort_keys=True, ensure_ascii=False, default=str)
    expected = hashlib.sha256(canonical.encode("utf-8")).hexdigest()
    assert _payload_hash(payload) == expected


def test_write_creates_file(audit_dir: Path) -> None:
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
    for i in range(5):
        write_audit_entry(
            actor_discord_id="111",
            action=f"action.{i}",
            target=None,
            payload={"i": i},
            result="ok",
        )
    lines = next(iter(audit_dir.glob("audit-*.jsonl"))).read_text().strip().splitlines()
    assert len(lines) == 5


def test_append_only_invariant(audit_dir: Path) -> None:
    """После записи N строк предыдущие строки не изменяются."""
    write_audit_entry(
        actor_discord_id="aaa",
        action="whitelist.add",
        target="bbb",
        payload={"role": "admin"},
        result="ok",
    )
    log_file = next(iter(audit_dir.glob("audit-*.jsonl")))
    first_line = log_file.read_text().splitlines()[0]

    for _ in range(3):
        write_audit_entry(
            actor_discord_id="ccc",
            action="whitelist.remove",
            target="ddd",
            payload={},
            result="ok",
        )

    lines = log_file.read_text().splitlines()
    assert lines[0] == first_line  # первая строка не изменилась
    assert len(lines) == 4


def test_each_entry_valid_json_with_required_fields(audit_dir: Path) -> None:
    write_audit_entry(
        actor_discord_id="x",
        action="command.denied",
        target="matchup",
        payload={"role_required": "viewer"},
        result="denied",
    )
    log_file = next(iter(audit_dir.glob("audit-*.jsonl")))
    entry = json.loads(log_file.read_text().strip())
    for field in ("ts", "actor", "action", "payload_hash", "result"):
        assert field in entry


def test_read_recent_entries_returns_today(audit_dir: Path) -> None:
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


def test_read_recent_empty_dir(tmp_path: Path) -> None:
    assert read_recent_entries(days=7, audit_dir=tmp_path) == []
