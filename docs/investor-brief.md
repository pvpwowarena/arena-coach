# Arena Coach — Investor / Stakeholder Brief

**One-liner:** Arena Coach turns high-level WoW PvP matchup knowledge into live tactical voice guidance during arena matches.

*RU подпись:* AI-коуч для 2v2/3v3 арены **WoW: Burning Crusade Classic Anniversary**, превращающий гайды топ-стримеров в персональные голосовые подсказки по ходу матча.

---

## Проблема

PvP-арена WoW BCC Anniversary — нишевый, но активный рынок:
- **20-50 тыс. одновременных пвп-игроков** в момент релиза Anniversary (2024).
- Кривая обучения **колоссальная**: 100+ матчапов комба-на-комбу, у каждого свой opener, post-trinket play, kill priority, ротация КД.
- Существующие ресурсы (Mirlol, tbcpvp, YouTube) — **статический текст**, который читать в процессе матча некогда.
- Топ-30% игроков знают эти гайды наизусть; нижние 70% играют интуитивно и тонут на низком рейтинге.

**Боль:** игрок видит вражеский состав → жмёт «бой» → за 5 секунд должен вспомнить kill target, sap-stall стратегию, что делать на trinket'е друида. Чаще всего не вспоминает.

---

## Решение

Голосовой коуч в Discord-voice-канале, который:

1. **Перед матчем:** говорит «ты против Warrior/Druid — kill druid, открой sap на warrior, держи double wound».
2. **В матче (≤2 сек реакция):** «druid трикетнул kidney — готовь повторный stun», «warrior пошёл в spell reflect — выходи из nova».
3. **После матча:** короткий разбор того что прошло хорошо / плохо, со ссылкой на KB-документ.

Источник знаний — структурированная база матчапов, собранная из гайдов Mirlol/tbcpvp/Twitch-стримеров (на старте — 22 матчапа RM/RP, далее — расширение через LLM-ingest пайплайн).

---

## Архитектура (схематично)

```
   ┌───────────────────────────────────────────────────────┐
   │  WoW Client (TBC 2.4.3 Anniversary)                   │
   │     /combatlog → Logs/WoWCombatLog.txt (read-only)    │
   │     Опционально: addon ArenaCoach (Lua, read-only)    │
   └───────────────────┬───────────────────────────────────┘
                       │
                       │  tail файла (legitimate read)
                       ▼
   ┌───────────────────────────────────────────────────────┐
   │  Local Bridge (Python, на машине игрока)              │
   │     WoWCombatLog.txt → JSON events → WSS              │
   └───────────────────┬───────────────────────────────────┘
                       │ WSS + bearer-token
                       ▼
   ┌───────────────────────────────────────────────────────┐
   │  Backend (FastAPI + discord.py + LLM-оркестратор)     │
   │    on Hetzner VPS (€4.5/мес)                          │
   │      ├── KB (Markdown + SQLite FTS5)                  │
   │      ├── Whitelist + audit log (Fernet + JSONL)       │
   │      ├── Anthropic Sonnet/Haiku — hint synth          │
   │      └── TTS (Edge-TTS бесплатно / OpenAI TTS)        │
   └───────────────────┬───────────────────────────────────┘
                       │
                       ▼
   ┌───────────────────────────────────────────────────────┐
   │  Discord voice channel                                │
   │     Бот говорит подсказки голосом по событиям матча   │
   └───────────────────────────────────────────────────────┘

   Read-only, no input injection, no memory reading, no automation.
   Same pattern as Warcraft Logs / Details! / Method — индустриальный стандарт.
```

---

## Cost-модель (per-player, monthly)

| Статья | Низкая загрузка (1-5 игроков) | Средняя (10-30) | Высокая (100+) |
|--------|-------------------------------|-----------------|----------------|
| VPS (Hetzner CX22 → CX32 → CCX23) | €0 (текущий shared сервер) | €4.5 | €15 |
| Anthropic API (Haiku для classify + Sonnet для synth) | $5-10 | $20-50 | $150-300 |
| TTS (Edge-TTS) | $0 (бесплатно) | $0 | $0 |
| TTS (premium, опционально OpenAI TTS) | $0 | $5-15 | $30-100 |
| Domain + TLS (Let's Encrypt) | $0 (Cloudflare DNS бесплатно) | $0-2 | $0-2 |
| Backups (B2/R2 S3-совместимое) | $0 (free-tier) | $1 | $5 |
| **Итого** | **≈ $10/мес** | **≈ $30-70/мес** | **≈ $200-400/мес** |

Расчёт исходит из ~100 hint'ов/час активной игры на игрока, средний hint 150-300 токенов.

---

## Дорожная карта (12 недель до closed-beta, 6 месяцев до open)

| Phase | Что | Срок | Статус |
|-------|-----|------|--------|
| 0 — Design | Архитектура, ADR, mock'и | 1 неделя | ✅ done |
| 1 — KB + ingest pipeline | 22 матчапа (RM/RP), парсер, тесты | 2 недели | ✅ done |
| 1.5 — RU translation | 22 драфта переведены на русский | 1 неделя | ✅ done |
| 2 — Discord-бот (read-only) | Slash-команды `/matchup`, `/glossary`, whitelist, audit log | 2 недели | 🟡 in progress |
| 3 — Combat-log bridge | Python-демон у тестеров, WSS на backend | 1 неделя | ⏳ next |
| 4 — Real-time hint pipeline | Event → matchup match → LLM synth → Discord embed | 2 недели | ⏳ |
| 4c — Voice hints | Edge-TTS в Discord voice channel | 1 неделя | ⏳ |
| 5 — Аддон (Lua, опционально) | Custom-события, ≤1 сек latency | 2 недели | ⏳ |
| Beta — расширение KB | До 50+ матчапов через LLM-ingest | continuous | ⏳ |

**Closed beta** — 10-20 тестеров через ручной whitelist в Discord.
**Open** — публичный Discord-сервер, self-serve onboarding через slash-команду `/coach apply`.

---

## Defensibility / Moat

1. **База знаний.** Структурированная KB матчапов с трейсабельностью к источнику и системой review — единственный в своём роде ресурс. Конкуренту нужно либо лицензировать (Mirlol/tbcpvp не лицензируют), либо построить аналогичный pipeline (3-6 месяцев).
2. **Метаданные с боёв.** Каждый матч тестеров обогащает аналитику: какие подсказки сработали, какие были проигнорированы, какие шаблоны опенера популярны. Это датасет для file-tuning'а через несколько месяцев.
3. **Brand в нишевом сообществе.** Сейчас на рынке **нет** real-time голосового коуча для WoW Classic. Конкурентов 0. Окно для захвата — 6-12 месяцев до того как кто-то ещё догадается / возьмётся.
4. **Платформенная инфраструктура.** После закрытия TBC Anniversary (через 1.5-2 года) — переходим на WotLK Classic (тот же engine), потом Cata, MoP. Каждое расширение — новый цикл активной PvP-сцены и новая нишевая monetisation.

---

## Риски и митигация

| Риск | Вероятность | Митигация |
|------|-------------|-----------|
| Blizzard расценит как нарушение ToS | Низкая | Все компоненты read-only, индустриальный стандарт (см. Warcraft Logs). [`docs/decisions/0003-chatframe-realtime-channel.md`](decisions/0003-chatframe-realtime-channel.md) |
| Mirlol/tbcpvp выкатывают свой коуч | Средняя через 6 мес | Первый mover advantage; интеграция с Twitch-стримерами как маркетинг |
| LLM-API стоимость растёт | Низкая (тенденция к удешевлению) | Локальные модели как fallback (Llama 3.1 8B на собственном GPU), Haiku для классификации |
| Anniversary заканчивается раньше срока | Низкая | Переход на WotLK Classic (объявлено Blizzard) |
| Аудитория слишком маленькая для unit economics | Средняя | Freemium: free базовые подсказки в Discord, premium $5/мес за per-player голос + расширенную KB |

---

## Финансовая модель (ориентировочно)

**Условия:**
- 50 платящих игроков по $5/мес → $250 MRR
- Cost эксплуатации на 50 игроков: ~$80/мес
- Gross margin: ~70%
- Break-even на 30 игроках

**Прогноз закрытой беты (3 месяца):**
- 10-20 тестеров (бесплатно, для feedback)
- Стоимость: VPS + Anthropic = $30-50/мес
- ROI: данные + product-market fit

**Прогноз года 1:**
- 100-300 платящих игроков → $500-$1500 MRR
- Маркетинг: партнёрство с Twitch-стримерами (revshare за referral)
- Operational cost: $300-600/мес
- Net: $200-900/мес (на жизнь хобби-проекта или развитие)

---

## Текущий статус (на 2026-05-13)

- ✅ Phase 0 design complete — [`docs/phase-0-design.md`](phase-0-design.md)
- ✅ Phase 1 complete — 22 KB-драфта, 34 теста, CI зелёный, GitHub-репо приватный
- ✅ Phase 1.5 complete — все драфты переведены на русский
- ✅ Сервер арендован (Hetzner)
- 🟡 Phase 2 setup — environment в подготовке
- ⏳ Phase 2 implementation — Discord-бот, следующий шаг

**Что нужно для следующего этапа:**
- Discord-сервер для тестов (можно создать пустой за 30 сек)
- Discord Bot Application (бесплатно через Developer Portal)
- Anthropic API key с $5-20 баланса (есть free credit для регистрации)
- ~2-3 недели разработки до Phase 2 ship'а

---

## Контакты

**Автор:** Vladislav · [github.com/pvpwowarena](https://github.com/pvpwowarena)
**Репозиторий:** приватный, `pvpwowarena/arena-coach`
**Стек:** Python 3.10+, FastAPI, discord.py, Anthropic SDK, SQLite, Lua (для опционального аддона)
