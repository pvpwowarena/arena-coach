# Arena Coach — ежедневный скан источников, отчёт 2026-07-28

> Авто-запуск `arena-coach-daily-source-scan`. Владелец отсутствовал — действовал автономно.
> **Ничего не аппрувил, не мёржил в `kb/matchups/`, новых драфтов не создавал, трекнутые файлы `kb/`/`tests/` не менял.**
> Единственная запись — этот отчёт в `docs/`.

## TL;DR

- **Гипотезы: 0 засорсено** (5-й ран подряд: 07-24, 07-26, 07-27, 07-28). Те же 4 несоурснутые пары — `rm-vs-hunter-hpala`, `rm-vs-hunter-rsham`, `rm-vs-mage-rdruid`, `rp-vs-hunter-rsham` — по-прежнему без бесплатного per-pair источника под наш POV. Промоут из соседних секций = conflation → запрещён guardrail'ом (06-29/06-30).
- **Новое за сегодня — отсеян ложный кандидат:** WebSearch на `rm-vs-mage-rdruid` первым выдаёт тред Blizzard-форума «Rogue Mage vs. Resto Druid» (`us.forums.blizzard.com/.../402785`) — server-rendered, читается через WebFetch. **Но это RETAIL (BFA-эра), не TBC 2.4.3:** в теле Vendetta, Combustion как burst-CD, Incarnation, Soul of the Forest, feral/balance **affinity**, dampening 23%, Klepto, Overgrowth, Ironbark, Rake-stun. По правилу «никаких retail/WotLK способностей» — **отклонён, не источник.** Логирую, чтобы будущие раны не приняли его за TBC-якорь.
- **Каналы перепроверены, все негативы стабильны:**
  - `silentshadows.net/disc-rogue-tactics-deadlycoward/` (нативный URL Deadlycoward) → снова **WT nav-shell 75 089 симв.**, тело матчапов client-rendered, в HTML его нет. WebFetch тело не достаёт (как 07-24/26/27).
  - **YouTube/yt-dlp — заблокирован** (прокси песочницы 403 на youtube.com, как в прошлых ранах). RM-гайд `DLEZ7Yi4-jU` («Anniversary TBC Rogue/Mage 2v2», 04.02.2026) всё ещё висит кандидатом, но транскрипт снять из песочницы нельзя.
  - **rank1academy** per-matchup (RM-POV `rogue-mage-matchup-tbc`, Mage-POV, RP-POV `rogue-priest-matchup-tbc`) — по-прежнему пейвол **148,95 €**, тело недоступно.
- **Обогащение:** новых проверенных author/tier-якорей сегодня не добыл. Предложения от 07-26 (§3: 11 RP-драфтов ← Deadlycoward per-matchup; §4: 6 comp-якорей Icy Veins) — **по-прежнему ждут решения владельца**, переношу как pending.
- **Репо зелёное:** `validate-kb kb/drafts/` → **80 OK**; `pytest tests/` → **388 passed**. Счётчик драфтов уже `== 80` в `tests/test_kb_loader.py` (обновлён владельцем вместе с 12 RD-драфтами 07-27) — не трогал, совпадает с диском (80 файлов).

## 1. Что просканировано и результат

| Источник | Доступ этот ран | Итог |
|---|---|---|
| **WebSearch ×6** (RM vs hunter+hpala; RM vs hunter+rsham; RM vs mage+rdruid; RP vs hunter+rsham; Anniversary-2026 RM-видео; RMP-3v3) | ✅ | Ни одного бесплатного per-pair TBC-источника под наш POV по 4 целевым парам. Только comp-level тир-листы (aoeah, skill-capped, koroboost, Icy Veins, frostyboost, overgear), boost-SEO и ссылки на платный/видео-контент. Сводки поиска путают соседние матчапы — проверял по телу. |
| **Blizzard forum — «Rogue Mage vs. Resto Druid»** `…/t/…/402785` | WebFetch ✅ (server-rendered, тело целиком) | **RETAIL, не TBC.** Vendetta/Combustion/Incarnation/affinity/dampening/Klepto/Overgrowth/Ironbark. Отклонён (см. TL;DR). Единственный per-topic тред на пару — и тот не той эпохи. |
| **silentshadows.net — Deadlycoward DP/R** (нативный URL) | WebFetch ⚠ | WT nav-shell (75 089 симв., только меню класс-гайдов). Тело client-rendered → только через Chrome. Подтверждает 07-24/26/27. |
| **YouTube** `DLEZ7Yi4-jU` (Anniversary RM 2v2, фев-2026) | ❌ blocked | `yt-dlp` упирается в прокси песочницы (403 youtube). Транскрипт не снят. Общий RM-гайд, не per-pair под 4 цели. |
| **rank1academy** RM-POV / Mage-POV / RP-POV per-matchup | (превью) | Пейвол 148,95 €. Ровно недостающие per-pair источники, но тело за оплатой. |
| **koroboost / frostyboost / overgear / aoeah / skill-capped / Icy Veins** тир-листы | ✅ | Comp-level. Наши 4 enemy-пары не оцениваются per-pair. Boost-shop'ы — низкая авторитетность. Не KB-якорь. |

## 2. Вердикт по 4 несоурснутым гипотезам (без изменений)

Все 4 **остаются гипотезами** — нет бесплатного per-pair источника под наш POV. Ничего не переписывал.

| Гипотеза | Пара | Статус этого рана |
|---|---|---|
| `rm-vs-mage-rdruid` | RM vs Mage+RDruid | Ближе всех к source (enemy-comp `Druid/Mage` 5/10 оценён Deadlycoward'ом — но это DP/R-план, несовместим с RM). Единственный ложный per-topic хит (Blizzard-форум) оказался RETAIL → отсеян. RM-POV план только в платном rank1academy. Бесплатно — нет. |
| `rm-vs-hunter-hpala` | RM vs Hunter+HPala | Пара не оценивается ни RM-overview (Counter Comps), ни Icy Veins, ни koroboost. Нужен RM-POV per-matchup (платный) или стрим-VOD. |
| `rm-vs-hunter-rsham` | RM vs Hunter+RSham | То же. Из hunter-комбо тир-листы оценивают только Hunter+RDruid. |
| `rp-vs-hunter-rsham` | RP vs Hunter+RSham | Deadlycoward (20 матчапов, вербатим 07-26) Hunter/Rsham **не содержит**; DP/R-мана-дрейнеры называют Hunter/Druid, Hunter/Priest, Hunter/HPala — **Rsham нет** (сегодня подтверждено и сводкой поиска). Тянуть из `Druid/Hunter` нельзя (друид ≠ шаман). |

> Staged, но НЕ промоутнутые (в `docs/proposals/` с 07-19): `rm-vs-hunter-rsham.draft.md`, `rp-vs-hunter-rsham.draft.md` — заблокированы тем же conflation-guardrail'ом. Не трогал.

## 3. Обогащение существующих драфтов — ПЕРЕНЕСЕНО (pending с 07-26)

Новых проверенных author/tier-якорей сегодня не добыл. Ранее подготовленные, всё ещё ждут решения владельца «применять/нет»:

- **§3 от 07-26 — 11 RP-драфтов ← per-matchup Deadlycoward** (`rp-vs-rogue-priest`, `-rogue-rdruid`, `-warlock-rdruid`, `-warrior-rdruid`, `-warrior-hpala`, `-mage-priest`, `-warlock-priest`, `-retpala-rsham`, `-rogue-mage`, `-rogue-spriest`, `-rogue-rogue`): добавить `{type: web, url: ".../rogue-disc-priest-2v2/", title: "Deadlycoward DP/R per-matchup — секция «…», Difficulty x/10"}` + тег `author-guide`. Чисто-аддитивный апгрейд провенанса, тело не меняется.
- **§4 от 07-26 — 6 comp-якорей Icy Veins 2v2 tier list** для `*-hunter-rdruid`, `*-warrior-hpala`, `*-warrior-rsham`, `*-retpala-rsham`, `*-rogue-rdruid`, `*-mage-priest` (RM/RP/RL). 2-й независимый comp-tier источник.

> NB: с 07-27 в `kb/drafts/` появились **12 RD-драфтов** (`rd-vs-*`, comp rogue+resto-druid, добавлены владельцем). Их провенанс сегодня не аудировал — если нужно, в следующем ране сверю их source-блоки и предложу такие же comp/author-якоря. Скажешь «да» по §3/§4 — внесу пофайлово с diff. Сам не применял.

## 4. Проверки и состояние репо

```
$ PYTHONPATH=backend python -m arena_coach validate-kb kb/drafts/
OK: 80 документов прошли валидацию            # exit 0

$ (unset *_proxy) PYTHONPATH=backend:ingest:bridge python -m pytest tests/
388 passed in ~9s                              # exit 0
```

- Драфтов не добавлял → счётчик `tests/test_kb_loader.py` (`assert ok == 80`) не трогал, совпадает с диском (80 файлов). Рост `68→80` — работа владельца 07-27 (12 RD-драфтов, main `7098ee3`). Docstring на L80 всё ещё говорит «68» (косметика) — ассерт корректный `== 80`.
- Рост тестов `336 → 388` — тоже работа владельца между 07-27 и 07-28 (RD-драфты + `test_meta_priors`, `test_stealth_announce`, `test_advice_spec_fallback` в наборе). Мой вклад в тесты — нулевой.
- **Артефакт песочницы (env-drift, НЕ код):** свежая песочница ставит по умолчанию `fastapi 0.140 / starlette 1.3 / httpx 0.28 / новый python-multipart`. На них: (а) collection падал (`starlette.testclient` требует `httpx2`; `multipart` шлёт PendingDeprecationWarning → error), (б) 1 тест `test_hint_queue::test_requires_auth` давал `401` вместо `403` (новый FastAPI сменил поведение `HTTPBearer(auto_error)` на missing-header). **Пин под версии проекта** (`fastapi==0.111.0`, `starlette==0.37.2`, `httpx==0.27.2`, `python-multipart==0.0.9`) → **388 passed, чисто**. Это ровно как прошлый socks/proxy-артефакт: на CI/машине владельца с зафиксированными версиями — зелено. Кода не касается. *(Рекомендация: если у проекта нет lock-файла зависимостей — стоит запинить fastapi/starlette/httpx в окружении, чтобы CI не поймал тот же drift.)*
- `ruff`/`mypy` этим раном не гонял (не менял код). Слэнг не рендерил (`tools/render_slang.py` не трогал — правок в `slang.json` нет).

## 5. Что ждёт владельца

1. **Approve — на паузе.** 12 ранее засорсенных гипотез лежат в `kb/drafts/`, ждут `python -m arena_ingest review approve --slug <slug>`. Новых к очереди не добавил.
2. **Решение по §3/§4** (перенесены с 07-26): применять ли добавление source+tag к 11 RP-драфтам (Deadlycoward) и 6 comp-якорям (Icy Veins). Плюс: аудировать ли source-блоки 12 новых RD-драфтов.
3. **Разблокировка 4 пар** (единственные честные пути, оба требуют участия владельца):
   - прогнать `yt-dlp --write-auto-subs --skip-download <url>` локально по RM-гайду `DLEZ7Yi4-jU` (+ ранее найденным `mHgkNzlnpPQ`, `dKgQ4pP7EL0`) и положить `.vtt`/текст в репо (напр. `kb/_ingest_inbox/`) → распарсю, сверю с гипотезой, оформлю sourced-draft (community-tier, помечу тегом);
   - либо дать конспект/тайм-коды платного rank1academy (RM-POV закрывает `rm-vs-*`, RP-POV — `rp-vs-*`).
4. **Политический вопрос (открыт с 06-30):** разрешить ли class-synthesis-промоут (склейка class-handling секций с явными тегами) — тогда часть hunter-гипотез можно оформить. Пока по guardrail'у — нет.
5. **Хозяйственное:** разгрести накопившиеся untracked `docs/scan-reports/SCAN-REPORT-*.md` (07-11…07-28) + `docs/proposals/` + унаследованные правки гипотез `sacred shield → BoP` — решить push/применить/выкинуть.
