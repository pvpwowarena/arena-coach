# Kickoff prompt для нового Cowork-сеанса (Phase 2)

> **Как использовать:** скопируй блок ниже целиком и вставь как первое сообщение в новый Cowork-сеанс. Не нужно ничего объяснять предыдущей сессии — новый агент прочитает доки и будет в курсе.

---

```
Контекст: продолжаем проект Arena Coach (AI-коуч для 2v2/3v3 арены WoW BC
Classic Anniversary). Phase 0 (design), Phase 1 (KB + ingest + tests),
Phase 1.5 (RU translation) — закрыты. CI зелёный. Сейчас Phase 2:
Discord-бот.

ПЕРВЫЙ ШАГ: прочитай документы в этом порядке, чтобы войти в контекст.
1. system_instructions_arena_coach_dev.md — твоя роль и стиль
2. arena-coach/docs/phase-0-design.md — архитектура и решения
3. arena-coach/docs/strategy-data-acquisition.md — стратегия источников
   данных (combat-log → addon → twitch); ВАЖНО: порядок Phase 3 ↔ Phase 4
   переключён, сначала combat-log bridge, потом аддон
4. arena-coach/docs/investor-brief.md — где мы и куда идём
5. arena-coach/README.md — текущее состояние кода

ЦЕЛИ PHASE 2 (Discord-бот, read-only):
- backend/arena_coach/api/app.py — FastAPI factory с health, kb, whitelist routes
- backend/arena_coach/bot/client.py — discord.py 2.x main
- backend/arena_coach/bot/cogs/matchup.py — slash /matchup, /opener
- backend/arena_coach/bot/cogs/glossary.py — /glossary, /list_comps, /source
- backend/arena_coach/bot/cogs/access.py — /access add/remove/list/audit
- backend/arena_coach/bot/cogs/coach.py — /coach pause/resume (заглушка под
  Phase 4)
- backend/arena_coach/bot/checks.py — @whitelist_required(role=...) декоратор
- backend/arena_coach/access/models.py — SQLAlchemy: WhitelistEntry, Role
- backend/arena_coach/access/crypto.py — Fernet wrappers (encrypt игровых ников)
- backend/arena_coach/access/service.py — add/remove/check бизнес-логика
- backend/arena_coach/access/audit.py — append-only JSONL writer
- backend/arena_coach/kb/retriever.py — query → ranked KB chunks (SQLite FTS5)
- backend/arena_coach/kb/indexer.py — index kb/matchups/*.md → SQLite FTS5
- backend/alembic/ — миграция: initial schema (whitelist_entries)
- Тесты: cog smoke с mock discord-interaction, whitelist deny/allow, Fernet
  round-trip, audit append-only invariants

ОГРАНИЧЕНИЯ:
- KB — source of truth. Бот никогда не выдумывает совет. Нет матчапа →
  отвечает «нет в KB, добавь источник через /source request».
- Default-deny whitelist везде, включая /glossary и /list_comps.
- Append-only audit на любую mutate операцию + denied запросы.
- Никаких хардкодов матчап-логики в коде.
- mypy --strict для KB-слоя; для бот-cog'ов допустима стандартная типизация
  (см. tool.mypy.overrides в pyproject.toml).
- Python 3.10 — минимум (на проде VPS).

ИНФРАСТРУКТУРА:
- VPS: Hetzner CX11 (1 GB RAM / 9.8 GB диск, 2.1 GB свободно). Shared с
  webmin на :10000 — НЕ ТРОГАТЬ. /opt/certbot есть, переиспользуем для
  TLS в Phase 4. Без UFW (пользователь сознательно). Только Python 3.10
  (deadsnakes не ставим).
- GitHub: pvpwowarena/arena-coach (private). Push через SSH (PAT не имеет
  workflow scope).
- CI: GitHub Actions, ruff + mypy --strict + pytest на py3.10/3.11/3.12.
- Discord-бот scope: single-guild private (пользователь + тестеры).

ПЕРЕД ПИСАНИЕМ КОДА — задай мне через AskUserQuestion:
1. Подтверждение что переключение Phase 3 ↔ Phase 4 (combat-log первым,
   аддон позже) ОК. Если ОК — обнови roadmap в README.md и phase-0-design.md.
2. Какие из этих секретов уже подготовлены, и куда их класть:
   - DISCORD_BOT_TOKEN
   - ARENA_COACH_OWNER_DISCORD_IDS
   - ARENA_COACH_FERNET_KEY (или сгенерируем тут)
   - ANTHROPIC_API_KEY (для Phase 4, не Phase 2)
3. Готов ли VPS (environment setup из «Phase 2 setup на сервере»
   в предыдущем сеансе) или начинаем с локальной разработки на Mac'е.
4. Какой набор slash-команд приоритетен на первую итерацию (только
   /matchup + /access? Все сразу?)

DEMO PHASE 2 (acceptance):
1. На сервере (или локально) бот запускается через `python -m arena_coach.bot.client`.
2. В Discord-сервере slash-команды видны для администратора.
3. `/access add @user role:player character:Stabby realm:Gorefiend` →
   запись зашифрована в SQLite, audit-entry в audit-YYYY-MM.jsonl.
4. Тестовый пользователь (без whitelist) → `/matchup our:rogue+mage
   vs:warrior+resto-druid` → ephemeral access denied embed.
5. Admin → тот же запрос → возвращает embed с opener/alternatives/CDs из
   kb/matchups/rm-vs-warrior-rdruid.md.
6. `/access audit days:1` → последние записи journal.
7. Все 4-5 audit-entries — append-only, не редактируемые, с SHA-256 hash
   payload'ов.
8. Тесты: pytest зелёный, mypy --strict зелёный, ruff зелёный, CI
   зелёный на push'е.

После Phase 2 — Phase 4 (combat-log bridge + realtime hints), потом
Phase 4c (voice через discord.py voice + Edge-TTS), потом Phase 5
(аддон опционально + Twitch fallback).

Начни с пункта «ПЕРЕД ПИСАНИЕМ КОДА» — задай вопросы.
```

---

## Что новый агент должен сделать сразу

1. Прочитать docs в указанном порядке (5-10 минут).
2. Задать 1-3 уточняющих вопроса через `AskUserQuestion` про секреты и порядок реализации.
3. Если переключение Phase 3 ↔ Phase 4 OK — обновить roadmap в README и phase-0-design.
4. Реализовать Phase 2 итерациями: сначала минимальный бот с `/matchup` без whitelist для smoke-test, потом whitelist + Fernet + audit, потом остальные slash-команды.

## Почему отдельный Cowork-сеанс

- Текущий сеанс длинный (~30+ сообщений), много контекста ушло на Phase 0 / 1.
- Новый сеанс начнётся «с чистым контекстом» + точечно прочитает docs, что даёт более фокусированную работу над Phase 2.
- Можно открыть параллельно: текущий сеанс держим как «архив + правки KB», новый — для Phase 2 кода.
