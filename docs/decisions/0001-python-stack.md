# ADR-0001: Python 3.11+ как основной язык backend, bridge и ingest

- **Status:** Accepted
- **Date:** 2026-05-12
- **Deciders:** Vladislav, Arena Coach Dev
- **Tags:** stack, language

## Context

Arena Coach состоит из трёх Python-компонентов (backend на VPS, bridge на игровой PC, ingest CLI на dev-машине) плюс Lua-аддон в клиенте. Нужен язык для трёх Python-компонент с минимальным risk'ом и максимальной экосистемой под наши задачи: discord-бот, LLM-оркестратор, FastAPI, локальный демон tail'инга файлов, ingest с парсингом HTML/Markdown/YouTube-транскриптов, в перспективе — OCR/CV.

## Decision

Принят **Python 3.11+** для всех трёх компонент.

Конкретные библиотеки:

- `discord.py` 2.x — slash-команды, ephemeral, permissions API. Зрелый, активно поддерживается.
- `FastAPI` + `uvicorn` — async REST + WSS, pydantic-валидация, OpenAPI бесплатно.
- `pydantic` v2 — модели KB-документов, валидация frontmatter и event-схем.
- `SQLAlchemy` 2 + `alembic` — БД-слой и миграции (Phase 2+).
- `anthropic` Python SDK — first-class поддержка от Anthropic.
- `cryptography` (Fernet) — симметричное шифрование игровых ников в whitelist.
- `watchdog` — file watching для SavedVariables + chat-log.
- `websockets` — bridge ↔ backend.
- `yt-dlp` + `openai-whisper` / Whisper API — YouTube transcript ingest (Phase 1.5+).
- `mss` + `opencv-python` + `pytesseract` — задел под Phase 5 (CV/OCR).

Tooling:

- `ruff` (lint + format)
- `mypy --strict` (типизация)
- `pytest` + `pytest-asyncio`
- `pre-commit`

## Alternatives Considered

### Node.js / TypeScript
- **Плюсы:** `discord.js` популярен, экосистема WSS зрелая, TypeScript-типы.
- **Минусы:** Anthropic SDK для JS менее «нативный» для агентских паттернов; OCR/CV экосистема существенно беднее (Tesseract.js работает, но не сравним с Python-OpenCV); whisper-обработка YouTube-VOD'ов требует обвязки.
- **Вердикт:** отвергнуто из-за слабого Phase 5-стека и менее зрелого ML-tooling.

### Go
- **Плюсы:** один статический бинарник для bridge, отличный async, низкое потребление памяти.
- **Минусы:** Anthropic SDK для Go сильно отстаёт; discord-библиотеки (discordgo) живы, но менее богаты slash/ephemeral helper'ами; whisper/OCR — через FFI обёртки.
- **Вердикт:** отвергнуто. Если в Phase 4 bridge станет узким местом по латенси, его одного можно переписать на Go без затрагивания backend/ingest.

### Rust
- **Плюсы:** идеально для bridge (fast, low-overhead).
- **Минусы:** разработка медленнее; экосистема Discord и Anthropic слабее; на v1 переборщит.
- **Вердикт:** отвергнуто для v1, возможен вариант для bridge в v2.

## Consequences

**Позитивные:**

- Унифицированный язык для трёх компонент → один tooling-stack, один CI workflow.
- Anthropic SDK + discord.py + FastAPI работают «из коробки» в одном venv.
- Будущий Phase 5 (CV/OCR) не требует смены стека.

**Негативные / trade-off'ы:**

- Bridge на Python потребляет больше памяти и имеет хуже latency, чем эквивалент на Go/Rust. Приемлемо, потому что подсказки требуют ≤2 сек reaction time, а не ≤50 мс.
- Распространение bridge'а игрокам требует Python-runtime у них на машине (или packaging через PyInstaller — обсудим в Phase 4).

## Validation

В Phase 1 проверяем стек на ingest-пайплайне: парсер Mirlol-файлов, pydantic-модель, тесты — всё на 3.11+, ruff+mypy --strict проходит. Если выявится несовместимость — пересматриваем.
