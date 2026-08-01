# Proposal: паттерны из видео-транскриптов → триггеры рекомендаций в аддоне

Дата: 2026-08-01. Автор: Arena Coach Dev (тактический разбор транскриптов `video-transcripts/`).
Статус: предложение, ничего из этого не реализовано и не аппрувлено.

## Контекст и ограничение

Все realtime-паттерны обязаны исполняться в аддоне (Core/Tracker/Overlay/Voice/Openers.lua):
combat-лог флашится клиентом блоками ~48КБ → канал через мост опаздывает на 13-28с структурно
(память проекта: log-buffer-48kb, phase-4.19). Мост и бэкенд в этом документе не получают ни
одного нового тактического правила — им остаются постматч и DM вне боя.

Источники паттернов: `DLEZ7Yi4-jU` (Arena Stories, 18 глав по матчапам RM — основной фактический
источник), `axI9kxAn1gM` (Aphane, фундаментальные принципы + тир-лист матчапов), шортсы Aphane
(стиль/подтверждения), VOD с войс-чатом (стиль). KB-драфты обновлены отдельно (18 файлов
`kb/drafts/rm-vs-*.md`, см. список в конце).

## Сводная таблица паттернов

Колонки: готов к генератору = KB-драфт достаточно, существующие `gen_addon_openers.py` /
`gen_addon_killtargets.py` подхватят без правок Lua; новый триггер = нужно событие/логика в аддоне;
новое состояние = чего не хватает в Tracker.lua/Overlay.lua.

| # | Паттерн | Матчап | Источник (video ID + таймкод) | Готов к генератору | Нужен новый Lua-триггер | Новое состояние в Tracker/Overlay |
|---|---|---|---|---|---|---|
| 1 | Колаут на воротах для 4 новых матчапов (hunter+priest, retpala+rogue, warrior+priest, rogue+feral) | новые | DLEZ7Yi4-jU 19:47 / 30:32 / 42:34 / 22:21 | **да** — драфты написаны, перегенерить Openers.lua + KillTargets.lua + ogg | нет | нет |
| 2 | Обновлённые опенер-цепочки (rupture вместо раннего kidney в mirror; premed→cheap→hemo→gouge в war/druid и т.п.) | mirror, war/rdruid, war/rsham и др. | DLEZ7Yi4-jU 0:45, 6:48, 25:09 | **да** — цепочки `[[a]] → [[b]]` в обновлённых драфтах; вычитать `--dry-run --md` | нет | нет |
| 3 | «Дворф-прист — не открывайся на нём» (stoneform снимает bleeds/wound/silence) | rogue/priest, lock/priest, mage/priest | DLEZ7Yi4-jU 13:08, 17:51–19:36, 41:40 | нет (правило расовое, в KB-ключе расы нет) | да: на воротах `UnitRace("arenaN")=="Dwarf" && class=="PRIEST"` → клип «Прист дворф — не бей его» + пометка на панели | поле `race` в `Overlay.units` (Tracker уже читает UnitRace — скопировать в ScanRoster) |
| 4 | Пост-тринкет план: «друид тринкетнул кидни → блайнд+ваниш, победа закреплена»; «пала тринкетнул чип → полный кидни→эвис» | war/rdruid, pala/war, lock/rdruid, hunter/rdruid и др. | DLEZ7Yi4-jU 7:03, 28:08, 37:36, 23:29 | нет (нужен НОВЫЙ генератор `gen_addon_posttrinket.py` из секций «If enemy trinkets») | триггер существует (`Overlay:NoteTrinket`) — добавить lookup «ключ матчапа + класс тринкетнувшего → клип» | нет (`trinketUsed` уже есть) |
| 5 | «Оба тринкета врага потрачены → чистый сетап / дожимайте» | универсально (явно: war/rsham, pala/war, RR) | DLEZ7Yi4-jU 27:15, 28:29, 47:41 | нет | мини-триггер в `NoteTrinket`: `all(u.trinketUsed)` → клип «Тринкетов нет — сетап!» (edge, раз за матч) | нет |
| 6 | Формы: «ghost wolf не сапается», «не блайндить друида в bear form», «tree form → пробный gouge (бейт тринкета)» | war/rsham, war/rdruid, lock/rdruid, rogue/feral | DLEZ7Yi4-jU 25:02, 7:51–8:13, 9:38, 37:04 | нет | да: CLEU `SPELL_AURA_APPLIED/REMOVED` форм (Bear 9634, Dire Bear, Tree, Ghost Wolf — id сверить по abilities.json) → edge-советы «Друид в мишке — не блайндь» / «Вышел из формы — сап/блайнд окно» | да: `enemyForm[guid] = bear/tree/wolf/humanoid` |
| 7 | Intervene-правило: «след. абилка по хилу перекинется в вара — не сапь/не чипай» (+wand-трюк мага) | war/rdruid, war/priest | DLEZ7Yi4-jU 10:18–11:00, 42:42 | нет | да: CLEU `SPELL_CAST_SUCCESS` "Intervene" от вражеского вара → клип «Интервин — не сапь!» (по имени спелла, как HEAL_CASTS) | опционально: таймер «цель под интервином» для панели |
| 8 | Felhunter: «кликни с себя магические бафы — Devour Magic выбьет из стелса» | lock/rdruid, lock/priest, lock/rogue | DLEZ7Yi4-jU 39:07–40:14 | нет | да: (а) на воротах при классе WARLOCK у врага → клип-напоминание; (б) CLEU "Summon Felhunter" → повтор | нет |
| 9 | Тринкет-дисциплина по станам: «не тринкеть первый полный стан без давления», «тринкеть чардж-стан (следом дизарм), не фир» | rogue/rdruid, war/rsham, lock/priest (фир без давления — не тринкетить) | DLEZ7Yi4-jU 23:52, 25:26, 41:16 | нет | да: `SPELL_AURA_APPLIED` стана/фира с dest=player → клип по таблице «матчап+абилка → сиди/тринкети» (таблицу компилировать из KB новым генератором, как #4) | нет (источник события уже в CLEU-обработчике) |
| 10 | Sap-окно: опенер на счёт «сап спадает через 3-2-1» | универсально (стиль-эталон: Lik9TjeN3w 0:29–0:36) | Lik9TjeN3w 0:29 (стиль), DLEZ7Yi4-jU 20:26 (сап спадает → кидни готов) | нет | возможен: наш Sap `SPELL_AURA_APPLIED` на враге → таймер; НО длительность зависит от DR/талантов — без DR-реестра давать отсчёт нельзя (ложный отсчёт хуже молчания) | да: DR-реестр (см. #11) |
| 11 | DR-цепочки: не терять станы/incap (чип и кидни делят DR; порядок сетапов «стан → овца → блайнд») | универсально | terms.md (sourced-глоссарий DR); DLEZ7Yi4-jU 8:13, 28:29 («ждём DR» повсеместно) | нет | да, крупный: DRTracker по CLEU aura applied/removed, категории из `abilities.json dr_category`, окно 15с → совет «DR отошёл — реопен» | да: `drState[guid][category] = {level, resetAt}` |
| 12 | Смена килл-таргета по HP: «вар аномально низкий → своп на вара» | pala/war (явно), универсальный принцип | DLEZ7Yi4-jU 29:38 | частично | уже близко: `PickUnit` выбирает по HP внутри КЛАССА цели; нужен порог кросс-класс свопа (враг не-цель < X% HP → «Своп на N!») — аккуратно с анти-спамом (урок 4.20.1) | нет (HP уже опрашивается в OnUpdate 2/с) |
| 13 | Разовые напоминания прочих рас: gnome warrior (escape artist снимает нову — блайнд ок, нова нет), undead (WotF vs гарота — «гарота после расовика») | war/rdruid, war/priest, mirror | DLEZ7Yi4-jU 12:29–12:45, 43:34 | нет | да: та же механика, что #3 — `UnitRace` на воротах → модификатор колаута/панели | `race` в `Overlay.units` (общее с #3) |

## Что уже покрыто существующим аддоном (ничего делать не надо)

- «Тринкет!», «Ваниш!», «Иммун!», «Кик хил!», «Сбей каст!» — Voice.lua 4.19.
- Килл-таргет + череп + «БЕЗ ТРИНКЕТА» + дубли классов по HP/тринкету — Overlay.lua 4.18/4.20.1.
- Тактический колаут на воротах — Openers.lua 4.20; новые драфты просто расширяют покрытие (#1).

## Приоритет внедрения (моя рекомендация, решение за владельцем)

1. **#1/#2 — бесплатно**: перегенерить `gen_addon_openers.py && gen_addon_killtargets.py && gen_addon_voice.py --only openers` после ревью драфтов. Внимание: (а) `rogue+feral-druid` схлопнется в тот же ключ `2v2|mage+rogue|druid+rogue`, что и resto-вариант → колаут станет `sure=false` (штатное поведение, как у спеков); (б) `_DANGERS` сканирует весь документ — новые секции могут добавить/сменить фразу угрозы, обязателен `--dry-run --md` на вычитку.
2. **#5 — 5 строк** в `NoteTrinket` + 1 клип.
3. **#3/#13 — расовый слой**: `race` уже отдаётся `UnitRace` на воротах, детерминизм 100%, сеть не нужна.
4. **#4/#9 — пост-тринкет/стан-дисциплина**: новый компилятор из «If enemy trinkets»/«Common mistakes» по образцу `gen_addon_openers.py` (факты из KB, слова из вычитанных таблиц).
5. **#6/#7/#8 — событийные edge-триггеры** по именам спеллов (по образцу HEAL_CASTS; помнить об ограничении «английский клиент»).
6. **#11 (+#10, #12) — DR-реестр**: самый дорогой, делать последним и только после живой валидации остального.

## Псевдокод ключевых триггеров

```lua
-- #3/#13: расовый слой (Overlay:ScanRoster дополняется race)
table.insert(self.units, { unit=unit, class=..., race=select(2, UnitRace(unit)), ... })
-- в Recompute, после выбора цели:
if pick.class=="PRIEST" and pick.race=="Dwarf" then Voice:Say("warn_dwarf_priest") end

-- #5: все тринкеты потрачены (Overlay:NoteTrinket, после changed)
local all = true
for _, u in ipairs(self.units) do
    if IsAlive(u.unit) and not u.trinketUsed then all = false end
end
if all and not self.allTrinketsAnnounced then
    self.allTrinketsAnnounced = true            -- сброс в StartMatch
    Voice:Say("no_trinkets_go")
end

-- #7: intervene (Voice:OnCombatLog, ветка SPELL_CAST_SUCCESS)
local WARN_CASTS = { ["Intervene"] = "warn_intervene" }  -- + "Summon Felhunter" (#8)
if WARN_CASTS[spellName] then self:Say(WARN_CASTS[spellName]) end

-- #6: формы (новая таблица + состояние)
local FORM_AURAS = { ["Dire Bear Form"]="bear", ["Bear Form"]="bear",
                     ["Tree of Life"]="tree", ["Ghost Wolf"]="wolf" }
-- SPELL_AURA_APPLIED src=enemy: enemyForm[srcGUID]=FORM_AURAS[spellName]
-- SPELL_AURA_REMOVED: enemyForm[srcGUID]="humanoid" → если класс DRUID и он килл-таргет:
--   Voice:Say("druid_out_of_form")   -- «Вышел — сап/блайнд окно»
```

## Паттерны, НЕ пригодные для realtime (постматч / KB-текст / LLM вне боя)

1. **Позиционка**: споты (верёвка моста Blade's Edge vs RR — DLEZ7Yi4-jU 48:25, D583YaGwLU4 0:44), «пала ушёл за угол — окно» (29:21), макс-дистанция сапа (2:14), LoS-игра. API 2.4.3 не даёт координат в арене — детерминировать нечем. → постматч-разбор/KB.
2. **Стелс-паттерны и чтение оппонента**: «миксуй стелс-паттерн», пре-vanish решения, предсказание опенера RR (DLEZ7Yi4-jU 47:05+, Mirlol rogue-rogue). Требует распознавания намерения — не событие.
3. **Оценка «кто выигрывает mage 1v1» в mirror** (Mirlol/DLEZ7Yi4-jU 0:06) — скилл-оценка, не событие.
4. **Координация партнёра**: «дай рогу сапнуть до спелл-стила барьера» (3:20), «маг wand'ит интервин» (10:51 — совет МАГУ, а аддон у рога), «прист-партнёр диспелит X». Аддон видит события, но исполнитель — другой игрок; максимум — текст в постматч.
5. **Пре-матч чеклист**: яды по матчапу (wound/crippling/mind-numbing — конфликт Mirlol vs Arena Stories зафиксирован в rm-vs-rogue-mage), свап кинжала на воротах, бафф-фуд/gem'ы (axI9kxAn1gM 4:15). До ворот состав врага неизвестен (prep-фаза пуста) → колаут не успевает повлиять на выбор ядов. → KB/DM-чеклист вне боя.
6. **Выбор килл-таргета при конфликте источников** (pala/war: warrior vs paladin; sham/ret: paladin vs shaman; druid/hunt: hunter vs druid) — решение владельца KB, не автоматики.
7. **Difficulty-тиринг Aphane vs Mirlol** (rogue/priest easy↔hard и др.) — метаданные KB, в бою не участвуют.

## Дыры покрытия (зафиксировать)

- **Видео-партия не дала контента под наш RR (rogue+rogue)**: единственное профильное видео `cQMl2TAuTAo` (Double Rogue 2v2, 90% winrate) БЕЗ субтитров — транскрипта не существует. NB: RR-драфты `rr-vs-*` уже заведены отдельной сессией (Phase 4.21, ждут ревью владельца) — но видео-источником их не подкрепить, нужен другой.
- 2 видео — фоновая музыка вместо речи (`kSkihAas1yM`, `lNEbcLebmpQ`), контента нет.
- Full-game VOD (`OcWMmy3lChU` RMP 19-0, `IEW101yDeYA` RLD, `c7D8VDwJPtw` 5v5) — войс-чат без называния составов врага: пригодны как эталон стиля реплик и подтверждения (цитируются точечно), в KB-факты не превращены. `Kh5Ny4fdBpQ` — эталон стиля (автосубтитры ломают термины: rogue→rock, sap→stop/sub, kidney→kitty).

## Изменённые/новые KB-файлы этой сессии

Новые: `rm-vs-hunter-priest.md`, `rm-vs-retpala-rogue.md`, `rm-vs-warrior-priest.md`, `rm-vs-rogue-feral.md`.
Обновлены (добавлены youtube-источники с таймкодами, секции Alternative opener / If enemy trinkets / Common mistakes, зафиксированы конфликты источников): `rm-vs-rogue-mage`, `rm-vs-warrior-rdruid`, `rm-vs-rogue-priest`, `rm-vs-rogue-rdruid`, `rm-vs-warrior-rsham`, `rm-vs-warrior-hpala` (⚠️ конфликт килл-таргета), `rm-vs-retpala-rsham` (⚠️ конфликт килл-таргета), `rm-vs-rogue-spriest`, `rm-vs-hunter-rdruid` (⚠️ расхождение планов), `rm-vs-warlock-rdruid` (⚠️ конфликт сложности), `rm-vs-warlock-priest`, `rm-vs-mage-priest`, `rm-vs-warlock-rogue`, `rm-vs-rogue-rogue`.

Ничего не аппрувлено в `kb/matchups/` — всё в `kb/drafts/`, решение за владельцем.
