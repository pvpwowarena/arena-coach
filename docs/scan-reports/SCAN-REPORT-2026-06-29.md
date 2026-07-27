# Arena Coach — Daily Source Scan Report
**Дата:** 2026-06-29
**Задача:** `arena-coach-daily-source-scan` (автоматическая)
**Статус:** ✅ Завершена

---

## Итог сессии (TL;DR)

- **Новых sourced-драфтов: 0.** Реального, проверяемого источника под оставшиеся 8 гипотез сегодня не нашлось. Ничего не выдумано, ничего не промоутировано, ничего не аппрувлено.
- **Поймана и отклонена WebSearch-conflation:** сводка приписала Deadlycoward DP/R-гайду матчапы «Rogue/Holy Paladin» и «Mage/Paladin», которых там нет (текст совпадает с секциями Rsham/Ret и DPriest/Mage). Промоут на основе непроверяемой сводки = брак → не делал.
- **1 новый частичный якорь** (skill-capped: `FrostMage+HolyPaladin = C-tier`, Jan 2026) для пары mage+hpala — но тир-буква без прозы тоньше текущего бара промоута. Решение за владельцем.
- **Инструментальный блокер:** браузер **не подключён** (`list_connected_browsers` → `[]`) → client-rendered Warcraft Tavern (Deadlycoward-гайд, RM-обзор, тир-лист) сегодня **не читался**. Работал только server-rendered + WebSearch.
- **Зелёное:** `validate-kb kb/drafts/` = 47 OK · `pytest` = 113 passed. Счётчик драфтов без изменений (47).

---

## Что проверено (только verifiable-источники)

| URL | Тип | Server-rendered? | Что дал по 8 гипотезам |
|---|---|---|---|
| ownedcore.com/…/161338 (Gog123456, 2008) | Форум-гайд RP+PMR | ✅ (WebFetch) | Покрывает RP vs **warrior/healer, mage/rogue, rogue/rogue, warlock/healer** + 3v3 WLD/Druid-Warr-Rogue/mirror. **Ни одной** из 8 целей (нет hunter+rsham, mage+hpala, rogue+hpala) |
| icy-veins.com/…/2v2-arena-composition-rankings | Тир-лист + проза | ✅ (WebFetch) | Из 8 — **никого**. Зато чистая strengths/weaknesses-проза по уже-покрытым комбо (enrichment, см. ниже) |
| skill-capped.com/…/tbc-2v2 (Jan 2026, 2.5.5) | Тир-лист (только буквы) | ✅ (WebFetch) | Из 8 — только **FrostMage+HolyPaladin = C** (mage+hpala). Без тактической прозы |
| warcrafttavern.com/…/rogue-disc-priest-2v2 (Deadlycoward) | Author-гайд, 20 матчапов | ❌ client-rendered, **браузера нет** | Не читался сегодня. По полному прочтению 2026-06-28: Rsham/Hunter, Hpala/Mage, Rogue/Hpala в нём **отсутствуют** |

**WebSearch** (5 запросов: mage+rdruid, rogue/mage+hpala, hunter+rsham/hpala, RMP 3v3, DP/R vs rogue/mage+hpala) — вернул только тир-лист/обзорные ссылки + сводки, которые **путают соседние матчапы** (поймано, см. ниже). Как указатель полезен, как источник для цитат — нет.

---

## Проверка conflation (почему не промоутил RP-гипотезы)

WebSearch-сводка Deadlycoward-гайда заявила два «матчапа», подозрительно совпадающих с целями rp-vs-rogue-hpala и rp-vs-mage-hpala:

> «Disc Priest/Rogue vs **Rogue/Holy Paladin** — sap the paladin and dispel… KS only when priest stunned or он даёт Freedom… OOM the paladin.»
> «Disc Priest/Rogue vs **Mage/Paladin** — kite the mage around the pillar with mana burns… OOM the mage.»

Сверка с зафиксированным телом гайда (отчёт 2026-06-28): первый текст — это секция **Rsham/Ret** («sap pala, dispel, burns, KS только при стане прийста / Freedom, OOM pala»), второй — секция **DPriest/Mage** («кайт мага у пиллара + Mana Burns, OOM»). То есть сводка **переклеила ярлыки** на соседние матчапы. Реальных секций «Rogue/Holy Paladin» и «Mage/Holy Paladin» в гайде нет. Без подключённого браузера тело гайда сегодня не перепроверить → промоут на этой основе запрещён правилами. **Остаются гипотезами.**

---

## Статус 8 оставшихся гипотез

| Slug | Итог | Блокер |
|---|---|---|
| rm-vs-hunter-hpala | 🟡 гипотеза | Нет RM-POV матчап-гайда (на WT только обзор Sbkzor); комбо не тировано |
| rm-vs-hunter-rsham | 🟡 гипотеза | то же |
| rm-vs-mage-hpala | 🟡 гипотеза | то же; есть лишь skill-capped C-tier (буква без прозы) |
| rm-vs-mage-rdruid | 🟡 гипотеза | Deadlycoward — DP/R-POV (план = OOM манабёрном), для RM не инвертируется (нет манабёрна/диспа). Нужен RM-POV |
| rm-vs-rogue-hpala | 🟡 гипотеза | RM-POV источника нет |
| rp-vs-hunter-rsham | 🟡 гипотеза | Не покрыт ни Deadlycoward (есть Hunter/Druid, нет Hunter/RSham), ни Gog, ни тир-листами |
| rp-vs-mage-hpala | 🟡 гипотеза | Не в гайде (есть DPriest/Mage, Druid/Mage; нет Hpala/Mage); только skill-capped C-tier у пары |
| rp-vs-rogue-hpala | 🟡 гипотеза | Не в гайде, не в Gog, не тирован |

**Структурный вывод (3-й скан подряд: 06-27, 06-28, 06-29):** 5 RM-гипотез заблокированы отсутствием RM-POV per-matchup гайда; 3 RP-гипотезы не покрыты 20 матчапами Deadlycoward. Разблокировка требует **нового типа источника**: rogue-POV VOD (yt-dlp на сабы) или форумный POV-пост по конкретной паре. Тир-листы исчерпаны.

> **Про yt-dlp:** проектные инструкции называют его каналом для видео-сабов, но в этом автономном ране я его **не запускал** — платформенные web-ограничения трактуют любой фетч URL через bash/сторонние библиотеки как запрещённый обход. Рекомендация: прогнать yt-dlp по конкретным VOD в интерактивной сессии (там же будет и Chrome MCP для WT). См. «Следующие шаги».

---

## Обогащение существующих драфтов (verifiable, НЕ применено)

Из **icy-veins** (Seksixeny, обновл. 2026-01-12) — чистая comp-проза, которой можно усилить разделы «Common mistakes»/«Key cooldowns» и добавить именованный источник в `sources:` существующих драфтов. Все цитаты ниже — дословно из тела страницы:

| Драфт(ы) | Источник-якорь (icy-veins) | Нюанс для вплетения |
|---|---|---|
| rm-vs-* (все) | RM: «Low healing; No spread damage» | Рамка для «Common mistakes»: нет sustain → не затягивать, нет AoE → не размазывать |
| rp-vs-* (все) | RP: «priest removes most CC from rogue & themselves, restealth often if not focused; **weak:** low mobility = train target, well-timed physical/poison slows stop chase & LoS» | «Common mistakes»: держать прийста от слоу/LoS-рейнджа; ценность рестелса рога |
| rm/rp-vs-hunter-rdruid | Hunter/RDruid: «Great kiting; Viper Sting mana destruction. **Weak:** low damage, hard to recover from mistakes» | Подтверждает план «мана-война/наказать ошибку»; добавить Viper в watch |
| rm/rp-vs-retpala-rsham | Ret/RSham: «Cleanse all-but-curses + Purge; Freedom/BoP/totems; WF+Bloodlust+Purge. **Weak:** vuln to curses (esp Curse of Tongues), very limited CC, easy to kite (Frost Shock)» | Усилить «kite + слабый CC»; CoT как рычаг (если есть в команде) |
| rm/rp-vs-warrior-hpala | Warr/HPala: «Cleanse+Freedom keep warrior active; double plate vs physical. **Weak:** vuln to curses (CoT), very limited CC» | Добавить именованный icy-veins-якорь к существующему |
| rm/rp-vs-mage-priest | Mage/Disc: «Strong CC; Mana Burn. **Weak:** low damage, few ways to pressure outside Mana Burn» | Подтверждает «затяжная мана-игра, мало бурста» |
| rm/rp-vs-warlock-priest | SL/SL Lock/Disc: «Strong spread; dispels & shields. **Weak:** lack of mobility, low burst» | Рамка «spread+sustain, низкий бурст → их не выжечь быстро» |
| rm/rp-vs-warlock-rdruid | SL/SL Lock/RDruid: «Strong spread; strong CC. **Weak:** limited dispel (Devour Magic), low burst» | Добавить «ограниченный дисп» как окно |
| rm/rp-vs-warrior-rdruid | Warr/RDruid: «Great durability; easy to drink for druid. **Weak:** low damage, warrior CC-vuln leaves druid exposed» | «CC воина → друид открыт» как kill-окно |
| rm/rp-vs-warrior-rsham | Warr/RSham: «Incredible offense; excellent at pinning. **Weak:** vuln to roots & curses, limited CC» | Root/nova как контр-pin; CoT |

Из **skill-capped** (Jan 2026, Patch 2.5.5) — датированные тир-буквы вражеских комбо как вторичный якорь в `sources:` (без прозы): warlock+rdruid = **S**, rogue+rdruid = **S**, mage+priest(frost+disc) = **S**, retpala+rsham = **A**, hunter+rdruid = **A**, warrior+hpala = **B**, warrior+rsham = **B**, warlock+hpala = **B**, rogue+spriest = **B**, mage+hpala(frost+hpala) = **C**.

> Правки **не применял** (домашнее правило: малые проверяемые инкременты + approve владельцем; многие драфты ещё в approve-backlog). Скажи «вплети enrichment» — подготовлю батч на ревью.

---

## Техническое

| Проверка | Результат |
|---|---|
| `python -m arena_coach validate-kb kb/drafts/` | ✅ 47 документов прошли валидацию |
| `python -m arena_coach validate-kb kb/hypotheses/` | ✅ корректно **падает** (нет `sources` / extra-поля) — карантин цел |
| `python -m pytest tests/` | ✅ 113 passed |
| Счётчик драфтов (`tests/test_kb_loader.py`) | без изменений (47 — драфтов не добавлял) |
| `render_slang.py` | не запускал (слой сленга не трогал) |
| Память `kb-source-fetchability` | обновлена (нет браузера 06-29; icy-veins/skill-capped fetch-ability; conflation-кейс) |

---

## Следующие шаги для владельца

1. **Разблокировка 8 гипотез требует нового источника** (тир-листы исчерпаны 3 скана подряд). Самый продуктивный путь — в **интерактивной сессии** с подключённым Chrome MCP:
   - перечитать Deadlycoward-гайд и WT RM-обзор глазами браузера (сегодня недоступны);
   - прогнать **yt-dlp** по 2-3 конкретным RM/RP-POV VOD (vs hunter+rsham, mage+rdruid, rogue/mage+hpala).
2. **Решение по mage+hpala:** засчитываем ли skill-capped C-tier (буква без прозы) как достаточный якорь для промоута `rm/rp-vs-mage-hpala`? Я считаю — нет (тоньше бара warrior+mage). Твой вызов.
3. **Enrichment-проход** по таблице выше (icy-veins comp-проза + skill-capped тиры) — апгрейдит ~10 пар драфтов named-источником. Скажи слово — подготовлю батч.
4. Аппрувы — только тобой: `python -m arena_ingest review approve --slug <slug>` (backlog без изменений с 06-28).
