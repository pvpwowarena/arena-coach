#!/usr/bin/env bash
# Печатает DATABASE_URL из systemd EnvironmentFile. Единственный аргумент — путь к файлу.
#
# Почему отдельный скрипт, а не строчка внутри vps-deploy.sh: логика покрыта тестом
# (`tests/test_deploy_db_url.py`). Шаг деплоя дважды ронял прод, и оба раза — молча.
#
# Почему НЕ `. api.env`: это systemd EnvironmentFile, а не shell-скрипт. У него свой
# формат, и значение с `(`, `)`, `#`, пробелом или кавычками шелл выполнить не может:
#   $ . api.env
#   api.env: line 2: syntax error near unexpected token `('
# Под `set -euo pipefail` это убивает деплой, а с `2>/dev/null` (как было до 4.16) —
# тихо оставляет DATABASE_URL пустым, и alembic уезжает мигрировать не ту БД.
# Инцидент 30.07.2026: docs/incident-2026-07-30-500-events.md
#
# Бонус: секреты из api.env (токены, ключ Anthropic) больше не попадают в окружение
# деплой-шелла — берём ровно одну нужную строку.
#
# Формат systemd, который поддерживаем: `KEY=value`, ведущие пробелы, `#`-комментарии,
# значение в одинарных или двойных кавычках. Последнее вхождение ключа побеждает
# (так же ведёт себя systemd).
set -euo pipefail

file="${1:?usage: read-db-url.sh <env-file>}"
[ -r "$file" ] || { echo "read-db-url: $file не читается" >&2; exit 1; }

raw="$(sed -n 's/^[[:space:]]*DATABASE_URL[[:space:]]*=//p' "$file" | tail -n 1)"
[ -n "$raw" ] || { echo "read-db-url: DATABASE_URL не найден в $file" >&2; exit 1; }

# Обрезаем внешние кавычки, если есть (systemd их снимает, шелл-присваивание — нет).
case "$raw" in
  \"*\") raw="${raw#\"}"; raw="${raw%\"}" ;;
  \'*\') raw="${raw#\'}"; raw="${raw%\'}" ;;
esac

printf '%s\n' "$raw"
