#!/usr/bin/env bash
# Arena Coach — deploy script
# Rsync код на VPS и перезапускает оба сервиса (API + Bot).
#
# Usage:
#   ARENA_VPS_HOST=root@77.239.120.150 ./ops/scripts/deploy.sh
#   # или если уже добавлен SSH-alias:
#   ARENA_VPS_HOST=arenacoach-vps ./ops/scripts/deploy.sh

set -euo pipefail

VPS_HOST="${ARENA_VPS_HOST:?ERROR: set ARENA_VPS_HOST=user@host}"
REPO_ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
VENV="/opt/arena-coach/.venv"

echo "==> rsync $REPO_ROOT → $VPS_HOST:/opt/arena-coach/"
rsync -av --delete \
  --exclude='.venv' \
  --exclude='__pycache__' \
  --exclude='.pytest_cache' \
  --exclude='.mypy_cache' \
  --exclude='.ruff_cache' \
  --exclude='.git' \
  --exclude='*.pyc' \
  --exclude='*.db' \
  --exclude='*.db-journal' \
  --exclude='kb/drafts/' \
  --exclude='audit.jsonl' \
  "$REPO_ROOT/" \
  "$VPS_HOST:/opt/arena-coach/"

echo "==> Обновляю зависимости + миграции + перезапуск сервисов..."
ssh "$VPS_HOST" 'bash -s' <<REMOTE
set -euo pipefail
cd /opt/arena-coach

# Обновляем зависимости backend
$VENV/bin/pip install --upgrade pip --quiet
$VENV/bin/pip install -e backend --quiet

# Применяем DB миграции (idempotent)
cd backend
$VENV/bin/python -m arena_coach db upgrade 2>/dev/null || \
  (source /etc/arena-coach/api.env 2>/dev/null && $VENV/bin/python -m arena_coach db upgrade)
cd ..

# Обновляем /download страницу
sudo cp /opt/arena-coach/ops/nginx/html/download.html /var/www/arena-coach/download.html
sudo chown www-data:www-data /var/www/arena-coach/download.html

# Перезапускаем оба сервиса
sudo systemctl restart arena-coach-api.service arena-coach-bot.service

# Короткий статус
echo ""
echo "── Статус сервисов ──"
sudo systemctl status arena-coach-api.service --no-pager -l | head -12
echo ""
sudo systemctl status arena-coach-bot.service --no-pager -l | head -12
REMOTE

echo ""
echo "==> deploy done ✓"
echo "    API:      https://pvpwowarena.surprise4you.dev/health"
echo "    Download: https://pvpwowarena.surprise4you.dev/download"
