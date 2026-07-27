# Arena Coach — ежедневный скан источников, отчёт 2026-07-27

> Авто-запуск `arena-coach-daily-source-scan`. Владелец отсутствовал — действовал автономно.
> **Ничего не аппрувил, не мёржил в `kb/matchups/`, новых драфтов не создавал, трекнутые файлы `kb/`/`tests/` не менял.**
> Единственная запись — этот отчёт в `docs/`.

## TL;DR

- **Гипотезы: 0 засорсено** (как 07-24 и 07-26). Те же 4 несоурснутые пары (`rm-vs-hunter-hpala`, `rm-vs-hunter-rsham`, `rm-vs-mage-rdruid`, `rp-vs-hunter-rsham`) — по-прежнему без бесплатного per-pair источника. Промоут из соседних секций = conflation → запрещён guardrail'ом (06-29/06-30).
- **Главный блокер подтверждён свежими проверками:** единственные per-matchup источники под наши составы — **платные** гайды rank1academy: подтвердил вербатим и **Rogue-POV** (`rogue-mage-matchup-tbc`), и **Rogue-POV DP/R** (`rogue-priest-matchup-tbc`), и **Mage-POV** (`mage-rogue-matchup-tbc`) — все за пейволом **148,95 €**, тело (per-matchup видео) недоступно.
- **YouTube-канал ингеста недоступен в этой песочнице:** `yt-dlp` установлен, но HTTP-прокси сэндбокса (`localhost:3128`) отдаёт **403 на youtube.com**, без прокси DNS не резолвится. Три релевантных RM-гайда на YT найдены, но транскрипты снять нельзя (см. §4 — это единственный реалистичный путь к бесплатному per-pair контенту, нужен запуск `yt-dlp` на машине владельца).
- **Новых проверенных источников для обогащения нет.** Всё, что нашлось свежего (koroboost 2026, aoeah, Icy Veins, skill-capped tier list) — **comp-level** и/или **boost-shop SEO низкой авторитетности**; наши 4 целевые enemy-пары там не оцениваются. Не годятся как KB-якорь.
- **Предложения по обогащению от 07-26 (§3: 11 RP-якорей Deadlycoward; §4: 6 comp-якорей Icy Veins) — по-прежнему ждут решения владельца.** Сегодня новых author-якорей не добыл, переношу их как pending.
- **Репо зелёное:** `validate-kb kb/drafts/` → **68 OK**; `pytest tests/` → **336 passed** (при `unset *_proxy` — иначе 7 ложных фейлов от httpx+socks, артефакт песочницы). Счётчик драфтов (68) не трогал.
- **Инородное состояние рабочего дерева** (не моё, унаследовано): 4 гипотезы с правкой `sacred shield → BoP` + 13 untracked `SCAN-REPORT-*` + `arena-comps-meta.patch`. Проверил правки — корректны (TBC-фикс). Не менял и не коммитил (§5).

## 1. Что просканировано и результат

| Источник | Доступ этот ран | Итог |
|---|---|---|
| **rank1academy — Rogue Mage Matchup (Rogue POV)** `…/rogue-mage-matchup-tbc` | WebFetch ✅ (server-rendered превью) | **Пейвол 148,95 €.** Подтверждено: библиотека per-matchup видео «covering all the team compositions… win conditions, kill setups, defensive priorities, common mistakes» — ровно недостающий RM-POV per-pair источник, но за оплатой. Бесплатный трейлер — YT `UOq0SEwP_Ro` (недоступен, см. §4). |
| **rank1academy — каталог TBC-гайдов** (та же страница) | WebFetch ✅ | В каталоге есть и **Rogue DP/R (Rogue POV)** `rogue-priest-matchup-tbc`, и **Mage/Rogue (Mage POV)** — оба тоже платные. То есть per-pair источники под RM и RP существуют, но все под пейволом. |
| **koroboost — TBC Arena Guide (2026)** `/guide/tbc-arena-guide` | WebFetch ✅ (server-rendered, полный текст) | Свежий (2026) boost-shop гайд. Comp-level: RM «Very High» сложность, «weak to anti-caster», нет сустейна; Rogue/Druid — лучший 2v2; RMP — топ-3v3, контрится WLD; Drain team. **Наши 4 enemy-пары не оценены.** Низкая авторитетность (SEO под продажу бустов) → не KB-якорь. |
| **silentshadows.net — Mage/Rogue** (нативный URL, не WT-миррор) `…/arena-strategies/mage-rogue-burning-crusade/` | WebFetch ⚠ | Снова тот же **WarcraftTavern nav-shell (75 101 симв., 220 «совпадений» = пункты меню класс-гайдов)**; тело матчапа client-rendered, в HTML его нет. Подтверждает 07-24/07-26: тело только через Chrome. |
| **Warmane forum — «Rogue/Mage 2s tips» t=371848** | WebFetch ⚠ | Редирект `showthread.php?t=…` **сбрасывает id темы** → «No Topic specified». Плюс Warmane сейчас WotLK/Cata/MoP-сервер (нет актуального TBC-реалма) → низкая авторитетность. Не тянул героикой. |
| WebSearch ×6 (reddit, skill-capped, mage/druid kill-target, hunter/hpala) | ✅ | Ни одного бесплатного per-pair источника по 4 целевым парам. Только comp-level сводки, тир-листы, boost-SEO и ссылки на платный/видео-контент. |
| **YouTube** — `DLEZ7Yi4-jU` (Rogue/Mage 2v2 guide), `mHgkNzlnpPQ` (2.5k Rated), `dKgQ4pP7EL0` (ULTIMATE Rogue Mage) | ❌ blocked | `yt-dlp` OK, но прокси песочницы = **403 на youtube.com** (см. §4). Транскрипты не сняты. |

## 2. Вердикт по 4 несоурснутым гипотезам (без изменений)

Все 4 **остаются гипотезами** — нет бесплатного per-pair источника. Ничего не переписывал.

| Гипотеза | Пара | Статус этого рана |
|---|---|---|
| `rm-vs-mage-rdruid` | RM vs Mage+RDruid | Ближе всех к source (enemy-comp `Druid/Mage` оценён Deadlycoward'ом, но это DP/R-план — несовместим с RM). RM-POV план есть **только** в платном rank1academy `rogue-mage-matchup-tbc`. Бесплатно — нет. |
| `rm-vs-hunter-hpala` | RM vs Hunter+HPala | Пара не оценивается ни RM-overview (Counter Comps), ни Icy Veins, ни koroboost. Нужен RM-POV per-matchup (платный) или стрим-VOD. |
| `rm-vs-hunter-rsham` | RM vs Hunter+RSham | То же. Из hunter-комбо тир-листы оценивают только Hunter+RDruid. |
| `rp-vs-hunter-rsham` | RP vs Hunter+RSham | Deadlycoward (20 матчапов, вербатим 07-26) Hunter/Rsham **не содержит**; DP/R-мана-дрейнеры называют Hunter/Druid, Hunter/Priest, Hunter/HPala — **Rsham нет**. Тянуть из `Druid/Hunter` нельзя (друид ≠ шаман). |

> Staged, но НЕ промоутнутые (лежат в `docs/proposals/` с 07-19): `rm-vs-hunter-rsham.draft.md`, `rp-vs-hunter-rsham.draft.md` — заблокированы тем же conflation-guardrail'ом. Не трогал.

## 3. Обогащение существующих драфтов — предложения ПЕРЕНЕСЕНЫ (pending с 07-26)

Новых проверенных author/tier-якорей сегодня не добыл (единственный свежий источник — koroboost — низкоавторитетный boost-SEO, не годится). Ранее подготовленные, всё ещё ждут решения владельца «применять/нет»:

- **§3 от 07-26 — 11 RP-драфтов ← per-matchup Deadlycoward** (`rp-vs-rogue-priest`, `-rogue-rdruid`, `-warlock-rdruid`, `-warrior-rdruid`, `-warrior-hpala`, `-mage-priest`, `-warlock-priest`, `-retpala-rsham`, `-rogue-mage`, `-rogue-spriest`, `-rogue-rogue`): добавить `{type: web, url: ".../rogue-disc-priest-2v2/", title: "Deadlycoward DP/R per-matchup — секция «…», Difficulty x/10"}` + тег `author-guide`. Чисто-аддитивный апгрейд провенанса, тело не меняется.
- **§4 от 07-26 — 6 comp-якорей Icy Veins 2v2 tier list** для `*-hunter-rdruid`, `*-warrior-hpala`, `*-warrior-rsham`, `*-retpala-rsham`, `*-rogue-rdruid`, `*-mage-priest` (RM/RP/RL). 2-й независимый comp-tier источник.

> Скажешь «да» — внесу пофайлово с diff в следующем ране. Сам не применял.

## 4. Рекомендация: как разблокировать 4 пары (для владельца)

Обе честные дороги требуют участия владельца — автономно из песочницы не решается:

1. **YouTube-транскрипты** (самый дешёвый бесплатный путь). Найдены 3 RM-гайда: `DLEZ7Yi4-jU`, `mHgkNzlnpPQ` («2.5k Rated»), `dKgQ4pP7EL0` («ULTIMATE Rogue Mage»). В этой песочнице `yt-dlp` упирается в прокси (403 youtube). **Если запустишь `yt-dlp --write-auto-subs --skip-download <url>` на своей машине и положишь `.vtt`/текст в репо (например `kb/_ingest_inbox/`)** — я на следующем ране распарсю, сверю с гипотезой и, если тактика подтверждается, оформлю sourced-draft. NB: это community-tier источник (не топ-гайд) — помечу тегом.
2. **rank1academy** (платный, 148,95 €). `rogue-mage-matchup-tbc` (RM-POV) закрывает `rm-vs-*` пары, `rogue-priest-matchup-tbc` (RP-POV) — `rp-vs-*`. Если купишь — дай мне конспект/тайм-коды по нужным матчапам, засорсю честно с атрибуцией.

## 5. Проверки и состояние репо

```
$ PYTHONPATH=backend python -m arena_coach validate-kb kb/drafts/
OK: 68 документов прошли валидацию            # exit 0

$ (unset *_proxy) PYTHONPATH=backend:ingest:bridge python -m pytest tests/
336 passed in ~7s                              # exit 0
```

- Драфтов не добавлял → счётчик `tests/test_kb_loader.py` (68) не трогал, совпадает с диском (68 файлов).
- **Проксинапоминание для CI/локали:** в песочнице выставлен `ALL_PROXY=socks5h://localhost:1080`; `httpx` в `tests/test_bridge_hint_poller.py::TestGetHints` жадно строит SOCKS-транспорт и падает без `socksio` (7 ложных фейлов). На CI/машине владельца прокси нет — зелено (проверено `unset *_proxy` → 336 passed).
- **Унаследованное состояние рабочего дерева (НЕ моё, не менял):**
  - `kb/hypotheses/{rm-vs-hunter-hpala, rm-vs-mage-hpala, rm-vs-warlock-hpala, rp-vs-warlock-hpala}.md` — правка `sacred shield → BoP (Blessing of Protection)/Divine Protection`. **Проверил: корректно** — Sacred Shield это WotLK 3.0-абилка, в TBC 2.4.3 её нет (правило «никаких retail/WotLK»). Рекомендую закоммитить.
  - 13 untracked `docs/SCAN-REPORT-*.md` (07-11…07-26) + `docs/proposals/` + корневой `arena-comps-meta.patch` — ждут решения владельца (push/применить/выкинуть). Не трогал.

## 6. Что ждёт владельца

1. **Approve — на паузе.** 12 ранее засорсенных гипотез лежат в `kb/drafts/`, ждут `python -m arena_ingest review approve --slug <slug>`. Новых к очереди не добавил.
2. **Решение по §3/§4** (перенесены с 07-26): применять ли добавление source+tag к 11 RP-драфтам (Deadlycoward) и 6 comp-якорям (Icy Veins).
3. **Разблокировка 4 пар** (§4): либо прогнать `yt-dlp` локально по 3 найденным RM-гайдам и закинуть транскрипты в репо, либо дать конспект платного rank1academy.
4. **Коммит унаследованных правок** гипотез (`sacred shield → BoP`) + разгрести накопившиеся untracked scan-репорты (§5).
5. **Политический вопрос (открыт с 06-30):** разрешить ли class-synthesis-промоут (склейка class-handling секций с явными тегами) — тогда часть hunter-гипотез можно оформить. Пока по guardrail'у — нет.
