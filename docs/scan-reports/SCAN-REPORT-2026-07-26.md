# Arena Coach — ежедневный скан источников, отчёт 2026-07-26

> Авто-запуск `arena-coach-daily-source-scan`. Владелец отсутствовал — действовал автономно.
> **Ничего не аппрувил, не мёржил в `kb/matchups/`, новых драфтов не создавал, трекнутые файлы `kb/`/`tests/` не менял.**
> Единственная запись — этот отчёт в `docs/`.

## TL;DR

- **Chrome MCP подключён** (Browser 1, macOS). В этот раз прочитан **вербатим, first-hand** не только WT-overview, а **полный per-matchup гайд Deadlycoward** `…/rogue-disc-priest-2v2/` (все 20 матчапов с difficulty-рейтингами) + WT Mage/Rogue overview. Плюс WebFetch: **Icy Veins 2v2 tier list** (server-rendered, полный текст), WebSearch ×5.
- **Гипотезы: 0 засорсено** (как 07-24). Все 4 оставшиеся пары (`rm-vs-hunter-hpala`, `rm-vs-hunter-rsham`, `rm-vs-mage-rdruid`, `rp-vs-hunter-rsham`) **не оцениваются per-pair** ни в одном найденном источнике. Промоут = conflation → запрещён guardrail'ом 06-29/06-30.
- **Ключевая проверка (Deadlycoward, 20 матчапов, вербатим):** его Healer/DPS-список — `DPriest/Rogue, DS/Rogue, Druid/Hunter, Druid/Lock, Druid/Warr, Hpala/Warr, Rsham/Warr, DPriest/Mage, DPriest/Lock, Druid/Mage, Rsham/Ret`. **Hunter/Rsham и Hunter/Hpala там НЕТ.** Значит `rp-vs-hunter-rsham` из секции `Druid/Hunter` тянуть нельзя (друид ≠ шаман по кит-набору) — это ровно запрещённый conflation.
- **Новая ценность рана — обогащение существующих драфтов:** полный per-matchup Deadlycoward даёт **вербатим-якорь для 11 существующих RP-драфтов**, которые его ещё НЕ цитируют (см. §3). Icy Veins 2v2 tier list — comp-level якорь для ряда RM/RP/RL-драфтов (§4). Это **предложения**, не применял.
- **rank1academy «Mage Rogue Matchup Guide (Mage POV)»** — это именно недостающий RM-POV per-matchup источник, НО **платный, €148.95**, тело за пейволом. Не источник (только подтверждает, что такой гайд существует).
- **Репо зелёное:** `validate-kb kb/drafts/` → **68 OK**; `pytest tests/` → **295 passed** (7 «падений» — артефакт песочницы: `ALL_PROXY=socks5h://…` + нет `socksio`; при `unset *_proxy` → все зелёные). Счётчик драфтов (68) не трогал — драфтов не добавлял.

## 1. Что просканировано и результат

| Источник | Доступ этот ран | Итог |
|---|---|---|
| **WT — Disc Priest/Rogue, per-matchup** `…/rogue-disc-priest-2v2/` (Deadlycoward, Infernal Glad, 2919 rating S1) | **Chrome** ✅ (client-rendered) | **Вербатим все 20 матчапов + difficulty.** Hunter/Rsham и Hunter/Hpala — **не оцениваются**. Даёт per-matchup якоря для существующих RP-драфтов (§3). |
| **WT — Mage/Rogue overview** `…/rogue-mage-rogue-arena-strategies/` | **Chrome** ✅ | Вербатим. **RM Counter Comps:** Human-rogue combs · Dwarf Disc+Mage/Warlock · Rogue/Druid · Lock/Druid · Lock/Hpala. Hunter/Hpala, Hunter/Rsham, **Mage/Druid — не названы.** Это overview, per-matchup секций нет. |
| **Icy Veins — 2v2 Arena Composition Tier List** (Seksixeny, upd. 2026-01-12) | **WebFetch** ✅ (server-rendered, полный текст) | Оценивает как comp'ы: **Hunter+RDruid** (kite + Viper Sting mana-drain, low dmg, hard to recover), **Arms Warr+HPala**, **Arms Warr+RSham**, **Ret+RSham**, **Rogue+RDruid**, **Mage+DiscPriest**. Наши целевые пары (hunter+rsham/hpala, mage+rdruid) **НЕ** в списке. Годится как якорь для существующих драфтов (§4). |
| **rank1academy — Mage Rogue Matchup Guide (Mage POV)** (Spottman & Petraxs) | **Chrome** ✅ (preview) | **Пейвол €148.95.** Тело (per-matchup видео) недоступно. Подтверждает: RM-POV per-matchup гайд существует — это и есть недостающий источник для `rm-vs-mage-rdruid` и RM-vs-hunter, но платный. |
| **silentshadows.net** (DPR/RM mirror) | WebFetch ⚠ | Как 07-24: WebFetch отдаёт только WT nav-шелл (75k симв.), тело client-rendered. Тело читается только через Chrome по WT-URL. |
| WebSearch ×5 (mmo-champion, ownedcore, tier-lists) | ✅ | Ни одного per-pair source по 4 целевым парам. Форумные ветки (mmo-champion 604611 Shaman/Warrior, ownedcore) — не про наши пары либо устаревшие 2007-08. |

## 2. Вердикт по 4 несоурснутым гипотезам

Все 4 — **остаются гипотезами** (нет per-pair источника). Ничего не переписывал.

| Гипотеза | Пара | Почему не засорсено | Ближайший путь к source |
|---|---|---|---|
| `rm-vs-hunter-hpala` | RM vs Hunter+HPala | Hunter/HPala не оценивается ни RM-overview (Counter Comps), ни Icy Veins, ни Deadlycoward. Comp'а как такового в тир-листах нет. | RM-POV per-matchup гайд (rank1academy — платный) или стрим-VOD с этим матчапом. |
| `rm-vs-hunter-rsham` | RM vs Hunter+RSham | То же: пара не названа нигде. Icy Veins из hunter-комбо оценивает только Hunter+RDruid. | То же. |
| `rm-vs-mage-rdruid` | RM vs Mage+RDruid | **Enemy-comp оценён** (Deadlycoward `Druid/Mage` 5/10), но это **DPR-гайд** — план RP (OOM манабёрном, дисп), несовместим с RM (бурст, нет манабёрна/диспа). RM-overview Mage/Druid в Counter Comps **не** называет. Промоут по DPR-секции = conflation. | RM-POV источник (rank1academy — платный) или стрим. **Из 4 — ближе всех** (enemy-comp уже кем-то оценён). |
| `rp-vs-hunter-rsham` | RP vs Hunter+RSham | Deadlycoward per-matchup (вербатим): Hunter/Rsham **не входит** в 20 матчапов. DPR-overview из мана-дрейнеров называет `Hunter/Druid, Hunter/Priest, even Hunter/HPaladin` — **Hunter/Rsham нет.** Тянуть из `Druid/Hunter` (10/10) нельзя — друид ≠ шаман. | Источник, где RP/DPR оценивает именно hunter+resto-shaman. Пока нет. |

## 3. Обогащение существующих RP-драфтов — Deadlycoward per-matchup (ПРЕДЛОЖЕНИЕ)

Прочитав **весь** per-matchup гайд Deadlycoward вербатим, нашёл прямые матчап-секции (с его difficulty-рейтингом и планом), которые ложатся на **существующие RP-драфты, ещё не цитирующие этот гайд**. Это апгрейд провенанса (author-guide, Infernal Gladiator) — особенно для драфтов с одним источником.

**Уже цитируют `rogue-disc-priest-2v2`** (не трогать): `rp-vs-mage-hpala`, `rp-vs-mage-rdruid`, `rp-vs-rogue-hpala`, `rp-vs-warlock-rogue`, `rp-vs-warrior-rsham`.

**Кандидаты на добавление источника** (маппинг «наш драфт ← секция Deadlycoward»):

| Драфт (тек. кол-во src) | Секция Deadlycoward | Diff | Суть плана из источника (для сверки с телом драфта) |
|---|---|---|---|
| `rp-vs-rogue-priest` (1) | Mirror DPriest/Rogue | 5/10 | Фокус вражеского рога; свитч на прийста если рог под контролем/прийст в плохой позе под дисп. Осторожно с Mass Dispel в старте. |
| `rp-vs-rogue-rdruid` (1) | Druid/Rogue | 9/10 | Kill рога на 2-м Blind; друида — в human form после Fear→Sap/Blind без тринкета. Сидеть у пиллара, все fear на рога, рестелс+новый опенер. |
| `rp-vs-warlock-rdruid` (1) | Druid/SL Warlock | 7/10 | Sap лока+фулл дисп, липнуть к локу хардом; Blind на друида. Опции: OOM друида, kill лока на 2-м blind, или снять пета. |
| `rp-vs-warrior-rdruid` (1) | Druid/Warrior | 7/10 | В осн. kill warrior; sap warrior + фейк Berserker Rage → ресап; либо прийст 1v1 воина, рог CS-KS друида → фри Fear. |
| `rp-vs-warrior-hpala` (3, нет Deadlycoward) | Holy paladin/Warrior | 7/10 | Kill warr 90%; пала — манабёрнами. Опенер: CS-KS по пале, KS придержать до чарджа воина, свитч на воина под давлением. Не сапать палу в старте. |
| `rp-vs-mage-priest` (1) | Disc Priest/Frost Mage | 7/10 | Никогда не агриться (иначе луз); кайт мага у пиллара + манабёрны, рестелс. Kill: либо OOM мага, либо sap+дисп прийста и добить. |
| `rp-vs-warlock-priest` (1) | Disc Priest/SL Warlock | 7/10 | Как DP/M, но кайт длинными дистанциями, не у пиллара (у Disc/Lock нет poison-диспа). Kill прийста (не дворф) или лока под давлением. |
| `rp-vs-retpala-rsham` (1) | Resto shaman/Ret paladin | 7/10 | Kill пала: sap+дисп, бёрны, KS только когда прийст застанен / на BoF (прийст диспелит). Пала лёгок после OOM. |
| `rp-vs-rogue-mage` (1) | Frost Mage/Rogue | 7/10 | В осн. kill рога; беречься сапа (мага Spellsteal), дистанция от прийста. Shadowstep/Garrote в окно sap+Poly; трин от KS по ситуации. |
| `rp-vs-rogue-spriest` (3, Windz-гайд, нет Deadlycoward) | Shadow Priest/Rogue | 5/10 | Kill SP как можно дальше от своего прийста, без сапа рашить SP; «DP/R counters SP/R». Второй, независимый author-якорь к существующему Windz. |
| `rp-vs-rogue-rogue` (1) | Rogue/Rogue | 7/10 | Прийст спиной к стене (от гарроты), рог поодаль (от сапа). Хард на одного рога bleeds/Vanish-CS-Evisc до сброса DR блайнда. |

> Итого: **11 предложений**. Приоритет — драфты с 1 источником. Для каждого предлагаю добавить `{type: web, url: "https://www.warcrafttavern.com/tbc/guides/rogue-disc-priest-2v2/", title: "Deadlycoward DP/R per-matchup — секция «<...>», Difficulty <x>/10: <короткая цитата плана>", retrieved: "2026-07-26"}` и тег `author-guide`. Тело править не требуется, если план не расходится — где разойдётся, отмечу в следующем ране. **Сам не применял.**

## 4. Обогащение RM/RP/RL-драфтов — Icy Veins 2v2 tier list (ПРЕДЛОЖЕНИЕ)

Icy Veins (server-rendered, свежий upd. 2026-01-12) даёт comp-level оценку enemy-comp'ов, которые уже покрыты драфтами. Годится 2-м независимым comp-якорем (в дополнение к WT/AOEAH):

| Enemy comp (Icy Veins) | Оценка (кратко) | Существующие драфты |
|---|---|---|
| Hunter + Resto Druid | kite + Viper Sting mana-drain; low damage; hard to recover from mistakes | `rm-vs-hunter-rdruid`, `rp-vs-hunter-rdruid` |
| Arms Warrior + Holy Paladin | Cleanse/Freedom держат воина, double-plate; vuln. Curse of Tongues, very limited CC | `rm-vs-warrior-hpala`, `rp-vs-warrior-hpala`, `rl-vs-warrior-holy-paladin` |
| Arms Warrior + Resto Shaman | огромный офф-потенциал, пиннинг цели; vuln. roots/curses, limited CC | `rm-vs-warrior-rsham`, `rp-vs-warrior-rsham`, `rl-vs-warrior-resto-shaman` |
| Ret Paladin + Resto Shaman | Cleanse/Purge/Freedom/BoP/Windfury/Bloodlust; vuln. CoT, very limited CC, easy to kite (Frost Shock) | `rm-vs-retpala-rsham`, `rp-vs-retpala-rsham`, `rl-vs-ret-paladin-resto-shaman` |
| Rogue + Resto Druid | double-stealth опенеры, CC-чейн (stun/cyclone/blind без общего DR), Restokin dmg; low tankiness, нет диспа → рог уязвим к CC | `rm-vs-rogue-rdruid`, `rp-vs-rogue-rdruid`, `rl-vs-rogue-resto-druid` |
| Mage + Disc Priest | сильный CC + Mana Burn; low damage, мало давления вне манабёрна | `rm-vs-mage-priest`, `rp-vs-mage-priest`, `rl-vs-mage-priest` |

> Предложение: где у драфта нет независимого comp-tier якоря — добавить Icy Veins `{type: web, url: "https://www.icy-veins.com/tbc-classic/2v2-arena-composition-rankings", ...}`. Особенно полезно для `*-warrior-rsham`, `*-retpala-rsham`, `*-rogue-rdruid`. **Не применял.**

## 5. Проверки (репо не менял)

```
$ PYTHONPATH=backend python -m arena_coach validate-kb kb/drafts/
OK: 68 документов прошли валидацию            # exit 0

$ PYTHONPATH=backend:ingest:bridge python -m pytest tests/    # (proxy env unset)
295 passed in ~5s                              # exit 0
```

Примечание для CI/локали: в песочнице этого рана был выставлен `ALL_PROXY=socks5h://localhost:1080`; `httpx` при инициализации клиента в `tests/test_bridge_hint_poller.py::TestGetHints` жадно строит SOCKS-транспорт и падает без пакета `socksio` (7 ложных фейлов). На CI/локали владельца этого прокси нет — тесты зелёные (проверено `unset *_proxy` → 295 passed). Кода это не касается.

## 6. Что ждёт владельца

1. **Approve — по-прежнему на паузе.** 12 ранее засорсенных гипотез лежат в `kb/drafts/` и ждут `python -m arena_ingest review approve --slug <slug>`. Ничего нового к очереди не добавил.
2. **Решение по §3 (11 RP-обогащений Deadlycoward)** — применять ли добавление source+tag. Быстрый, чисто-аддитивный апгрейд провенанса; тело драфтов не меняется. Скажешь «да» — внесу в следующем ране пофайлово с diff.
3. **Решение по §4 (Icy Veins comp-якоря)** — добавлять ли 2-й независимый comp-tier источник.
4. **`rm-vs-mage-rdruid`** — единственная из 4 гипотез, где enemy-comp уже кем-то оценён. Если добудешь RM-POV источник (rank1academy платный; либо дай стрим/VOD) — засорсю честно.
5. **Политический вопрос (открыт с 06-30):** разрешить ли class-synthesis-промоут (склейка class-handling секций) — тогда часть hunter-гипотез можно оформить с явными тегами. Пока по guardrail'у — нет.
