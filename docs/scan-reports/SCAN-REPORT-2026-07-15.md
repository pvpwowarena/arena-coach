# Source-scan report — 2026-07-15 (авто-задача)

**Итог: 0 новых sourced-драфтов, 0 засорсенных гипотез.** KB **не изменялась** (51 драфт / 16 гипотез, 4 незасорсенных), ничего не аппрувлено, в `kb/matchups/` ничего не мёржено.

**Главное за ран:** ещё один проход по 4 заблокированным парам + попытка достать queued-страницу WT `rogue-subtlety-openers` через WebFetch. Результат подтверждает картину 07-14: per-matchup источника по блок-парам нет, WT-тело по-прежнему client-rendered. **Chrome MCP в этом автономном ране не подключён**, поэтому client-rendered тела (WT/mirlol) недоступны — работал только WebSearch + WebFetch.

**Проверки:** KB не менялась (ни одной записи мной), поэтому валидатор/тесты в состоянии 07-14 — `validate-kb kb/drafts/` = **51 OK**, `pytest tests/` = **146 passed**. Прогонять заново незачем: в песочнице нет установленного `arena_coach`/venv, а вход не изменился. Счётчик драфтов в `test_kb_loader.py` не трогал, `render_slang` не требуется.

---

## 1. Что сканировал

| Источник / запрос | Метод | Результат |
|---|---|---|
| `rogue+mage vs hunter+rsham` | WebSearch | Только tier-list + общий Resto-Shaman-гайд (icy-veins/wowhead). Per-matchup — нет. Подтверждает: шаман слаб в 2v2, «no reliable dispel» — но это общий тезис, не пара |
| `rogue+mage vs mage+rdruid` | WebSearch | **Двенадцатый conflation:** сводка снова свела `mage+rdruid` → `rogue+rdruid` («Rogue/Druid is the best 2v2…»). Реального `mage+rdruid`-контента ноль |
| `rogue+mage vs hunter+hpala` | WebSearch | Только tier-list/обзор (skill-capped, icy-veins, pvpskills). Per-matchup — нет |
| WT `rogue-subtlety-openers` | WebFetch | **Тело client-rendered** — WebFetch отдал nav+meta-теги, не прозу статьи. Через `meta-description` утекает лид-абзац (Cheap Shot→Kidney = 10с стан-лок), но не разбор по мажам. Для полного тела нужен Chrome |

**Корректировка к промежуточной догадке этого рана:** сначала показалось, что WT стал WebFetch-доступным (77k символов). Проверка grep'ом: это nav-меню + `<meta>`, **не** тело статьи. **07-14 был прав — тело WT остаётся client-rendered.** Единственное, что реально утекает через WebFetch, — `meta-description` (лид-предложение).

## 2. Гипотезы: по-прежнему 4 незасорсенных, блок держится

| Slug | Статус |
|---|---|
| `rm-vs-hunter-rsham` | блок; пара отсутствует в комп-листах обеих сторон (подтверждено ~12 источниками к 07-14). Сегодня — ещё один WebSearch-проход, ноль per-matchup |
| `rp-vs-hunter-rsham` | то же |
| `rm-vs-mage-rdruid` | блок; двенадцатый conflation `mage+rdruid`→`rogue+rdruid`. Пары как меты не существует |
| `rm-vs-hunter-hpala` | блок на `## Opener` сохраняется. **Решение A/B за владельцем — открыто с 07-13** |

Сорсить эти 4 из общих гайдов бессмысленно — исчерпано. Разблокировать может только: (а) RM/RP-POV видео-транскрипт (yt-dlp = 403 из песочницы, нужна интерактивная сессия), (б) mirlol-подписка владельца + ручной паст, (в) экспертный approve владельца (тогда это не «источник», а его решение).

## 3. Enrichment: новый кандидат (НЕ применял, требует верификации тела)

WebSearch-сводка `rogue-subtlety-openers` даёт конкретику по опенеру против мага:
- **Sap с макс-дистанции** против мага с insignia-тринкетом (иначе он тринкетует сап и Nova-выбивает рога из стелса) → подождать пару секунд, посмотреть реакцию.
- **Premeditation** для быстрого набора 5 CP; альтернативные опенеры — **Garrote / Ambush**.

⚠ Это **сводка WebSearch, а не прочитанное тело**. По железному правилу «совет = проверяемый источник» из пересказа сорсить нельзя. → Кандидат в `## Opener` / `## Alternative opener` RM-драфтов, но **сначала Chrome-чтение тела WT** для точной цитаты. Пока помечаю `needs-verification`, в драфты не тащу.

Остальной enrichment-бэклог (07-13 §3, 07-14 §3: Spellsteal-дыра в RM, Bloodlust-диспел в RP, BW-окно хантера, Faerie Fire, Mass Dispel в пяти `rp-*-hpala`, Cyclone/Grounding/UA-правила) — **без изменений, ждёт отмашки владельца**; предусловие — патч глоссария (§3h, 07-14: ~17 отсутствующих слагов).

## 4. Очереди (без изменений с 07-14)

- **Требует Chrome (client-rendered тело):** WT `rogue-subtlety-openers`, `rogue-swap-in-arenas`, `rogue-introduction-to-arenas` (Five Pillars), `rogue-kiting`; mirlol (+ paywall).
- **Видео (yt-dlp = 403 из песочницы, нужна интерактивная сессия):** `PcfLBroowrM` (Earpugs, RP 2100 live comms) → `qJn9rLhDLZU` → `mHgkNzlnpPQ` → `DLEZ7Yi4-jU` → `yKp5DzXgu34`.
- **Silentshadows:** снять локальные копии `arena-strategies/*`, пока живы (редирект на WT уже начался).
- **AJ (Wayback):** остаток `Pri_Rog_2 / Dru_Htr` (низкий приоритет).

## 5. Housekeeping

- Stale hypothesis-дубликаты: **12** — ждут удаления владельцем (07-03 §3). 4 «живых» незасорсенных = блок-пары §2.
- Незакоммичено (untracked): отчёты 07-11…07-14 + этот. `.git/index.lock` в песочнице неудаляем (нет прав) — коммит только вручную владельцем: `git add docs/SCAN-REPORT-2026-07-*.md && git commit`.
- Счётчик тестов «113» в `CLAUDE.md` и в системных инструкциях проекта устарел — фактически **146**.

## 6. Следующие шаги (по убыванию ценности)

1. **Отмашка на enrichment-батч** (07-13/07-14 §3) + патч глоссария как предусловие. Реальные дыры (Spellsteal, Bloodlust-диспел, Mass Dispel, Faerie Fire), не косметика.
2. **Решение A/B по `rm-vs-hunter-hpala`** (висит с 07-13).
3. **Интерактивная/Chrome-сессия:** прочитать тело WT `rogue-subtlety-openers` + `rogue-swap-in-arenas` (прямой материал в `## Opener`) и снять yt-dlp-транскрипты — единственный реалистичный путь разблокировать 4 гипотезы.
4. Mirlol: подписка владельца → паст матчапов в ingest.
