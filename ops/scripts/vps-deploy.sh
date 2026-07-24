#!/usr/bin/env bash
# Arena Coach — VPS post-pull deploy (idempotent).
#
# Runs ON the VPS as root, invoked by CI (.github/workflows/ci.yml "deploy" job)
# right AFTER `git pull` on /opt/arena-coach. Mirrors the manual deploy documented
# in CLAUDE.md / ops/scripts/deploy.sh (minus rsync — code is already pulled).
#
# Steps: backend deps → DB migrations → static HTML → restart services → health.
# Every step is idempotent, so re-running is safe.
set -euo pipefail

REPO=/opt/arena-coach
VENV="$REPO/.venv"
DOMAIN="https://pvpwowarena.surprise4you.dev"

echo "==> system deps for voice (ffmpeg — idempotent, Phase 4.5)"
command -v ffmpeg >/dev/null 2>&1 || { apt-get update -qq && apt-get install -y -qq ffmpeg; }

echo "==> backend deps (idempotent)"
"$VENV/bin/pip" install -e "$REPO/backend" --quiet

echo "==> DB migrations (alembic direct — CLI has no 'db upgrade'; idempotent)"
cd "$REPO/backend"
"$VENV/bin/alembic" -c alembic.ini upgrade head 2>/dev/null \
  || ( set -a; . /etc/arena-coach/api.env 2>/dev/null; set +a; "$VENV/bin/alembic" -c alembic.ini upgrade head )
cd "$REPO"

echo "==> static HTML → /var/www/arena-coach"
cp -f "$REPO"/ops/nginx/html/*.html /var/www/arena-coach/
chown www-data:www-data /var/www/arena-coach/*.html

echo "==> restart services"
systemctl restart arena-coach-api.service arena-coach-bot.service

echo "==> health check (uvicorn boots for a couple seconds → retry)"
sleep 3
for i in 1 2 3 4 5; do
  if curl -fsS "$DOMAIN/health"; then
    echo "  <- deploy OK"
    exit 0
  fi
  echo "  ...health not ready (try $i/5), waiting"
  sleep 3
done
echo "ERROR: /health did not return OK after restart" >&2
exit 1
