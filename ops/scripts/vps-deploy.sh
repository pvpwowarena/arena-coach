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

echo "==> backend deps (idempotent)"
"$VENV/bin/pip" install -e "$REPO/backend" --quiet

echo "==> DB migrations (alembic direct — CLI has no 'db upgrade'; idempotent)"
# Прод-инцидент 30.07.2026. Здесь была «тихая» первая попытка:
#   alembic upgrade head 2>/dev/null || ( . api.env; alembic upgrade head )
# Без api.env переменной DATABASE_URL нет, а дефолт в settings — ОТНОСИТЕЛЬНЫЙ путь
# (sqlite:///./coach.db). Alembic создавал и честно мигрировал файл
# /opt/arena-coach/backend/coach.db, выходил с кодом 0, фолбэк не срабатывал — и
# боевая БД в /var/lib оставалась без миграции. Вся диагностика ушла в /dev/null,
# а прод получил 500 на каждый /v1/events (no such column: combat_text).
# Теперь: URL читаем ВСЕГДА и заранее, вывод НЕ глушим, а относительный путь к БД
# считаем ошибкой конфигурации, а не поводом молча мигрировать не туда.
#
# api.env НЕ исполняем (`. api.env`): это systemd EnvironmentFile, а не shell-скрипт —
# значение с `(`, `#` или пробелом валит sourcing синтаксической ошибкой. Под `set -e`
# это убивало бы деплой, а с `2>/dev/null` (как было) тихо оставляло URL пустым — то
# есть ровно та ловушка, из которой инцидент и вырос. Берём одну строку скриптом,
# покрытым тестом (`tests/test_deploy_db_url.py`); секреты в окружение не попадают.
API_ENV=/etc/arena-coach/api.env
DATABASE_URL="$("$REPO/ops/scripts/read-db-url.sh" "$API_ENV")"
export DATABASE_URL
case "$DATABASE_URL" in
  sqlite*:////*) : ;;                 # sqlite с АБСОЛЮТНЫМ путём — то, что нужно
  sqlite*)                            # sqlite:///./coach.db и подобное — ловушка
    echo "ERROR: DATABASE_URL='$DATABASE_URL' — относительный путь к sqlite." >&2
    echo "       Нужен абсолютный: sqlite+aiosqlite:////var/lib/arena-coach/coach.db" >&2
    exit 1 ;;
  *) : ;;                             # не sqlite (postgres и т.п.) — путь не при чём
esac

echo "    БД: $DATABASE_URL"
cd "$REPO/backend"
echo "    ревизия до:"
"$VENV/bin/alembic" -c alembic.ini current
"$VENV/bin/alembic" -c alembic.ini upgrade head || {
  # Вторая половина инцидента 30.07.2026: боевую БД создал `Base.metadata.create_all`
  # при старте приложения, поэтому таблицы есть, а `alembic_version` НЕТ. Alembic в
  # таком случае идёт с 0001 и падает на «table whitelist_entries already exists».
  # `create_all` при этом создаёт только ОТСУТСТВУЮЩИЕ таблицы и никогда не меняет
  # существующие — отсюда и пропавшая колонка player_settings.combat_text.
  echo "" >&2
  echo "ERROR: alembic upgrade не прошёл." >&2
  echo "  Если ошибка вида 'table ... already exists' — БД не зарегистрирована в alembic" >&2
  echo "  (нет alembic_version, её создал create_all). Разово, на ВПС:" >&2
  echo "    alembic -c alembic.ini stamp 0002 && alembic -c alembic.ini upgrade head" >&2
  echo "  stamp именно 0002, а не 0004: тогда 0003/0004 создадут свои таблицы, если их нет," >&2
  echo "  а если есть — самопропустятся guard'ами." >&2
  exit 1
}
echo "    ревизия после:"
"$VENV/bin/alembic" -c alembic.ini current
cd "$REPO"

echo "==> static HTML → /var/www/arena-coach"
cp -f "$REPO"/ops/nginx/html/*.html /var/www/arena-coach/

echo "==> status page (живой статус KB/прода) → /var/www/arena-coach/status.html"
# Не валим деплой, если генератор упал — страница статуса не должна блокировать прод.
"$VENV/bin/python" "$REPO/tools/gen_status_page.py" -o /var/www/arena-coach/status.html \
  || echo "WARN: status page generation failed — /status.html не обновлён" >&2
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
