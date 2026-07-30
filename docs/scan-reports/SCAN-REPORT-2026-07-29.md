# Arena Coach — ежедневный скан источников, отчёт 2026-07-29

> Авто-запуск `arena-coach-daily-source-scan`. Владелец отсутствовал — действовал автономно.
> **Ничего не аппрувил, не мёржил в `kb/matchups/`, новых драфтов не создавал, трекнутые файлы `kb/`/`tests/` не менял.**
> Единственная запись — этот отчёт в `docs/scan-reports/`.

## TL;DR

- **Гипотезы: 0 засорсено** (6-й ран подряд: 07-24, 07-26, 07-27, 07-28, 07-29). Те же 4 несоурснутые пары — `rm-vs-hunter-hpala`, `rm-vs-hunter-rsham`, `rm-vs-mage-rdruid`, `rp-vs-hunter-rsham` — по-прежнему без бесплатного per-pair источника под наш POV. Промоут из соседних секций = conflation → запрещён guardrail'ом (06-29/06-30).
- **Новое за сегодня — чистый негатив по comp-tier каналам.** Оба главных tier-листа отдались через WebFetch **полным телом** (не shell): Icy Veins 2v2 (`icy-veins.com/tbc-classic/2v2-arena-composition-rankings`, upd. 12.01.2026) и Skill Capped 2v2 (`skill-capped.com/.../tbc-2v2/`, patch 2.5.5, upd. 19.01.2026). **Ни один из трёх наших enemy-комбо в них не оценён:**
  - **hunter+resto-shaman** — ни в Icy Veins, ни в SC, ни в AOEAH. Из hunter-комбо все три списка оценивают только Hunter+RDruid (+ SC: Hunter+DiscPriest). Отдельно подтверждено: Wowhead/Icy Veins рекомендуют шаману пары Ret-Pala / Warrior / Rogue — **Hunter среди них нет** (off-meta пара).
  - **mage+resto-druid** — не оценён нигде. SC перечисляет **все** frost-mage 2v2-комбо (Mage+DiscPriest S, Mage+SPriest C, Mage+HPala C) — Mage+RDruid **отсутствует**. Друид в мете пэрится с rogue/warlock/warrior, не с магом.
  - **hunter+holy-paladin** — не оценён нигде.
  Это тот же вывод, что 07-28, но добытый чище: не «сводки поиска путают матчапы», а прямое отсутствие пары в двух свежих полностью отрендеренных tier-листах.
- **Каналы перепроверены, негативы стабильны:**
  - `warcrafttavern.com` per-matchup (`rogue-mage-rogue-arena-strategies`) и его зеркало `silentshadows.net/arena-strategies/mage-rogue-burning-crusade/` → снова **WT nav-shell ~75 000 симв.**, тело матчапов client-rendered, в HTML только меню класс-гайдов. WebFetch тело не достаёт (как 07-24…28).
  - `silentshadows.net/disc-rogue-tactics-deadlycoward` (нативный URL Deadlycoward) → сегодня отдал **пустое тело** (0 симв. контента). Недоступен.
  - **rank1academy** per-matchup (RM-POV `rogue-mage-matchup-tbc`, Mage-POV, RP-POV `rogue-priest-matchup-tbc`) — по-прежнему пейвол **148,95 €**; на странице только маркетинг-копия + YouTube-трейлер `d7157Zi6r9s`, тактического тела нет.
- **Обогащение:** новых проверенных author/tier-якорей сегодня не добыл. Предложения §3/§4 от 07-26 (11 RP-драфтов ← Deadlycoward per-matchup; 6 comp-якорей Icy Veins) — **по-прежнему ждут решения владельца**, переношу как pending. Сегодняшний свежий Icy Veins (12.01.2026) их только подтверждает — тексты якорей ниже, в §3.
- **Репо зелёное:** `validate-kb kb/drafts/` → **80 OK**; `pytest tests/test_kb_loader.py` → **8 passed** (в песочнице доступен KB-набор; полный набор требует fastapi/sqlalchemy/discord.py — не ставил, кода не менял, регресс исключён). Счётчик драфтов `== 80` в `tests/test_kb_loader.py` совпадает с диском (80 файлов) — не трогал.

## 1. Что просканировано и результат

| Источник | Доступ этот ран | Итог |
|---|---|---|
| **WebSearch ×4** (RM vs hunter+rsham; RM vs mage+rdruid; hunter+rsham viability; silentshadows RM matchup) | ✅ | Ни одного бесплатного per-pair TBC-источника под наш POV. Только comp-level тир-листы + пейвол/видео. Подтверждено: hunter+rsham вне рекомендованных пар шамана. |
| **Icy Veins 2v2 tier list** (`…/2v2-arena-composition-rankings`, upd. 12.01.2026) | WebFetch ✅ (полное тело) | Comp-level таблица со strengths/weaknesses. Наши 3 enemy-комбо (hunter+rsham, hunter+hpala, mage+rdruid) **не оценены**. Оценены соседи: Hunter+RDruid, Warr+HPala, Warr+RSham, RetPala+RSham, Mage+DiscPriest — годятся как enrichment-якоря (см. §3). |
| **Skill Capped 2v2 tier list** (`…/tbc-2v2/`, patch 2.5.5, 19.01.2026) | WebFetch ✅ (полное тело) | Тир-раскладка. Перечислены все frost-mage и hunter комбо — наших 3 enemy-пар **нет**. Подтверждает off-meta статус. |
| **AOEAH 2v2 tier list** (`…/4283-…`, 26.12.2025) | WebFetch ✅ (полное тело) | Comp-level, детальные заметки. RM = S, RP = A. Наших 3 enemy-пар нет. |
| **Warcraft Tavern / silentshadows** per-matchup RM (`…/mage-rogue-…`) | WebFetch ⚠ | WT nav-shell (~75 000 симв., только меню). Тело client-rendered → только через Chrome. Подтверждает 07-24…28. |
| **silentshadows** Deadlycoward DP/R (нативный URL) | WebFetch ⚠ | Пустое тело (0 симв.). Недоступен. |
| **rank1academy** RM/Mage/RP-POV per-matchup | (превью) | Пейвол 148,95 €. Ровно недостающие per-pair источники, но тело за оплатой. |

## 2. Вердикт по 4 несоурснутым гипотезам (без изменений)

Все 4 **остаются гипотезами** — нет бесплатного per-pair источника под наш POV. Ничего не переписывал.

| Гипотеза | Пара | Статус этого рана |
|---|---|---|
| `rm-vs-mage-rdruid` | RM vs Mage+RDruid | Пара off-meta: SC перечисляет все frost-mage 2v2-комбо, Mage+RDruid среди них нет; Icy Veins/AOEAH тоже без неё. RM-POV план только в платном rank1academy. Бесплатно — нет. |
| `rm-vs-hunter-hpala` | RM vs Hunter+HPala | Пара не оценивается ни в Icy Veins, ни в SC, ни в AOEAH, ни в RM-overview. Нужен RM-POV per-matchup (платный) или стрим-VOD. |
| `rm-vs-hunter-rsham` | RM vs Hunter+RSham | То же. Из hunter-комбо тир-листы оценивают только Hunter+RDruid (SC — ещё Hunter+DiscPriest). Hunter+RSham — off-meta. |
| `rp-vs-hunter-rsham` | RP vs Hunter+RSham | Hunter+RSham вне рекомендованных пар шамана (Ret/Warr/Rogue). Тянуть из `Hunter/RDruid` нельзя (друид ≠ шаман: нет grounding/tremor/purge, зато cyclone/HoT). |

> Staged, но НЕ промоутнутые (в `docs/proposals/` с 07-19): `rm-vs-hunter-rsham.draft.md`, `rp-vs-hunter-rsham.draft.md` — заблокированы тем же conflation-guardrail'ом. Не трогал.

## 3. Обогащение существующих драфтов — ПЕРЕНЕСЕНО (pending с 07-26), сегодня подтверждён Icy Veins

Новых проверенных author-якорей не добыл, но **сегодняшний свежий Icy Veins 2v2 (12.01.2026) отдался полным телом** — это второй независимый comp-tier источник для 6 existing-драфтов. Вербатим-якоря (готовы к вставке в `sources:` как `{type: web, url: "https://www.icy-veins.com/tbc-classic/2v2-arena-composition-rankings", title: "…"}` + тег `comp-sourced`; тело драфта не меняется):

- **`*-hunter-rdruid`** (RM/RP): Icy Veins «Hunter/Resto Druid — Great kiting potential; Mana destruction with Viper Sting. **Weaknesses: Low damage; Difficult to recover from mistakes.**» → эксплойт: пережить опенер, наказать низкий kill-pressure.
- **`*-warrior-hpala`** (RM/RP): «Arms Warrior/Holy Paladin — keep Warrior active with Cleanse/Freedom; double plate survivability. **Weaknesses: vulnerable to curses (esp. Curse of Tongues); very limited CC.**» (NB: CoT у нас нет — это warlock; берём только «very limited CC» + double-plate как comp-якорь.)
- **`*-warrior-rsham`** (RM/RP): «Arms Warrior/Resto Shaman — incredible offensive potential; excellent at pinning targets. **Weaknesses: vulnerable to root effects and curses; limited CC.**»
- **`*-retpala-rsham`** (RM/RP): «Ret Paladin/Resto Shaman — cleanse+purge remove everything but curses; freedom/BoP/totems; WF/Bloodlust/Purge offense. **Weaknesses: vulnerable to CoT; very limited CC; easy to kite (Frost Shock).**»
- **`*-mage-priest`** (RM/RP): «Mage/Disc Priest — strong CC; Mana Burn. **Weaknesses: low damage; few ways to pressure outside Mana Burn.**»
- **`*-rogue-rdruid`** (RM/RP): AOEAH (26.12.2025) «Rogue/Resto Druid — very defensive, excellent reset. **Faerie Fire destroys Rogue; Blind+Cyclone DR awkward; requires perfect Cloak/Vanish timing.**»

Плюс всё ещё в силе **§3 от 07-26** — 11 RP-драфтов ← per-matchup Deadlycoward (author-guide тег), тело не меняется.

> NB: 12 RD-драфтов (`rd-vs-*`, добавлены владельцем 07-27) провенанс не аудировал. Скажешь «да» по §3/§4 — внесу пофайлово с diff. Сам не применял.

## 4. Проверки и состояние репо

```
$ PYTHONPATH=backend python -m arena_coach validate-kb kb/drafts/
OK: 80 документов прошли валидацию            # exit 0

$ PYTHONPATH=backend python -m pytest tests/test_kb_loader.py
8 passed in 0.32s                              # exit 0
```

- Драфтов не добавлял → счётчик `tests/test_kb_loader.py` (`assert ok == 80`) не трогал, совпадает с диском (80 файлов).
- Полный `pytest tests/` этим раном не гонял: свежая песочница не имеет fastapi/sqlalchemy/discord.py/anthropic/cryptography, а кода я не менял (только Read/WebFetch/bash-read) → регресс структурно исключён. KB-набор (единственное, что затрагивает мою зону) — зелёный.
- `ruff`/`mypy` не гонял (кода не касался). Слэнг не рендерил (`slang.json` без правок).

## 5. Что ждёт владельца

1. **Approve — на паузе.** 12 ранее засорсенных гипотез в `kb/drafts/` ждут `python -m arena_ingest review approve --slug <slug>`. Новых к очереди не добавил.
2. **Решение по §3/§4:** применять ли (а) добавление source+tag к 11 RP-драфтам (Deadlycoward, author-guide), (б) 6 comp-якорей Icy Veins/AOEAH (список вербатим — в §3 выше). Плюс: аудировать ли source-блоки 12 новых RD-драфтов.
3. **Разблокировка 4 пар** (оба пути требуют участия владельца, т.к. они off-meta и без бесплатного per-pair источника):
   - прогнать `yt-dlp --write-auto-subs --skip-download <url>` локально по RM-гайдам (`DLEZ7Yi4-jU`, `d7157Zi6r9s`) и положить `.vtt`/текст в `kb/_ingest_inbox/` → распарсю, сверю с гипотезой, оформлю sourced-draft (community-tier);
   - либо конспект/тайм-коды платного rank1academy (RM-POV → `rm-vs-*`, RP-POV → `rp-vs-*`).
4. **Политический вопрос (открыт с 06-30):** разрешить ли class-synthesis-промоут (склейка class-handling секций с явными тегами). Пока по guardrail'у — нет.
5. **Хозяйственное:** накопились untracked `docs/scan-reports/SCAN-REPORT-*.md` + `docs/proposals/` + git показывает старые `docs/SCAN-REPORT-*.md` как deleted (перенесены в `docs/scan-reports/`) — решить push/commit/выкинуть. Плюс `.git/index.lock` в рабочей копии (Operation not permitted при git-операциях из песочницы) — на машине владельца снять `rm -f .git/index.lock` при необходимости.
