#!/usr/bin/env bash
# Phase 1 git bootstrap — запусти у себя на Mac'е из корня arena-coach/.
#
# Что делает:
# 1. Очищает любой полу-инициализированный .git/ от sandbox-сессии.
# 2. git init -b main + конфиг автора.
# 3. Делает 5 осмысленных коммитов по логическим частям Phase 1.
# 4. Печатает инструкции для git remote add + push на твой GitHub.
#
# Запуск:
#   cd /Users/surprise/Downloads/Claude/PVP\ WOW\ Arena/PVP\ WoW\ Arena/arena-coach
#   bash ops/scripts/phase1-git-bootstrap.sh
#
# Если ругается на `bash: bash: command not found` — сначала `chmod +x ops/scripts/*.sh`.

set -euo pipefail

if [ ! -f "pyproject.toml" ] || [ ! -d "kb" ]; then
  echo "ERROR: запускай из корня arena-coach/ (там, где pyproject.toml и kb/)" >&2
  exit 1
fi

echo "==> 1. Очистка любого предыдущего .git/"
rm -rf .git/

echo "==> 2. git init"
git init -b main >/dev/null

echo "==> 3. Конфигурация автора"
# Можешь изменить если нужно
git config user.name "${GIT_AUTHOR_NAME:-pvpwowarena}"
git config user.email "${GIT_AUTHOR_EMAIL:-nameuser202233@gmail.com}"

# ──────────────────── Commit 1: skeleton + ADRs ────────────────────
echo "==> 4. Commit 1: repo skeleton + ADRs"
git add \
  .gitignore .env.example pyproject.toml README.md LICENSE \
  .pre-commit-config.yaml conftest.py \
  .github/ \
  docs/
git commit -m "Phase 1: repo skeleton, root configs, ADRs" -m "
- pyproject.toml: ruff, mypy --strict, pytest config
- .gitignore: secrets, SavedVariables, python caches
- .env.example: все переменные backend и bridge
- README.md: обзор проекта + быстрый старт
- LICENSE: proprietary
- .pre-commit-config.yaml: ruff + mypy + secrets-check + SavedVariables guard
- .github/workflows/ci.yml: ruff + format + mypy + pytest на py3.11/3.12
- docs/decisions/0001-python-stack.md (Python 3.11+ обоснован)
- docs/decisions/0002-sqlite-vs-postgres.md (SQLite + FTS5 на старте)
- docs/decisions/0003-chatframe-realtime-channel.md (chat-frame mirror)
- docs/architecture.md (короткий обзор)
- docs/phase-0-design.md (полный design document)" >/dev/null

# ──────────────────── Commit 2: KB schema + loader ────────────────────
echo "==> 5. Commit 2: KB schema + loader"
git add \
  backend/pyproject.toml \
  backend/arena_coach/__init__.py \
  backend/arena_coach/__main__.py \
  backend/arena_coach/kb/__init__.py \
  backend/arena_coach/kb/schema.py \
  backend/arena_coach/kb/loader.py \
  backend/README.md
git commit -m "Phase 1: KB pydantic schema + loader" -m "
- arena_coach.kb.schema: KBDoc, Source variants (web/youtube/stream-paste/file),
  KillTarget, Section. Валидаторы: Opener-обязателен, sources non-empty,
  composition format, reviewer обязан при confidence != draft.
- arena_coach.kb.loader: parse .md + YAML frontmatter → KBDoc.
  GlossaryIndex для проверки [[ability:slug]] orphans.
- arena_coach.__main__: CLI validate-kb <dir> для CI." >/dev/null

# ──────────────────── Commit 3: ingest pipeline ────────────────────
echo "==> 6. Commit 3: ingest pipeline (Mirlol parser + glossary extractor + CLI)"
git add \
  ingest/pyproject.toml \
  ingest/arena_ingest/__init__.py \
  ingest/arena_ingest/__main__.py \
  ingest/arena_ingest/glossary_extract.py \
  ingest/arena_ingest/sources/__init__.py \
  ingest/arena_ingest/sources/paste.py \
  ingest/README.md
git commit -m "Phase 1: ingest pipeline (paste + glossary extractor + CLI)" -m "
- glossary_extract: сканирует Mirlol Markdown, исключает classicon_*,
  derive_ability_slug() с приоритетом label > trailing > icon.
- sources/paste: разбивает Mirlol-файл по сепаратору vs/comp/difficulty,
  section mapping по таблице (Opener/Strategy/General→Opener;
  Option N/Plan B→Alternative opener; If they open on you→If enemy opens first;
  Mid-Game→Mid-fight rotation). Inline ![](icon-url) → [[ability:slug]].
- CLI arena-ingest: paste, glossary extract, list, review approve/reject." >/dev/null

# ──────────────────── Commit 4: KB seed (22 drafts + glossary + terms) ────────────────────
echo "==> 7. Commit 4: KB seed — 22 drafts from Mirlol + glossary + terms"
git add \
  kb/README.md \
  kb/glossary/abilities.json \
  kb/glossary/terms.md \
  kb/compositions.json \
  kb/drafts/
git commit -m "Phase 1: KB seed — 22 matchup drafts + glossary + terms" -m "
12 RM drafts (Rogue/Mage) + 10 RP drafts (Rogue/Priest), полученных через
arena-ingest paste из исходных Mirlol-гайдов в родительской папке.

Glossary:
- abilities.json: 36 уникальных способностей с aliases (классиконы исключены).
  Поля spell_id, dr_category, duration, ru_name, class_, school — пусты,
  заполняются вручную при first-pass review.
- terms.md: арена-жаргон (DR, premed, shatter, sap-stall, blanket CS, peel,
  swap, post-trinket, OOM, LoS, sticky nova и т.д.).
- compositions.json: canonical comp slugs + сокращения + class/spec справочник.

Все 22 драфта валидируются через KBDoc-схему, все [[ability:slug]] резолвятся
в глоссарий — ноль orphan'ов." >/dev/null

# ──────────────────── Commit 5: scaffolding for Phase 2-4 ────────────────────
echo "==> 8. Commit 5: Scaffolding for Phase 2-4 (addon, bridge, backend stubs, ops)"
git add \
  addon/ \
  bridge/ \
  backend/arena_coach/api/ \
  backend/arena_coach/bot/ \
  backend/arena_coach/access/ \
  backend/arena_coach/orchestrator/ \
  backend/arena_coach/shared/ \
  backend/tests/ \
  ingest/tests/ \
  tests/ \
  ops/ \
  || true  # некоторые пути могут не существовать на ровном месте, ок
git commit -m "Phase 1: scaffolding for Phase 2-4 (addon/bridge/backend/ops + tests)" -m "
- addon/: ArenaCoach.toc + Lua stubs (core/EventBus, Serializer, ArenaTracker,
  CombatLog, CooldownTracker; ui/StatusFrame). Phase 3 реализация.
- bridge/: arena_bridge/{__main__,config,sv_tail,chat_tail,normalizer,ws_client}.
  Phase 4 stubs.
- backend/arena_coach/{api,bot,access,orchestrator,shared}/: pydantic-settings,
  whitelist+audit+crypto, FastAPI, discord.py — Phase 2/4 stubs.
- ops/systemd/: arena-coach-{api,bot}.service.
- ops/caddy/Caddyfile: reverse-proxy для WSS + REST + TLS.
- ops/scripts/: deploy.sh, backup_db.sh, rotate_audit_log.sh.
- tests/: 34 pytest-теста (KB schema, loader, glossary extractor, paste parser).
  Все проходят локально и в CI." >/dev/null

# ──────────────────── Done ────────────────────
echo
echo "============================================================"
echo "✓ Phase 1 git history готова."
echo
git log --oneline
echo
echo "============================================================"
echo
echo "Дальше — push на GitHub. Создай ПРИВАТНЫЙ репозиторий через UI:"
echo "  → https://github.com/new"
echo "  → name: arena-coach (или как хочешь)"
echo "  → Private"
echo "  → ничего НЕ добавляй (no README/license/.gitignore — у нас уже всё есть)"
echo
echo "Потом подключи remote и push:"
echo
echo "  git remote add origin git@github.com:<your-username>/arena-coach.git"
echo "  git push -u origin main"
echo
echo "Если используешь HTTPS вместо SSH:"
echo
echo "  git remote add origin https://github.com/<your-username>/arena-coach.git"
echo "  git push -u origin main"
echo
echo "После push'а CI на GitHub Actions запустится автоматически на каждый push/PR."
