# Arena Coach — Daily Source Scan Report
**Дата:** 2026-06-30
**Задача:** `arena-coach-daily-source-scan` (автоматическая, автономный ран)
**Статус:** ✅ Завершена

---

## Итог сессии (TL;DR)

- **Новых sourced-драфтов: 0 (нетто).** Я подготовил 2 драфта (`rp-vs-mage-hpala`, `rp-vs-rogue-hpala`) из соседних секций гайда Deadlycoward, прогнал зелёные тесты — **и откатил их** на проверке консистентности: в гайде **нет отдельной секции** под эти пары, только class-handling соседних. Это ровно тот промоут-на-склейке, который SCAN-REPORT 2026-06-29 пометил как conflation-риск, и который ниже бара проекта (источник должен оценивать **саму пару** — тир-лист её называет ИЛИ есть посвящённая секция). Ничего не выдумано, ничего не зааппрувлено, в `kb/drafts/` ничего не просочилось.
- **Браузер подключён сегодня** (`list_connected_browsers` → Browser 1, macOS) — в отличие от 06-29. Поэтому **впервые с 06-28 client-rendered Warcraft Tavern прочитан напрямую через Chrome MCP** (не по старому захвату): полный гайд Deadlycoward (20 матчапов), WT RM-обзор, WT DPR-обзор. Это **первичное подтверждение** структурного вывода 06-29: целевых секций mage+hpala / rogue+hpala / hunter+rsham в гайде действительно нет.
- **Главная ценность дня — enrichment.** Гайд Deadlycoward (Infernal Gladiator, top-10 EU DP/R) — богатый, on-version (2.4.3), named-author источник с **посвящёнными секциями под ~14 уже существующих RP-драфтов** (Druid/Hunter, Druid/Rogue, Hpala/Warr, Rsham/Ret, Rogue/Rogue и т.д.). Многие из них в approve-backlog на более слабых источниках — Deadlycoward усиливает их до approve-готовности. Таблица ниже.
- **rank1academy RM/RP матчап-гайды = платные** (148.95 €, контент за пейволлом — подтверждено фетчем сегодня). Как источник тактик непригодны.
- **8 гипотез — без изменений** (5 RM заблокированы отсутствием RM-POV per-matchup гайда; 3 RP не покрыты как пары 20 матчапами Deadlycoward).
- **Зелёное:** `validate-kb kb/drafts/` = **47 OK** · `pytest` = **113 passed** · `ruff` clean. Счётчик драфтов без изменений (47). `render_slang.py --all` перезапущен (слой в синке, 47 файлов).
- **Открытый вопрос владельцу (policy):** разрешаем ли промоут «class-handling synthesis» (пара не оценена источником, но обработка каждого класса — да)? Если да — якоря под mage+hpala и rogue+hpala готовы. Если нет (статус-кво) — остаются гипотезами.

---

## Что прочитано напрямую сегодня (verifiable)

| URL | Тип | Канал | Что дал |
|---|---|---|---|
| warcrafttavern.com/…/rogue-disc-priest-2v2 (Deadlycoward) | Author-гайд, 20 матчапов, RP-POV | **Chrome MCP** (client-rendered) | Полное тело. Подтверждено: **нет** секций mage+hpala, rogue+hpala, hunter+rsham. Богатый enrichment под существующие RP-драфты (см. ниже) |
| warcrafttavern.com/…/rogue-discipline-priest-rogue-arena-strategies | DPR-обзор | **Chrome MCP** | Strengths (dispels, Mana Burn, reset/regen), weaknesses; «DPR Counter Comps: suffers a lot against mana drainers such as Hunter/Druid, Hunter/Priest, or even Hunter/HPaladin» |
| warcrafttavern.com/…/rogue-mage-rogue-arena-strategies | RM-обзор | **Chrome MCP** | Только обзор + counter-list (Human Rogue combs, Dwarf Disc+Mage/Lock, Rogue/Druid, Lock/Druid, **Lock/Hpala**). **Per-matchup стратегий нет.** Ни одной из 5 RM-целей |
| ownedcore.com/…/83143 (DP/R → 1850) | Форум-гайд, original TBC 2008 | WebFetch (server-rendered) | Чистый TBC (fearward/mana-burn/totems). Покрывает Druid/Lock, Pala/Lock, Pala/Warr, Warr/Shaman, Rogue/SP, Mirror, Druid/Hunter, hunter/rogue, Shaman/Lock. **Ни одной** из 8 целей напрямую |
| rank1academy.com/guide/rogue-mage-matchup-tbc (+ mage-rogue) | Платный матчап-курс | WebFetch | **Пейволл** (148.95 €, видео за оплатой). Тактик не извлечь |

**WebSearch** (RM vs hunter/mage/rogue+pala; hunter+rsham; Deadlycoward matchups) — указатели на источники выше + shaman-POV гайды (Wowhead/Icy Veins, не инвертируются в RM/RP-план). Сводки по-прежнему путают соседние матчапы.

---

## Почему откатил 2 драфта (анти-conflation, в продолжение 06-29)

Гайд Deadlycoward даёт **дословные** якоря по обработке классов:
- frost-маг: «Focus Kill mage by making him run out of mana», «Never go aggressive vs DP/M», «kite the mage around the pillar with a lot of Mana Burns» (секции *DPriest/Frost Mage* 7/10, *Druid/Frost Mage* 5/10);
- holy-пала: «Killing Pala with a few Mana Burns on him», «stick to pala who should be an easy kill after he has no mana left», dispel BoF (секции *Hpala/Warr* 7/10, *Rsham/Ret* 7/10);
- вражеский рог: «priest back against a wall (anti-garrote), stand away (anti-sap)… blind on the rogue… easy to die if Blind misses» (секции *Rogue/Rogue* 7/10, *Mirror* 5/10).

**Но** ни «Mage/Holy Paladin», ни «Rogue/Holy Paladin» автор как пару не разбирает (взаимодействие пала-бабл/фридом на маге, приоритет цели между двумя мана-юзерами и т.п. — в источнике отсутствует). Склейка class-handling → «sourced-draft» подразумевала бы, что источник оценил комбо. Это нарушает бар проекта и совпадает с conflation-кейсом 06-29 → **оба остаются гипотезами**, в их файлы добавлена дата-метка `🔎 Пере-проверено 2026-06-30` с зафиксированными якорями.

> Прецеденты, которые ЗА баром (для контраста): `rm-vs-warrior-mage` — warrior+mage **назван** D-tier в AOEAH; `rp-vs-warlock-hpala` — warlock+hpala **назван** B-tier в WT; `rp-vs-mage-rdruid` — **посвящённая секция** «DPR vs Druid/Frost Mage». У mage+hpala и rogue+hpala — ни тир-буквы, ни секции.

---

## Статус 8 оставшихся гипотез (без изменений)

| Slug | Итог | Блокер (подтверждён сегодня) |
|---|---|---|
| rm-vs-hunter-hpala | 🟡 гипотеза | Нет RM-POV per-matchup гайда (WT RM = только обзор; rank1academy платный); комбо не тировано |
| rm-vs-hunter-rsham | 🟡 гипотеза | то же |
| rm-vs-mage-hpala | 🟡 гипотеза | то же |
| rm-vs-mage-rdruid | 🟡 гипотеза | Deadlycoward — DP/R-POV (план = OOM манабёрном), для RM не инвертируется. Нужен RM-POV |
| rm-vs-rogue-hpala | 🟡 гипотеза | RM-POV источника нет |
| rp-vs-hunter-rsham | 🟡 гипотеза | В гайде есть Druid/Hunter (10/10), но **нет Hunter/RSham**; обзор перечисляет hunter+healer как «suffers a lot», но shaman-вариант не назван |
| rp-vs-mage-hpala | 🟡 гипотеза | Нет секции пары (есть DPriest/Mage, Druid/Mage). Якоря class-handling зафиксированы — policy-вопрос |
| rp-vs-rogue-hpala | 🟡 гипотеза | Нет секции пары (есть Hpala/Warr, Rogue/Rogue). Якоря зафиксированы — policy-вопрос |

---

## Enrichment существующих RP-драфтов (Deadlycoward, НЕ применено)

Гайд содержит **посвящённые секции** под пары, по которым у нас **уже есть драфты**. Это named-author, on-version источник — добавляется в `sources:` и усиливает разделы Opener / If enemy trinkets / Common mistakes. Все цитаты — дословно из тела гайда (прочитано через Chrome сегодня).

| Существующий драфт | Секция Deadlycoward (сложн.) | Ключевой якорь для вплетения |
|---|---|---|
| rp-vs-hunter-rdruid | Druid/Hunter (10/10) | «permanent mana drain via Viper Sting», «RNG Roots from Frost Trap», «kill pet and Mana Burn the hunter / kill druid after trinket in human form». Поднять difficulty к very-hard |
| rp-vs-rogue-rdruid | Druid/Rogue (9/10) | «Kill rogue on 2nd Blind; sit around pillar, land every fear on the rogue, restealth; catch druid in human form after Fear→Sap/Blind when no trinket» |
| rp-vs-warrior-hpala | Holy paladin/Warrior (7/10) | Точный опенер: «Cheap Shot–Kidney pala, **wait for warrior to charge** before Kidney, swap to warrior; CC chain Kidney/Fear/Sap/Blind/Shadowstep-Kick/Vanish-CS/Kidney; warrior dead 90%». FAQ: почему не сапать пала |
| rp-vs-retpala-rsham | Resto shaman/Ret paladin (7/10) | «Kill the paladin: Sap pala, dispel, burns, Kidney only when priest stunned or он даёт BoF (priest dispels); easy kill after no mana» |
| rp-vs-mage-priest | Disc Priest/Frost Mage (7/10) | «kill mage by OOM OR sap+fully dispel priest then kill (not vs dwarves); **never go aggressive**; kite mage at pillar + Mana Burns» |
| rp-vs-warlock-priest | Disc Priest/SL Warlock (7/10) | «kill priest (not if dwarf) OR kill lock with pressure; vs Disc/Lock run **long distances** — у них нет poison dispel (e.g. Lordaeron room-to-room)» |
| rp-vs-rogue-mage | Frost Mage/Rogue (7/10) | «avoid Sap (mage Spellsteal); keep distance from priest; Shadowstep/Garrote to stop Polymorph-steal; trinket Kidney situational; Vanish→CS-KS-Rupture rogue» |
| rp-vs-rogue-rogue | Rogue/Rogue (7/10) | «priest back to wall (anti-garrote), stand away (anti-sap); go hard on one rogue Vanish-CS-Evisc; CS-KS the other if priest in trouble; easy to die if Blind misses» |
| rp-vs-warlock-rogue | SL Warlock/Rogue (7/10) | «Rush lock with Sprint, avoid Sap, do **not** trinket first Kidney, kill lock hard» |
| rp-vs-warrior-rdruid | Druid/Warrior (7/10) | «kill warrior; sap warrior + fake Berserker Rage for re-sap; CS-KS druid for free priest Fear; kill druid only if trinket down + human form» |
| rp-vs-warlock-rdruid | Druid/SL Warlock (7/10) | «kill lock's pet then lock; Blind druid; **killing pet removes Devour Magic → Fear sticks on druid**» |
| rp-vs-warrior-rsham | Resto Shaman/Warrior (5/10) | «Kill the warrior (same as Hpala/Warr); aggressive stuns/kicks/fears on shaman» |
| rp-vs-rogue-priest | Mirror Disc Priest/Rogue (5/10) | «beware enemy Mass Dispel pulling you into combat; sap enemy priest + your priest dispels opposite + Fears; restealth Crippling Shiv; keep CoS for Greater Heal» |
| rp-vs-rogue-spriest | Shadow Priest/Rogue (5/10) | 2-й корроборирующий источник к Windz: «rush SP far from your priest, kill priest while CCing rogue; **DP/R counters SP/R**» |

Плюс: гайд — **Horde/Undead POV** (WoTF). Полезный нюанс «not vs dwarves» (Stoneform снимает наши яды) для alliance-противников.

> Правки **не применял** (домашнее правило: малые проверяемые инкременты + approve владельцем). Скажи «вплети Deadlycoward-enrichment» — подготовлю батч на ревью (приоритет: warrior-hpala, retpala-rsham, hunter-rdruid, rogue-rdruid — там named-author заметно усилит approve-готовность).

---

## Техническое

| Проверка | Результат |
|---|---|
| `python -m arena_coach validate-kb kb/drafts/` | ✅ 47 документов прошли валидацию |
| `python -m arena_coach validate-kb kb/hypotheses/` | ✅ корректно **падает** (нет `sources`) — карантин цел |
| `python -m pytest tests/` | ✅ 113 passed |
| `ruff check backend bridge ingest tests` | ✅ All checks passed |
| Счётчик драфтов (`tests/test_kb_loader.py`) | без изменений (47) |
| `render_slang.py --all` | перезапущен — 47 файлов, слой в синке. Slang-gap (pre-existing): `ambush, deadly-throw, expose-armor, pain-suppression, rupture, will-of-the-forsaken` (кандидаты в slang.json) |
| Файлы тронуты | 2 гипотезы (дата-метка `🔎 2026-06-30`), этот отчёт. Драфты/тест/счётчик — без нетто-изменений |

---

## Следующие шаги для владельца

1. **Policy-решение (главное):** разрешить ли промоут на «class-handling synthesis» (пара не оценена источником, но обработка обоих классов — да)? Касается `rp-vs-mage-hpala`, `rp-vs-rogue-hpala` (якоря готовы) и потенциально упрощает long-tail. Моя рекомендация — **держать бар** (источник оценивает пару), но это твой вызов. Скажешь «да» — оформлю оба за 5 минут.
2. **Enrichment-батч Deadlycoward** по 14 RP-драфтам (таблица выше) — named-author, on-version источник; усиливает approve-backlog. Скажи слово — подготовлю на ревью.
3. **Разблокировка 5 RM-гипотез** требует RM-POV per-matchup источника (WT даёт только обзор; rank1academy платный). Путь — yt-dlp по конкретным RM-POV VOD **в интерактивной сессии** (платформенные ограничения автономного рана не дают качать произвольные URL через bash). 
4. **rp-vs-hunter-rsham:** ближе всех к сорсингу (обзор: hunter+healer = «suffers a lot»; Druid/Hunter даёт hunter-механику), но resto-shaman-вариант источником не назван. Решишь принять hunter-архетип — оформлю source-faithful (kill = pet/hunter + мана-война, не «kill shaman»).
5. Аппрувы — только тобой: `python -m arena_ingest review approve --slug <slug>`.
