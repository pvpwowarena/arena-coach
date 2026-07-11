# Source-scan report — 2026-07-09 (авто-задача)

**Итог: 0 новых sourced-драфтов** (4 гипотезы остаются заблокированными — блок сегодня подтверждён двумя НЕ читанными ранее tier-list сайтами, см. §2). AJ-дочитка закрыла всю очередь 07-07/07-08 §7: прочитаны **4 страницы** (RM `Dru_Rog`, RM `Pal_War`, RP `Dru_Rog`, RP `Dru_Wlk`) → enrichment-материал для 4 драфтов, включая maps_notes по Lordaeron и Blade's Edge и три enemy-POV плана. Плюс найден **свежий R1-видеоисточник** (май 2026): SPR-POV против нашего RM (см. §5). Ничего не аппрувлено, в `kb/matchups/` ничего не мёржено, драфты не изменялись.

**Проверки (green):** `validate-kb kb/drafts/` = **51 OK** · `pytest tests/` = **113 passed** · KB не менялась → счётчик тестов и render_slang без изменений. Браузер подключён (Browser 1, macOS).

---

## 1. Два новых tier-list сайта проверены (оба — НЕ источники для KB)

| Сайт | Что это | Вердикт |
|---|---|---|
| `aoeah.com/news/4283` «TBC Classic Anniversary 2v2 Comps Tier List» (26 дек 2025) | SEO-блог голд-селлера, без автора | **В sources не берём** (категория koroboost, решение 07-08 §5): нет автора-игрока, есть прямые признаки сгенерированности — Rogue+Disc Priest стоит и в S, и в B; SPriest+Rogue и в A, и в B |
| `pvpskills.com` (© 2026 Vaionex) | Фан-сайт: комп-страницы 2v2/3v3 + «Matchup Matrix» | Без автора, generic-контент; Matchup Matrix — **class-vs-class (не пары!)** и client-rendered. Cite-уровень в лучшем случае, пока не используем |

Ценность обоих — **отрицательное подтверждение**: ни на одном нет пар hunter+hpala, hunter+rsham, mage+rdruid (2v2). Наши 4 гипотезы — стабильно не-мета во всех пяти известных tier-list источниках (WT, SC, Icy Veins, aoeah, pvpskills).

## 2. Гипотезы: осталось 4, блок подтверждён

| Slug | Статус сегодня |
|---|---|
| rm-vs-hunter-hpala | aoeah/pvpskills: пары нет. Targeted-поиск — ничего. Блок прежний |
| rm-vs-hunter-rsham | то же (aoeah имеет MM Hunter+**Disc Priest** A-tier — это ячейка hunter+priest, ⬜ todo, не наша гипотеза) |
| rp-vs-hunter-rsham | то же |
| rm-vs-mage-rdruid | WebSearch-сводка опять склеила с rogue+rdruid (conflation, в дело не идёт). Блок прежний: нужен RM-POV или пара-оценка |

Пути прежние: mirlol Twitch-sub владельца → `arena_ingest paste`; yt-dlp транскрипты в интерактивной сессии (песочница — 403, перепроверено сегодня, см. §5).

## 3. Enrichment-предложения (НЕ применял — жду отмашки; добавляются к очереди 07-06/07-07/07-08)

Все 4 страницы — снапшоты Wayback июль-2008, комменты ≤ 11 июля 2008 → **до патча 3.0.2, TBC-чистые** (правило дат 07-08 §1 соблюдено).

### 3a. `rm-vs-rogue-rdruid` ← AJ Icycake Mage_Rogue_vs_Dru_Rog
База Icycake тонкая (гнать друида, кайтить/CC-ить рога, sheep на выжиг CD). Комменты сильно богаче: **difficulty-сигнал** — Volkr «pretty sure this is the rogue/mage counter», Victus «против самых лучших друидов проигрываешь в любом случае», Seken «very hard unless executed perfectly» → сверить difficulty драфта. **Victus (детальный план)**: маг IB-ает опенер их рога → мгновенная nova на выходе → бег; blink беречь строго под kidney (на звук), тринкет на crippling; их умный рог откроет garrote (не CS) ради crippling под silence; окно килла друида = full-duration blind после того как рог тринкетнул первую nova; **Blades Edge = друид-мапа** (maps_notes!). **Demise (2272)**: human-рог (Perception) sap их рога → опен друида, друид умирает за 10-20с; sheep их рога ×2 + blind; sap/sheep на одном DR — не жечь подряд. **Seken**: пилларный старт мага; опенер впитать БЕЗ CD; шаттер по их рогу + 5pt KS; blind друида на выходе; imp CS в момент его тринкета от blind; precast poly под конец KS; **drink-bait** — маг пьёт, вынуждая sap на себя; их рога НЕ sap'ить — cheap shot. **Zerokelvin (дисент)**: килл-таргет — их РОГ («he wears leather not plate»), друида с ShS-рогом на хвосте не убить; контр-дисент Lorikan (rogue-POV): burn druid + sheep рога ×10, KS чейнить с silence; отходить от друида = ловить cyclone. **Icevein**: альтернатива — спам spellsteal хотов/баффов друида (вкл. **spellsteal NS и Barkskin**). **Puwet**: bleed (garrote/rupture) на их роге выключает vanish; 2-DPS враг = бой <1мин, CD не жалеть. Race-нюанс: dwarf-рог stoneform'ом снимает blind (Neok/Genz).

### 3b. `rm-vs-warrior-hpala` ← AJ Icycake Mage_Rogue_vs_Pal_War
База Icycake: кайтом **выманить BoF на воина → spellsteal → burst палы**; sheep воина до бабла; сквозь бабл — mage IB + rogue vanish; после бабла снова форс BoF → пала мёртв; умный пала даст BoSac воину + BoF себе → свап на воина, sheep палы, spellsteal BoSac; CS в хил. Комменты: **Dint (2200+ BG9, тот же что в rm-vs-warrior-rsham)**: sap палы → sheep воина → взрыв палы = быстрый бабл → vanish/restealth + IB → повторить; «really not hard»; evasion/ghostly strike против bleeds (bleed без vanish = самое опасное); при опене на палу — LoS от intercept, вплоть до deadly throw хилов с дистанции. **Дисент по difficulty — Sèlect**: «hardest combo along with warlock/druid»; его план: стан/sheep-тайминги на воина → форс бабла → дождаться стун-DR → реопен на палу с CS наготове; sap воина считает нереальным (zerker-станс/charge). **Валахар/Omonera (альтернативная линия)**: sheep палы, убивать ВОИНА (легче восстановиться, «pallys cant do crap»); бабл → контрить blind'ом. **Swifthand**: вариант nuke-warrior — на бабле пала кастует Holy Light → 2.5с окно на добив воина. **Nobode**: хороший пала BoSac'ом ломает sheep → DR 4с → **fake-sheep бейт**. **Mantocu**: старт mage-на-воина + rogue-на-палу = бабл ещё быстрее, sheep-DR не потрачен. **Joandarc (enemy pala POV!)**: **худшая мапа для pal/war против RM — Ruins of Lordaeron** (не кайтишь рога с freedom вокруг пилларов, не LoS'ишь мага) → maps_notes.lordaeron; его дилемма-цитата: freedom воину → сам съедает sheep, BoSac → воин не достаёт мага. Барви: sap палы → shatter bomb + imp CS + KS → форс бабла; dwarf-рог blind воина → тринкет → vanish → рестарт.

### 3c. `rp-vs-rogue-rdruid` ← AJ Mixster Pri_Rog_vs_Dru_Rog
База Mixster: endurance; crippling на их роге постоянно, LoS + пить при любом окне; агрессия на друида, fear друида+рога вместе, mana burn в caster-form. Комменты: **Mickster (важная поправка к базе!)**: НЕ пытаться оомить друида (видел innervate+spirit-тринкет 10%→100% под рогом) — вместо этого постоянные свапы + окна на питьё + ловить **fear→blind→sap→fear на их РОГА** как килл-линию; если всё же оомить — стоять готовым спам-диспелить innervate. **Maraiah**: SW:P rank 1 на nelf-друиде (запрет shadowmeld); тринкет беречь под cyclone→innervate, но не раньше чем их рог потратит blind; «если они сели на нашего рога — записывай win» (mana-war друид не выигрывает, он заперт в bear). **Myxx (против 2500 dwarf rogue/druid)**: первые 5-7 минут — диспел до abolish, пиллар, пить; fear на друида невозможен без stoneform/тринкета; выиграли, когда их рогу надоело и он свапнулся → прист освободился на fear/burn → fear/blind/sap. **Peanutbutter (enemy POV, dreamstate!)**: их план — rogue-on-rogue + mana-war (insect swarm дороже диспелить чем кастовать, r1 faerie fire ломает stealth/форсит комбат, travel form + lifebloom, r1 moonfire форсит комбат приста, cyclone-ротация) → прист оом за ~10 мин; **его же контр-совет нам**: blind друида в мидгейме = форс тринкета → потом fear→blind (ровно по КД)→sap без тринкета → убить их рога; каверза — друид уйдёт в bear до blind. Difficulty-сигнал: Zulthab «hardest setup», Peanutbutter уверен в win за друида → сверить difficulty драфта.

### 3d. `rp-vs-warlock-rdruid` ← AJ Mixster Pri_Rog_vs_Dru_Wlk
База Mixster: **3 оружия у рога** — wounding MH, crippling OH, mind-numbing запасной OH; fear беречь на момент bash/cyclone по рогу (лок не убегает далеко) или на хилящего друида + mana burns; спам-диспел Fel Armor; коллаут некикаемых fear'ов; PoM-баунс; **pet-kill линия**: пет низкий → fear друида → рог свапается на пета → после смерти — спам-диспел лока ради **диспела Fel Domination**. Комменты: **Chingwang**: после первого пет-килла рог меняет OH на mind-numbing → Fel Dom-суммон медленнее → стан на прерывание. **Ilyria**: Fel Dom (и Mass Dispel) **кикабельны и предсказуемы** — лок замирает перед кастом → kick. **Cydial (самый детальный, 2 июля)**: пет-килл в правильный момент решает матч («второй, fel-dom-нутый пет умер = победа»); пета убивать «незаметно» — уронить дамагом рога и добить свапом, prep+ShS на лока после первого пета, кик ресуммона; **blind на ПЕРВЫЙ cyclone = форс раннего тринкета друида; НИКОГДА не blind'ить лока**; focus-frame на друида для отслеживания cyclone; ShS-kick на cyclone друида, 1 комбо-поинт держать про запас на deadly throw в fear лока; **энергию копить >50** — освободившийся лок будет CoE-кайтить, нужен запас на shiv-crippling. **Aeriss/Oranmalice (enemy POV)**: их выигрышная линия = 3×cyclone+3×fear на рога при cyclone на присте; наша киллчейн-линия против них: после тринкета друида — fear (на низких fear-DR рога) → blind → vanish-sap → fear → **MC**; «в этой цепочке я умираю всегда». **Félice**: прист не даёт друиду пить; на Blade's Edge это тяжелее (map-note). Мелочь от Maleficarum (enemy lock POV): кикать fear'ы несмотря на фейк-бейты — лок сдаётся и перестаёт пытаться.

## 4. AJ-очередь: статус
Очередь 07-07 §7.1 / 07-08 §7.2 **полностью закрыта** (8 страниц за три рана: Pri_Rog+Mag_Rog+Dru_Htr+Rog_Rog 07-08, Dru_Rog×2+Pal_War+Dru_Wlk сегодня). Остаток резерва — enemy-POV из каталога 07-08 §4: приоритет **Megatf Druid/Hunter** (`vs_Mage_Rogue`), 3v3 **WLD-POV** и **RLD-POV** (`vs_Mag_Pri_Rog`), PomPyro Mage/Rogue (спек-кандидат). Плюс не читанная RP-подстраница `Pri_Rog_vs_Mag_Wlk` (ячейка mage+warlock — ⬜, решение владельца).

## 5. Прочее по источникам
- **Новый видео-кандидат (сильный)**: «R1 Rogue Shadow Priest — How We Play vs. Rogue Mage | TBC anniversary Season 1 Arena Analysis» (`qJn9rLhDLZU`, ~май 2026) — **R1-уровень, enemy-POV ровно нашей пары** → enrichment для `rm-vs-rogue-spriest` (и зеркально полезно RM-игрокам). yt-dlp из песочницы — 403 (перепроверено сегодня) → в очередь интерактивной сессии вместе с `DLEZ7Yi4-jU`.
- frostyboost.com «TBC Rogue PvP Guide — Season 2» — в выдаче повторно; судя по описанию — talents/gear + спек-рекомендация 17/0/44 под RM; per-matchup контента нет. Низкий приоритет, не читан.
- WebSearch conflation дня: на запрос mage+rdruid сводка опять подставила советы про rogue+rdruid. Правило «только живые страницы» работает.

## 6. Housekeeping
- Stale hypothesis-дубликатов по-прежнему **12** — ждут удаления владельцем (SCAN-REPORT 07-03 §3).
- Незакоммиченное продолжает копиться (с 07-02): 7 modified + все отчёты/драфты/доки untracked. Сегодня добавился только этот отчёт. Ждёт ручного `git add/commit/push`.
- `docs/NEXT-SESSION-HANDOFF.md` датирован 06-23 (цифры 39/16 устарели: сейчас **51 драфт / 16 гипотез, 4 незасорсенных**) — обновить в интерактивной сессии.

## 7. Следующие шаги
1. **Отмашка владельца на enrichment-батчи** — очередь: 07-06 §3a-3c + 07-07 §3a-3e + 07-08 §3a-3d + сегодняшние §3a-3d (12 страниц материала на 12 драфтов). Сегодняшние 3a/3b дают ещё и maps_notes (Blades Edge, Lordaeron) + difficulty-сверки для трёх драфтов.
2. AJ enemy-POV дочитка (3-4/ран): Megatf `Dru_Htr_vs_Mage_Rogue`, 3v3 `Dru_Wlk_War_vs_Mag_Pri_Rog` (WLD-POV), `Dru_Rog_Wlk_vs_Mag_Pri_Rog` (RLD-POV).
3. Интерактивная сессия: yt-dlp транскрипты **двух** видео — `qJn9rLhDLZU` (R1 SPR vs RM, май 2026) и `DLEZ7Yi4-jU` (RM-гайд, фев 2026).
4. Решения владельца: ячейки-кандидаты (mage+spriest готов полностью, 07-07 §4; mage+warlock — есть AJ-подстраница; PomPyro-спек; rogue+rsham) + удаление 12 stale-дубликатов гипотез.
