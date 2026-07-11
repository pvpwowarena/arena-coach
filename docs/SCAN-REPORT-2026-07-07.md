# Source-scan report — 2026-07-07 (авто-задача)

**Итог: +2 sourced-драфта** — `rm-vs-mage-hpala` и `rp-vs-mage-hpala` промоучены из гипотез. Разблокировка: comps-страницы **Skill Capped** (Season 2, Patch 2.5.5, upd. 2026-01-01) **называют пару тиром** — «C Tier: Holy Paladin + Frost Mage» на обеих сторонах (hpala-comps и fmage-comps). Это ровно условие (а) из пере-проверки 06-30 («источник, оценивающий саму пару»), conflation-блок снят честно, без склейки. Незасорсенных гипотез осталось **4**. Ничего не аппрувлено, в `kb/matchups/` ничего не мёржено.

**Проверки (green):** `validate-kb kb/drafts/` = **51 OK** · `pytest tests/` = **113 passed** · счётчик в `tests/test_kb_loader.py` обновлён 49 → **51** · `tools/coverage_matrix.py` перегенерирован (✅ 49 · 🟡 4 · ⬜ 202 класс-ячеек + spec ✅ 2) · `render_slang.py --all` перезапущен. Браузер подключён (Browser 1, macOS).

---

## 1. Промоут дня: mage+holy-paladin (обе стороны)

| Драфт | Якорь пары (primary) | Обвязка (secondary) |
|---|---|---|
| `rm-vs-mage-hpala` | Skill Capped hpala-comps + fmage-comps: пара **C Tier** (наш RM на той же странице — S Tier: FMage+SubRogue) | Icy Veins RM best-tier (цитата из rm-vs-warrior-mage, retrieved 06-27) |
| `rp-vs-mage-hpala` | те же two-way C Tier | Deadlycoward class-handling якоря 06-30 («OOM the mage, never go aggressive», «kill pala after no mana») — вплетены **с явной пометкой в sources**, что это соседние секции, НЕ оценка пары |

Оба: `tags: [community-sourced, needs-top-source, synthesized-execution]`, difficulty hard → **moderate** (тир-разрыв S vs C, по аналогии rm-vs-warrior-mage D→moderate), kill target mage. Гипотезы помечены `status: sourced-promoted` + ✅-баннер. Approve — только владелец: `python -m arena_ingest review approve --slug rm-vs-mage-hpala` / `rp-vs-mage-hpala`.

Методологическая заметка: SC comps-страницы — **per-class** (hpala/comps/, frost-mage/comps/ и т.д.), их не было в главном SC 2v2 tier-list (проверка 06-23 смотрела только его). Проверены и отрицательные: страниц restoration-shaman/comps и bm-hunter/comps **не существует** (пустой Next.js-шелл) → hunter+rsham SC-якоря не имеет; в fmage-comps 2v2 пары FMage+RDruid **нет** (только 3v3 RMD A-tier — другой брекет, не использовать).

## 2. Гипотезы: осталось 4 без источника

| Slug | Статус проверки сегодня |
|---|---|
| rm-vs-hunter-hpala | SC: hunter-гайдов нет, в hpala-comps пары нет (только Warr/Afflilock/FMage). AJ: пары нет (06-06). Блок прежний |
| rm-vs-hunter-rsham | SC-страниц обоих классов нет; AJ `BMHtr_Shm` = ele-шаман (не resto, 07-06). Блок прежний |
| rp-vs-hunter-rsham | то же. NB: коммент Woodblock (AJ Pri_Rog): «hunter anything with poison dispel will never lose to disc priest rogue» — категория, не пара; как якорь НЕ использован (conflation), но полезен как difficulty-сигнал при будущем сорсинге |
| rm-vs-mage-rdruid | fmage-comps 2v2 пары не содержит; AJ RM-гайд — пары нет. Блок прежний (нужен RM-POV или пара-оценка) |

Пути прежние: mirlol Twitch-sub владельца → `arena_ingest paste`; RM-POV VOD (см. §5 — свежий кандидат найден).

## 3. Enrichment-предложения (НЕ применял — жду отмашки; продолжение AJ-дочитки по плану 07-06)

Сегодня прочитаны 4 AJ-подстраницы (Wayback, июль 2008; паттерн RP-URL подтверждён: `Pri_Rog_vs_<Xxx_Yyy>`):

### 3a. `rm-vs-warlock-hpala` ← AJ Mage_Rogue vs Paladin/Warlock (Icycake, US-Nightfall)
Спек палы в гайде — хилер (dispel/BoF/bubble) → маппинг на наш драфт корректен. План автора: **фейк-фокус лока** → пала тратит BoF на него → свап на палу («all he can do is dispel»); sheep лока максимум 1-2 попытки (Azgoroth: felhunter снимает поли мгновенно + spell lock frost-школы); чейс палы без BoF → nova-root → **force bubble** → mage Ice Block + rogue CoS/Vanish переждать → добить палу после бабла, потом лока. Комменты: Barvi — sap лока, ранний burst палы до бабла, reset, mage hang back (detect invis), **Nagrand: инвиз до гейта** (maps_notes!); Grongel — альтернатива full-nuke лока с поли/CS палы; Iwln — дисент против reset-плана vs сильного lock/pala. Добавить named-author источник + Alternative opener + maps_notes.nagrand.

### 3b. `rm-vs-warrior-rsham` ← AJ Mage_Rogue vs Shaman/Warrior (Icycake + топ-комменты)
Самый детальный RM-POV план из добытых: **Dint (2000+ брекет, «80% побед»)**: рог открывает шамана стан-локом (CS → gouge → 5pt KS), burst в kidney → форс трикета; маг sheep/kite воина; давить до CS/kick хила → burst в silence → **stop DPS → blind шамана → mage IB + rogue vanish** → DR/KS/sheep ресетятся → full-duration sheep воина + garrote → 5pt KS → CS → добив с ≤50%. Обвязка: Jullommir — **evasion сразу на опенере** (disarm воина не срывает KS), ice lance съедает grounding; Genz — фростболты по шаману только в стане (earth shock/grounding), **silence на NS при низком HP шамана**; Victus — sap шамана в открытую = автовин; Icycake — **Blades Edge: шаман ставит тотем-лагерь внизу, тотемы работают наверх** (maps_notes!); Carrane/Luxbell — мotivированный дисент «kill warrior» (отразить в Alternative). Сильно конкретизирует текущий драфт.

### 3c. `rp-vs-warrior-hpala` ← AJ Pri_Rog vs Paladin/Warrior (Mixster, 2404 S2)
План автора: старт в воина (MB/SW:D), **дать воину intercept'нуться в прийста = вывести из LoS палы**, dispel Freedom постоянно, мана-бёрны+фиры на палу; ранний свап на палу сразу после траты Freedom на воина; окно килла палы при раннем bubble/trinket. Комменты: Outie — вариант «рог харассит палу» (mind-numbing+kick/gouge хилов, прийст соло-таскает воина) + **map-notes: BEM/Nagrand/Ruins точки танкования**; Noviolation (2401) — **evasion при defensive stance = disarm-предикт**, dwarf stoneform-стан, бейт pummel фейк-хилом при 65%+ HP, килл-чейн blind→sap→fear; Maraiah — дисент «rogue на палу с первого сапа»; Chromax — **MC-бейт**: bubble→каст MC, воин либо pummel'ит MC (фри GH+FH), либо ест MC. Хорошо дополняет существующий Deadlycoward-якорь (06-30) вторым named-author источником с другого POV.

### 3d. `rp-vs-hunter-rdruid` ← AJ Pri_Rog vs Druid/Hunter (Mixster: «hardest to beat»)
План автора: не LoS'ить хантера под Viper — наоборот, встать рядом и **спамить mana burn до нуля** (съесть bash/root/scatter/silencing как цену); shadowfiend в хантера/пета; **deliberate pet-kill**: fear друида → burst пета (SW:D/MB/**Smite** — Woodblock: у пета 150-180 shadow resist, smite нерезистится); Chingwang: PI+bubble smite-спам пета; **после смерти пета — fear друида + full KS хантера + PI mana burn в ноль = нет ресаммона** (1200 маны = порог второго пета, Azurriku, «90% побед»); Ordin/Pebbel — **ранний blind друида = бейт трикета** (blind CD < trinket CD, «все трикетят блайнд»); дисент: Kiryll (2200, mutilate) — свап в ДРУИДА при его выходе, KS беречь под caster-form; Setyo (opponent-POV) — почему комп считает себя контрой (scatter под pet-nuke, dismiss pet). Difficulty «very-hard» дополнительно подтверждена (у Deadlycoward уже 10/10). Плюс общий нюанс: дисент Woodblock (Pri_Rog main) про hunter+poison-dispel компы.

### 3e. Мелкие named-tier якоря из SC comps-страниц (добавить в sources)
- `rm-vs-hunter-rdruid`, `rp-vs-hunter-rdruid`: SC rdruid-comps — «**A Tier: Restoration Druid + Hunter**».
- `rm-vs-rogue-mage` (mirror): SC fmage-comps — «S Tier: Frost Mage + Subtlety Rogue» (усиливает mirror-якорь).
- `rm-vs-mage-priest`, `rp-vs-mage-priest`: SC fmage-comps — «S Tier: Frost Mage + Discipline Priest».
- `rm/rp-vs-rogue-spriest`-соседство: fmage-comps «C Tier: Frost Mage + Shadow Priest» — см. §4 (новая ячейка).

## 4. Кандидаты в новые ячейки (решение владельца; источники уже в руках)
К прежним (mage+rsham, rogue+rsham — Mixster-планы, 07-06) сегодня добавились:
- **mage+shadow-priest** (2v2): Mixster дал **развёрнутый план** в комментах Pri_Rog (Jun 7, 2008): сап мага или открытие в спириста; dispel+MB+mana burn спириста; рог **cloak на входящий frostbolt/shatter** = 5с фри-DPS, vanish до конца cloak под ре-опенер; бейт CS фейк-Flash Heal; «не попасть в чейн sheep→silence→silence = 10с без хилов»; рог floating 80%+. Плюс SC fmage-comps: пара **названа C Tier**. Двойной якорь готов — осталась только ячейка в `compositions.json` (по образцу rogue+shadow-priest).
- **priest+warrior** (2v2): Mixster-план (Jun 12, 2008): рог на воина; при свапе воина на прийста — SS к их присту + PI mana burn; трикет kidney → blind → SS priest.
- **mage+warlock** (2v2): в AJ RP-гайде есть посвящённая подстраница `Pri_Rog_vs_Mag_Wlk` (не читалась — вне текущих ячеек).

## 5. Прочее по источникам
- **YouTube-кандидат**: «Anniversary TBC — Rogue/Mage 2v2 Arena Guide!» (`DLEZ7Yi4-jU`) — первый свежий RM-POV видео-гайд в выдаче. **yt-dlp из песочницы не работает** (прокси 403 на YouTube — повторно подтверждено сегодня) → транскрипт добыть только в интерактивной сессии (или руками). Потенциал: RM-POV может закрыть rm-vs-mage-rdruid / rm-vs-hunter-*.
- frostyboost.com «TBC Rogue PvP Guide — Season 2» — в выдаче, не читан (низкий приоритет: судя по тайтлу — talents/gear, не per-matchup).
- WebFetch на skill-capped работает (server-rendered), но **только на URL из выдачи** (provenance-ограничение) — суб-страницы добирать через Chrome MCP.

## 6. Housekeeping
- Stale hypothesis-дубликатов теперь **12** (10 прежних + 2 сегодняшних mage-hpala) — ждут удаления владельцем (см. SCAN-REPORT 07-03 §3).
- Незакоммиченные изменения продолжают копиться (с 07-02) — сегодня добавились: 2 новых драфта, 2 помеченных гипотезы, счётчик теста, COVERAGE.md, kb/rendered/slang/. Ждёт ручного `git add/commit/push`.
- `docs/NEXT-SESSION-HANDOFF.md` датирован 06-23 (цифры 39/16 устарели: сейчас **51 драфт / 16 гипотез (4 незасорсенных)**) — обновить при следующей интерактивной сессии.
- Policy-вопрос про class-handling synthesis (с 06-30) для mage+hpala **закрыт сегодня** находкой пара-якоря; для оставшихся 4 гипотез — всё ещё актуален.

## 7. Следующие шаги
1. AJ-дочитка (по 3-4/ран): RM — `Dru_Htr`, `Dru_Rog`, `Pri_Rog`(vs RP!), `Pal_War`; RP — `Dru_Rog`, `Dru_Wlk`, `Rog_Rog`, `Mag_Rog`(vs RM!). Зеркальные пары AJ (RM vs RP и RP vs RM) особенно ценны — по ним у нас худшие источники.
2. Отмашка владельца на enrichment-батчи §3a-3e (+ прежние §3a-3c из 07-06).
3. Решение владельца по новым ячейкам §4 (mage+spriest — самый готовый: план+тир).
4. Интерактивная сессия: yt-dlp транскрипт `DLEZ7Yi4-jU`.
