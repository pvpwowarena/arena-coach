# Arena Coach — CLAUDE.md (контекст проекта для новых чатов)

> Последнее обновление: 2026-05-15
> Читай этот файл в начале каждого нового чата перед любой работой.

---

## Что это за проект

**WoW Arena Assistant** — система реал-тайм подсказок для 2v2/3v3 арены в **WoW: Burning Crusade Classic Anniversary** (клиент 2.4.3).

Игроки из вайтлиста получают советы прямо в Discord DM во время боя. Источник знаний — KB (база матчапов в Markdown), наполненная вручную из стримов/гайдов.

---

## Архитектура (текущая)

```
[WoW client + ArenaCoach addon (Lua)]
        │ пишет события в chat-frame с префиксом [AC]
        ▼
[arena-bridge.exe (Windows, Python → PyInstaller)]
        │ читает WoW chat log, нормализует события
        │ POST /v1/events  Bearer-токен
        ▼
[FastAPI backend (uvicorn, 127.0.0.1:8000)]
        ├── KB store (Markdown файлы + SQLite индекс)
        ├── Whitelist + Audit log (SQLite + Fernet шифрование)
        ├── LLM orchestrator (Anthropic API — опционально)
        └── Discord bot (discord.py slash-команды)
        ▼
[Discord DM / channel — подсказки игрокам]

Nginx (443 SSL) → proxy → FastAPI
                → static → /download страница + arena-bridge.exe
```

---

## VPS

| Параметр | Значение |
|---|---|
| IP | 77.239.120.150 |
| Домен | pvpwowarena.surprise4you.dev |
| ОС | Ubuntu 22.04 LTS |
| Python на VPS | **3.10** (не 3.11!) |
| Systemd сервисы | `arena-coach-api` (uvicorn :8000) + `arena-coach-bot` |
| Nginx | 1.18.0 — `listen 443 ssl;` без `http2` (не поддерживает `http2 on;`) |
| TLS | Let's Encrypt, certbot --nginx, автообновление через certbot.timer |
| Данные | `/var/lib/arena-coach/coach.db` (SQLite) |
| Конфиг | `/etc/arena-coach/api.env` (секреты) |
| Репо на VPS | `/opt/arena-coach/` |
| Venv | `/opt/arena-coach/.venv/` |
| Статика nginx | `/var/www/arena-coach/` (download.html, arena-bridge.exe) |
| Webmin | порт 10000, правило UFW открыто |

### Проверка работоспособности VPS
```bash
curl -s https://pvpwowarena.surprise4you.dev/health
# → {"status":"ok","uptime_s":...}

systemctl status arena-coach-api arena-coach-bot --no-pager
```

### Деплой на VPS
```bash
cd /path/to/arena-coach
ARENA_VPS_HOST=root@77.239.120.150 ./ops/scripts/deploy.sh
```

### api.env на VPS (структура)
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
- Layout репозитория, `.env.example`, список Discord-команд
- ADR-документы в `docs/decisions/`

### ✅ Phase 1 — База знаний + ingestion (DONE)
- Каноническая Markdown-схема KB-документа
- Глоссарий: `kb/glossary/abilities.json` + `kb/glossary/terms.md`
- Драфты матчапов в `kb/drafts/` (21 файл — RM и RP составы)
- Ingest CLI: `python -m arena_ingest paste --from-paste`
- Парсер глоссария: `ingest/arena_ingest/glossary_extract.py`
- **ВАЖНО: драфты в `kb/drafts/` не одобрены** — нет ни одного файла в `kb/matchups/`. Команда `/matchup` возвращает «нет данных» пока драфты не смёрджены.

### ✅ Phase 2 — Discord бот (DONE, работает на VPS)
Slash-команды:
- `/matchup our:<comp> vs:<comp>` — матчап из KB
- `/opener <comp> vs <comp>` — только опенер
- `/glossary <term>` — расшифровка термина
- `/list_comps` — все составы в KB
- `/source <slug>` — источники
- `/access add/remove/audit` — управление вайтлистом (только admin)

Баг исправлен: `/glossary` больше не показывает "None" для пустых полей.

### ✅ Phase 3 — Lua аддон (DONE, код есть)
Файлы в `addon/ArenaCoach/`:
- `Core.lua` — инициализация, namespace AC
- `Tracker.lua` — ARENA_OPPONENT_UPDATE, UNIT_AURA, COMBAT_LOG_EVENT_UNFILTERED
- `UI.lua` — StatusFrame (connected/idle)
- `ArenaCoach.toc` — TOC для TBC 2.4.3

Также дублирующие файлы в `addon/core/` и `addon/ui/` — надо разобрать дублирование.

**Статус аддона:** Код написан, но не тестировался в живой игре. Канал аддон→bridge: chat-frame с префиксом `[AC]`.

### 🔄 Phase 4 — Bridge + реал-тайм подсказки (ЧАСТИЧНО)
- `bridge/arena_bridge/` — пакет готов:
  - `chat_tail.py` — tail WoW chat log
  - `sv_tail.py` — tail SavedVariables (альтернатива)
  - `normalizer.py` — нормализация событий
  - `ws_client.py` — WebSocket клиент
  - `env_loader.py` — dotenv без зависимостей
  - `__main__.py` — CLI с `--env-file`, `--check-config`, авто-детект `bridge.env`
- `arena-bridge.spec` — PyInstaller onefile spec
- **НЕ собран** `arena-bridge.exe` — нужен первый тег `v0.1.0`

### ⏳ Phase 5 — CV/OCR (не начата)

---

## GitHub Actions

### `build-bridge-exe.yml`
- Триггер: `push tags v*` или `workflow_dispatch`
- Собирает `arena-bridge.exe` на `windows-latest` через PyInstaller
- Создаёт GitHub Release с бинарником
- **Деплоит `.exe` на VPS** (`/var/www/arena-coach/arena-bridge.exe`) по SSH
- Требует секрет `VPS_SSH_KEY` в настройках репозитория

### Секреты GitHub (нужно настроить)
- `VPS_SSH_KEY` — приватный ключ `/root/.ssh/id_ed25519` с VPS
- Публичный ключ должен быть в `/root/.ssh/authorized_keys` на VPS

### Выпустить первый релиз
```bash
cd arena-coach
git tag v0.1.0
git push origin v0.1.0
# → Actions соберёт .exe → задеплоит на VPS → /download/arena-bridge.exe заработает
```

---

## Структура репозитория

```
arena-coach/
├── addon/                      # Lua аддон (TBC 2.4.3)
│   ├── ArenaCoach/             # Основная папка аддона
│   │   ├── ArenaCoach.toc
│   │   ├── Core.lua
│   │   ├── Tracker.lua
│   │   └── UI.lua
│   ├── core/                   # Дубль — разобрать!
│   └── ui/                     # Дубль — разобрать!
├── backend/                    # FastAPI + discord.py
│   ├── arena_coach/
│   │   ├── __main__.py         # CLI: run-bot, gen-key, validate-kb
│   │   ├── api/app.py          # FastAPI create_app()
│   │   ├── bot/                # Discord бот
│   │   │   └── cogs/           # glossary, matchup, access, coach
│   │   ├── kb/                 # KB loader, render, retriever, schema
│   │   ├── access/             # Whitelist, audit, crypto (Fernet)
│   │   ├── orchestrator/       # Anthropic LLM клиент (Phase 4+)
│   │   └── shared/settings.py  # Pydantic Settings (env vars)
│   └── tests/unit/
├── bridge/                     # Windows bridge (.exe)
│   ├── arena_bridge/
│   ├── arena-bridge.spec       # PyInstaller
│   └── bridge.env.example
├── ingest/                     # KB ingestion CLI
│   └── arena_ingest/
├── kb/                         # База знаний
│   ├── drafts/                 # НЕ одобренные матчапы (21 файл)
│   ├── matchups/               # ПУСТО — нет одобренных матчапов!
│   ├── glossary/
│   │   ├── abilities.json
│   │   └── terms.md
│   └── compositions.json
├── ops/
│   ├── nginx/
│   │   ├── pvpwowarena.surprise4you.dev.conf
│   │   └── html/download.html
│   ├── systemd/
│   │   ├── arena-coach-api.service
│   │   └── arena-coach-bot.service
│   └── scripts/
│       ├── server-setup.sh     # Idempotent VPS setup
│       └── deploy.sh           # rsync + restart
├── docs/
│   ├── architecture.md
│   ├── decisions/              # ADR 0001-0003
│   └── phase-*.md
└── .github/workflows/
    ├── ci.yml                  # ruff + mypy + pytest
    └── build-bridge-exe.yml    # PyInstaller + VPS deploy
```

---

## Ключевые технические детали

### Python версии
- **Локально / CI:** Python 3.11
- **На VPS:** Python **3.10** (apt-installed). Код должен быть совместим с 3.10!

### CLI команды backend
```bash
python -m arena_coach run-bot        # запуск Discord бота
python -m arena_coach gen-key        # генерация Fernet ключа
python -m arena_coach validate-kb <path>  # валидация KB документов
# НЕТ команды db upgrade — Alembic запускается напрямую
```

### Alembic (БД миграции)
```bash
cd backend
alembic upgrade head
# или через env:
source /etc/arena-coach/api.env
alembic -c alembic.ini upgrade head
```

### KB документ — канонический формат
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
---

## Opener
...
## Alternative opener
...
## If enemy trinkets
...
## Common mistakes
...
## Key cooldowns to track
...
```

### Whitelist роли
- `viewer` — только KB read
- `player` — реал-тайм подсказки
- `admin` — мутация вайтлиста + аудит

### Критические ограничения
- Никакой автоматизации нажатий / input injection (ToS Blizzard)
- Только read-only телеметрия (chat log)
- Все матчап-советы только из KB со ссылкой на источник
- Audit log — append-only JSONL, никогда не редактировать

---

## Что нужно сделать (backlog)

### Срочно (блокирует игроков)
1. **Выпустить v0.1.0** — `git tag v0.1.0 && git push origin v0.1.0`
   - Actions соберёт .exe → задеплоит на VPS → `/download/arena-bridge.exe` заработает
2. **Одобрить хотя бы один матчап-драфт** — переместить из `kb/drafts/` в `kb/matchups/`
   - `/matchup` сейчас возвращает пустой результат
3. **Применить nginx патч на VPS** — корень (`/`) редиректит на `/download`, добавлен эндпоинт `/download/arena-bridge.exe`

### Среднесрочно
4. **Протестировать аддон в игре** — скопировать `addon/ArenaCoach/` в WoW Interface/AddOns/
5. **Разобрать дублирование аддона** — `addon/core/` vs `addon/ArenaCoach/`
6. **Phase 4 bridge интеграция** — проверить что bridge корректно читает chat-frame события от аддона
7. **Добавить ANTHROPIC_API_KEY** — сейчас заглушка `sk-ant-placeholder`

### Технический долг
8. `backend/__main__.py` не имеет команды `db upgrade` — добавить или задокументировать что использовать alembic напрямую
9. CI workflow `ci.yml` — проверить что работает с Python 3.10 (VPS версия)

---

## Nginx — важные нюансы

Текущий конфиг на VPS отличается от локального (certbot дописал SSL строки).
**Никогда не копировать локальный конфиг поверх VPS без проверки certbot-блоков.**

Для обновления nginx на VPS использовать `deploy.sh` + вручную добавлять только изменённые location-блоки, или патчить Python-скриптом.

Строки которые certbot добавил на VPS (не трогать):
```nginx
ssl_certificate     /etc/letsencrypt/live/pvpwowarena.surprise4you.dev/fullchain.pem;
ssl_certificate_key /etc/letsencrypt/live/pvpwowarena.surprise4you.dev/privkey.pem;
include             /etc/letsencrypt/options-ssl-nginx.conf;
ssl_dhparam         /etc/letsencrypt/ssl-dhparams.pem;
```

---

## Ссылки

- Сайт: https://pvpwowarena.surprise4you.dev
- Страница скачивания: https://pvpwowarena.surprise4you.dev/download
- Health check: https://pvpwowarena.surprise4you.dev/health
- GitHub repo: https://github.com/pvpwowarena/arena-coach (приватный)
- GitHub Secrets: https://github.com/pvpwowarena/arena-coach/settings/secrets/actions
