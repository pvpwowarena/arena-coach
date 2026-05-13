# Arena Coach

Мульти-компонентный помощник для 2v2/3v3 арены **WoW: Burning Crusade Classic Anniversary** (клиент 2.4.3).

> **Статус:** Phase 1. Скелет репо + KB-схема + ingest-пайплайн для Mirlol-гайдов. Discord-бот, Lua-аддон и bridge — в Phase 2/3/4.

## Что это

- База знаний (KB) по матчапам арены — Markdown с YAML frontmatter, source-of-truth на диске.
- Discord-бот с slash-командами `/matchup`, `/opener`, `/glossary` — отдаёт структурированный ответ из KB с цитатой источника. *(Phase 2)*
- Lua-аддон под клиент 2.4.3 — пишет события боя в SavedVariables и chat-frame mirror. *(Phase 3)*
- Локальный bridge — читает SavedVariables и chat-log, нормализует события, шлёт в backend. *(Phase 4)*
- Real-time подсказки в Discord (приватный канал) на ключевых событиях. *(Phase 4)*
- Whitelist с ролями `viewer` / `player` / `admin`, append-only audit log, Fernet-шифрование. *(Phase 2)*

## Архитектура

См. [`docs/architecture.md`](docs/architecture.md) и [`docs/phase-0-design.md`](docs/phase-0-design.md) — последний документ содержит mermaid-диаграмму и обоснования всех ключевых решений.

Деplyable артефакты:

| Артефакт | Где живёт | Что делает |
|----------|-----------|------------|
| `addon/` | WoW client (`Interface/AddOns/ArenaCoach/`) | Lua: tracker событий → SavedVariables + chat-frame |
| `bridge/` | игровая PC | Python-демон: tail SV + chat-log → WSS на backend |
| `backend/` | VPS (Ubuntu 22.04) | FastAPI + discord.py + LLM orchestrator + KB store |
| `ingest/` | dev-машина | CLI: Mirlol/tbcpvp/YouTube → `kb/drafts/` |
| `kb/` | git-versioned content | Markdown KB-документы, glossary, comp-slugs |

## Быстрый старт (dev)

```bash
# 1. Клон
git clone <repo-url>
cd arena-coach

# 2. Зависимости (Python 3.11+)
python -m venv .venv && source .venv/bin/activate
pip install --upgrade pip
pip install -e backend -e bridge -e ingest
pip install pre-commit ruff mypy pytest

# 3. Pre-commit
pre-commit install

# 4. Конфиг
cp .env.example .env
# заполни ключи в .env

# 5. Проверка
ruff check .
mypy backend bridge ingest
pytest

# 6. Демо: парсинг Mirlol-гайдов в KB-драфты
python -m arena_ingest paste \
  --file "../WOW TBC ARENA - Rogue  Mage.md" \
  --comp rogue+mage

python -m arena_ingest list  # увидишь 12 драфтов в kb/drafts/

# 7. Approve конкретного матчапа
python -m arena_ingest review approve --slug rm-vs-warrior-rdruid
# файл переезжает в kb/matchups/, audit log пополняется
```

## Структура репо

См. полное дерево с пояснениями в [`docs/phase-0-design.md`](docs/phase-0-design.md) §2.

```
arena-coach/
├── addon/              # WoW Lua addon (TBC 2.4.3)
├── bridge/             # local Python daemon
├── backend/            # FastAPI + discord.py (VPS)
├── ingest/             # CLI импортёры в KB
├── kb/                 # Source of truth: matchups, glossary, comp-slugs
├── docs/               # architecture, ADRs, phase designs
├── ops/                # systemd, Caddy, scripts
└── .github/workflows/  # CI (ruff + mypy --strict + pytest)
```

## Принципы

- **KB — единственный источник правды.** Код никогда не хардкодит матчап-логику.
- **Никогда не выдумываем советы.** Нет источника → честно говорим «нет, добавь его через `kb add`».
- **Read-only телеметрия.** Никакой автоматизации, нарушающей ToS Blizzard.
- **Default-deny whitelist.** Все интерфейсы (Discord/WSS/CLI) проверяют доступ.
- **Append-only audit.** Все привилегированные действия логируются необратимо.

## Phase-план

См. [`docs/phase-0-design.md`](docs/phase-0-design.md) §14 и [`docs/strategy-data-acquisition.md`](docs/strategy-data-acquisition.md) (стратегия источников данных).

- **Phase 0** — Design (готово). Документы, ADR, mock'и.
- **Phase 1** — Скелет + KB-ingest. *(готово — 22 драфта в `kb/drafts/`)*
- **Phase 1.5** — Russian prose translation, см. [`docs/phase-1.5-translation-plan.md`](docs/phase-1.5-translation-plan.md). *(готово)*
- **Phase 2** — Discord-бот (read-only): slash-команды `/matchup`, `/glossary`, `/access`, whitelist, audit log. *(in progress)*
- **Phase 3** — **Combat-log bridge** (Python-демон у тестера читает `Logs/WoWCombatLog.txt`, без аддона). Минимальный install у тестера.
- **Phase 4** — Real-time text-hints (event → KB-retrieve → LLM synth → Discord embed).
- **Phase 4c** — Voice hints (Edge-TTS в Discord voice channel), см. [`docs/phase-4.5-voice.md`](docs/phase-4.5-voice.md).
- **Phase 5a** — Lua-аддон (опциональный upgrade для ≤1 сек latency + custom-событий).
- **Phase 5b** — Twitch-CV fallback (видео-анализ для observer-режима).

**Важно:** порядок Phase 3 ↔ Phase 5a поменян относительно изначального Phase-0 design — combat-log файл идёт первым как MVP с минимальным барьером входа, аддон откладывается на upgrade-фазу. Обоснование — в [`docs/strategy-data-acquisition.md`](docs/strategy-data-acquisition.md).

## Безопасность

- Все секреты — через ENV, никогда в коде или KB.
- `SavedVariables.lua` хардкодом в `.gitignore` — не попадает в репо даже случайно.
- Whitelist-данные (игровые ники, реалмы) — Fernet-encrypted в БД.
- Audit log — append-only JSONL с SHA-256 hash payload'а.

## Лицензия

Proprietary, all rights reserved by Vladislav. См. [`LICENSE`](LICENSE).
