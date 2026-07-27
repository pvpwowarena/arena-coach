# Arena Coach — ежедневный скан источников, отчёт 2026-07-17

> Авто-запуск `arena-coach-daily-source-scan`. Владелец отсутствовал — действовал автономно, ничего не аппрувил и не мёржил. Все правки ниже — **предложения**, не применены.

## TL;DR

- **Нетто: 0 новых драфтов, 0 гипотез засорсено.** Блок из 4 непроверенных гипотез не сдвинулся — по тем же причинам, что и в прошлые сканы (не мета-пары → нет per-matchup источника; единственный RM-POV per-pair источник, Mirlol, за пейволлом).
- **Репо зелёное:** `validate-kb kb/drafts/` → **51 OK**; `pytest tests/` → **146 passed**. KB-контент не менялся, счётчик в `tests/test_kb_loader.py` (=51) верен.
- **Снят ложный housekeeping-флаг** прошлых сканов (см. §4).
- **Есть 1 конкретное enrichment-предложение** для 2 существующих драфтов (§3).

## 1. Что просканировано и с каким результатом

| Источник | Доступ этот ран | Итог |
|---|---|---|
| **mirlol.pro/matchups** (RM+RP per-pair) | Chrome MCP открыл | ⛔ «exclusively for Mirlol's Twitch subscribers» — пейволл. Единственный путь: подписка владельца → `arena_ingest paste`. |
| **WT «Mage/Rogue 2v2 Strategies»** (`rogue-mage-rogue-arena-strategies`) | Chrome MCP, `get_page_text` ok | Только обзор: strengths/weaknesses, **RM Counter Comps** (Rogue/Druid, Lock/Druid, Lock/Hpala, Human Rogue, Dwarf Disc+Mage/Lock), талант-билд (Shadowstep 20/0/41). **Per-pair секций нет.** |
| **silentshadows.net** (RM-mirror) | WebFetch (server-rendered) | Отдаёт **WT nav-shell** (75k, только меню) — как per-pair источник не годится (подтверждает находку 07-03). |
| **Локальные транскрипты** Mirlol (`WOW TBC ARENA - Rogue Mage.md` / `Rogue Priest.md`) | Read/grep | 12 RM + 10 RP матчапов; **ни одной из 4 целевых пар** (нет секций mage+druid, hunter+hpala, hunter+shaman). |
| **YouTube** (RM-POV видео, напр. `DLEZ7Yi4-jU`) | yt-dlp в песочнице | ⛔ прокси-403 на YouTube API — видео-транскрипты недоступны в авто-ране (только в интерактивной сессии). |
| WebSearch-сводки | — | Как указатели полезны; per-pair тактик не дают, путают соседние матчапы. |

## 2. Статус 4 активных гипотез (непомеченных)

| Гипотеза | Пара | Почему не засорсено |
|---|---|---|
| `rm-vs-hunter-hpala` | Hunter / Holy Paladin × RM | Не в RM Counter-list WT; не мета-пара 2v2; RM-POV per-pair источника нет. RP-аналог (`rp-vs-hunter-hpala`) засорсен через DPR-гайд, но у RM такого текста нет. |
| `rm-vs-hunter-rsham` | Hunter / Resto Shaman × RM | Не мета 2v2; нет ни в WT, ни в SC comps-страницах (страницы `restoration-shaman/comps` не существует). |
| `rm-vs-mage-rdruid` | Mage / Resto Druid × RM | RP-аналог засорсен (DPR-гайд «vs Druid/Frost Mage»), но это DPR-POV; RM-POV источника нет. FMage+RDruid отсутствует в 2v2-списке SC. |
| `rp-vs-hunter-rsham` | Hunter / Resto Shaman × RP | Не мета; в DPR-гайде названы hunter/druid, hunter/priest, hunter/hpala — **но не hunter/rshaman**. Промоут по генерик-паттерну = за баром (решение владельца, handoff §9). |

**Вывод:** это структурно long-tail пары. Реальный источник появится только если владелец (а) подпишется на Mirlol Twitch и запастит per-pair, либо (б) даст RM/RP-POV видео/форум-тред по конкретной паре. До этого — корректно остаются гипотезами.

## 3. Enrichment существующих драфтов — предложение (не применено)

`rm-vs-rogue-rdruid` и `rm-vs-warlock-rdruid` сейчас засорсены **только** локальным транскриптом Mirlol (`type: file`). WT RM-обзор **явно называет** обе эти пары в списке RM Counter Comps («Rogue/Druid», «Lock/Druid») и фиксирует RM «suffers vs locks, RD comps», «cannot be considered Tier 1» — прямая корроборация их `difficulty: hard`. Прецедент — `rm-vs-warlock-hpala`, где этот же URL уже добавлен вторым источником.

Готовый к вставке блок в `sources:` обоих файлов:

```yaml
- type: web
  url: "https://www.warcrafttavern.com/tbc/guides/rogue-mage-rogue-arena-strategies/"
  title: "Mage/Rogue — TBC 2v2 Arena Strategies (Warcraft Tavern) — «Rogue/Druid» и «Lock/Druid» прямо в списке RM Counter Comps; RM «suffers vs locks, RD comps», не Tier-1 — корроборация difficulty: hard"
  retrieved: '2026-07-17'
```

Ценность: усиливает трейсабельность difficulty для двух ключевых druid-матчапов без изменения тактики. Тактику (опенеры) WT-обзор не даёт → секции тела не трогаем.

## 4. Housekeeping — прошлый флаг СНЯТ

Сканы 07-03/07-05 отметили «10-12 засорсенных дублей в `kb/hypotheses/`, ждут удаления». **Это была ложная тревога.** Проверка: 12 «дублей» намеренно помечены `status: sourced-promoted` + `promoted_to: kb/drafts/<slug>.md` — это audit-trail, а не грязь. `validate-kb` их корректно реджектит (extra_forbidden на этих полях), `COVERAGE.md` считает 🟡 только 4 непомеченных. Удалять не нужно; формат маркировки засорсенной гипотезы = эти два поля.

Помечены (12): rm-vs-{mage,rogue,warlock}-hpala, rm-vs-warrior-{mage,rogue}, rp-vs-hunter-hpala, rp-vs-{mage,rogue,warlock}-hpala*, rp-vs-mage-rdruid, rp-vs-warrior-{mage,rogue}. *(rp-vs-warlock-hpala/rp-vs-rogue-hpala/rp-vs-mage-hpala)*

## 5. Ждёт владельца

- **Ничего срочного.** 4 гипотезы ждут либо Mirlol-подписки + паста, либо RM/RP-POV видео/форума по паре.
- (Опц.) Применить enrichment §3 — 2 однострочных правки source-блока.
- Approve-бэклог по драфтам не менялся этим сканом.

_Проверка: `pip install -e "backend[dev]" -e ingest -e bridge --break-system-packages` (в песочнице; на VPS/локально уже стоят) → `python -m arena_coach validate-kb kb/drafts/` = 51 OK → `python -m pytest tests/` = 146 passed._
