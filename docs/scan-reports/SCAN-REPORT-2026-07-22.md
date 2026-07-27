# Arena Coach — ежедневный скан источников, отчёт 2026-07-22

> Авто-запуск `arena-coach-daily-source-scan`. Владелец отсутствовал — действовал автономно.
> **Ничего не аппрувил, не мёржил в `kb/matchups/`, новых драфтов не создавал, трекнутые файлы `kb/` не менял.**
> Единственная запись — этот отчёт в `docs/`.

## TL;DR

- **1 новый пригодный источник:** **PvPSkills — 3v3 Arena Compositions** (`pvpskills.com/guides/3v3-compositions`, Vaionex, 2026). Server-rendered, TBC-чистый, structured. Даёт **опубликованный RMP-опенер + target priority** и разбор WLD/Shadowplay/Drain-комп. Ценно тем, что весь наш RMP-кластер (9 драфтов) сейчас держится на `synthesized-execution` с cite только из tier-листов — это **первый published RMP-POV опенер**, которым его можно корроборировать.
- **koroboost.com — НЕ новый.** Всплыл в выдаче как «TBC Arena Guide 2026», но уже зацитирован в `rmp-vs-warrior-warlock-druid.md` (community-tier, под тезис «WLD — контра RMP»). Это коммерческий boost-SEO: generic comp-overview, наши off-meta пары не покрывает, трейсабельность ниже существующих cite → нового применения не нашёл.
- **Гипотезы: 0 засорсено.** Все 4 оставшиеся (`rm-vs-hunter-hpala`, `rm-vs-mage-rdruid`, `rm/rp-vs-hunter-rsham`) заново подтверждены как off-meta: ни PvPSkills, ни koroboost, ни свежие WebSearch по конкретным парам не дали per-pair RM/RP-якоря. Пары `hunter+rsham` — по-прежнему застейджены в `docs/proposals/` (решение владельца, висит с 07-19).
- **3 конкретных enrichment-предложения** для RMP-драфтов из PvPSkills (§4) + один tier-дискрепанс к сведению (§4.2).
- **Репо зелёное:** `validate-kb kb/drafts/` → **51 OK**; `pytest tests/` → **146 passed**. Счётчик драфтов не менялся (новых драфтов нет).

## 1. Что просканировано и с каким результатом

| Источник | Доступ этот ран | Итог |
|---|---|---|
| **PvPSkills — 3v3 Arena Compositions** | WebFetch (server-rendered) ✅ | **Новый пригодный источник.** Полный текст: RMP-опенер, target priority, разборы WLD/Warrior Cleave/Jungle/Shadowplay + 3v3 tier-list. TBC-чистый (Scatter/Freezing Trap, Bestial Wrath, Mana Burn, SW:D, Shadowburn, Soul Link, Ice Block — без WotLK). См. §3. |
| **PvPSkills — Matchup Matrix** (`/matchups`) | WebFetch | **Client-rendered** — отдаёт только «Loading matchup data...». Интерактивная class-vs-class матрица через WebFetch недоступна (нужен Chrome MCP, в авто-ране нет). Comp-страницы при этом server-rendered и годны. |
| **koroboost.com — TBC Arena Guide (2026)** | WebFetch (server-rendered) ✅ | Полный текст. **Уже зацитирован** в `rmp-vs-warrior-warlock-druid.md`. Коммерческий boost-SEO, comp-overview-уровень; наши off-meta пары (hunter+hpala, mage+rdruid) не покрывает. Нового cite не даёт. |
| **WebSearch: RMP 3v3 anniversary; RM vs hunter/hpala; RM vs mage/rdruid** | — | Указатели, не источник. Как обычно, путают соседние матчапы (по запросу «RM vs mage/rdruid» выдал druid/**warrior** vs RM и rogue/rdruid — обе пары **уже засорсены**, а не искомую mage+rdruid). Подтвердили off-meta-статус оставшихся гипотез. |
| Icy Veins 3v3 rankings / WT 3v3 tier-list | (в выдаче) | Уже основа RMP-кластера. Нового нет. |

**Meta-факт (контекст, не тактика):** несколько источников этого рана подтверждают Anniversary-твик — оружие с арены теперь с **1700 рейтинга** (в оригинальном TBC было 1850). На матчап-тактику не влияет, фиксирую для полноты.

## 2. yt-dlp / YouTube

yt-dlp в песочнице **не установлен**, а shell-запрос к YouTube за субтитрами — это программный веб-фетч в обход WebFetch (нарушает web-fetch-политику окружения). Прошлые сканы 07-19/07-20 по факту тоже не гоняли yt-dlp, а работали через WebSearch/WebFetch — следую тому же прецеденту. YouTube-транскрипты по конкретным off-meta парам остаются задачей, которую владелец может прогнать локально (yt-dlp разрешён в проектной среде).

## 3. PvPSkills — что именно в нём есть

`https://www.pvpskills.com/guides/3v3-compositions` (Vaionex Corporation, © 2026, fan-guide):

**RMP (S-tier, Very Hard).** Published-опенер (дословно):
> 1 Sap healer · 2 Cheap Shot kill target · 3 Mage Poly 3rd target · 4 Kidney Shot + burst · 5 Blind → Poly healer (new DR)

Target priority: **Warlock (после смерти пета) → Shadow Priest → Resto Druid (в станах)**. Win condition: «Chain CC the healer while bursting a DPS target. Force trinket, then kill in the next CC chain.»

**WLD (S-tier).** Win condition: «Spread DoTs, train healer with Warrior, win through mana drain + sustained pressure. Kill when healer goes OOM.» Strengths: «Very tanky (Soul Link + Plate + Bear form)», «**Good vs RMP (survives burst)**». Weaknesses: «Slow kills — games take 5-10 min», «**Weak if Druid gets caught in CC**», «**Can lose to heavy burst before attrition kicks in**».

**Shadowplay (Spriest/Warlock/Healer, A-tier)** + в tier-листе отдельно **Drain Comp (Lock/Spriest/Rsham) = S-tier**. Механика: «Full DoT all 3 targets, fear chains, Mana Burn healer, kill through rot or hard swap when someone's low»; fear-цепочки на разные DR («Priest Fear → Warlock Fear → Psychic Scream»); «hard swap with **Shadowburn + SW:D**».

**PMR (Priest/Mage/Rogue) = A-tier** — по сути наш rmp-mirror.

3v3 tier-list PvPSkills: S — RMP, WLD, RLS, Drain(Lock/Spriest/Rsham); A — Warrior Cleave, Jungle Cleave, Shadowplay, PMR, Ele Cleave; B — PHP, Ret Cleave, MLD, TSG.

## 4. Enrichment-предложения для RMP-драфтов (НЕ применены)

Все — только добавление source-блока (усиление трейсабельности); тактический каркас тел не меняется. Прецедент — как прошлые сканы добавляли 2-й cite.

### 4.1 (сильное) `rmp-vs-warrior-warlock-druid` (WLD) — независимая корроборация core-плана

Драфт сейчас: Skill Capped + WT + koroboost + YouTube, весь `synthesized-execution`. PvPSkills со **стороны WLD** прямо подтверждает наш каркас: «Good vs RMP (survives burst)» (почему матчап very-hard), «Weak if Druid gets caught in CC» (= наш тезис: burst в окно, когда druid под CC), «Can lose to heavy burst before attrition kicks in» (= «нужен чистый CC-сетап и быстрый kill-window»). Готово к вставке:

```yaml
- type: web
  url: "https://www.pvpskills.com/guides/3v3-compositions"
  title: "3v3 Arena Compositions (PvPSkills, Vaionex, 2026) — WLD S-tier: win «spread DoTs, train healer, win through mana drain»; «Good vs RMP (survives burst)»; weakness «Weak if Druid gets caught in CC», «Can lose to heavy burst before attrition kicks in»"
  retrieved: '2026-07-22'
```

### 4.2 (сильное) `rmp-vs-shadow-priest-warlock-resto-shaman` (Drain/Shadowplay) — 2-й cite + tier-дискрепанс

Драфт сейчас: WT + Skill Capped (**B-tier Shadowplay**). PvPSkills подтверждает enemy-side механику (spread-DoT, fear-цепочки на разные DR, Mana Burn хилера, hard-swap Shadowburn+SW:D) — ровно то, от чего строится наш план (быстрый kill immobile SP, не передиспеливать весь spread).

⚠ **Tier-дискрепанс к сведению владельца:** PvPSkills рейтит вариант с resto-shaman хилером как **Drain Comp = S-tier** (наш cite — Skill Capped **B-tier «Shadowplay»**). Наш `difficulty: hard` — POV-оценка, тир-плейсмент ≠ наша сложность, менять поле не предлагаю; но расхождение S-vs-B стоит знать (возможно, Anniversary-мета подняла drain-вариант).

```yaml
- type: web
  url: "https://www.pvpskills.com/guides/3v3-compositions"
  title: "3v3 Arena Compositions (PvPSkills, Vaionex, 2026) — Drain Comp (Lock/Spriest/Rsham) S-tier / Shadowplay A-tier: «Full DoT all 3, fear chains on different DR (Priest Fear → Warlock Fear → Psychic Scream), Mana Burn healer, hard swap with Shadowburn + SW:D»"
  retrieved: '2026-07-22'
```

### 4.3 (среднее) `rmp-vs-rogue-mage-priest` (mirror/PMR) — современный 2-й cite к форуму 2008

Драфт сейчас: единственный cite — Gog123456/ownedcore (2008). PvPSkills даёт **современный (2026) published RMP-опенер** (Sap healer → Cheap Shot kill → Poly 3rd → Kidney+burst → Blind→Poly healer new DR), который корроборирует нашу синтезированную combo-цепочку (premed→cheap→kidney + shatter) и DR-менеджмент sap/sheep/kidney. Не меняет тактику, но добавляет свежий independent-якорь к лаконичному форум-посту.

```yaml
- type: web
  url: "https://www.pvpskills.com/guides/3v3-compositions"
  title: "3v3 Arena Compositions (PvPSkills, Vaionex, 2026) — RMP опенер «Sap healer → Cheap Shot kill target → Mage Poly 3rd → Kidney Shot + burst → Blind → Poly healer (new DR)»; target priority Warlock(after pet)→SPriest→Resto Druid"
  retrieved: '2026-07-22'
```

### 4.4 (опц.) общий RMP-опенер как cite ко всему кластеру

Тот же source-блок 4.3 — единственный **published RMP-POV опенер**, который у KB появляется впервые (сейчас всё execution — `synthesized-execution`). По желанию владельца можно добавить его вторым cite и к остальным RMP-драфтам (RLP/RLD/MLP/WMP/double-healer/Hunter-Disc-Druid) как общий каркас-якорь. Осторожно: PvPSkills — fan-aggregator, не top-player POV → тег `needs-top-source` остаётся, тир не апгрейдится.

**Что PvPSkills НЕ закрывает (проверено, чтобы не протащить wrong-comp cite):** `rmp-vs-mage-warlock-priest` (у PvPSkills MLD=mage+lock+**druid**, не MLP), `rmp-vs-hunter-priest-druid` (у PvPSkills PHP=pala+hunter+priest, не hunter+**disc-priest**+druid), `rmp-vs-mage-priest-resto-shaman` (double-heal не разобран). Для них PvPSkills НЕ cite.

## 5. Оставшиеся гипотезы — статус без изменений

| Гипотеза | Пара | Что этот ран | Вердикт |
|---|---|---|---|
| `rm-vs-hunter-hpala` | Hunter / Holy Paladin × RM | Не в PvPSkills 2v2/3v3 (PHP — это pala+hunter+priest 3v3, не наша 2v2-пара). Не в koroboost. | **Остаётся гипотезой.** Нет per-pair RM-POV якоря. |
| `rm-vs-mage-rdruid` | Mage / Resto Druid × RM | WebSearch по паре выдал только соседние (druid/warrior, rogue/rdruid — обе уже засорсены). Не в PvPSkills/koroboost. | **Остаётся гипотезой.** |
| `rm-vs-hunter-rsham` | Hunter / Resto Shaman × RM | Драфт готов и застейджен `docs/proposals/rm-vs-hunter-rsham.draft.md` (07-19). | **Ждёт go/no-go владельца.** |
| `rp-vs-hunter-rsham` | Hunter / Resto Shaman × RP | Драфт готов и застейджен `docs/proposals/rp-vs-hunter-rsham.draft.md` (07-19). | **Ждёт go/no-go владельца.** |

Прочие 12 файлов `kb/hypotheses/` — устаревшие дубликаты пар, у которых **уже есть засорсенный draft** (rogue-hpala, mage-hpala, warlock-hpala, hunter-hpala[RP], warrior-mage, warrior-rogue ×RM/RP): класс-ячейки ✅, гипотезы можно чистить (не моё решение — на владельца).

## 6. Ждёт владельца (сводка, с переносом из 07-19/07-20)

1. **§4.1–4.3 — три enrichment'а PvPSkills** для RMP-кластера (WLD, Drain/Shadowplay, mirror). Скажи «применяй» — впишу source-блоки, тело не трогаю. §4.4 (общий RMP-опенер ко всему кластеру) — опционально.
2. **§4.2 — tier-дискрепанс** Drain-компа: PvPSkills S-tier vs наш cite B-tier. К сведению.
3. **Висит с 07-19:** go/no-go по 2 драфтам `rm/rp-vs-hunter-rsham` в `docs/proposals/`.
4. **Висит с 07-20:** 6 enrichment-предложений (§5.1–5.6 отчёта 07-20) — DR-коллизии друида (9 драфтов), Mass Dispel против бабла (5 RP-hpala), Spellsteal BoF/BoP + BoP-снимает-Kidney (4 RM-hpala), The Beast Within, Concentration Aura. Не применены.
5. **2 гипотезы** (`rm-vs-hunter-hpala`, `rm-vs-mage-rdruid`) ждут per-pair источника (yt-dlp/форум по конкретной паре).
6. **Уборка (опц.):** 12 устаревших дубликат-гипотез (пары уже в `drafts/`); незакоммиченный `kb/glossary/slang — ред.md` (решить судьбу, из 07-11).

---

_Проверка: `pip install pydantic pydantic-settings PyYAML pytest pytest-asyncio SQLAlchemy aiosqlite cryptography httpx fastapi discord.py anthropic --break-system-packages` + `PYTHONPATH=backend:ingest:bridge` (editable-инсталл невозможен — build-backend без PEP 660 hook, обошёл через PYTHONPATH) → `python -m arena_coach validate-kb kb/drafts/` = **OK: 51 документов** → `python -m pytest tests/` = **146 passed**. Трекнутые файлы `kb/`, `tests/` не изменены._
