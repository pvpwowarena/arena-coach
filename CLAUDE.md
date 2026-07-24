# Arena Coach — CLAUDE.md (контекст проекта для новых чатов)

> Последнее обновление: 2026-07-24
> Читай этот файл в начале каждого нового чата перед любой работой.
> **Живые цифры KB** (драфты/гипотезы/покрытие) — в `docs/NEXT-SESSION-HANDOFF.md` и `docs/COVERAGE.md`, не здесь (этот файл — про архитектуру/инфру).

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
        │ (v0.2.0: ARENA_START шлёт и союзников; форс-флаш чат-лога LoggingChat toggle)
        ▼
[arena-bridge (Windows .exe + macOS arm64, PyInstaller onefile)]
        │ tail WoW Logs/WoWChatLog.txt ИЛИ Chat-YYYY-MM-DD.txt (автодетект, v0.3.0)
        │ → нормализация → HTTPS POST /v1/events, Bearer-токен аутентификация
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

**Realtime-канал (Phase 4.2, 2026-07-23):** bridge читает **COMBAT-лог**
(`Logs/WoWCombatLog-MMDDYY_HHMMSS.txt`, автодетект свежего) и сам собирает события:
ARENA_START по ауре Arena Preparation (32727/32728), классы игроков из кастов
(re-emit при уточнении), TRINKET/ABILITY по spell id. Причина: **chat-лог в
Anniversary-клиенте не флашится до полного выхода из игры** (буфер ~48КБ,
LoggingChat(false→true) — no-op; проверено живым тестом), combat-лог флашится в бою.
Аддон 0.2.2 включает LoggingCombat при логине. Chat-frame канал `[AC#...]`
(ADR-0003, разделитель `#` с 0.2.1 — «|» запрещён клиентом) остаётся легаси-режимом
(`--no-combat-log`); SavedVariables как realtime отвергнуты (только /reload и logout).

**Имя chat-лога (v0.3.0):** стандартно `/chatlog` пишет в `Logs/WoWChatLog.txt` (не `Chat-YYYY-MM-DD.txt`, как предполагал ADR-0003). Bridge следит за обоими кандидатами и выбирает растущий. Клиент буферизует запись → аддон форс-флашит `LoggingChat(false→true)` после критических событий (отключается `/ac flush off`).

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
# Phase 4.5 (опционально) — голосовые подсказки. 0/отсутствует = выкл.
# Задать ID Discord voice-канала команды, чтобы включить TTS-подсказки:
# DISCORD_VOICE_CHANNEL_ID=123456789012345678
```

---

## Статус по фазам (май 2026)

### ✅ Phase 0 — Дизайн и скелет (DONE)
- Архитектурная диаграмма, data-model, OpenAPI sketch
- ADR в `docs/decisions/`

### ✅ Phase 1 — KB + ingestion (DONE)
- Каноническая Markdown-схема, Pydantic-валидация
- Глоссарий: `kb/glossary/abilities.json` + `kb/glossary/terms.md`
- Драфты в `kb/drafts/` (RM + RP составы; живой счётчик — см. handoff/COVERAGE)
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
- `Tracker.lua` — ARENA_OPPONENT_UPDATE, UNIT_AURA, COMBAT_LOG_EVENT_UNFILTERED, трекинг тринкетов и CC
- `UI.lua` — StatusFrame

Канал в bridge: chat-frame с префиксом `[AC|...]`.

**v0.2.0 (2026-07-11):** `ARENA_START` шлёт 4-е поле — союзники (игрок первым, для
таргетирования советов); повторный emit при выходе врага из стелса (с дедупом);
bracket через `GetBattlefieldStatus` (teamSize) вместо подсчёта юнитов;
форс-флаш чат-лога (`LoggingChat(false→true)`, дебаунс 1с) + `/ac flush on|off`.

**Статус:** код написан, не тестировался в живой игре.

### 🔄 Phase 4 — Bridge + реал-тайм подсказки (ЧАСТИЧНО)
- `bridge/arena_bridge/` — пакет готов:
  - `chat_tail.py` — tail `WoW/Logs/Chat-YYYY-MM-DD.txt`, парсит `[AC|...]`
  - `sv_tail.py` — tail SavedVariables (резервный канал)
  - `normalizer.py` — нормализация событий в CanonicalEnvelope
  - `ws_client.py` / HTTPS-клиент — отправка на `/v1/events`
  - `env_loader.py` — dotenv без зависимостей
  - `__main__.py` — CLI с `--env-file`, `--check-config`, авто-детект `bridge.env`
- `arena-bridge.spec` — PyInstaller onefile spec, **кросс-платформенный** (Windows .exe + macOS arm64 binary, см. секцию GitHub Actions ниже).
- **Pipeline на бэке:** `backend/arena_coach/orchestrator/pipeline.py` (подключён к `/v1/events`) — KB lookup → LLM hint (опционально) → Discord DM через REST
- **Релизы собраны:** теги `v0.1.0`…`v0.2.0` выпущены, GitHub Actions собрал `arena-bridge.exe` (Windows) + `arena-bridge-macos-arm64.tar.gz` (macOS). `v0.2.0` = HEAD. (Старый пункт «выпустить v0.1.0» закрыт.)
- **Аддон починен (2026-06-05):** автозапуск `LoggingChat(true)` при `PLAYER_LOGIN` — без него whisper-to-self не попадал в `Logs/Chat-*.txt`, bridge не видел событий. Добавлена `/ac test` — self-test канала без арены. Версия аддона → `0.1.1`.
- **Серверная цепочка проверена без живой игры:** `tools/e2e_dryrun.py` (synthetic Chat-log → bridge → backend → DM, статусы зелёные). Живой тест-гайд (Mac arm64 + Windows): `docs/TESTING.md`.
- ✅ **Phase 4.1 ПОЧИНЕНА (2026-07-11, v0.3.0):** матчинг по базовым КЛАССАМ врагов
  (`KBIndex.find_by_classes` + `comp_to_classes`: `holy-paladin`→`paladin`) с фильтром
  по нашему составу (из allies аддона 0.2.0 или `$BRIDGE_OUR_COMP`). Спек с ворот не
  виден → кандидатов может быть несколько: DM показывает основной + альтернативы.
  DM на ARENA_START: опенер + килл-таргет + сложность, таргетировано под класс игрока
  (`player_class` = allies[0]). In-fight: TRINKET + ключевые дефы (`_ABILITY_HINT_KEYS`:
  evasion/ice block/bubble/wall/…) с троттлингом `HintThrottle` (20с интервал,
  60с на повтор ключа). CC-касты намеренно не хинтятся. Новый статус: `throttled`.
- **Bridge v0.3.0:** автодетект `WoWChatLog.txt`/`Chat-*.txt` (см. выше), устойчивость
  к усечению файла и оборванным строкам, `utf-8-sig` для bridge.env (BOM Блокнота),
  `$BRIDGE_OUR_COMP`/`--our-comp` fallback. Windows-ревью: `docs/TESTING.md` (внизу).
- **macOS поддержка (MVP, май 2026):** Apple Silicon arm64 unsigned binary, .tar.gz с sample env-файлом и инструкцией по обходу Gatekeeper. Apple Developer signing/notarization отложены — добавим если выйдем за пределы 5-10 юзеров. Intel-mac сборка пока не делается.

### ✅ Phase 4.2 — Combat-лог канал (2026-07-23, v0.4.0)
Живой тест показал: chat-лог не флашится до выхода из игры → realtime через
whisper-to-self невозможен. Решение — bridge парсит combat-лог напрямую:
- `bridge/arena_bridge/combat_tail.py`: `CombatTailer` (tail свежего
  `WoWCombatLog*.txt` по mtime, переключение на новее) + `CombatInterpreter`
  (CLEU → те же AC-payload строки → существующий `normalize_raw`, backend не тронут).
- Границы матча: аура Arena Preparation — APPLIED=prep-фаза (копим свою команду,
  bracket по её размеру), REMOVED=ворота → ARENA_START. ARENA_END: 90с тишины
  hostile-активности или новая prep-фаза.
- Классы обеих команд из кастов (`SPELL_TO_CLASS`, сигнатурные спеллы TBC) →
  re-emit ARENA_START с уточнением (session id сохраняется, backend обновляет матч).
  Расы неизвестны → `CLASS/UNKNOWN`. Рекомендуется `BRIDGE_OUR_COMP` как fallback.
- TRINKET/ABILITY: зеркала таблиц аддона (TRINKET_IDS/TRACKED_SPELLS), дедуп
  cast+aura 5с. Работает и в скирмише (prep-аура там есть).
- Аддон 0.2.2: `EnsureCombatLogging()` при логине + расширен `/ac log`.
- Chat-канал в combat-режиме ОТКЛЮЧЁН (иначе при выходе из клиента буфер выплюнет
  пачку устаревших [AC#...]). Легаси: `--no-combat-log` / `BRIDGE_COMBAT_LOG=0`.
- Тесты: `tests/test_bridge_combat_tail.py`; E2E onefile
  с синтетическим combat-логом зелёный.

**v0.4.1 (2026-07-23, разбор первого живого скирмиша — канал сработал E2E,
реальные DM в Discord!):** шумоподавление по итогам реального лога:
1. Ростер врагов капится размером команды (на воротах): **ордынцы из открытого
   мира — тоже hostile player (0x548)** и после матча записывались во «врагов»
   (Zonof с Flare → «HUNTER/UNKNOWN» в DM) и бесконечно продлевали сессию.
   Теперь: ростер полон → чужие hostile игноряться и НЕ обновляют quiet-таймер.
2. Re-emit ARENA_START только при изменении состава ВРАГОВ: раскрытие класса
   союзника меняло payload, но DM показывает только врагов → выглядело как
   спам дублей «Арена началась».
3. Spell-таблицы пополнены id из реального лога: Lifebloom 33763, Regrowth
   26980, Mangle(Cat) 33983, Bash 8983, Dire Bear 9634, Fel Armor 28189,
   Flare 1543, Wound Poison 27188, Chain Heal 25423, Summon Imp 688.
Тесты: 156 (13 combat-канал).

### ✅ Phase 4.3 — Постматч-анализ (2026-07-24)
После `ARENA_END` бот шлёт игроку DM-разбор боя. `orchestrator/postmatch.py`:
- `MatchRecorder` копит таймлайн всех TRINKET/ABILITY врагов (per player_name,
  **не** session_id — bridge ≤0.4.1 сбрасывает сессию до ARENA_END-envelope);
  запись — ДО хинт-фильтров, поэтому CC-касты (в реалтайме не хинтятся) попадают
  в разбор. Кап 300 событий/матч, TTL 2ч, ≤32 открытых записей.
- `build_postmatch_report`: тринкеты с таймстампами (мм:сс от ворот), дефы,
  CC агрегатом, сравнение с KB (kill_target, «If enemy trinkets», «Common mistakes»).
- Фикс bridge `normalizer.py`: ARENA_END-envelope теперь собирается ДО
  `session.end_session()` — уносит session_id+match (иначе backend не привязал бы
  конец к матчу). Тесты: `tests/test_postmatch.py` (27).

### ✅ Phase 4.4 — Автообновление моста/аддона (2026-07-24, bridge 0.5.0)
Мост на старте (до демона, best-effort): читает latest GitHub Release,
раскладывает свежий `ArenaCoach.zip` в `Interface/AddOns/` (staging → бэкап
`.bak` → rename, анти-traversal, нормализация backslash-путей PowerShell) и
уведомляет о новой версии моста (self-replace бинаря НЕ делаем — сборки не
подписаны). Любой сбой (офлайн/битый zip) не мешает запуску. Отключение:
`--no-update` / `BRIDGE_AUTO_UPDATE=0`. `bridge/arena_bridge/updater.py`,
тесты: `tests/test_bridge_updater.py` (21).

### ✅ Phase 4.5 — Голосовые подсказки (2026-07-24)
Бот в Discord voice + TTS (edge-tts, RU-голос). `bot/voice.py`:
- `VoiceManager` (singleton/guild): очередь коротких фраз, троттлинг 8с, TTL 15с,
  дедуп 10с, LRU-кэш TTS 256, в пустой канал не заходит, отключается по простою.
- Короткая RU-фраза строится ОТДЕЛЬНО (`orchestrator/voice_phrases.py`, ≤8 слов,
  сленг «айсблок/бабл/клок»), не режется из текстового hint.
- Канал api→bot: POST `/speak` на 127.0.0.1 (voice живёт в bot-процессе,
  pipeline — в api). Bearer = `BRIDGE_BEARER_TOKEN`.
- Per-player `/coach voice on|off|only` → SQLite `player_settings` (миграция 0002).
- **Включается только если `DISCORD_VOICE_CHANNEL_ID` задан в api.env** (default 0 =
  выкл, деплой ничего не меняет). Нужен `ffmpeg` (ставит `vps-deploy.sh`) + PyNaCl.
- Тесты: `tests/test_voice.py` (30). Docs: `docs/phase-4.5-voice.md`.

### ✅ Phase 4.6 — Локальный персональный голос (2026-07-24, bridge 0.6.0)
Каждый игрок слышит ТОЛЬКО свои подсказки локально, через системный TTS на своей
машине — без Discord voice-канала, приватно, с минимальной задержкой. Добавочный
канал: Discord-голос (4.5) и текстовые DM он НЕ заменяет.
- **Обратный канал бэкенд→мост** (мост был односторонним): backend держит
  per-player очередь фраз в памяти (`orchestrator/hint_queue.py`: TTL 10с —
  устаревшая подсказка в бою вредна; кап на игрока и на число игроков; часы
  инъектируются). Pipeline на каждый hint кладёт ТУ ЖЕ короткую фразу
  (`voice_phrases.py`), что и Discord-голос, под `player_name`; `voice_mode='off'`
  → не кладёт. Это ДОБАВОЧНЫЙ канал: на решение о тексте/Discord-голосе не влияет
  (backend не знает, реально ли мост поллит и озвучивает — суппресить текст по
  факту постановки в очередь опасно, игрок остался бы ни с чем).
- **Эндпоинт** `GET /v1/hints?player=<name>` (`api/routes/events.py`): тот же
  общий bearer, идентификация игрока по параметру `player` (та же модель доверия,
  что у POST /v1/events по `player_name`); возвращает и вычищает свежие фразы
  игрока, протухшие по TTL дропает.
- **Мост**: фоновый asyncio-поллер рядом с тейлером (`bridge/arena_bridge/hint_poller.py`),
  раз в ~1с `GET /v1/hints` по своему `BRIDGE_PLAYER_NAME` (`EventClient.get_hints`),
  каждую свежую фразу → локальный TTS. Локальный дедуп (окно 6с), чтобы речь не
  наслаивалась. Речь сериализуется (await на проговаривание).
- **Локальный TTS** (`bridge/arena_bridge/local_tts.py`): системный синтез по
  `sys.platform` — macOS `say -v Milena` (лениво резолвит RU-голос из `say -v ?`,
  иначе дефолт), Windows PowerShell `System.Speech` (RU через SelectVoiceByHints,
  иначе дефолт), Linux `espeak-ng`/`espeak`, иначе no-op. Через asyncio-subprocess,
  неблокирующе; нет бинаря/ошибка запуска → тихий no-op (мост не падает). БЕЗ новых
  Python-зависимостей и БЕЗ интернета — PyInstaller-бинарь не пухнет, hiddenimports
  не трогаем (в отличие от edge-tts из 4.5).
- **Конфиг**: `BRIDGE_LOCAL_VOICE` (env, default 1) + `--local-voice/--no-local-voice`;
  `--hint-poll-interval` (env `BRIDGE_HINT_POLL_INTERVAL`, default 1.0).
  `--check-config` показывает статус лок. голоса. Централизованно выключается через
  `/coach voice off` у игрока.
- **Обратная совместимость**: старый мост не поллит (просто нет локального голоса);
  новый мост против старого backend получает 404 → пусто, не падает. Backend-часть
  довозит autodeploy; новые бинари моста — релиз-тег `v0.6.0` (auto-update 4.4
  разнесёт игрокам). Bridge 0.5.0→**0.6.0** (`__init__.py` + `pyproject.toml`),
  `local_tts`/`hint_poller` добавлены в spec hiddenimports.
- Тесты: `tests/test_hint_queue.py` (23: очередь+TTL+эндпоинт+pipeline),
  `tests/test_bridge_local_tts.py` + `tests/test_bridge_hint_poller.py` (44:
  диспетч TTS по платформе, поллер, get_hints через MockTransport).

### ⏳ Phase 5 — CV/OCR (не начата)

---

## KB — как устроена и как работает

**Структура:**
```
kb/
├── matchups/      ← одобренные гайды (production-канон)
├── drafts/        ← sourced-черновики, до review (индексируются ботом)
├── hypotheses/    ← AI-синтез, карантин (НЕ индексируются, НЕ проходят validate-kb)
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
- **Две параллельные джобы:**
  - `build-windows` (windows-latest) → `arena-bridge.exe`
  - `build-macos` (macos-latest, Apple Silicon arm64) → `arena-bridge-macos-arm64.tar.gz` (unsigned + sample bridge.env + README.txt с инструкцией по Gatekeeper)
- Финальная джоба `release` подтягивает оба артефакта + `ArenaCoach.zip` и публикует GitHub Release.
- `arena-bridge.spec` теперь кросс-платформенный: hiddenimports и UPX-сжатие включаются условно через `sys.platform`.
- Intel-mac сборка пока не делается — если понадобится, добавить `macos-13` runner.

### Секреты GitHub
- `VPS_SSH_KEY` — приватный ключ для деплоя на VPS (сейчас не используется в workflow, артефакты раздаются через GitHub Releases).

### Выпустить первый релиз
```bash
git tag v0.1.0
git push origin v0.1.0
# → Actions параллельно соберут .exe и .tar.gz → создадут Release
# → /download страница ссылается на assets latest release
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
│   ├── drafts/                   # sourced-черновики — индекс грузит их тоже
│   ├── hypotheses/               # AI-синтез, карантин — НЕ индексируются
│   ├── glossary/
│   └── compositions.json
├── tests/                        # ← единственный test-набор (286 тестов)
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
# 286 passed, 9 skipped (Mirlol paste-фикстуры вне репо) in ~8s
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
1. ✅ ~~Выпустить v0.1.0~~ — сделано (теги `v0.1.0`…`v0.2.0`, артефакты в Releases).
2. ✅ ~~Выпустить v0.3.0~~ — выпущен 2026-07-11, но **все бинари v0.3.0 оказались
   битые** (первый реальный запуск 2026-07-23, Mac): PyInstaller запускал
   `arena_bridge/__main__.py` как скрипт без package-контекста →
   `ImportError: attempted relative import with no known parent package`.
   CI smoke это пропускал: принимал exit 1 «как ошибки конфига», а bootloader
   при краше тоже выходит с 1; плюс без bridge.env путь с импортом не выполнялся.
3. **Выпустить v0.3.1** — `git push && git tag v0.3.1 && git push origin v0.3.1`.
   Починено 2026-07-23 (проверено локальной onefile-сборкой: check-config exit 0,
   E2E tail→POST, graceful Ctrl+C):
   - entry-обёртка `bridge/bridge_entry.py` (абсолютный импорт пакета) + spec
     на неё; hiddenimports всех модулей `arena_bridge.*`;
   - excludes урезаны до `tkinter` — агрессивный список выкидывал stdlib
     `email`, нужный httpx → «No module named 'email'» при импорте ws_client;
   - SIGINT/SIGTERM теперь реально останавливают демон (раньше stop_event
     проверялся только на следующей строке лога — Ctrl+C «не работал»);
   - принудительный UTF-8 stdio с errors=replace (`_force_utf8_stdio`) — на
     Windows перенаправленный вывод (CI-пайп, `> файл`) получает cp1252, и
     кириллица/«✓» роняли процесс UnicodeEncodeError (первый прогон строгого
     smoke на windows-runner поймал ровно это);
   - `--check-config` импортирует runtime-модули (ловит битую сборку);
   - CI smoke: валидный bridge.env + строго exit 0 на обеих платформах.
   ⚠ Для живого теста нужен именно **v0.3.1**: в ≤ v0.2.0 — аддон 0.1.0 без
   LoggingChat-фикса, в v0.3.0 — битые бинари.
4. **Выпустить v0.3.2 — разделитель AC-формата `|` → `#`** (найдено на живом
   тесте 2026-07-23 после v0.3.1): современный Anniversary-клиент запрещает
   сырой `|` в SendChatMessage (тихая Lua-ошибка) — аддон 0.2.0 **вообще не
   отправлял события**: whisper-to-self при этом работает (проверено `/w себе`),
   счётчик «Событий» рос, а `WoWChatLog.txt` оставался 0 байт, и строка «2)…»
   в `/ac test` не печаталась (эмит умирал между принтами). В оригинальном
   2.4.3 пайп проходил — Anniversary работает на современном движке.
   Фикс: аддон **0.2.1** шлёт `[AC#TYPE#...]`; bridge **0.3.2** принимает оба
   разделителя (`_AC_RE = \[AC[#|]...`, `parse_ac_line` выбирает по наличию
   `#`); e2e_dryrun переведён на `#` + одна легаси-строка; +6 тестов
   (`tests/test_bridge_delimiter.py`, всего 143). Проверено: dryrun зелёный
   (3 DM), пересобранный onefile парсит `#`-события из лога.
5. **Живой тест аддона + bridge (Mac arm64 и Windows)** — по гайду `docs/TESTING.md`. Прогресс 2026-07-23: v0.3.x цепочка фиксов доведена до рабочих шёпотов `[AC#...]`, но выяснилось, что chat-лог не флашится до выхода из игры → **Phase 4.2** (combat-лог канал, v0.4.0). Продолжать на **v0.4.0**: аддон 0.2.2 (`/ac status` → 0.2.2, `/ac log` → «Запись боя: ВКЛ»), bridge 0.4.0 (`--check-config` → «Канал: combat-лог»). E2E-проверка теперь = скирмиш (prep-аура есть и там): на воротах DM с матчапом (уточняется по кастам), тринкет/дефы врагов — realtime-DM. Рекомендовано вписать `BRIDGE_OUR_COMP` в bridge.env каждому. Можно начать ДО арены: `/ac test` гоняет канал до Discord DM прямо в открытом мире. Аддон теперь сам включает Chat-логирование. Предусловие: добавить игрока через `/access add … role:player` (даже owner — иначе `no_player`). На живом тесте проверить: какой файл лога открыл bridge; реальную задержку доставки DM (буферизация); не бесит ли форс-флаш системными сообщениями (если да — `/ac flush off`).
6. ✅ ~~Phase 4.1 — починить KB-матчинг~~ — сделано 2026-07-11 (см. Phase 4).

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
