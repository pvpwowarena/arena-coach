#!/usr/bin/env bash
# Phase 2 deploy script. Запускается локально, rsync'ит код на VPS и перезапускает сервисы.
#
# Usage:
#   ARENA_VPS_HOST=user@host ./ops/scripts/deploy.sh

set -euo pipefail

VPS_HOST="${ARENA_VPS_HOST:?ERROR: set ARENA_VPS_HOST=user@host}"
REPO_ROOT="$(cd "$(dirname "$0")/../.." && pwd)"

echo "==> rsync $REPO_ROOT → $VPS_HOST:/opt/arena-coach/"
rsync -av --delete \
  --exclude='.venv' \
  --exclude='__pycache__' \
  --exclude='.pytest_cache' \
  --exclude='.mypy_cache' \
  --exclude='.ruff_cache' \
  --exclude='.git' \
  --exclude='*.pyc' \
  --exclude='kb/drafts/' \
  "$REPO_ROOT/" \
  "$VPS_HOST:/opt/arena-coach/"

echo "==> reinstall deps + migrate + restart"
ssh "$VPS_HOST" 'bash -s' <<'REMOTE'
set -euo pipefail
cd /opt/arena-coach
source .venv/bin/activate
pip install --upgrade pip
pip install -e backend
# Применяем миграции (idempotent — если уже на head, ничего не делает)
cd backend && alembic upgrade head && cd ..
sudo systemctl restart arena-coach-bot.service
sudo systemctl status arena-coach-bot.service --no-pager | head -20
REMOTE

echo "==> deploy done"
