# Arena Coach — ежедневный скан источников, отчёт 2026-07-19

> Авто-запуск `arena-coach-daily-source-scan`. Владелец отсутствовал — действовал автономно, **ничего не аппрувил, не мёржил и не промоутил в `kb/drafts/`**. Все правки ниже — **предложения**, не применены к живой KB.

## TL;DR

- **Нетто в живой KB: 0 новых драфтов, 0 гипотез засорсено.** `kb/drafts/` остаётся 51, гипотезы не помечены. Причина — см. §3 (решение зарезервировано за владельцем, handoff §9).
- **НО впервые за серию сканов найдены 2 реальных, верифицируемых источника** по паре `hunter+resto-shaman`, которых прошлые сканы не находили: **Icy Veins Resto Shaman PvP guide** (shaman-side, upd. Jan 2026) и **OwnedCore тред 83143** (tfortyranth, TBC S3). Из них собраны **2 готовых-к-применению sourced-драфта** (`rm-` и `rp-vs-hunter-rsham`) — **застейджены в `docs/proposals/`**, ждут go/no-go владельца (§3).
- **Репо зелёное:** `validate-kb kb/drafts/` → **51 OK**; `pytest tests/` → **146 passed**. Трекнутые файлы не изменены (гипотезы/тест-счётчик откачены в исходное состояние).
- **4 конкретных enrichment-предложения** для существующих драфтов из тех же двух источников (§5) — включая одну сильную (public-cite вместо paywalled-only для `rp-vs-hunter-rdruid`).

## 1. Что просканировано и с каким результатом

| Источник | Доступ этот ран | Итог |
|---|---|---|
| **AOEAH 2v2 tier-list** (`/news/4283`) | WebFetch (server-rendered) ✅ | Полный текст. Наши: **RM = S**, **Rogue+Disc Priest = S**. Enemy hunter+rsham / hunter+hpala / mage+rdruid — **не названы**. Полезная строка: «Arms Warrior + Restoration Shaman… no reliable dispel… **Loses hard to coordinated Mage teams**». |
| **Icy Veins — Restoration Shaman PvP** | WebFetch (server-rendered) ✅ | **Новый пригодный источник.** Shaman-side механики (см. §2). Автор Seksi, upd. 12 Jan 2026 → актуально для Anniversary. |
| **OwnedCore 83143** (rogue/disc-priest→1850) | WebFetch (server-rendered) ✅ | **Новый пригодный источник.** Per-matchup секции (Druid/Hunter, hunter/rogue, Warrior/Shaman, Rogue/Shadowpriest). Автор tfortyranth, TBC S3 (2008) — чистый TBC. |
| **silentshadows.net** (disc-rogue mirror) | WebFetch | Отдаёт **WT nav-shell** (75k, только меню) — как источник не годится (подтверждает находки прошлых сканов). |
| **warcrafttavern.com** (Mage/Rogue, Resto-Shaman strat) | WebFetch | Client-rendered → только шелл. Для полного текста нужен Chrome MCP (в авто-ране недоступен). |
| **WebSearch-сводки** | — | Полезны как указатели; per-pair тактик не дают, путают соседние матчапы (напр. смешивают warrior+rsham с hunter+rsham). |

## 2. Два новых источника — что именно в них есть

**Icy Veins — Restoration Shaman PvP Guide** — `https://www.icy-veins.com/tbc-classic/restoration-shaman-pvp-guide` (Seksi, upd. 2026-01-12):
- «Restoration Shamans are **relatively weak in 2v2 and 3v3**… reliance on high cast times… **vulnerable to being interrupted or crowd controlled**.»
- Grounding Totem «**instantly nullify incoming enemy spells**, which is of great value against any caster team».
- Tremor Totem «removing charm, **fear** and sleep… amazing against fears… **beware… Priests fearing at the same time they attack your totem**».
- Purge «remove up to two beneficial magic effects… **strip kill targets clean**… against the… HoTs and shields of Priests and Druids».
- Best 2v2 партнёры шамана = **RetPala / Warrior / Rogue** (хантер НЕ в списке → пара hunter+rsham off-meta). Мана легко теряется.

**OwnedCore 83143** — `https://www.ownedcore.com/forums/world-of-warcraft/world-of-warcraft-guides/83143-rogues-disc-priest-way-up-1850-rating-2v2-guide.html` (tfortyranth):
- **Druid/Hunter:** «Hunter will **vipersting youre priest, kite you around**, while youre rooted, frozen, Cycloned, and **scattered**. i would **take down his pet** if i can… let the priest drain… its hard, but thats basicly every team with a hunter or a mage.»
- **Warrior/Shaman:** «let youre priest use **rank 1 smites on the shamans totems**… make sure the Windfury totem is down.»
- **Rogue/Shadowpriest:** «Take the one with the fearward… nuke one… pop in a fear… throw in a blind… vanish/sap the CC one… problem when these rogue/sp are **undeads** (WotF).»

## 3. Пара `hunter+resto-shaman` (RM и RP) — РЕШЕНИЕ ЗА ВЛАДЕЛЬЦЕМ

**Что подготовлено:** два полных sourced-драфта по канонической схеме (frontmatter + Opener / Alternative opener / If enemy trinkets / Common mistakes / Key cooldowns; inline-способности только из glossary; блок `sources` с тремя трейсабельными URL). Оба прошли `validate-kb` и ability-resolution, когда лежали в `kb/drafts/`. **Застейджены (не в живой KB):**

- `docs/proposals/rm-vs-hunter-rsham.draft.md`
- `docs/proposals/rp-vs-hunter-rsham.draft.md`
- (+ `*.slang-preview.md` — авто-рендер, регенерится `render_slang.py --all` после применения)

**Почему НЕ промоутил сам (честно):** handoff §9 и сканы 07-11…07-17 зафиксировали решение владельца — long-tail пары вроде `hunter+rsham` **не апгрейдятся «по генерик-паттерну»**; для sourced нужен **RM/RP-POV источник по конкретной паре** (Mirlol-паста или видео/форум именно по этой паре). Мои два источника — сильнее прежнего (Icy Veins даёт shaman-side из первых рук, OwnedCore — поведение хантера), **но ни один не является per-pair RM/RP-гайдом по hunter+rsham**: Icy Veins — класс-гайд шамана, OwnedCore — соседние секции (Druid/Hunter + Warrior/Shaman). Это ровно тот «generic-pattern» кейс, что §9 оставляет на решение владельца. Инструкция авто-задачи в спорном случае предписывает отчёт, а не write-действие → застейджил как предложение.

**Оценка качества:** по трейсабельности эти два драфта **на уровне** уже засорсенных (comp-anchor + community-tier + `synthesized-execution`, помечены `community-sourced`/`needs-top-source`/`synthesized-execution`). Каждое тактическое утверждение привязано к источнику или помечено как синтез. Никакой фабрикации/фейк-ссылок.

**Как применить (если ОК):**
```bash
mv docs/proposals/rm-vs-hunter-rsham.draft.md  kb/drafts/rm-vs-hunter-rsham.md
mv docs/proposals/rp-vs-hunter-rsham.draft.md  kb/drafts/rp-vs-hunter-rsham.md
# пометить гипотезы sourced-promoted (как у rp-vs-warrior-mage), затем:
python tools/render_slang.py --all
# счётчик в tests/test_kb_loader.py: 51 → 53
python -m arena_coach validate-kb kb/drafts/   # ждём 53 OK
python -m pytest tests/                          # ждём green
# и только потом, если решишь пустить игрокам:
python -m arena_ingest review approve --slug rm-vs-hunter-rsham   # (по желанию)
```
**Если no-go:** оставить в `docs/proposals/` или удалить — пары остаются гипотезами.

## 4. Остальные 2 непроверенные гипотезы — без изменений

| Гипотеза | Пара | Почему не засорсено этим сканом |
|---|---|---|
| `rm-vs-mage-rdruid` | Mage / Resto Druid × RM | Пара не в AOEAH; отдельного RM-POV гайда по mage+rdruid нет. Есть лишь общие заметки (Cyclone рвёт kill, double-caster+healer живучее double-mage) — недостаточно для полного sourced-драфта. RP-аналог был засорсен ранее через DPR-гайд, но это DPR-POV. |
| `rm-vs-hunter-hpala` | Hunter / Holy Paladin × RM | Пара off-meta, не в AOEAH; Wowhead hpala-гайд покрывает **warrior**/paladin, не hunter/paladin. RP-аналог засорсен через DPR-текст, у RM такого нет. |

**Вывод:** структурно long-tail. Нужен Mirlol-паста или RM-POV видео/форум по конкретной паре.

## 5. Enrichment существующих драфтов — предложения (не применены)

Все четыре — **только добавление source-блока** (усиление трейсабельности), тактика тела НЕ меняется. Прецедент — `rm-vs-warlock-hpala` (2-й source добавлен).

**5.1 (сильное) `rp-vs-hunter-rdruid`** — сейчас источник **только** paywalled-транскрипт Mirlol (`type: file`, 1 шт). OwnedCore 83143 имеет **прямую секцию Druid/Hunter** — публичный, верифицируемый per-pair cite. Готово к вставке:
```yaml
- type: web
  url: "https://www.ownedcore.com/forums/world-of-warcraft/world-of-warcraft-guides/83143-rogues-disc-priest-way-up-1850-rating-2v2-guide.html"
  title: "OwnedCore 83143 (tfortyranth) — секция Druid/Hunter: «Hunter will vipersting youre priest, kite you around... Cycloned, and scattered... take down his pet... let the priest drain the druid» — прямая корроборация RP-vs-hunter/druid"
  retrieved: '2026-07-19'
```

**5.2 (сильное) `rp-vs-retpala-rsham`** — сейчас **1 source**, шаман-механику (grounding и т.д.) держит прозой без cite. Icy Veins Resto Shaman — чистый источник на shaman-kit:
```yaml
- type: web
  url: "https://www.icy-veins.com/tbc-classic/restoration-shaman-pvp-guide"
  title: "Restoration Shaman PvP (Icy Veins, Seksi, Jan 2026) — shaman «relatively weak in 2v2... vulnerable to interrupt/CC»; Grounding «instantly nullify incoming enemy spells»; Purge strips HoTs/shields; mana-fragile"
  retrieved: '2026-07-19'
```

**5.3 (среднее) rsham-кластер** — `rp-vs-warrior-rsham`, `rm-vs-warlock-rsham`, `rm-vs-retpala-rsham`, `rp-vs-warlock-rsham`, `rm-vs-warrior-rsham`: активно ссылаются на grounding/tremor/purge прозой. Тот же Icy Veins source-блок (5.2) корроборирует эти механики (в т.ч. tremor↔fear и totem-stomp взаимодействие).

**5.4 (среднее) `rm-vs-rogue-spriest` / `rp-vs-rogue-spriest`** — OwnedCore 83143 имеет секцию **Rogue/Shadowpriest** (приоритет цели по fear-ward; fear→blind→vanish/sap; предупреждение про undead WotF) — 2-й forum-cite к уже существующему Windz-гайду.

## 6. Ждёт владельца

- **Go/no-go по §3** — 2 драфта hunter+rsham (RM+RP) в `docs/proposals/`. Это первый ран, где по этой паре есть реальные источники; решение о планке — за тобой.
- **(Опц.) 4 enrichment-правки §5** — добавление source-блоков; самая ценная — `rp-vs-hunter-rdruid` (public-cite вместо paywalled-only).
- **2 гипотезы** (`rm-vs-mage-rdruid`, `rm-vs-hunter-hpala`) ждут per-pair источника.
- **Инфра-нюанс:** в `.git/index.lock` висит stale-lock (не смог снять из песочницы — «Operation not permitted»). Если локальный `git` ругается «Another git process seems to be running» — удали `.git/index.lock` вручную.

_Проверка: `pip install pydantic pydantic-settings PyYAML pytest pytest-asyncio` + editable `backend`/`ingest`/`bridge` (в песочнице) → `python -m arena_coach validate-kb kb/drafts/` = **51 OK** → `python -m pytest tests/` = **146 passed**. Трекнутые файлы репо не изменены._
