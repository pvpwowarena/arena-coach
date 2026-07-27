# Source-scan report — 2026-07-03 (авто-задача)

**Итог:** нетто **0 новых sourced-драфтов**. drafts = **49** (без изменений), validate-kb 49 OK, pytest **113 passed**, счётчик в `test_kb_loader.py` = 49 (трогать не нужно). Браузер (Chrome MCP) **подключён** этот ран (Browser 1, macOS).

---

## 1. Скан источников для наших составов (RM / RP / RMP)

Проверенные каналы этот ран:
- **WebSearch** по парам hunter+rsham, mage+rdruid (RM/RP-POV) → вернул те же известные страницы: Skill Capped 2v2 tier-list (только буквы), Icy Veins 2v2 rankings (comp-level проза), WT RM-strategies overview, koroboost, aoeah. Ни одной новой **посвящённой per-pair** секции. Сводки снова смешивают generic-RM-инфо (opener/blind/sap) с конкретной парой — не цитируемо (тот же conflation-паттерн, что фиксировали 06-29/06-30/07-01).
- **silentshadows.net/arena-strategies/mage-rogue-burning-crusade/** — раньше был server-rendered fallback; **сейчас отдаёт WT nav-shell** (939 строк меню, тело только через JS). Как per-pair источник больше не годится через WebFetch.
- **mirlol.pro** per-pair страницы (`/matchups/rogue-mage`, `/matchups/rogue-priest`) — по-прежнему за **Twitch-sub пейволлом** (подтверждено 07-02). Легитимный путь остаётся: владелец подписывается → `arena_ingest paste` (stream-paste).

**Вывод неизменен:** новых внешних per-pair источников для наших матчапов в открытом доступе не появилось.

## 2. Гипотезы (`kb/hypotheses/`) — попытка засорсить

6 **реально несорсенных** гипотез (остальные — см. §3):

| slug | статус поиска | почему нет драфта |
|---|---|---|
| rm-vs-hunter-hpala | нет источника | пара не тируется (Icy Veins/SkillCapped), нет в RM counter-list, нет per-pair гайда |
| rm-vs-hunter-rsham | нет источника | off-meta 2v2, RM-POV якоря по паре нет |
| rm-vs-mage-hpala | нет источника | off-meta, только class-handling соседних секций (conflation-риск) |
| rm-vs-mage-rdruid | нет источника | RP-аналог засорсён (Deadlycoward Druid/FrostMage), но **RM-POV** по этой паре нет |
| rp-vs-hunter-rsham | нет источника | off-meta 2v2, per-pair RP-POV нет |
| rp-vs-mage-hpala | нет источника | якоря Deadlycoward = class-handling, не оценка пары → ждёт policy-решения владельца (см. ниже) |

Все 6 остаются гипотезами. Ни одна не переписана в draft — бар «источник оценивает саму пару» не выполнен.

## 3. ⚠ Housekeeping-находка: 10 stale hypothesis-дубликатов

10 файлов в `kb/hypotheses/` уже **засорсены и лежат как драфты**, но их гипотеза-версии не удалены (по workflow README гипотеза при засорсивании *переписывается* в draft, т.е. должна исчезнуть из `hypotheses/`):

```
rm-vs-rogue-hpala      rp-vs-hunter-hpala
rm-vs-warlock-hpala    rp-vs-mage-rdruid
rm-vs-warrior-mage     rp-vs-rogue-hpala
rm-vs-warrior-rogue    rp-vs-warlock-hpala
                       rp-vs-warrior-mage
                       rp-vs-warrior-rogue
```

Функционально безвредны (гипотезы не индексируются, не валидируются), но вводят в заблуждение при подсчёте «сколько ещё ждёт источника». **Предлагаю владельцу:** удалить эти 10 файлов из `kb/hypotheses/`. Сам не удаляю — не входит в мандат авто-задачи (это не approve/merge, но и не «пометить засорсенным»). После чистки в `hypotheses/` останется ровно 6 файлов из §2 + README.

## 4. Enrichment-предложения для существующих драфтов

Новых источников этот ран не появилось → набор enrichment-якорей **не изменился** с 06-30/07-01. Актуальные, ещё не вплетённые предложения (ждут явного «вплети enrichment» от владельца):
- **~14 RP-драфтов** — посвящённые секции из гайда Deadlycoward (Infernal Gladiator, WT `rogue-disc-priest-2v2/`): Druid/Hunter 10/10, Druid/Rogue 9/10, Hpala/Warr, Rsham/Ret, R/R, FrostMage/Rogue, Druid/Warr, Druid/Lock, Rsham/Warr, DPriest/Mage, DPriest/Lock, SP/Rogue, mirror. Named-author, on-version — усилит approve-backlog. Таблица: `docs/SCAN-REPORT-2026-06-30.md`.
- **rm-vs-rogue-rdruid / rm-vs-warlock-rdruid** — corroborating comp-level source Icy Veins 2v2 (RM «suffers vs Rogue/Druid, Lock/Druid»).

## 5. Открытый policy-вопрос (переносится, 4-й ран подряд)

Где бар промоута гипотеза→draft: разрешить ли **class-handling synthesis** (источник разбирает обработку каждого класса пары по отдельности, но не саму пару). Затрагивает `rp-vs-mage-hpala` / `rm-vs-mage-hpala` / `rp-vs-rogue-hpala`-типа кейсы. Текущий применяемый бар: источник должен назвать пару в tier-листе ИЛИ иметь посвящённую секцию. Ждёт решения владельца.

## 6. Проверки перед завершением

```
python -m arena_coach validate-kb kb/drafts/   → OK: 49 документов
python -m pytest tests/                         → 113 passed
```
Ничего не аппрувлено, ничего не смёржено в `kb/matchups/`. KB не менялась.
