"""Минимальный dotenv-парсер без внешних зависимостей.

Загружает KEY=VALUE строки из файла в os.environ.
Поддерживает:
- Комментарии (#)
- Кавычки: "value" / 'value' → убираем кавычки
- Пустые строки
- Пробелы вокруг = и значения

НЕ поддерживает:
- Многострочные значения
- Variable expansion ($VAR)

Это намеренно простая реализация — не заменяем python-dotenv,
а избегаем лишней зависимости в бандле .exe.
"""

from __future__ import annotations

import os
from pathlib import Path


def load_env_file(path: Path) -> dict[str, str]:
    """Прочитать KEY=VALUE файл и вернуть словарь без изменения os.environ."""
    result: dict[str, str] = {}
    try:
        text = path.read_text(encoding="utf-8")
    except OSError:
        return result

    for _lineno, line in enumerate(text.splitlines(), start=1):
        # Убираем whitespace и пропускаем пустые / комментарии
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue

        # Разбиваем по первому '='
        if "=" not in stripped:
            continue  # Некорректная строка — пропускаем

        key, _, raw_value = stripped.partition("=")
        key = key.strip()
        raw_value = raw_value.strip()

        if not key:
            continue

        # Убираем inline-комментарий (только если значение без кавычек)
        if raw_value and raw_value[0] not in ('"', "'"):
            comment_pos = raw_value.find(" #")
            if comment_pos >= 0:
                raw_value = raw_value[:comment_pos].rstrip()

        # Снимаем кавычки
        value = _strip_quotes(raw_value)

        result[key] = value

    return result


def apply_env_file(path: Path, *, override: bool = False) -> list[str]:
    """Загрузить .env файл и применить переменные к os.environ.

    Args:
        path:     Путь к .env файлу.
        override: Если True — перезаписываем уже установленные переменные.
                  Если False (default) — существующие переменные имеют приоритет
                  (поведение как у python-dotenv по умолчанию).

    Returns:
        Список ключей, которые были установлены/обновлены.
    """
    loaded = load_env_file(path)
    applied: list[str] = []
    for key, value in loaded.items():
        if override or key not in os.environ:
            os.environ[key] = value
            applied.append(key)
    return applied


def _strip_quotes(value: str) -> str:
    """Убрать парные одинарные или двойные кавычки вокруг значения."""
    if len(value) >= 2 and value[0] == value[-1] and value[0] in ('"', "'"):
        return value[1:-1]
    return value
