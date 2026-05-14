"""Append-only audit log writer.

Формат: один JSONL-файл в месяц — audit-YYYY-MM.jsonl
  - chmod 600 (только service-user читает)
  - SHA-256 от payload (для integrity-проверки)
  - write-ahead: сначала audit-запись, потом mutate в БД

Инвариант append-only: файл открывается только в режиме "a",
никогда не перезаписывается и не редактируется задним числом.
"""

from __future__ import annotations

import hashlib
import json
import threading
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

# Файловый лок — защищает от параллельных записей в одном процессе.
# Для multi-process достаточно: JSONL-append атомарен на Linux (O_APPEND).
_lock = threading.Lock()


def _payload_hash(payload: dict[str, Any]) -> str:
    """SHA-256 от канонического JSON представления payload."""
    canonical = json.dumps(payload, sort_keys=True, ensure_ascii=False, default=str)
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def write_audit_entry(
    *,
    actor_discord_id: str,
    action: str,
    target: str | None,
    payload: dict[str, Any],
    result: str,
) -> None:
    """Добавить запись в текущий месячный JSONL-файл.

    Аргументы:
        actor_discord_id: Discord-ID пользователя, совершившего действие.
        action: Строка вида «whitelist.add», «whitelist.remove», «command.denied».
        target: Discord-ID цели (если применимо) или None.
        payload: Произвольные данные о действии (НЕ хранится — только hash).
        result: «ok» | «denied» | «not_found» | «error».

    Инвариант: функция только добавляет строки, никогда не читает и не изменяет файл.
    """
    from arena_coach.shared.settings import settings

    ts = datetime.now(tz=timezone.utc).isoformat()
    entry: dict[str, Any] = {
        "ts": ts,
        "actor": actor_discord_id,
        "action": action,
        "target": target,
        "payload_hash": _payload_hash(payload),
        "result": result,
    }

    audit_dir = Path(settings.audit_log_dir)
    audit_dir.mkdir(parents=True, exist_ok=True)

    month_key = datetime.now(tz=timezone.utc).strftime("%Y-%m")
    log_file = audit_dir / f"audit-{month_key}.jsonl"

    line = json.dumps(entry, ensure_ascii=False) + "\n"

    with _lock:
        with open(log_file, "a", encoding="utf-8") as fh:
            fh.write(line)
        # Ограничиваем права доступа: только владелец процесса
        import contextlib

        with contextlib.suppress(OSError):
            log_file.chmod(0o600)


def read_recent_entries(
    days: int = 7,
    audit_dir: Path | None = None,
) -> list[dict[str, Any]]:
    """Прочитать записи за последние N дней (для /access audit).

    Читает только для display-команд; не модифицирует файлы.
    """
    from arena_coach.shared.settings import settings

    base = audit_dir or Path(settings.audit_log_dir)
    if not base.exists():
        return []

    cutoff = datetime.now(tz=timezone.utc).replace(
        hour=0, minute=0, second=0, microsecond=0
    )
    from datetime import timedelta

    cutoff = cutoff - timedelta(days=days - 1)

    entries: list[dict[str, Any]] = []
    for log_file in sorted(base.glob("audit-*.jsonl")):
        with open(log_file, encoding="utf-8") as fh:
            for raw_line in fh:
                raw_line = raw_line.strip()
                if not raw_line:
                    continue
                try:
                    entry = json.loads(raw_line)
                    entry_ts = datetime.fromisoformat(entry["ts"])
                    if entry_ts >= cutoff:
                        entries.append(entry)
                except (json.JSONDecodeError, KeyError, ValueError):
                    continue

    return entries


__all__ = ["read_recent_entries", "write_audit_entry"]
