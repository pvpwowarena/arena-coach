"""Append-only audit log writer.

Phase 2 skeleton. См. docs/phase-0-design.md §5.3.
- Один JSONL-файл в месяц: audit-YYYY-MM.jsonl
- chmod 600, service-user owner
- write-ahead: запись audit до mutate, второй event 'action.failed' если ошибка
"""

from __future__ import annotations


def write_audit_entry(
    *,
    actor_discord_id: str,
    action: str,
    target: str | None,
    payload: dict[str, object],
    result: str,
) -> None:
    """TODO(Phase 2): append-only JSONL writer с SHA-256 payload-hash."""
    raise NotImplementedError("Phase 2")
