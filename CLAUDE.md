# Arena Coach — CLAUDE.md (контекст проекта для новых чатов)

> Последнее обновление: 2026-05-15
> Читай этот файл в начале каждого нового чата перед любой работой.

---

## Что это за проект

**WoW Arena Assistant** — система реал-тайм подсказок для 2v2/3v3 арены в **WoW: Burning Crusade Classic Anniversary** (клиент 2.4.3).

Игроки из вайтлиста получают советы в Discord DM во время боя. Источник знаний — KB (база матчапов в Markdown), наполненная вручную из стримов/гайдов.

**Репо:** https://github.com/pvpwowarena/arena-coach — **публичный** (с 2026-05-15).

---

## Архитектура (актуальная)

```
[WoW client + ArenaCoach addon (Lua 2.4.3)]
        │ пишет события в chat-frame с префиксом [AC|TYPE|f1|f2|...]
        ▼
[arena-bridge.exe (Windows, PyInstaller onefile)]
        │ tail WoW Logs/Chat-YYYY-MM-DD.txt → нормализация → HTTPS POST /v1/events
        │ Bearer-токен аутентификация
        ▼
[Backend VPS: pvpwowarena.surprise4you.dev]
        ├── FastAPI (uvicorn, 127.0.0.1:8000) — systemd arena-coach-api
        ├── Discord bot (discord.py)           — systemd arena-coach-bot
        ├── KB store (Markdown matchups + in-memory KBIndex)
        ├── Whitelist + Audit log (SQLite + Fernet шифрование, append-only JSONL)
        └── LLM orchestrator (Anthropic API — опционально, сейчас заглушка)
        ▼
[Nginx 1.18 + TLS (Let's Encrypt)]
        ├── /              → /var/www/arena-coach/index.html
        ├── /download      → download.html (аддон + arena-bridge.exe)
        ├── /how-it-works  → how-it-works.html
        ├── /v1/           → FastAPI
        └── /health        → FastAPI
        ▼
[Discord DM — текстовые подсказки игрокам]
```

**Канал addon ⇄ bridge:** chat-frame с префиксом `[AC|...]` (см. ADR-0003). SavedVariables как realtime-канал отвергнут — пишутся только при /reload и logout.

---

## VPS

| Параметр | Значение |
|---|---|
| IP | 77.239.120.150 |
| Домен | pvpwowarena.surprise4you.dev |
| ОС | Ubuntu 22.04 LTS |
| Python на VPS | **3.10** (не 3.11!) |
| Systemd сервисы | `arena-coach-api` (uvicorn :8000) + `arena-coach-bot` |
| Nginx | 1.18.0 — `listen 443 ssl;` без `http2 on;` |
| TLS | Let's Encrypt, certbot --nginx, автообновление через certbot.timer |
| Данные | `/var/lib/arena-coach/coach.db` (SQLite) |
| Конфиг | `/etc/arena-coach/api.env` (секреты) |
| Репо на VPS | `/opt/arena-coach/` |
| Venv | `/opt/arena-coach/.venv/` |
| Статика nginx | `/var/www/arena-coach/` (index.html, download.html, how-it-works.html, arena-bridge.exe) |
| Webmin | порт 10000, правило UFW открыто |

### Проверка работоспособности
```bash
curl -s https://pvpwowarena.surprise4you.dev/health
# → {"status":"ok","uptime_s":...}

systemctl status arena-coach-api arena-coach-bot --no-pager
```

### Деплой
```bash
# Через Webmin terminal на VPS:
cd /opt/arena-coach
sudo -u arenacoach git pull --ff-only
cp ops/nginx/html/*.html /var/www/arena-coach/   # если статика менялась
cd backend && sudo -u arenacoach /opt/arena-coach/.venv/bin/alembic -c alembic.ini upgrade head
sudo systemctl restart arena-coach-api arena-coach-bot
```

Альтернатива с локальной машины:
```bash
ARENA_VPS_HOST=root@77.239.120.150 ./ops/scripts/deploy.sh
```

### api.env на VPS
```
DISCORD_BOT_TOKEN=...
DISCORD_GUILD_ID=...
ARENA_COACH_OWNER_DISCORD_IDS=...
ANTHROPIC_API_KEY=sk-ant-placeholder  # заглушка пока, LLM-фичи не работают
ARENA_COACH_FERNET_KEY=...
BRIDGE_BEARER_TOKEN=...
DATABASE_URL=sqlite+aiosqlite:////var/lib/arena-coach/coach.db
KB_PATH=/opt/arena-coach/kb
```

---

## Статус по фазам (май 2026)

### ✅ Phase 0 — Дизайн и скелет (DONE)
- Архитектурная диаграмма, data-model, OpenAPI sketch
- ADR в `docs/decisions/`

### ✅ Phase 1 — KB + ingestion (DONE)
- Каноническая Markdown-схема, Pydantic-валидация
- Глоссарий: `kb/glossary/abilities.json` + `kb/glossary/terms.md`
- 22 драфта в `kb/drafts/` (RM + RP составы)
- Ingest CLI: `python -m arena_ingest paste --from-paste`

### ✅ Phase 2 — Discord бот (DONE, работает на VPS)
Slash-команды:
- `/matchup our:<comp> vs:<comp>` — матчап из KB
- `/opener <comp> vs <comp>` — только опенер
- `/glossary <term>` — расшифровка термина
- `/list_comps` — все составы в KB
- `/source <slug>` — источники
- `/access add/remove/audit` — управление вайтлистом (только admin)

### ✅ Phase 3 — Lua аддон (DONE, код есть)
Файлы — **только `addon/ArenaCoach/`**:
- `ArenaCoach.toc` — TOC для TBC 2.4.3 (Interface 20400)
- `Core.lua` — namespace, SavedVariables-схема
- `Tracker.lua` — ARENA_OPPONENT_UPDATE, UNIT_AURA, COMBAT_LOG_EVENT_UNFILTERED, трекинг трикетов и CC
- `UI.lua` — StatusFrame

Канал в bridge: chat-frame с префиксом `[AC|...]`.

**Статус:** код написан, не тестировался в живой игре.

### 🔄 Phase 4 — Bridge + реал-тайм подсказки (ЧАСТИЧНО)
- `bridge/arena_bridge/` — пакет готов:
  - `chat_tail.py` — tail `WoW/Logs/Chat-YYYY-MM-DD.txt`, парсит `[AC|...]`
  - `sv_tail.py` — tail SavedVariables (резервный канал)
  - `normalizer.py` — нормализация событий в CanonicalEnvelope
  - `ws_client.py` / HTTPS-клиент — отправка на `/v1/events`
  - `env_loader.py` — dotenv без зависимостей
  - `__main__.py` — CLI с `--env-file`, `--check-config`, авто-детект `bridge.env`
- `arena-bridge.spec` — PyInstaller onefile spec
- **Pipeline на бэке:** `backend/arena_coach/orchestrator/pipeline.py` (подключён к `/v1/events`) — KB lookup → LLM hint (опционально) → Discord DM через REST
- **НЕ собран** `arena-bridge.exe` — нужен первый тег `v0.1.0` для запуска GitHub Actions

### ⏳ Phase 5 — CV/OCR (не начата)

---

## KB — как устроена и как работает

**Структура:**
```
kb/
├── matchups/      ← одобренные гайды (production-канон)
├── drafts/        ← черновики после ingest, до review (22 файла)
├── glossary/
│   ├── abilities.json   ← spell-id → {icon, duration, DR-category}
│   └── terms.md         ← опенер, шаттер, sap-stall, etc.
└── compositions.json
```

**Поведение индекса (`KBIndex.load`):**

`indexer.py` сканирует обе директории — `matchups/` и `drafts/` — и грузит их в один in-memory индекс. То есть `/matchup` и `/opener` **отвечают и по черновикам тоже**. Это намеренное решение для Phase 2: иначе бот стоял бы пустой, пока не одобришь руками 22 файла.

Когда придёт время разделить: или ввести `KB_INCLUDE_DRAFTS` env-flag, или явно промотировать драфты в `kb/matchups/` (перемещение файла + поле `last_reviewed`).

Loader корректно работает на пустом `matchups/` — `if matchups_dir.exists()` и graceful fallback.

**Канонический формат документа:**
```markdown
---
slug: rm-vs-warrior-rdruid
composition: rogue+mage
vs: warrior+resto-druid
expansion: tbc
difficulty: easy
kill_target: druid
sources:
  - { type: web, url: "https://..." }
last_reviewed: 2026-05-12
reviewer: <discord-id>
---

## Opener
Prose с inline [[ability:cheap-shot]].

## Alternative opener / If enemy trinkets / Common mistakes / Key cooldowns to track
...
```

---

## GitHub Actions

### `ci.yml`
Matrix `[3.10, 3.11, 3.12]`, ruff + mypy --strict + pytest. Job `kb-validation` валидирует `kb/drafts/*.md` против схемы на Python 3.10.

### `build-bridge-exe.yml`
- Триггер: `push tags v*` или `workflow_dispatch`
- Собирает `arena-bridge.exe` на `windows-latest` через PyInstaller
- Создаёт GitHub Release с бинарником
- Деплоит `.exe` на VPS (`/var/www/arena-coach/arena-bridge.exe`) по SSH

### Секреты GitHub
- `VPS_SSH_KEY` — приватный ключ для деплоя .exe на VPS

### Выпустить первый релиз
```bash
git tag v0.1.0
git push origin v0.1.0
# → Actions соберут .exe → задеплоят на VPS → /download/arena-bridge.exe заработает
```

---

## Структура репозитория

```
arena-coach/
├── addon/
│   ├── ArenaCoach/               # ← ЕДИНСТВЕННАЯ актуальная папка аддона
│   │   ├── ArenaCoach.toc
│   │   ├── Core.lua
│   │   ├── Tracker.lua
│   │   └── UI.lua
│   ├── INSTALL.md
│   └── README.md
├── backend/
│   ├── arena_coach/
│   │   ├── __main__.py           # CLI: validate-kb, run-bot, gen-key (НЕТ db upgrade!)
│   │   ├── api/                  # FastAPI app, routes/events.py
│   │   ├── bot/cogs/             # glossary, matchup, access, coach
│   │   ├── kb/                   # loader, indexer, retriever, schema, render
│   │   ├── access/               # whitelist, audit, Fernet crypto
│   │   ├── orchestrator/
│   │   │   ├── pipeline.py       # ← live, подключён к /v1/events
│   │   │   └── client.py         # placeholder, нигде не используется
│   │   └── shared/settings.py
│   └── alembic.ini, alembic/
├── bridge/
│   ├── arena_bridge/             # chat_tail, sv_tail, normalizer, ws_client
│   └── arena-bridge.spec         # PyInstaller
├── ingest/
│   └── arena_ingest/             # paste-parser, glossary-extract, CLI
├── kb/
│   ├── matchups/                 # одобренные (сейчас пусто)
│   ├── drafts/                   # 22 черновика — индекс грузит их тоже
│   ├── glossary/
│   └── compositions.json
├── tests/                        # ← единственный test-набор (113 тестов)
├── conftest.py                   # общие фикстуры
├── ops/
│   ├── nginx/
│   │   ├── pvpwowarena.surprise4you.dev.conf   # ⚠ НЕ копировать поверх VPS!
│   │   └── html/                 # index, download, how-it-works
│   ├── systemd/
│   └── scripts/
│       ├── server-setup.sh       # Idempotent VPS setup (Python 3.10, alembic напрямую)
│       ├── deploy.sh             # rsync + restart
│       └── cleanup-legacy.sh     # safety net (легаси уже удалён)
├── docs/
│   ├── architecture.md
│   ├── decisions/                # ADR 0001-0003
│   ├── phase-0-design.md
│   ├── phase-1.5-translation-plan.md   # [PLANNED]
│   ├── phase-4.5-voice.md              # [PLANNED]
│   ├── investor-brief.md               # [ARCHIVED — pitch deck]
│   └── strategy-data-acquisition.md
├── pyproject.toml                # workspace marker + ruff/mypy/pytest config
└── .github/workflows/            # ci.yml, build-bridge-exe.yml
```

**Легаси удалён (май 2026):** Phase 0 stub-папки `addon/core/`, `addon/ui/`, корневые `addon/ArenaCoach.{lua,toc}`, легаси `backend/tests/`, `bridge/tests/`, `ingest/tests/` — физически снесены. Скрипт `ops/scripts/cleanup-legacy.sh` оставлен как safety net (идемпотентный, если запустить ещё раз — ничего не найдёт).

---

## Ключевые технические детали

### Python версии
- **Локально / CI:** matrix 3.10, 3.11, 3.12
- **На VPS:** Python **3.10** (apt-installed Ubuntu 22.04). Код должен работать на 3.10!
- Использовать `from __future__ import annotations` для PEP-604 синтаксиса.

### CLI команды backend
```bash
python -m arena_coach run-bot            # Discord-бот
python -m arena_coach gen-key            # Fernet-ключ
python -m arena_coach validate-kb <path> # валидация KB-документов
# НЕТ команды db upgrade — alembic запускается напрямую (см. ниже)
```

### Alembic (БД миграции)
```bash
cd backend
alembic -c alembic.ini upgrade head
# на VPS:
cd /opt/arena-coach/backend
sudo -u arenacoach /opt/arena-coach/.venv/bin/alembic -c alembic.ini upgrade head
```

### Тесты
```bash
# Из корня репо:
python -m pytest tests/ -v
# 113 passed in ~1s
```
Конфиг в `pyproject.toml` (`testpaths=tests`, `asyncio_mode=auto`). `conftest.py` в корне даёт общие фикстуры (`kb_dir`, `fixtures_dir`, `mirlol_rm_file`, etc.).

### Whitelist роли
- `viewer` — только KB read
- `player` — реал-тайм подсказки
- `admin` — мутация вайтлиста + аудит

### Жёсткие правила
- Никакой автоматизации нажатий / input injection (ToS Blizzard)
- Только read-only телеметрия (chat log)
- Все матчап-советы только из KB со ссылкой на источник
- Audit log — append-only JSONL, никогда не редактировать

---

## Nginx — критическое правило

⚠ **НЕ копировать `ops/nginx/pvpwowarena.surprise4you.dev.conf` поверх `/etc/nginx/sites-available/*` на VPS!**

Certbot уже вписал в боевой конфиг SSL-блоки:
```nginx
ssl_certificate     /etc/letsencrypt/live/pvpwowarena.surprise4you.dev/fullchain.pem;
ssl_certificate_key /etc/letsencrypt/live/pvpwowarena.surprise4you.dev/privkey.pem;
include             /etc/letsencrypt/options-ssl-nginx.conf;
ssl_dhparam         /etc/letsencrypt/ssl-dhparams.pem;
```

В локальной версии файла они закомментированы (чтобы `nginx -t` локально не падал). Прямое `cp` затрёт SSL и сайт ляжет.

Безопасный путь: обновлять только location-блоки руками, либо `deploy.sh` rsync-ает только статику в `/var/www/arena-coach/`, не трогая `/etc/nginx/`.

---

## Что нужно сделать (backlog)

### Срочно (блокирует игроков)
1. **Выпустить v0.1.0** — `git tag v0.1.0 && git push origin v0.1.0`
   - Actions соберут .exe → задеплоят на VPS → `/download/arena-bridge.exe` заработает
2. **Протестировать аддон в живой игре** — скопировать `addon/ArenaCoach/` в WoW Interface/AddOns/, зайти на арену, проверить что в `Logs/Chat-*.txt` появляются `[AC|...]` строки.
3. **Phase 4 интеграция end-to-end** — bridge запустить против аддона, проверить что POST /v1/events доходят и Discord DM приходит.

### Среднесрочно
4. Добавить настоящий `ANTHROPIC_API_KEY` (сейчас заглушка `sk-ant-placeholder` — LLM-hint не работает, pipeline отправляет KB-текст напрямую).
5. Промотировать драфты в `matchups/` или ввести `KB_INCLUDE_DRAFTS` env-flag.

---

## Ссылки

- Сайт: https://pvpwowarena.surprise4you.dev
- Скачать: https://pvpwowarena.surprise4you.dev/download
- Health: https://pvpwowarena.surprise4you.dev/health
- GitHub: https://github.com/pvpwowarena/arena-coach (публичный)
- GitHub Secrets: https://github.com/pvpwowarena/arena-coach/settings/secrets/actions
