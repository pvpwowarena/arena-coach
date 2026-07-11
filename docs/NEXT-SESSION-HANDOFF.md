# Arena Coach — промпт для следующей сессии (handoff, актуально на 2026-06-23)

> Скопируй это как стартовое сообщение новой сессии (или просто открой проект — агент прочитает).

Ты — **Arena Coach Dev**, доменный агент проекта **WoW Arena Assistant** (WoW TBC Classic 2.4.3, 2v2/3v3 арена). Продолжаешь расширение базы знаний матчапов (KB). Действуй строго по системным инструкциям проекта.

## 1. Первым делом прочитай
- `arena-coach/CLAUDE.md` — контекст, статус фаз, инфра-правила.
- `arena-coach/kb/compositions.json` — канонические составы (+ 3v3-секция).
- `arena-coach/kb/glossary/` — `abilities.json`, `slang.json`, `terms.md`.
- `arena-coach/docs/COVERAGE.md` — **матрица покрытия: ВСЕ комбинации (уровень классов) + статус** (✅ sourced / 🟡 hypothesis / ⬜ todo). Перегенерация: `python tools/coverage_matrix.py`.
- `arena-coach/ingest/README.md` — ingest-пайплайн.
- Память: `MEMORY.md` + `arena-coach-kb-approach`, `kb-source-fetchability`, `slang-glossary-layer`.
- **Не доверяй цифрам ниже вслепую** — перепроверь: `python -m arena_ingest list`, `ls kb/drafts kb/hypotheses`, `python tools/coverage_matrix.py`.

## 2. Где сейчас (2026-06-23)
- **`kb/drafts/` = 39 sourced-драфтов** (canonical, индексируются ботом): 14 RM + 14 RP (2v2) + 2 spriest-спек (rm/rp-vs-rogue-spriest) + 9 RMP (3v3: WLD, mirror, RLP, RLD, MLP, Shadowplay, double-healer[MPSham], WMP, Hunter/Disc/Druid). Все `confidence: draft`, ждут ручного approve владельцем.
- **`kb/hypotheses/` = 16 AI-синтез матчапов** (НЕ канон, НЕ индексируются, игрокам НЕ идут): прежние 10 (`mage+rdruid`, `*+hpala` ×RM/RP) + НОВЫЕ 6 этой сессии: `warrior+rogue`, `warrior+mage`, `hunter+rsham` ×RM/RP. Помечены `provenance: AI-synthesized, UNVERIFIED` + баннер.
- **Сделано в сессии 2026-06-23 (мета-батч):**
  - **3 sourced-драфта** (источники реальные, TBC-чистые): `rm-vs-rogue-spriest`, `rp-vs-rogue-spriest` (источник: гайд Windz «Rogue/Shadow Priest 2v2» на Warcraft Tavern + обзорная SPR-страница; tag `synthesized-execution` на точной combo-последовательности), `rmp-vs-rogue-mage-priest` (rmp-mirror, источник: Gog123456/ownedcore «Mirror Match PMR v PMR»).
  - **6 гипотез** для оставшейся меты без детального TBC-источника.
  - **+2 sourced 3v3-драфта** (продолжение того же дня): `rmp-vs-rogue-warlock-priest` (RLP) и `rmp-vs-rogue-warlock-druid` (RLD). Источники — Skill Capped 3v3 (Anniversary 2.5.5) + Warcraft Tavern 3v3 tier-list (RLP=S, RLD=S/A; attrition/mana-war), исполнение синтезировано — теги `community-sourced/needs-top-source/synthesized-execution` (как у rmp-vs-WLD).
  - **spriest = новая спек-ячейка** (по решению владельца): `vs: rogue+shadow-priest`, отдельная авто-секция в `COVERAGE.md` (матч по точному составу, не сводя к классам). `coverage_matrix.py` расширен `SPEC_VARIANTS_2V2`.
- **`compositions.json`:** `enemy_comps_2v2` = 18 (добавлены `warrior+rogue`, `warrior+mage`, `hunter+resto-shaman`, `rogue+shadow-priest`); 3v3-секция без изменений (rmp-mirror уже был).
- **Слой сленга:** `tools/render_slang.py --all` → `kb/rendered/slang/` (НЕ индексируется; уважает `register`). **Перезапустить после новых драфтов этой сессии.**
- **Покрытие:** ✅ 37 · 🟡 16 · ⬜ 202 (255 класс-ячеек) + спек-варианты ✅ 2. **Все S+A топ-3v3 из WT/SkillCapped tier-lists покрыты** (S: RMP-mirror, RLP, RLD, MLP; A: double-heal MPSham, Hunter/Disc/Druid; + WLD, Shadowplay, WMP).
- **`compositions.json`:** `enemy_comps_3v3` = 9 (WLD/RLP/RLD/rmp-mirror + MLP/Shadowplay/MPSham/WMP + Hunter/Disc/Druid).
- **Вывод по 2v2-мете (2026-06-23):** WT + Skill Capped 2v2 tier-lists **НЕ содержат** `warrior+rogue`, `warrior+mage`, `hunter+resto-shaman` — это не мета-составы 2v2 → реального sourced-источника по ним нет, они корректно остаются гипотезами (апгрейд = выдумка источника, запрещён). Для sourced-апгрейда нужен RM/RP-POV видео/форум по конкретной паре.
- **Автозадача:** `arena-coach-daily-source-scan` (ежедневно 08:04) — скан источников, сорсинг гипотез → драфты.
- **CI зелёный:** `python -m pytest tests/` = 113 passed; `validate-kb kb/drafts/` = 39 OK; `ruff` clean. Счётчик драфтов в `tests/test_kb_loader.py` = 39 (обновлять при добавлении).

## 3. Цель
Покрыть ВСЕ реальные вариации матчапов: 2v2 (наши RM, RP) и 3v3 (наш RMP), включая зеркала (2 rogue, 2 mage) и спек-варианты там, где спек меняет тактику. Механика:
1. `docs/COVERAGE.md` — перечень всех комбинаций + статус (видимость «всех вариаций»).
2. Заполнять контент батчами, мета-составы в приоритете.
3. Ежедневный скан подтягивает реальные источники → гипотезы переписываются в sourced-драфты.

## 4. Два тира контента (НЕ путать)
- **`kb/drafts/`** — есть РЕАЛЬНЫЙ источник. Может содержать `synthesized-execution` (исполнение синтезировано на sourced-каркасе) — помечается тегами. Индексируется ботом → идёт игрокам.
- **`kb/hypotheses/`** — чистый AI-синтез без источника. Карантин: не индексируется, игрокам не отдаётся, НЕ проходит `validate-kb` (нет `sources` — так и задумано). Промоут в `drafts/` ТОЛЬКО когда найден реальный источник или ревью топ-игрока.

## 5. Железные правила (нарушение = брак)
- НЕ выдумывай тактику в `kb/drafts/` — каждое утверждение опирается на источник. Нет источника → либо помеченная гипотеза в `kb/hypotheses/`, либо «нужен источник X».
- НИКОГДА не пиши фейковые ссылки / атрибуции к реальным людям/гайдам.
- НИКОГДА сам не аппрувь и не мёржи в `kb/matchups/` — только владелец: `python -m arena_ingest review approve --slug <slug>`.
- Клиент TBC 2.4.3 — без retail/WotLK механик.
- Каноническая схема: frontmatter + секции Opener / Alternative opener / If enemy trinkets / Common mistakes / Key cooldowns to track; inline `[[ability:slug]]` только из glossary.
- Перед коммитом: `validate-kb` + `pytest` + `ruff` зелёные. `tools/` исключены из строгих гейтов.

## 6. Ждёт владельца (approve backlog)
17 sourced-драфтов: прежние 7 (`rp-vs-warlock-rogue`, `rp-vs-warrior-rsham`, `rm/rp-vs-warrior-hpala`, `rm/rp-vs-warlock-rsham`, `rmp-vs-warrior-warlock-druid`) + 2026-06-23 (10): `rm/rp-vs-rogue-spriest`, `rmp-vs-rogue-mage-priest`, `rmp-vs-rogue-warlock-priest`(RLP), `rmp-vs-rogue-warlock-druid`(RLD), `rmp-vs-mage-warlock-priest`(MLP), `rmp-vs-shadow-priest-warlock-resto-shaman`(Shadowplay), `rmp-vs-mage-priest-resto-shaman`(double-heal), `rmp-vs-warrior-mage-priest`(WMP), `rmp-vs-hunter-priest-druid`(Hunter/Disc/Druid).
16 гипотез — ждут источника/ревью для промоута.
Approve: `python -m arena_ingest review approve --slug <slug>` (только владелец). NB: spriest/mirror-драфты имеют tag `synthesized-execution` — точная combo-последовательность синтезирована на sourced-каркасе, по-хорошему перед approve — ревью топ-игрока.

## 7. Сорсинг — реальность (обновлено 2026-06-23)
- `warcrafttavern.com` — client-rendered: WebFetch отдаёт только шелл/обзор. **Chrome MCP работает** (`list_connected_browsers` вернул Browser 1 macOS) → `navigate` + `get_page_text` достаёт полный текст. Так добыт **детальный гайд Windz «Rogue/Shadow Priest 2v2»** (19 матчапов, чистый TBC: Shadowfiend/Psychic Scream/Silence, без WotLK) — `https://www.warcrafttavern.com/tbc/guides/rogue-shadow-priest-2v2/`. Внутри есть SPR-перспектива против RM, RR, WL/R, Feral/R, Druid/War, Hpala/War, Rsham/War, DPriest/Mage и др. — **инвертируется** под наши матчапы.
- ⚠ **mmo-champion SPR-тред — WotLK-эпохи** (Psychic Horror, Dispersion, Penance, DK, resil 1.2k). **НЕ использовать для TBC-драфтов** (протащит не-TBC механику). Хороший пример source-confusion.
- `ownedcore` (server-rendered, WebFetch ok): Gog123456 «2v2 RP & 3v3 PMR» (2008, оригинальный TBC) — есть чистая секция **Mirror Match PMR v PMR** (использована для rmp-mirror).
- Обзорные comp-страницы WT/silentshadows дают cite-уровень: counter-листы, kit, strengths/weaknesses (напр. «RM контрит SPR»).
- WebSearch-сводки путают соседние матчапы — проверяй. Видео: `yt-dlp` на субтитры.
- См. память: [[kb-source-fetchability]].

## 8. Стиль работы
- Перед большой задачей/фазой: `AskUserQuestion` — «допущения для X: A, B, C — подтверди».
- Маленькие запускаемые инкременты; показывай результат (`present_files`) и жди approve перед merge.
- Отвечай по-русски; финал — кратко.

## 9. Следующие шаги (батч 2026-06-23 закрыт — старт отсюда)
Закрыто 2026-06-23: `spriest+rogue` (sourced спек-ячейка ×RM/RP), `rmp-mirror`, `warrior+rogue`/`warrior+mage`/`hunter+rsham` (гипотезы ×RM/RP), **3v3 RLP, RLD, MLP, Shadowplay, double-healer(MPSham), WMP, Hunter/Disc/Druid** (sourced через WT/Skill Capped tier-lists). **Все S+A топ-3v3 из tier-листов покрыты.**

Дальше (мета вперёд):
- **3v3 остаток (B и ниже):** Warrior+RSham+Priest/Druid (B), Warrior+Mage+Druid (WMD, B), Warrior+Sub Rogue+Disc, Hunter+Warlock+Druid, Rogue+Feral+Disc и т.п. Источники WT/SkillCapped 3v3 (WT через Chrome, SkillCapped через WebFetch) дают tier-каркас — паттерн community-sourced. Ценность ниже (long-tail) — по желанию владельца.
- **6 гипотез (`warrior+rogue`/`warrior+mage`/`hunter+rsham` ×RM/RP) НЕ апгрейдятся** из tier-листов — их там нет (не мета 2v2). Для sourced нужен RM/RP-POV видео (yt-dlp) или форум по конкретной паре; иначе остаются гипотезами.
- **Оставшаяся 2v2-мета ⬜:** `warrior+warrior`, `warrior+hunter`, `warrior+priest`, `warrior+warlock`, `paladin+*`, `priest+priest`, `shaman+*`, зеркала (`mage+mage`, `druid+druid`).
- **Спек-варианты:** при нахождении источников добавлять в `SPEC_VARIANTS_2V2` (`coverage_matrix.py`) — напр. frost/fire mage, arms/prot warrior, BM/MM hunter, balance/feral druid там, где спек реально меняет тактику.
- **Глоссарий-дыра:** для spriest-механик нет ability-слагов (`silence`, `mind-blast`, `shadow-word-death`, `dispel-magic`, `mass-dispel`) — сейчас написаны прозой. Если будем расширять priest/3v3-контент — добавить их в `kb/glossary/abilities.json` (+ sync slang).
- Нативное уведомление «матчап = AI-синтез» — решение отложено владельцем «когда соберём все матчапы».
- После новых драфтов: `tools/render_slang.py --all`, `python tools/coverage_matrix.py`, обновить счётчик в `tests/test_kb_loader.py`.

---

## Сессия 2026-07-11 — v0.3.0: Phase 4.1 + Mac-мост + Windows-ревью

- **Phase 4.1 починена**: real-time матчинг по базовым классам врагов
  (`comp_to_classes`, `KBIndex.find_by_classes`, `KBRetriever.find_realtime_candidates`)
  + фильтр по нашему составу. DM на открытие ворот: опенер, килл-таргет, сложность,
  таргетинг под класс игрока; неоднозначные спеки → альтернативы в DM.
- **In-fight подсказки**: TRINKET + ключевые дефы (`_ABILITY_HINT_KEYS`) с
  `HintThrottle` (20с/60с). CC-касты не хинтятся. Новый статус `throttled`.
- **Аддон 0.2.0**: ARENA_START с союзниками (игрок первый), re-emit при выходе
  из стелса (дедуп), bracket из GetBattlefieldStatus, форс-флаш чат-лога
  (`LoggingChat(false→true)`, `/ac flush on|off`).
- **Bridge v0.3.0**: автодетект `WoWChatLog.txt`/`Chat-*.txt` (ГЛАВНАЯ находка ревью:
  стандартное имя — WoWChatLog.txt, ADR-0003 ошибался), защита от усечения и оборванных
  строк, `utf-8-sig` для bridge.env (BOM Блокнота), `$BRIDGE_OUR_COMP` fallback.
- **Windows-ревью**: чеклист в конце `docs/TESTING.md`. 4 бага починено, остальное ОК.
- **Тесты**: 146 passed (`tests/test_bridge_chat_autodetect.py`,
  `tests/test_bridge_allies.py`, `tests/test_realtime_matching.py` — новые);
  ruff/mypy зелёные; `tools/e2e_dryrun.py` обновлён под v0.3.0-сценарий и прогнан.
- **След. шаг**: `git push` + тег `v0.3.0` (владелец) → Actions собирает Mac+Win бинари
  → живой тест по `docs/TESTING.md`.
- Не закоммичен: `kb/glossary/slang — ред.md` (NBSP в имени, редакторская копия) —
  решить судьбу (переименовать/удалить).
