#!/usr/bin/env bash
# =============================================================================
# Arena Coach — очистка устаревших файлов
#
# Запускать ЛОКАЛЬНО (sandbox-сессии разработчика-агента не имеют прав
# на удаление файлов — поэтому они только перезаписаны заглушками-маркерами).
#
# Что удаляется:
#   - addon/ArenaCoach.lua           — старый Phase 0 bootstrap (заменён addon/ArenaCoach/Core.lua)
#   - addon/ArenaCoach.toc           — старый skeleton .toc
#   - addon/core/                    — пустые stub'ы (заменены addon/ArenaCoach/Tracker.lua)
#   - addon/ui/                      — пустые stub'ы (заменены addon/ArenaCoach/UI.lua)
#   - backend/tests/                 — дубль /tests (pytest/ruff/mypy уже игнорируют)
#   - bridge/tests/                  — пустой scaffold (pytest уже игнорирует)
#   - ingest/tests/                  — дубль /tests
#
# После запуска:
#   1. git add -A && git commit -m "chore: remove legacy skeleton files"
#   2. Обновить README/CLAUDE.md (упоминание дублей удалить)
# =============================================================================
set -euo pipefail

cd "$(git rev-parse --show-toplevel)"

rm -rf addon/core addon/ui addon/ArenaCoach.lua addon/ArenaCoach.toc
rm -rf backend/tests bridge/tests ingest/tests

# В pyproject.toml убрать упоминания backend/tests, bridge/tests, ingest/tests
# из ruff.extend-exclude, mypy.exclude, pytest norecursedirs.
# Сделать вручную или sed-патч:
#   sed -i -E '/"(backend|bridge|ingest)\/tests"/d' pyproject.toml

echo "OK — устаревшие файлы удалены. Не забудь поправить pyproject.toml и закоммитить."
