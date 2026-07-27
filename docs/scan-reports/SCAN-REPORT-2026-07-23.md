# Arena Coach — ежедневный скан источников, отчёт 2026-07-23

> Авто-запуск `arena-coach-daily-source-scan`. Владелец отсутствовал — действовал автономно.
> **Ничего не аппрувил, не мёржил в `kb/matchups/`, новых драфтов не создавал, трекнутые файлы `kb/` не менял.**
> Единственная запись — этот отчёт в `docs/`.

## TL;DR

- **Chrome MCP в этом ране БЫЛ подключён** (Browser 1, macOS) — в отличие от авто-ранов 07-19…07-22, где Chrome не было. Это позволило **напрямую вытащить client-rendered Warcraft Tavern**, который прошлые сканы могли оценивать только по WebSearch-сводкам. Прочитаны вербатим: **WT 2v2 tier-list**, **полный гайд Deadlycoward «Rogue/Disc Priest 2v2» (20 матчапов)** и **RM-overview «Mage/Rogue»**. Плюс WebFetch: Icy Veins 2v2, Skill Capped 2v2, AOEAH 2v2, Wowhead Resto-Shaman arena guide.
- **Гипотезы: 0 засорсено** — но теперь вердикт «off-meta» подтверждён **прямым чтением канонических гайдов**, а не WebSearch-выводом. Все 4 оставшиеся пары (`rm-vs-hunter-hpala`, `rm-vs-mage-rdruid`, `rm/rp-vs-hunter-rsham`) **не названы ни в одном** из пяти tier-листов и **отсутствуют** в специализированных гайдах (Deadlycoward DP/R, Wowhead Resto-Sham). Комп-level якоря нет → промоут запрещён (был бы conflation/выдумка).
- **5 конкретных enrichment-предложений** (§4): пять RP-драфтов сейчас держатся на **одном** источнике (транскрипция Mirlol, май 2026). Гайд Deadlycoward (Infernal Gladiator, 2919 rating, top-11 world) даёт по каждому **независимый elite-POV разбор ровно той же пары** — готовые source-блоки прилагаю. Тела не тронуты.
- **Репо зелёное:** `validate-kb kb/drafts/` → **51 OK**; `pytest tests/` → **146 passed**. Счётчик драфтов не менялся (новых драфтов нет).

## 1. Что просканировано и с каким результатом

| Источник | Доступ этот ран | Итог |
|---|---|---|
| **WT — Rogue/Disc Priest 2v2 (Deadlycoward)** `…/rogue-disc-priest-2v2/` | **Chrome MCP** ✅ (client-rendered) | **Полный текст 20 матчапов.** TBC-чистый (Sap/Blind/Kidney/Garrote/Mana Burn/Cloak/WotF, Viper Sting, Frost Trap — без WotLK). Инвентарь матчапов — §3. Даёт 5 enrichment'ов (§4). |
| **WT — 2v2 Arena Tier List** `…/2v2-arena-tier-list/` | **Chrome MCP** ✅ | S/A/B тиры перечислены; **всё остальное — C-tier и ниже**. Hunter+Rsham, Hunter+Hpala, Mage+Rdruid **не названы**. |
| **WT — Mage/Rogue overview** `…/rogue-mage-rogue-arena-strategies/` | **Chrome MCP** ✅ | Overview (strengths/weaknesses/**counter-comps**/talents/видео), НЕ per-matchup. RM counter-comps: Human Rogue combs · Dwarf Disc+Mage/Lock · Rogue/Druid · Lock/Druid · **Lock/Hpala**. Mage/Druid, Hunter/Hpala, Hunter/Rsham — **не в списке**. |
| **Icy Veins — 2v2 comp rankings** (upd. 2026-01-12) | WebFetch ✅ | Best + «Other» таблицы. Есть **Hunter/Resto Druid**, Warr/Hpala, RetPala/Rsham, Mage/DiscPriest. **Нет** hunter+rsham, hunter+hpala, mage+rdruid. |
| **Skill Capped — 2v2 tier-list** (upd. 2026-01-19, Patch 2.5.5) | WebFetch ✅ | S…C по спекам. A: **Hunter+RestoDruid, Hunter+DiscPriest**; C: **FrostMage+HolyPaladin**. **Нет** hunter+rsham, hunter+hpala, mage+rdruid. |
| **AOEAH — 2v2 tier-list** (Dec 2025) | WebFetch ✅ | Богатый список S–D с описаниями. **Hunter+RestoDruid = S**, ArmsWarr+RestoShaman = A, MM Hunter+DiscPriest = A. **Нет** hunter+rsham, hunter+hpala, mage+rdruid. |
| **Wowhead — Resto Shaman Arena guide** (Woah, upd. 2026-02-10) | WebFetch ✅ | Специалист-гайд по resto-shaman. 2v2-партнёры названы **только**: Shaman/Warrior, Shaman/Ret, Shaman/Rogue. **Hunter НЕ в списке** — сильный негатив-сигнал для hunter+rsham. |
| WebSearch: «RM vs hunter/hpala», «RM vs mage/rdruid», «hunter resto shaman 2v2» | — | Указатели, не источник; путают соседние пары. Подтвердили off-meta-статус. |

**yt-dlp:** в песочнице не установлен; shell-фетч к YouTube = обход web-fetch-политики окружения. Как и сканы 07-19…07-22, не гонял. YouTube-транскрипты по конкретным off-meta парам — задача для локального прогона владельцем (yt-dlp разрешён в проектной среде).

## 2. Оставшиеся 4 гипотезы — статус без изменений (теперь с прямым доказательством)

| Гипотеза | Пара | Прямая проверка этого рана | Вердикт |
|---|---|---|---|
| `rm-vs-hunter-hpala` | Hunter / Holy Paladin × RM | Нет в 5 tier-листах. RM-overview counter-comps **не содержит** Hunter/Hpala (в отличие от Lock/Hpala, которым засорсен `rm-vs-warlock-hpala`). | **Гипотеза.** Нет RM-POV комп-якоря. |
| `rm-vs-mage-rdruid` | Mage / Resto Druid × RM | Нет в 5 tier-листах. RM-overview **не** называет Mage/Druid контрой (называет Rogue/Druid, Lock/Druid). RP-версия засорсена Deadlycoward'ом «Druid/Frost Mage», но его тактика (Mana Burn OOM + диспел) **не переносится на RM** (нет манабёрна/диспела) → для RM это была бы выдумка. | **Гипотеза.** |
| `rm-vs-hunter-rsham` | Hunter / Resto Shaman × RM | Нет в 5 tier-листах. Wowhead Resto-Sham guide **не** называет hunter партнёром. Драфт-кандидат застейджен `docs/proposals/rm-vs-hunter-rsham.draft.md` (07-19). | **Ждёт go/no-go владельца.** |
| `rp-vs-hunter-rsham` | Hunter / Resto Shaman × RP | То же + Deadlycoward DP/R guide **не имеет секции Hunter/Rsham** (есть Druid/Hunter, Rsham/Warr, Rsham/Ret — но не hunter+rsham). Застейджен `docs/proposals/rp-vs-hunter-rsham.draft.md` (07-19). | **Ждёт go/no-go владельца.** |

**Вывод:** пять независимых источников (3 tier-листа + WT tier-list + 2 специализированных гайда) сходятся — эти три пары off-meta и **не имеют** источника, оценивающего саму пару. Это устойчивый результат: дальнейший авто-сорсинг по ним без **per-pair** видео/форума бессмысленен.

Прочие 12 файлов `kb/hypotheses/` — устаревшие дубликаты пар, у которых **уже есть засорсенный draft** (класс-ячейки ✅). Чистка — на усмотрение владельца.

## 3. Инвентарь гайда Deadlycoward (что он покрывает — и чего нет)

`…/rogue-disc-priest-2v2/`, Undead Rogue/Priest POV, Infernal Gladiator (2919 rating). Разобранные матчапы (difficulty автора):

- **Healer/DPS:** DP/R mirror (5), **Druid/Rogue (9)**, **Druid/Hunter (10)**, Druid/SL-Lock (7), Druid/Warrior (7), Hpala/Warrior (7), Rsham/Warrior (5), DiscPriest/Mage (7), DiscPriest/SL-Lock (7), **Druid/Frost Mage (5)**, Rsham/Ret (7).
- **Double DPS:** Frost Mage/Rogue (7), Spriest/Rogue (5), Rogue/Rogue (7), SL-Lock/Rogue (7), Feral/Rogue (6), Warrior/SL-Lock (4), Spriest/Mage (7), Spriest/Aff-Lock (4).

**Нет секций:** Hunter/Resto-Shaman, Hunter/Holy-Paladin (подтверждает §2). Hunter покрыт только в связке **Druid/Hunter**.

## 4. Enrichment-предложения (НЕ применены — тела не тронуты)

Все пять драфтов сейчас цитируют **единственный** источник — транскрипцию `WOW TBC ARENA - Rogue Priest.md` (Mirlol, 2026-05-12). Deadlycoward даёт по каждому **вторую, независимую, elite-POV** привязку к **той же паре**. Добавляется только source-блок (усиление трейсабельности), тактический каркас не меняется. Прецедент — как прошлые сканы добавляли 2-й cite.

### 4.1 (сильное) `rp-vs-hunter-rdruid` — точный матчап 10/10
```yaml
- type: web
  url: "https://www.warcrafttavern.com/tbc/guides/rogue-disc-priest-2v2/"
  title: "Rogue/Disc Priest 2v2 (Deadlycoward, Infernal Gladiator) — «DPR vs. Druid / Hunter» (10/10): kill pet/hunter or druid; Sap hunter как Flare истекает; если друид вышел → Cheap Shot–Kidney–Gouge без DoT'ов, чтобы прийст мог Fear; alt-линия kill pet + Mana Burn hunter; core-угроза = Frost Trap RNG-роуты + Viper Sting мана-дрейн"
  retrieved: '2026-07-23'
```

### 4.2 (сильное) `rp-vs-rogue-mage` — точный матчап 7/10
```yaml
- type: web
  url: "https://www.warcrafttavern.com/tbc/guides/rogue-disc-priest-2v2/"
  title: "Rogue/Disc Priest 2v2 (Deadlycoward) — «DPR vs. Frost Mage / Rogue» (7/10): обычно kill rogue, редко mage; избегать sap (Spellsteal-угроза), держать дистанцию от прийста; Shadowstep/Garrote чтобы сорвать poly-on-priest сетап; нюанс тринкета Kidney"
  retrieved: '2026-07-23'
```

### 4.3 (сильное) `rp-vs-rogue-rogue` — точный матчап 7/10
```yaml
- type: web
  url: "https://www.warcrafttavern.com/tbc/guides/rogue-disc-priest-2v2/"
  title: "Rogue/Disc Priest 2v2 (Deadlycoward) — «DPR vs. Rogue / Rogue» (7/10): прийст спиной к стене от Garrote, стой раздельно от sap; бёрсти одного рога (bleeds/Vanish–Cheap–Evisc) до сброса Blind-DR; пил Cheap–Kidney по второму, если прийст в беде"
  retrieved: '2026-07-23'
```

### 4.4 (среднее) `rp-vs-mage-priest` — совпадение с нюансом спека
Enemy `mage+priest`; у Deadlycoward — «DPR vs. Discipline Priest / Frost Mage» (7/10). Совпадает, если вражеский прийст — **disc** (наиболее вероятный healer-вариант; shadow-версия — отдельная спек-ячейка). Ключевое: «Never go aggressive vs DP/M; kite mage around pillar с Mana Burns, restealth; держи Cloak до пиллара».
```yaml
- type: web
  url: "https://www.warcrafttavern.com/tbc/guides/rogue-disc-priest-2v2/"
  title: "Rogue/Disc Priest 2v2 (Deadlycoward) — «DPR vs. Discipline Priest / Frost Mage» (7/10): kill mage через OOM ЛИБО sap+full-dispel прийста; «never go aggressive vs DP/M»; кайт мага у пиллара + Mana Burns, restealth, Crippling Shiv обоих"
  retrieved: '2026-07-23'
  note: "Применять если vs=mage+disc-priest; для shadow-варианта — отдельная спек-ячейка."
```

### 4.5 (среднее) `rp-vs-warlock-priest` — совпадение с нюансом спека
Enemy `warlock+priest`; у Deadlycoward — «DPR vs. Discipline Priest / SL Warlock» (7/10). Совпадает при disc-прийсте + SL-локе.
```yaml
- type: web
  url: "https://www.warcrafttavern.com/tbc/guides/rogue-disc-priest-2v2/"
  title: "Rogue/Disc Priest 2v2 (Deadlycoward) — «DPR vs. Discipline Priest / SL Warlock» (7/10): kill priest (не dwarf) ЛИБО kill lock с высоким давлением; sap прийста; при опасности Crippling Shiv обоих и кайт длинными дистанциями (не у пилларов — у Disc/Lock нет poison-dispel), напр. Lordaeron из комнаты в комнату"
  retrieved: '2026-07-23'
  note: "Применять если vs=warlock+disc-priest."
```

**Реконфирмации (cite уже стоит, менять нечего):** `rp-vs-mage-rdruid` (Druid/Frost Mage 5/10), `rp-vs-rogue-hpala` (Hpala/Warrior 7/10 как анти-hpala каркас), `rp-vs-warrior-rsham` (Rsham/Warrior 5/10), `rp-vs-warlock-rogue` (SL-Lock/Rogue 7/10), `rp-vs-mage-hpala` (DP/M-обвязка) — все уже цитируют Deadlycoward, вербатим-чтение сегодня совпало с телами.

## 5. Ждёт владельца (сводка, с переносом)

1. **§4.1–4.3 — три сильных enrichment'а** (`rp-vs-hunter-rdruid`, `rp-vs-rogue-mage`, `rp-vs-rogue-rogue`): сейчас single-source (Mirlol) → добавить 2-й elite-cite Deadlycoward. Скажи «применяй» — впишу source-блоки, тела не трогаю.
2. **§4.4–4.5 — два средних** (`rp-vs-mage-priest`, `rp-vs-warlock-priest`): те же, с проверкой спека вражеского прийста (disc).
3. **Висит с 07-19:** go/no-go по 2 драфтам `rm/rp-vs-hunter-rsham` в `docs/proposals/`.
4. **Висит с 07-22:** enrichment'ы PvPSkills для RMP-кластера (§4.1–4.4 отчёта 07-22) + tier-дискрепанс Drain-компа.
5. **Висит с 07-20:** 6 enrichment-предложений (DR-коллизии друида, Mass Dispel против бабла, Spellsteal BoF/BoP, The Beast Within, Concentration Aura).
6. **2 гипотезы** (`rm-vs-hunter-hpala`, `rm-vs-mage-rdruid`) ждут per-pair источника (yt-dlp/форум по конкретной паре) — tier-листы их не покрывают (проверено этим раном напрямую).
7. **Уборка (опц.):** 12 устаревших дубликат-гипотез (пары уже в `drafts/`); незакоммиченный `kb/glossary/slang — ред.md` (из 07-11).

---

_Проверка: `pip install pydantic pydantic-settings PyYAML pytest pytest-asyncio SQLAlchemy aiosqlite cryptography httpx fastapi discord.py anthropic --break-system-packages` + `PYTHONPATH=backend:ingest:bridge` → `python -m arena_coach validate-kb kb/drafts/` = **OK: 51 документов** → `python -m pytest tests/` = **146 passed**. Трекнутые файлы `kb/`, `tests/` не изменены._
