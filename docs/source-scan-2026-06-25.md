# Daily source-scan — 2026-06-25 (Arena Coach)

> Автозадача `arena-coach-daily-source-scan`. Ничего не аппрувлено и не смёржено — только подготовлены sourced-драфты в `kb/drafts/` и обновлены счётчики/покрытие. Approve — только владельцем: `python -m arena_ingest review approve --slug <slug>`.

## TL;DR
- **Засорсено 3 гипотезы → 3 новых sourced-драфта** (RM/RP vs Warlock+HPala, RP vs Hunter+HPala). Источники реальные, прочитаны напрямую через Chrome (Warcraft Tavern client-rendered).
- **Драфты: 41 → 44.** Покрытие (класс-уровень): ✅ 39→**42** · 🟡 14→**11** · ⬜ 202. Тест-счётчик в `tests/test_kb_loader.py` обновлён 41→44.
- **Зелёное:** `validate-kb kb/drafts/` = 44 OK; `pytest tests/` = 113 passed; ability-resolution чистая. (`ruff`/`mypy` локально не гонялись — нет в песочнице; гейтит CI на push.)
- **11 гипотез остаются без источника** (см. ниже) — корректно, не апгрейдил без реального source.

## Источники, найденные в этот скан (прочитаны напрямую)
Все три — server of truth = **Warcraft Tavern**, доставаемы только через Chrome MCP (`navigate`+`get_page_text`); WebFetch отдаёт лишь nav-шелл (подтвердил: 939 строк = одно меню). Браузер был подключён (Browser 1, macOS).

1. **WT — 2v2 Arena Tier List** (`/tbc/guides/2v2-arena-tier-list/`): полный список тиров с описаниями. Ключевое:
   - **Warlock/Holy Paladin = B-tier**: «If the enemy can't keep the Paladin from healing, you will win fights. It just takes a while. A long while.»
   - **Warrior/Holy Paladin = B-tier**: «struggling to find kills and unable to keep anyone CC'd for long».
   - **Hunter/Disc = A** («Viper Sting and Mana Burn» — мана-война), **Hunter/RDruid = A** («Viper Sting drains healer comps… constant attrition»), **Warrior/RSham = B** («sacrifices BoF and tankiness for higher burst — WF Totem + Bloodlust»), **Ret/RSham = A** («massive Ret burst… distinct lack of CC, both can be kited»), **Warlock/Disc = S** («catch out of position with Psychic Scream, chain dispel»), **Mage/Disc = S** («high defensive utility + CC, very slow but strong»), **Rogue/RDruid = S**, **Warlock/RDruid = S** («overwhelming CC… keep one player CC'd, slowly wear down»).
2. **WT — Mage/Rogue 2v2 Strategies** (`/tbc/guides/rogue-mage-rogue-arena-strategies/`): RM = «best double DPS», «insane burst», но **не Tier-1**, «suffers vs locks, RD comps, good discs». **RM Counter Comps**: Human Rogue combs, Dwarf Disc+Mage/Warlock, Rogue/Druid, Lock/Druid, **Lock/Hpala**.
3. **WT — Disc Priest/Rogue 2v2 Strategies** (`/tbc/guides/rogue-discipline-priest-rogue-arena-strategies/`): сильные стороны DPR (off/def dispels, Mana Burn pressure, mobility vs casters, reset/regen). **«DPR suffers a lot against mana drainers comps such as Hunter/Druid, Hunter/Priest, or even Hunter/HPaladin»**; weakness «vs mana drain (Hunters)» и «vs dual melee (esp. if not Dwarf)».

## Гипотезы → засорсены (переписаны в драфты)
| Hypothesis | → Draft | Якорь (источник) | difficulty / kill |
|---|---|---|---|
| `rm-vs-warlock-hpala` | `kb/drafts/rm-vs-warlock-hpala.md` | WT tier-list (Lock/HPala B, «keep paladin from healing») + WT RM-strategies («Lock/Hpala» в RM counters) | very-hard / warlock |
| `rp-vs-warlock-hpala` | `kb/drafts/rp-vs-warlock-hpala.md` | WT tier-list (Lock/HPala B) + WT DPR-strategies (mana-burn = win-con «не дать паладину хилить») | very-hard / warlock |
| `rp-vs-hunter-hpala` | `kb/drafts/rp-vs-hunter-hpala.md` | WT DPR-strategies (прямо: «Hunter/HPaladin» в списке комбо, против которых DPR «suffers a lot», mana drain) | hard / hunter |

Все три помечены тегами `community-sourced` / `needs-top-source` / `synthesized-execution`: comp-level факты (тир, win-con, kit) — из источника; пошаговая combo-последовательность синтезирована на каркасе механик TBC 2.4.3 (как у precedent `rm/rp-vs-warrior-rogue`). Соответствующие гипотезы помечены `status: sourced-promoted` + ✅-баннер, оставлены как исходники.

## Остаются гипотезами (источника НЕ нашёл — НЕ апгрейдил)
11 класс-ячеек / 11 файлов:
- `rm-vs-hunter-hpala` — для RP якорь есть (DPR counter-list), **для RM нет**: hunter/hpala не тирован в WT и не в RM counter-list. Нужен RM-POV источник.
- `rm/rp-vs-mage-rdruid` — **mage/rdruid не тирован** в WT 2v2 (тированы rogue/rdruid, lock/rdruid, hunter/rdruid, warrior/rdruid). RM-strategies называет контрами Rogue/Druid и Lock/Druid, но **не Mage/Druid**. Похоже, не мета-комбо → реального source по конкретной паре нет.
- `rm/rp-vs-mage-hpala`, `rm/rp-vs-rogue-hpala` — не тированы, не в counter-листах. Холи-пала как слабый/немобильный хилер — общий anchor, но конкретные пары не засорсены.
- `rm/rp-vs-hunter-rsham` — hunter/rsham не тирован; WT называет hunter-мана-дрейн контрами Hunter/Druid/Priest/HPaladin, **shaman не в списке**. Паттерн «hunter+healer = attrition» есть, по конкретной паре — нет.
- `rm/rp-vs-warrior-mage` — подтверждение из прошлой сессии: не мета 2v2, в тир-листах отсутствует. Нужен POV-видео/форум по паре.

## Предлагаемые обогащения существующих драфтов (НЕ применял — на ревью владельца)
Источник для всех ниже — **WT 2v2 tier-list** (можно добавить в `sources:` соответствующих драфтов + усилить раздел «Common mistakes»/intro):
- `rm/rp-vs-warlock-rdruid`: WT (Lock/RDruid = **S**, «overwhelming CC, keep one player CC'd, slowly wear down») — добавить акцент: это CC-attrition, переживать цепочки CC, не оверкоммитить burst; (для RM) WT прямо относит Lock/Druid к RM-контрам.
- `rm/rp-vs-rogue-rdruid`: WT (Rogue/RDruid = **S**, «weaker damage… slow controlled match… multiple CC chains before any kill») — ожидать reset-войну; (для RM) Rogue/Druid в RM-контрах.
- `rm/rp-vs-warrior-rdruid`: WT (Warrior/RDruid = **A**, «Druid locks you in place… fight Warrior on their terms: mace stun + MS; **High CC comps can shut this team down**») — RM/RP именно high-CC; подчеркнуть mace-stun/MS-окна.
- `rm/rp-vs-retpala-rsham`: WT (Ret/RSham = **A**, «massive Ret burst + WF + Bloodlust… **distinct lack of CC, both can be kited**») — план: пережить burst-окно (WF/BL), кайтить обоих, эксплуатировать нехватку CC.
- `rm/rp-vs-warrior-rsham`: WT (Warrior/RSham = **B**, «sacrifices **Blessing of Freedom** and tankiness for higher burst — WF Totem + Bloodlust») — важный нюанс: **нет BoF** → наши root/snare/nova держатся; беречься burst-окон WF/BL.
- `rm/rp-vs-warlock-rogue`: WT (Rogue/Warlock = **B**, «don't synergize well… a lot of issues peeling») — эксплуатировать слабый peel/синергию.
- `rm/rp-vs-rogue-spriest`: WT (Rogue/SPriest = **B**, «kits don't synergize… struggles with peeling and synchronized CC») — согласуется с текущим драфтом; добавить tier-anchor.
- `rm/rp-vs-mage-priest`: WT (Mage/Disc = **S**, «very slow but strong») — ожидать медленный грайнд.
- `rm/rp-vs-warlock-priest`: WT (Lock/Disc = **S**, «catch out of position with Psychic Scream, then chain dispel») — не попадаться на scream-пик, беречь позицию.

## Прочее
- **Slang-дыра (pre-existing, не блокер):** `render_slang.py` напоминает, что `ambush, deadly-throw, expose-armor, pain-suppression, rupture, will-of-the-forsaken` используются в драфтах без slang-записи. См. память `slang-glossary-layer`. Кандидаты в `slang.json` при следующем расширении глоссария.
- **Для апгрейда оставшихся гипотез** нужен RM/RP-POV источник по конкретной паре: детальные WT-гайды (Deadlycoward «Disc/Rogue 20 matchups» — на их Discord; Windz SPR-гайд уже использован) или YouTube Rogue-POV (yt-dlp на субтитры). Tier-листы по этим парам каркас не дают (не мета).

## Approve-backlog (напоминание; делает только владелец)
Новые в этот скан (3): `rm-vs-warlock-hpala`, `rp-vs-warlock-hpala`, `rp-vs-hunter-hpala`. Плюс прежний backlog из handoff. NB: у всех тег `synthesized-execution` — перед approve желательно ревью топ-RM/RP.
