# Kickoff prompt для нового Cowork-сеанса (Phase 2: server setup + Discord-бот)

> **Как использовать:** скопируй блок ниже целиком (между ``` ... ```) и вставь как первое сообщение в новый Cowork-сеанс. Папку проекта в Cowork выбирай ту же: `/Users/surprise/Downloads/Claude/PVP WOW Arena/PVP WoW Arena/`.

---

```
Контекст: Arena Coach — AI-голосовой коуч для 2v2/3v3 арены WoW: Burning
Crusade Classic Anniversary. Phase 0 (design), Phase 1 (KB + ingest), Phase
1.5 (RU translation) — закрыты. Репо на GitHub: pvpwowarena/arena-coach
(приватный, push через SSH). CI зелёный на py3.10/3.11/3.12.

Сейчас Phase 2: server setup на свежепереустановленном VPS + Discord-бот.

═══════════════════════════════════════════════════════════════════════
СОСТОЯНИЕ СЕРВЕРА
═══════════════════════════════════════════════════════════════════════

VPS у Senko Digital (реселлер Hetzner Cloud). Владелец решил переустановить
ОС из админки → CHИСТЫЙ сервер, Ubuntu 22.04 или 24.04 LTS, 1 GB RAM.

Шаги setup'а описаны ДЕТАЛЬНО в arena-coach/docs/server-setup-clean.md.
Этот документ — твой основной guide на этапе деплоя. Шаги A→K, без
shortcut'ов. Никакого Webmin / x-ui / certbot legacy уже нет.

═══════════════════════════════════════════════════════════════════════
ПЕРВЫЙ ШАГ: ВХОД В КОНТЕКСТ
═══════════════════════════════════════════════════════════════════════

Прочитай в этом порядке (5-10 минут):
1. arena-coach/docs/server-setup-clean.md — пошаговая инструкция для чистого
   Ubuntu (шаги A-K: reinstall → ssh-keys → user → deploy key → venv → check).
   На этапе server setup твоя главная роль — провести владельца по шагам.
2. arena-coach/docs/strategy-data-acquisition.md — стратегия источников
   данных. ВАЖНО: Phase 3 = combat-log bridge (НЕ аддон). Аддон откладывается
   на Phase 5a как опциональный upgrade.
3. arena-coach/docs/investor-brief.md — где мы и куда идём
4. arena-coach/docs/phase-0-design.md — архитектура и решения (старая
   roadmap там, но §5/§6 про whitelist и события актуальны)
5. arena-coach/docs/decisions/ — три ADR (Python-стек, SQLite, chat-frame)
6. arena-coach/README.md — текущая (обновлённая) roadmap

═══════════════════════════════════════════════════════════════════════
ЦЕЛИ PHASE 2 (Discord-бот, read-only, без realtime)
═══════════════════════════════════════════════════════════════════════

Реализация в backend/arena_coach/:

- bot/client.py — discord.py 2.x main, регистрация cog'ов
- bot/cogs/matchup.py — /matchup our:<comp> vs:<comp>, /opener
- bot/cogs/glossary.py — /glossary <term>, /list_comps, /source <slug>
- bot/cogs/access.py — /access add/remove/list/audit (admin only)
- bot/cogs/coach.py — /coach pause/resume (заглушка под Phase 4 realtime)
- bot/checks.py — @whitelist_required(role=...) декоратор, default-deny

- access/models.py — SQLAlchemy 2 declarative: WhitelistEntry с
  Fernet-encrypted character/realm
- access/crypto.py — Fernet wrappers, MultiFernet для ротации ключа
- access/service.py — add/remove/check/list бизнес-логика
- access/audit.py — append-only JSONL writer, SHA-256 hash payload
- alembic/ — initial migration (whitelist_entries таблица)

- kb/retriever.py — query → ranked KB chunks через SQLite FTS5
- kb/indexer.py — index kb/matchups/*.md → SQLite FTS5 на старте
- kb/render.py — KBDoc → Discord embed (mock'и в phase-0-design §4)

- api/app.py — FastAPI factory с /health, /v1/kb, /v1/whitelist routes
  (для admin tooling через CLI потом)

ТЕСТЫ:
- cog smoke с mock discord-interaction (через discord.py test patterns)
- whitelist deny/allow paths (тест на каждую role)
- Fernet round-trip + ротация
- audit append-only invariant (тест: запись добавляется, существующие не
  меняются после mutate)

═══════════════════════════════════════════════════════════════════════
ОГРАНИЧЕНИЯ И ПРИНЦИПЫ
═══════════════════════════════════════════════════════════════════════

- Python 3.10+ на сервере (22.04). На 24.04 — 3.12 системный, тоже OK.
- KB — единственный источник правды. Бот никогда не выдумывает совет.
  Нет матчапа → ephemeral "нет в KB, добавь через /source request".
- Default-deny whitelist на ВСЕХ командах, включая /glossary и /list_comps.
- Append-only audit на любую mutate operation + denied access attempt.
- Никаких хардкодов матчап-логики в коде.
- mypy --strict для backend/arena_coach/kb/ и access/. Для bot/cogs/ —
  расслаблено (см. tool.mypy.overrides в pyproject.toml).
- Voice OUT only в v1 (voice IN с STT — отложен, может никогда не делать).

═══════════════════════════════════════════════════════════════════════
INFRA
═══════════════════════════════════════════════════════════════════════

- VPS Senko Digital (Hetzner reseller), 1 GB RAM, чистый Ubuntu
- Discord scope: single-guild private (владелец + тестеры по whitelist)
- Push через SSH (PAT не имеет workflow scope, поэтому HTTPS не работает
  для коммитов с изменениями в .github/workflows/)
- CI: ruff + mypy --strict + pytest на py3.10/3.11/3.12, KB-validation на 3.10
- Phase 4 (realtime) поднимет certbot + WSS на 443 (uфw уже открыт)

═══════════════════════════════════════════════════════════════════════
ПЕРЕД ПИСАНИЕМ КОДА — ЗАДАЙ МНЕ через AskUserQuestion
═══════════════════════════════════════════════════════════════════════

1. Сервер уже переустановил через админку Senko Digital или ещё нет?
   - Если нет — сначала пройдись по docs/server-setup-clean.md шагам A-K
     с владельцем (он на сервере под root через панельку).
   - Если да и шаги A-K пройдены — переходим сразу к Phase 2 коду.

2. Какие Discord-секреты подготовлены и где они:
   - DISCORD_BOT_TOKEN (из Developer Portal → Bot → Token)
   - DISCORD_APPLICATION_ID
   - DISCORD_GUILD_ID (private server)
   - ARENA_COACH_OWNER_DISCORD_IDS (мой User ID)
   Я сохранил их в (Notes / 1Password / нигде ещё) — куда класть?

3. Куда деплоить первую версию бота:
   - Сразу на VPS (нужен SSH-доступ под arenacoach)
   - Сначала локально на Mac, потом VPS
   - Параллельно: код локально + тесты CI, деплой на VPS отдельно

4. Какие slash-команды приоритетны на первую итерацию (MVP бота):
   - Только /matchup + /access add (минимум для проверки KB → Discord)
   - Полный набор сразу
   - По приоритету: /access add → /matchup → /glossary → остальные

После ответов — план + реализация + acceptance demo.

═══════════════════════════════════════════════════════════════════════
ACCEPTANCE PHASE 2 (5-7 шагов чтобы потрогать живой бот)
═══════════════════════════════════════════════════════════════════════

1. На VPS под arenacoach: `python -m arena_coach.bot.client` → бот онлайн.
2. В Discord-сервере slash-команды видны для админа.
3. /access add @user role:player character:Stabby realm:Gorefiend →
   запись в SQLite (зашифрована), audit-entry в audit-YYYY-MM.jsonl.
4. /matchup our:rogue+mage vs:warrior+resto-druid → embed с opener / alt /
   if-trinkets / CDs из kb/matchups/rm-vs-warrior-rdruid.md (или kb/drafts/
   пока review-flow не отработан).
5. Тестовый user без whitelist → /matchup → ephemeral access-denied embed.
6. /access audit days:1 → последние записи.
7. Все audit-entries — append-only, не редактируемые, с SHA-256 hash
   payload'а.
8. CI зелёный, тесты зелёные, ruff+mypy зелёные.

После Phase 2 → Phase 3 (combat-log bridge) → Phase 4 (realtime hints) →
Phase 4c (voice через Edge-TTS) → Phase 5a (опциональный Lua-аддон).

Начни с пункта "ПЕРЕД ПИСАНИЕМ КОДА" — задай 4 вопроса.
```

---

## Что новый агент сделает первым делом

1. Прочитает 6 указанных docs (~10 минут).
2. Через `AskUserQuestion` спросит 4 ключевых вопроса (статус reinstall, секреты, локально/VPS, приоритет команд).
3. Если сервер ещё не переустановлен — проведёт владельца по [`docs/server-setup-clean.md`](server-setup-clean.md) шаги A-K.
4. После того как `validate-kb` прошёл на сервере → начнёт писать Discord-бот итеративно.

Если новый агент застрянет — возвращайся в этот сеанс, проверим архитектуру и стратегию.
