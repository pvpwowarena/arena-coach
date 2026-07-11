# Source-scan report — 2026-07-10 (авто-задача)

**Итог: 0 новых sourced-драфтов** (4 гипотезы остаются заблокированными — сегодня добавлено шестое отрицательное подтверждение, см. §2). Главное за ран: **приоритетная enemy-POV очередь 07-09 §7.2 закрыта полностью** — прочитаны Megatf Druid/Hunter (главная + `vs_Mag_Rog` + бонусом `vs_Pri_Rog`), 3v3 **WLD-POV** и **RLD-POV** `vs_Mag_Pri_Rog` → enrichment-материал для 4 драфтов (два 2v2 + два 3v3-драфта, у которых до сих пор были только tier-list якоря + synthesized-execution). Плюс найден новый видео-кандидат: **Kooba 2.5k RM-гайд** (см. §5). Ничего не аппрувлено, в `kb/matchups/` ничего не мёржено, драфты не изменялись.

**Проверки (green):** `validate-kb kb/drafts/` = **51 OK** · `pytest tests/` = **113 passed** · KB не менялась → счётчик тестов и render_slang без изменений. Браузер подключён (Chrome, macOS).

**Правило дат соблюдено:** все 5 прочитанных AJ-страниц — снапшоты 14–20 июля 2008, все использованные комменты ≤ 20 июля 2008 → до патча 3.0.2, TBC-чистые.

---

## 1. Свежий скан (WebSearch)

- Новых per-matchup источников по RM/RP/RMP в открытом вебе нет. Выдача — знакомый набор (WT, SC, Icy Veins, koroboost, frostyboost, ownedcore Gog123456).
- **ssegold.com** «Best Arena Compositions in TBC Anniversary» — голд-селлер SEO-блог без автора (категория aoeah/koroboost, решение 07-08 §5): comp-level общие места, per-matchup нет. **В sources не берём.** Ценность — отрицательное подтверждение (§2).
- **Conflation дня (двойной):** (а) на запрос mage+rdruid сводка опять подсунула rogue+rdruid; (б) на запрос hunter+rsham vs RM сводка выдала пара-утверждение «Hunter/RSham is better into Mage/Rogue than Warrior/Druid» — **на живой странице Icy Veins 2v2 этого нет** (перечитана целиком: пар hunter+rsham / hunter+hpala / mage+rdruid в обоих списках нет). Утверждение не трейсабельно → в дело не идёт. Правило «только живые страницы» снова спасло.

## 2. Гипотезы: осталось 4, блок подтверждён (6-й сайт)

| Slug | Статус сегодня |
|---|---|
| rm-vs-hunter-hpala | ssegold: пары нет. Icy Veins live: нет. Блок прежний |
| rm-vs-hunter-rsham | то же + сфабрикованное пара-утверждение сводки отклонено (§1) |
| rp-vs-hunter-rsham | то же |
| rm-vs-mage-rdruid | conflation с rogue+rdruid (очередной). Блок прежний: нужен RM-POV или пара-оценка |

Не-мета статус 4 пар теперь подтверждён **шестью** tier-list сайтами (WT, SC, Icy Veins, aoeah, pvpskills, ssegold). Пути прежние: mirlol Twitch-sub владельца → `arena_ingest paste`; yt-dlp транскрипты в интерактивной сессии (песочница — 403, перепроверено сегодня).

## 3. Enrichment-предложения (НЕ применял — жду отмашки; добавляются к очереди 07-06/07-07/07-08/07-09)

### 3a. `rm-vs-hunter-rdruid` ← AJ Megatf (Dru_Htr_2, главная + vs_Mag_Rog)

Enemy-POV от второго авторитетного Dru/Htr-автора (Megatf, Dragonmaw/US-Reckoning, 2.3-гайд, 11/41/9): **пет сидит на маге** (viper-фокус = маг, «Mage is Drainable»), **киллят водного элементаля** («life or death», auto+multi+arcane); FD наготове под poly (если валят друида) или под frostbolt (если валят хантера); **тринкет-дисциплина** — Megatf тринкетит ВТОРУЮ или ТРЕТЬЮ nova: «первая волна бурста — сбить хилера с ритма, вторая nova + Blind + CS — на убийство». Для нашего драфта: хороший хантер прочитает наш fake-burst → планировать килл-окно на 2-3-ю nova и жечь его FD/Silencing заранее. Комменты: Longshot (enemy) — их вин-лайн «fully nuke their mage → iceblock or die», друид переживёт рога легко → наш маг обязан пилларить старт; Sixotwo (RM-POV, дисент по килл-таргету) — «huge nuke on the Hunter» + CC друида → форс NS/тринкета → sheep-спам хантера → добить друида (альтернативная линия к нашей druid-first, кандидат в Alternative opener). Из general-tips Megatf: **Hunter's Mark поднимает пьющего** (наш drink-bait от Seken ломается об это), скорпид-пет с r5 ядом, элементаля прячем от него за LoS (совпадает с Tzatziki 07-08).

### 3b. `rp-vs-hunter-rdruid` ← AJ Megatf vs_Pri_Rog (бонус — не было в очереди)

Enemy-план: пет/viper-фокус на нашем ПРИСТЕ, DPS в нашего рога — «чтобы прист был вынужден выйти в LOS хилить рога» → viper каждые 15с; chain-cyclone рога под Pain Suppression; Silencing Shot бережётся **только под манабёрны** и добивающий хил; mutilate-рог для них хуже shadowstep (abolish-resist + дамаг). **Cyclonian (2100+, прямой difficulty-сигнал в НАШУ пользу):** «Have yet to beat Priest/Rogue 2100+» — их ломает агрессивный прист: **PI + спам Mana Burn хантера в 0**, прист сам догоняет хантера, рог вставляет Blind чтобы прист добежал, тринкет → fear. Это готовая вин-лайн для нашего драфта (сверить kill-приоритет: у нас акцент на выжигание хантера — Cyclonian подтверждает). Их контр-меры для Common mistakes: silencing на бёрны (джук), сник-бёрны на друиде, кайт нашего Shadowfiend'а (из general-tips: «KITE IT»; ставить фиенда на пета/защищённую цель).

### 3c. `rmp-vs-warrior-warlock-druid` (WLD) ← AJ Talmon Dru_Wlk_War_vs_Mag_Pri_Rog

Первый **посвящённый WLD-POV** план против нас (Talmon, Dragonmaw/US-Reckoning): фелхант **камперит нашего мага** (авто-devour выключен, руками мгновенно жрёт sheep; пет держит LoS цели sheep'а) → фейк-каст sheep = бейт devour'а; Spell Lock юзается по магу как **school-lockout об любой каст** (не как silence) → наш маг обязан джучить; **элементаля убивают целенаправленно** (dot + свап воина) — хилить/щитовать элементаля (совпадает с планом Factionz); их fear только с half-cast proc или когда наш рог в CC; Death Coil тратится рано и на нашего рога; их лок тринкетит «когда маг чейн-кастит + рог на нём + полный kidney в открытую» → наше килл-окно должно закладывать тринкет; их друид **прячется от манабёрнов и фира приста** — burn-окна создаются только форсом друида в открытую (hamstring воина на нашем присте — их контр-мера). Комменты-дисенты по их килл-таргету (нам в Common mistakes/difficulty): Tutenstain — **проигрывали, когда RMP шёл в ДРУИДА**; Gnomomuk (RMP-игрок) — «go for the mage» им выгоднее чем нам кажется («druid has to heal the warlock a lot more»…) + предупреждение: после их spell lock ждать **быстрый свап на нашего воина**… (у нас нет воина — его ремарка про их свапы на 3-ю цель после CD, применимо как «ждать свап на рога»); Baskoud/Dokterplants — их альтернатива «dps наш прист», «атаковать мага = suicide if the mage is decent». Расхождение difficulty (Talmon «relatively easy» за WLD 2008 vs koroboost-2026 «WLD бьёт RMP») — та же вилка, что у Factionz (07-06 §3a): добавить примечание, difficulty не менять.

### 3d. `rmp-vs-rogue-warlock-druid` (RLD) ← AJ Duckerss Dru_Rog_Wlk_vs_Mag_Pri_Rog

Первый **посвящённый RLD-POV** (Duckerss, Barthilas/US-Bloodlust; считают себя фаворитами против RMP — сверить с нашим difficulty): их опенер — **sap-war** (human-рог Perception), иначе **sap нашего ПРИСТА + опен в нашего МАГА**, их рог весь бой липнет к магу и рубит касты; лок дотит мага + элементаля и **ждёт наших спам-диспелов** (наш диспел-прессинг подтверждён их же планом), devour'ит наши poly и фиры с друида — **друид бережёт тринкет строго под Blind** (бейтить не-blind CC перед киллом); CoEx на нашего приста при чейсе друида (анти-манабёрн); их друид abolish'ит wounds с лока. Эволюция их килл-таргета в комментах: Basketitus + сам Duckerss — «gibbing the priest» стал их основной линией (druid CC мага, lock spell-lock + devour, пре-cloak/vanish их рога, Death Coil в хил приста) → наш прист = главная мишень, закладывать в позиционирование; Grunge — миноритарная линия «riding the rogue» (тонны дамага в рога форсят приста «врасти и хилить» вместо chase-dispel; фиры под коллауты kidney); Inhume — их контр-довод: пост-2.3 cheat death + shadowstep делают train-rogue невыгодным («allows the mage easy polymorph, shatter combos»). Для нашего драфта: ждать sap-приоритет прист→опен маг; фейк-sheep на devour-бейт; fear ward дисциплина (они фирят «at every opportunity»).

## 4. AJ-очередь: статус

Приоритетный резерв 07-08 §4 / 07-09 §7.2 **закрыт** (Megatf ×2 + WLD-POV + RLD-POV; всего за ран 5 страниц с главной Megatf). Остаток резерва (низкий приоритет, по желанию): PomPyro Mage/Rogue (спек-кандидат SPEC_VARIANTS_2V2), `Pri_Rog_vs_Mag_Wlk` (ячейка mage+warlock — ⬜, решение владельца), `Pri_Rog_2` (Faction-вариант), Therst/Darkalpha `Dru_Htr_vs_Pri_Rog` (сверка с Megatf), 3v3 `Dru_Mag_Rog_vs_Mag_Pri_Rog` и `Dru_Mag_War`/`Dru_Rog_War`/`Htr_Mag_Pri`/`Pal_Shm_War` vs нас (ячейки 3v3-long-tail, в KB их пока нет — RLD-гайд подтвердил и наличие `Ret Paladin/Resto Shaman/Warrior` подстраницы).

## 5. Прочее по источникам

- **Новый видео-кандидат:** «TBC Arena Rogue Mage 2v2 Guide | 2.5k Rated Strategies» (`mHgkNzlnpPQ`), автор **Kooba** (Twitch: Thekooba), опубликовано 2021-12-06 (TBC Classic эпоха, механики валидны) — RM-POV 2.5k. В yt-dlp-очередь интерактивной сессии **третьим** (после `qJn9rLhDLZU` R1 SPR vs RM и `DLEZ7Yi4-jU`).
- yt-dlp из песочницы — **403 подтверждён сегодня** (proxy tunnel failed, все 3 ретрая).
- Icy Veins 2v2 перечитан live (заодно с §1): comp-уровень, «Restokin»-нюанс для rogue+rdruid (друид даёт заметный дамаг) — микро-факт, можно упомянуть в `rm/rp-vs-rogue-rdruid` при следующем enrichment-батче.

## 6. Housekeeping

- Stale hypothesis-дубликатов по-прежнему **12** — ждут удаления владельцем (SCAN-REPORT 07-03 §3).
- Незакоммиченное копится с 07-02 (7 modified + отчёты/драфты untracked; сегодня добавился только этот отчёт). Ждёт ручного `git add/commit/push`.
- `docs/NEXT-SESSION-HANDOFF.md` датирован 06-23 (39/16) — актуально **51 драфт / 16 гипотез (4 незасорсенных)**; обновить в интерактивной сессии.

## 7. Следующие шаги

1. **Отмашка владельца на enrichment-батчи** — очередь выросла до **16 страниц материала на ~14 драфтов**: 07-06 §3a-3c + 07-07 §3a-3e + 07-08 §3a-3d + 07-09 §3a-3d + сегодняшние §3a-3d. Сегодняшние закрывают самое ценное: оба 3v3-драфта (WLD, RLD) получают dedicated enemy-POV вместо голых tier-якорей.
2. Интерактивная сессия: yt-dlp транскрипты **трёх** видео — `qJn9rLhDLZU`, `DLEZ7Yi4-jU`, `mHgkNzlnpPQ` (Kooba).
3. AJ-дочитка по желанию (низкий приоритет, §4): PomPyro (спек-кандидат), `Pri_Rog_vs_Mag_Wlk` (ячейка-кандидат).
4. Решения владельца: удаление 12 stale-дубликатов; ячейки-кандидаты (mage+spriest, mage+warlock, rogue+rsham, PomPyro-спек); обновление handoff.
