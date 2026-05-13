#!/usr/bin/env bash
# Fix-CI: прогоняет ruff format + ruff check --fix на всём проекте,
# показывает оставшиеся ошибки mypy и pytest, помогает довести CI до зелёного.
#
# Запуск:
#   bash ops/scripts/fix-ci.sh

set -euo pipefail

if [ ! -f "pyproject.toml" ] || [ ! -d "kb" ]; then
  echo "ERROR: запускай из корня arena-coach/" >&2
  exit 1
fi

echo "==> 1. Установка тулинга (если ещё не)"
pip3 install --quiet --upgrade ruff mypy pytest pytest-asyncio types-PyYAML pydantic PyYAML --break-system-packages 2>&1 | tail -3 || true

echo
echo "==> 2. Ruff format (фиксит форматирование автоматом)"
python3 -m ruff format .

echo
echo "==> 3. Ruff check --fix (фиксит автофиксимые lint-ошибки)"
python3 -m ruff check --fix .

echo
echo "==> 4. Что осталось из ruff (если что-то осталось — нужен ручной фикс)"
python3 -m ruff check . || true

echo
echo "==> 5. Mypy --strict (показывает оставшиеся type-ошибки)"
PYTHONPATH=backend:bridge:ingest python3 -m mypy backend bridge ingest || true

echo
echo "==> 6. Pytest"
PYTHONPATH=backend:bridge:ingest python3 -m pytest -q --tb=short || true

echo
echo "============================================================"
echo "Если ruff/mypy/pytest всё зелёное — закоммить фикс:"
echo
echo "  git add -A"
echo '  git commit -m "Phase 1: ruff format + lint fixes"'
echo "  git push"
echo
echo "После push'а CI на GitHub проигрывает заново."
