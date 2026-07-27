# Arena Coach — Daily Source Scan Report
**Дата:** 2026-07-02
**Задача:** `arena-coach-daily-source-scan` (автоматическая, автономный ран)
**Статус:** ✅ Завершена

---

## Итог (TL;DR)

- **+2 sourced-драфта: `rm-vs-rogue-hpala`, `rp-vs-rogue-hpala`** (47 → 49). Разблокировал **официальный Wowhead hpala-arena-гайд** (patch 2.5.5, обновлён 2026-02-10): «Paladin / Warrior or **Rogue**» назван самым распространённым 2v2-сетапом hpala, с **посвящённой секцией** (Cleanse, Freedom, HoJ, Consecration против стелса, bubble/BoP+Forbearance) и оценкой компа («the worst healers to bring», hard-cast хилы, нет мобильности). Это ровно бар проекта («пара названа источником»), которого не хватало 06-29/06-30 — class-handling якоря Deadlycoward (mana-burn план, зафикс. 06-30) и Hesback (поведение hpala против rogue-команд) теперь легально пошли как обвязка. В rp-драфте kill_target сменён на **paladin** (по Deadlycoward «easy kill after he has no mana left»); гипотезы помечены `sourced-promoted`.
- **Фикс TBC-чистоты: «sacred shield» удалён из 4 существующих драфтов** (8 мест: rm/rp-vs-warlock-hpala, rm/rp-vs-warrior-hpala). Sacred Shield — WotLK 3.0, в 2.4.3 её нет; заменено на реальные BoP / Blessing of Sacrifice (последняя — source-corroborated: Hesback описывает Sac-аптайм hpala, диспелится нашим прийстом). Просочилось мимо validate-kb, т.к. не было `[[ability:]]`-ссылкой.
- **mirlol.pro прочитан впервые** (Chrome MCP, client-rendered): есть `/matchups/rogue-mage` и `/matchups/rogue-priest` — посвящённые матчап-страницы под ОБА наших состава, но контент **за Twitch-sub пейволлом**. Публичная главная: tier-list Мирлола — **RM, RP, RR = S+** (2v2, S1-2). Легитимный путь к разблокировке 5 RM-гипотез: владелец подписывается на Twitch и вносит через `arena_ingest paste` (type: stream-paste).
- **Новые tier-источники:** AOEAH 3v3 tier list (2026-01-28) и Koroboost TBC Arena Guide (2026-06-17) — не разблокируют оставшиеся гипотезы, но дают корроборацию для 6+ RMP-драфтов и **новые 3v3-кандидаты** (см. ниже).
- **Оставшиеся 6 гипотез — без изменений** (блокеры пере-подтверждены сегодня по полным текстам).
- **Зелёное:** `validate-kb kb/drafts/` = **49 OK** · `pytest` = **113 passed** · `ruff` clean · счётчик в `test_kb_loader.py` 47→49 · `coverage_matrix.py` → ✅ 47 🟡 6 ⬜ 202 (+spec ✅ 2) · `render_slang.py --all` → 49 файлов.
- **yt-dlp в песочнице не работает** (прокси 403 на YouTube API) — RM-POV видео (напр. «Anniversary TBC — Rogue/Mage 2v2 Arena Guide!», DLEZ7Yi4-jU) добывать только в интерактивной сессии.

---

## Прочитано сегодня (verifiable)

| Источник | Канал | Что дал |
|---|---|---|
| wowhead.com/…/holy-paladin-healer-pvp-arena-guide (upd. 2026-02-10, 2.5.5) | WebFetch | **Якорь пары rogue+hpala** (посвящённая 2v2-секция) + слабости hpala. Основа обоих промоутов |
| wowhead.com/…/15309 Hesback (Gladiator S2, Firemaw-EU) | WebFetch (полный текст) | 15 матчапов Warr/Pala POV с рейтингами: **«Mage Rogue 7/10»** (усиливает rm-vs-warrior-hpala: уже в sources), **«Rogue DPriest 4/10»** (rp-vs-warrior-hpala: уже в sources), hpala-техники vs rogue-команды (Stoneform, Sac-аптайм, BoP/тринкет-экономия) → обвязка новых драфтов |
| aoeah.com/news/4283 (2v2 tier list, полный текст) | WebFetch | Пере-подтверждено: mage+hpala, rogue+hpala, hunter+hpala, hunter+rsham, mage+rdruid **не тированы** → tier-anchor путь для остальных гипотез закрыт |
| **aoeah.com/news/4352 (3v3 tier list, 2026-01-28) — НОВЫЙ** | WebFetch | S: RMP/RLD/RLP · A: WLD, Shadowplay-mage-вариант, MLP, double-healer · B: **Thug Cleave («struggles into … RMP»)**, Warrior/Rogue/Druid, Turbo/Thunder Cleave, Ret/Rogue/Priest, Shadowplay-lock («all-in, no reset») |
| **koroboost.com/guide/tbc-arena-guide (2026-06-17) — НОВЫЙ** | WebFetch | «**WLD is the only comp that consistently beats RMP**», «RMP destroys double-healer comps (priest gets mana burned)»; 3v3-таблица: RMP 2400+, WLD 2300+, **RLS 2200+**, Drain Team (Lock/SP/Druid) 2150+; 2v2-таблица: RM «Very High» difficulty, RP «High» |
| ownedcore.com/…/161338 Gog123456 (2008, полный текст) | WebFetch | Тред, из которого ранее взят только rmp-mirror. Полный текст даёт RP-секции: vs Warrior/healer (smite-план с 40%, fear→blind→MC), vs Mage/Rogue, vs Rogue/Rogue, vs Warlock/healer; PMR: vs WLD (rogue→lock, mage→warr lockdown), vs Druid/Warr/Rogue |
| mirlol.pro (Chrome MCP) | Chrome | Матчапы за пейволлом; публичный tier-list: RM/RP/RR = S+ |

---

## Статус оставшихся 6 гипотез

| Slug | Блокер (пере-подтверждён сегодня) |
|---|---|
| rm-vs-hunter-hpala | Не тирован (AOEAH полный текст); RM-POV нет. Кандидат №1 на mirlol-paywall путь |
| rm-vs-hunter-rsham | То же (AOEAH: hunter+rdruid S, MM-hunter+disc A — rsham-вариант отсутствует) |
| rm-vs-mage-hpala | Wowhead hpala-гайд называет Pala+Mage только как **3v3**-вариант — 2v2-пары нет |
| rm-vs-mage-rdruid | RM-POV нет (Deadlycoward — DP/R POV, не инвертируется) |
| rm-vs-rogue-hpala | ✅ **промоутнут сегодня** |
| rp-vs-hunter-rsham | Пара по-прежнему не названа ни одним источником |
| rp-vs-mage-hpala | Как rm-версия: пара в 2v2 не названа. Policy-вопрос 06-30 остаётся открытым |
| rp-vs-rogue-hpala | ✅ **промоутнут сегодня** |

---

## Enrichment-предложения (НЕ применял — жду отмашки)

1. **AOEAH 3v3 (4352)** добавить в `sources:` шести RMP-драфтов: rmp-vs-RLP/RLD (S-tier + «dampening»-нюанс), rmp-vs-WLD (A, «strongest non-Rogue comp»), rmp-vs-Shadowplay (B lock-вариант: «extremely aggressive, no real reset» → наш план пережить первый го), rmp-vs-MPSham (double-healer «top-tier comps can break them»), rmp-vs-mirror (S, «unmatched control»).
2. **Koroboost** → rmp-vs-WLD (difficulty-якорь «only comp that consistently beats RMP» — согласуется с very-hard) и rmp-vs-MPSham («priest gets mana burned» — win-con).
3. **Gog123456 (161338)** → добавить вторым источником в rp-vs-rogue-mage («defensive, burn fears asap, LOS sheeps»), rp-vs-rogue-rogue («separate them»), rp-vs-warlock-priest/rdruid/rsham («rogue on warlock, mana burn healer — pretty easy» + наш already-cited Deadlycoward), rmp-vs-warrior-warlock-druid (WLD-lockdown разводка rogue→lock / mage→warr).
4. **Hesback «Mage Rogue 7/10»** уже в sources rm-vs-warrior-hpala — проверить, вплетён ли условный нюанс: их оценка **2/10 если RM идёт в паладина (dwarf) vs 8-9/10 если в воина** → сильный аргумент за kill_target=warrior. Аналогично «Rogue DPriest 4/10» для rp-vs-warrior-hpala («выигрываем ману → дави рано»).
5. **Прежний батч Deadlycoward по 14 RP-драфтам** (SCAN-REPORT 06-30) — всё ещё не применён.

## Новые 3v3-кандидаты для compositions.json (решение владельца)

С tier-якорями, готовы под sourced-драфты по прецеденту RLP/RLD (tier-anchor + synthesized-execution): **Thug Cleave** hunter+rogue+healer (AOEAH B + прямой матчап-якорь «struggles into RMP»), **Warrior/Rogue/Druid** (AOEAH B), **Turbo/Thunder Cleave** (AOEAH B), **Ret/Rogue/Priest** (AOEAH B), **RLS** rogue+warlock+resto-shaman (Koroboost 2200+), **Drain Team** warlock+shadow-priest+druid (Koroboost), **Shadowplay-mage-вариант** shadow-priest+mage+resto-shaman (AOEAH A, «best Resto Shaman comp») — NB: отличен от нашего shadowplay (lock-вариант) третьим слотом.

---

## Техническое

| Проверка | Результат |
|---|---|
| `python -m arena_coach validate-kb kb/drafts/` | ✅ 49 OK |
| `python -m pytest tests/` | ✅ 113 passed |
| `ruff check backend bridge ingest tests` | ✅ All checks passed |
| Счётчик драфтов (`tests/test_kb_loader.py`) | 47 → **49** |
| `tools/coverage_matrix.py` | ✅ 47 · 🟡 6 · ⬜ 202 (255) + spec ✅ 2 → `docs/COVERAGE.md` перегенерирован |
| `tools/render_slang.py --all` | ✅ 49 файлов; slang-gap прежний (ambush, deadly-throw, expose-armor, pain-suppression, rupture, will-of-the-forsaken) |
| Файлы тронуты | +2 драфта, 2 гипотезы (sourced-promoted), 4 драфта (sacred-shield фикс), test_kb_loader.py, COVERAGE.md, этот отчёт |

⚠ **Замечание по git:** в рабочей копии накопились незакоммиченные изменения нескольких сессий (CLAUDE.md, addon/*, compositions.json, все SCAN-REPORT'ы, COVERAGE.md, handoff). Автономные раны не коммитят — нужен ручной `git add/commit/push` владельцем, иначе VPS-деплой (`git pull`) этого не увидит.

## Следующие шаги для владельца

1. **Approve backlog +2:** `python -m arena_ingest review approve --slug rm-vs-rogue-hpala` / `--slug rp-vs-rogue-hpala` (оба `synthesized-execution` — желательно ревью топ-игрока).
2. **Mirlol paywall:** Twitch-sub → `/matchups/rogue-mage`, `/matchups/rogue-priest` → `arena_ingest paste`. Разблокирует до 5 RM-гипотез разом.
3. Отмашка на enrichment-батчи (пп. 1-5 выше) и решение по новым 3v3-кандидатам.
4. Закоммитить накопленное (см. замечание по git).
