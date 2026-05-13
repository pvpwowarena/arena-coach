# Kickoff prompt для нового Cowork-сеанса (Phase 2: server setup + Discord-бот)

> **Как использовать:** скопируй блок ниже целиком (между ``` ... ```) и вставь как первое сообщение в новый Cowork-сеанс. Папку проекта в Cowork выбирай ту же: `/Users/surprise/Downloads/Claude/PVP WOW Arena/PVP WoW Arena/`.

---

```
Контекст: Arena Coach — AI-голосовой коуч для 2v2/3v3 арены WoW: Burning
Crusade Classic Anniversary. Phase 0 (design), Phase 1 (KB + ingest), Phase
1.5 (RU translation) — закрыты. Репо на GitHub: pvpwowarena/arena-coach
(приватный, push через SSH). CI зелёный на py3.10/3.11/3.12.

Сейчас Phase 2: дозавершить server setup + написать Discord-бот.

═══════════════════════════════════════════════════════════════════════
СОСТОЯНИЕ СЕРВЕРА (Hetzner, root@55184, Ubuntu 22.04 LTS, 1 GB RAM)
═══════════════════════════════════════════════════════════════════════

ГОТОВО:
✓ Disk cleanup: ~600 MB освобождено (apt clean + autoremove)
✓ Swap 512 MB создан (/swapfile, в /etc/fstab)
✓ Установлены: git 2.34, python3.10-venv, python3-pip
✓ Системно уже было: python3.10, webmin (port 10000), certbot в /opt/certbot
  (старые TLS-ключи для забытого поддомена — переиспользуем в Phase 4)
✓ Disk free: ~1.5 GB после swap (был 2.1, swap занял 512)

НЕ ТРОГАТЬ:
✗ Webmin (port 10000) — оставлен по решению владельца
✗ /etc/ssh/sshd_config — пользователь зашёл по паролю под root, ssh
  готовый, ключ ещё не настроен
✗ Существующий firewall (UFW нет, iptables пустой) — не лезем без явного
  запроса владельца

ОСТАЛОСЬ ДОДЕЛАТЬ НА СЕРВЕРЕ (5-10 минут):
1. Скопировать SSH-ключ Mac'а пользователя через ssh-copy-id, отключить
   парольную auth для root, перевести на ключ
2. Создать пользователя arenacoach (без пароля, без sudo)
3. Создать /opt/arena-coach, /var/lib/arena-coach, /etc/arena-coach
   (последняя chmod 750)
4. Скопировать SSH-ключ root'а в /home/arenacoach/.ssh/authorized_keys
5. Под arenacoach: сгенерировать deploy-key, добавить в GitHub repo
   (Settings → Deploy keys → read-only)
6. Клонировать git@github.com:pvpwowarena/arena-coach.git в /opt/arena-coach
7. python3.10 -m venv .venv + pip install -e backend -e ingest
8. Acceptance: `python -m arena_coach validate-kb kb/drafts` → "OK: 22"

Конкретные команды для пунктов 1-8 — в предыдущей Cowork-сессии. Можешь
их повторить или предложить свои если есть лучше.

═══════════════════════════════════════════════════════════════════════
ПЕРВЫЙ ШАГ: ВХОД В КОНТЕКСТ
═══════════════════════════════════════════════════════════════════════

Прочитай в этом порядке (5-10 минут):
1. arena-coach/docs/strategy-data-acquisition.md — стратегия источников
   данных. ВАЖНО: Phase 3 = combat-log bridge (НЕ аддон). Аддон откладывается
   на Phase 5a как опциональный upgrade.
2. arena-coach/docs/investor-brief.md — где мы и куда идём
3. arena-coach/docs/phase-0-design.md — архитектура и решения (старая
   roadmap там, но §5/§6 про whitelist и события актуальны)
4. arena-coach/docs/decisions/ — три ADR (Python-стек, SQLite, chat-frame)
5. arena-coach/README.md — текущая (обновлённая) roadmap

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
  Fernet-encrypted character/realm, AuditEntry (но писать в JSONL не БД!)
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

- Python 3.10+ (на сервере 3.10, не 3.11). Уже в pyproject.toml.
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

- VPS Hetzner: 1 GB RAM + 512 MB swap, 1.5 GB диск свободно
- Discord scope: single-guild private (владелец + тестеры по whitelist)
- Push через SSH (PAT не имеет workflow scope, поэтому HTTPS не работает
  для коммитов с изменениями в .github/workflows/)
- CI: ruff + mypy --strict + pytest на py3.10/3.11/3.12, KB-validation на 3.10
- Phase 4 будет переиспользовать certbot из /opt/certbot для TLS на WSS

═══════════════════════════════════════════════════════════════════════
ПЕРЕД ПИСАНИЕМ КОДА — ЗАДАЙ МНЕ через AskUserQuestion
═══════════════════════════════════════════════════════════════════════

1. Какие Discord-секреты подготовлены и где они:
   - DISCORD_BOT_TOKEN (из Developer Portal → Bot → Token)
   - DISCORD_APPLICATION_ID
   - DISCORD_GUILD_ID (private server)
   - ARENA_COACH_OWNER_DISCORD_IDS (мой User ID)
   Я сохранил их в (Notes / 1Password / нигде ещё) — куда класть?

2. Куда деплоить первую версию бота:
   - Сразу на VPS (нужен SSH-доступ под arenacoach)
   - Сначала локально на Mac, потом VPS
   - Параллельно: дописывать код локально, тесты гонять локально + CI,
     деплой на VPS отдельным шагом

3. Какие slash-команды приоритетны на первую итерацию (MVP бота):
   - Только /matchup + /access add (минимум для проверки KB → Discord)
   - Полный набор сразу
   - По приоритету: /access add → /matchup → /glossary → остальные

4. Server setup пункты 1-7 — выполняем (а) ты даёшь команды по одной
   я выполняю на сервере, (б) я сам справлюсь с командами из предыдущего
   сеанса, дай мне только дельта-команды если есть отличия.

После ответов 1-4 — план + реализация + acceptance demo.

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

Начни с пункта "ПЕРЕД ПИСАНИЕМ КОДА" — задай мне 4 вопроса.
```

---

## Что новый агент сделает первым делом

1. Прочитает 5 указанных docs (~10 минут).
2. Через `AskUserQuestion` спросит 4 ключевых вопроса (секреты, локально или VPS, приоритет команд, формат server setup).
3. На основании ответов — даст пошаговый план Phase 2 implementation.
4. Будет вкатывать итеративно: server setup → минимальный бот с /matchup → whitelist + Fernet → audit → остальные команды → демо.

Если новый агент застрянет — возвращайся в этот сеанс, проверим архитектуру и стратегию.
