-- ArenaCoach/Tracker.lua
-- Регистрирует события арены и пишет их в SavedVariables.
-- Отслеживает: тринкеты, основные CC/defensive CDs, старт/конец матча.

local AC = ArenaCoach

-- ── Spell ID таблицы ─────────────────────────────────────────────────────────

-- PvP-тринкеты (Every Man for Himself = 59752, стандартный = 42292 / 7744)
AC.TRINKET_IDS = {
    [42292] = "pvp_trinket",       -- Medallion of the Alliance/Horde
    [59752] = "every_man",         -- Every Man for Himself (human racial)
    [7744]  = "wotf",              -- Will of the Forsaken
}

-- Ключевые defensive и CC спеллы для трекинга
AC.TRACKED_SPELLS = {
    -- Rogue
    [1856]  = "vanish",
    [26669] = "evasion",
    [31224] = "cloak_of_shadows",
    [14185] = "preparation",
    [2094]  = "blind",
    [408]   = "kidney_shot",
    [1833]  = "cheap_shot",
    [6770]  = "sap",

    -- Mage
    [45438] = "ice_block",
    [2139]  = "counterspell",
    [118]   = "polymorph",
    [122]   = "frost_nova",

    -- Warrior
    [871]   = "shield_wall",
    [1161]  = "challenging_shout",
    [5246]  = "intimidating_shout",
    [20230] = "retaliation",

    -- Druid
    [33786] = "cyclone",
    [22812] = "barkskin",
    [29166] = "innervate",

    -- Priest
    [33206] = "pain_suppression",
    [8122]  = "psychic_scream",
    [10060] = "power_infusion",

    -- Warlock
    [5782]  = "fear",
    [6789]  = "death_coil",
    [47897] = "shadowfury",

    -- Paladin
    [853]   = "hammer_of_justice",
    [642]   = "divine_shield",
    [1044]  = "blessing_of_freedom",

    -- Hunter
    [19503] = "scatter_shot",
    [34477] = "misdirection",

    -- Shaman
    [16166] = "elemental_mastery",
    [2825]  = "bloodlust",
}

-- Arena unit-ы
local ARENA_UNITS = { "arena1", "arena2", "arena3" }
local PLAYER_UNITS = { "player", "party1", "party2" }

-- ── Вспомогательные функции ──────────────────────────────────────────────────

local function IsArenaUnit(unitGUID)
    for _, unit in ipairs(ARENA_UNITS) do
        if UnitExists(unit) and UnitGUID(unit) == unitGUID then
            return unit
        end
    end
    return nil
end

local function AppendEvent(session, eventType, source, target, abilityId, abilityName, payload)
    local ev = {
        ts           = AC.Now(),
        event        = eventType,
        source       = source,
        target       = target,
        ability_id   = abilityId,
        ability_name = abilityName,
        payload      = payload,
    }
    table.insert(session.events, ev)
end

-- ── Простой OnUpdate-таймер (замена C_Timer.After, которого нет в 2.4.3) ──────
-- Определён здесь (до bridge-секции), т.к. используется в RequestChatFlush.

local function ScheduleCall(delay, func)
    local elapsed = 0
    local t = CreateFrame("Frame")
    t:SetScript("OnUpdate", function(self, e)
        elapsed = elapsed + e
        if elapsed >= delay then
            self:SetScript("OnUpdate", nil)
            func()
        end
    end)
end

-- ── Bridge-канал: whisper-to-self → Logs/WoWChatLog.txt (или Chat-*.txt) ─────
-- WoW TBC не имеет прямого API для записи в файл, но SendChatMessage("WHISPER")
-- к самому игроку логируется в chat-лог (при включённом LoggingChat).
-- ВАЖНО: клиент буферизует запись — на диск строки попадают с задержкой.
-- Поэтому после критических событий дёргаем LoggingChat(false→true):
-- закрытие лога сбрасывает буфер (форс-флаш), bridge видит событие сразу.
-- Формат: [AC#TYPE#field1#field2#...]  (символы # и ] в именах игроков не встречаются)
-- Bridge (Python) читает файл каждые ~0.5с и фильтрует строки с [AC# (и легаси [AC|).
--
-- ⚠ Разделитель «#», а НЕ «|» (v0.2.1): современный Anniversary-клиент запрещает
-- сырой «|» в SendChatMessage — Lua-ошибка «invalid escape», события вообще не
-- отправлялись (первый живой тест 2026-07-23). В оригинальном 2.4.3 «|» проходил.

local bridgeEnabled = true   -- выключается через /ac coach pause

function AC.EmitToChat(eventType, ...)
    if not bridgeEnabled then return end
    local parts = { "[AC", eventType }
    for i = 1, select("#", ...) do
        local v = select(i, ...)
        table.insert(parts, tostring(v or ""))
    end
    local msg = table.concat(parts, "#") .. "]"
    -- Whisper к самому игроку: не виден другим, попадает в Chat-лог
    local playerName = UnitName("player")
    if playerName then
        SendChatMessage(msg, "WHISPER", nil, playerName)
    end
end

function AC.SetBridgeEnabled(val)
    bridgeEnabled = val
    AC.Print("Bridge: " .. (val and "активен" or "пауза"))
end

-- ── Форс-флаш чат-лога ───────────────────────────────────────────────────────
-- LoggingChat(false) закрывает файл лога → клиент сбрасывает буфер на диск.
-- LoggingChat(true) сразу включает запись обратно. Дебаунс 1с коалесцирует
-- пачки событий (опенер = несколько кастов подряд → один флаш).
-- Побочный эффект: системные сообщения о вкл/выкл логирования в чате.
-- Отключается через /ac flush off, если на живом тесте окажется лишним.

local flushEnabled = true
local flushPending = false

function AC.SetFlushEnabled(val)
    flushEnabled = val
    AC.Print("Форс-флаш чат-лога: " .. (val and "ВКЛ" or "ВЫКЛ"))
end

function AC.IsFlushEnabled()
    return flushEnabled
end

function AC.RequestChatFlush()
    if not flushEnabled or flushPending then return end
    if not LoggingChat then return end
    flushPending = true
    ScheduleCall(1.0, function()
        flushPending = false
        if not flushEnabled or not LoggingChat then return end
        LoggingChat(false)
        LoggingChat(true)
    end)
end

-- Принудительно включить запись чата в файл. Без этого whisper-to-self
-- НЕ попадает в Logs/Chat-*.txt и bridge не видит ни одного события.
-- LoggingChat идемпотентна — повторный вызов безопасен.
function AC.EnsureChatLogging()
    if LoggingChat then
        LoggingChat(true)
        return true
    end
    return false
end

-- Phase 4.2: главный realtime-канал bridge — COMBAT-лог (chat-лог клиент
-- не флашит до выхода из игры). Включаем запись боя при логине, чтобы
-- игроку не приходилось помнить про /combatlog. LoggingCombat идемпотентна.
function AC.EnsureCombatLogging()
    if LoggingCombat then
        LoggingCombat(true)
        return true
    end
    return false
end

-- Форс-флаш COMBAT-лога: гипотеза под проверку (Phase 4.18).
-- Разбор живого лога 30.07 показал, что на воротах строки лежат в буфере клиента
-- ДЕСЯТКИ СЕКУНД: ворота 14:56:44, а мост увидел их в 14:57:04 — при том что
-- отправлять ему в этот момент было почти нечего. Ворота — самый тихий момент
-- матча, буфер не заполняется, и именно там окно вслепую максимально.
-- LoggingChat(false→true) в Anniversary оказался no-op (ADR-0003); для боевого
-- лога это НЕ проверено. Команда ставит эксперимент вручную, поведение аддона
-- при этом не меняется.
function AC.FlushCombatLog()
    if not LoggingCombat then
        AC.Print("LoggingCombat недоступна в этом клиенте.")
        return
    end
    AC.Print("Флашу боевой лог: выключаю и включаю запись…")
    LoggingCombat(false)
    LoggingCombat(true)
    AC.Print("Готово. Проверь папку Logs: вырос ли старый WoWCombatLog-*.txt "
        .. "и появился ли новый файл.")
end

-- Self-test канала addon→bridge без захода на арену.
-- Включает логирование и шлёт тестовые ARENA_START + TRINKET (оба — hint-события
-- на бэке, т.е. при поднятом bridge должен прийти Discord DM).
function AC.RunBridgeTest()
    AC.EnsureChatLogging()
    local myClass = select(2, UnitClass("player")) or "ROGUE"
    local myRace = select(2, UnitRace("player")) or "HUMAN"
    AC.Print("=== Bridge self-test ===")
    AC.Print("1) Запись чата включена принудительно.")
    AC.EmitToChat("ARENA_START", "2v2", "WARRIOR/ORC,PALADIN/BLOODELF",
        myClass .. "/" .. myRace .. ",MAGE/UNDEAD")
    AC.EmitToChat("TRINKET", "TestEnemy", "42292", "pvp_trinket")
    AC.RequestChatFlush()
    AC.Print("2) Отправлены тестовые ARENA_START + TRINKET (+ форс-флаш через ~1с).")
    AC.Print("3) Проверь Logs/WoWChatLog.txt (или Chat-<дата>.txt) — строки [AC#...].")
    AC.Print("4) Если bridge запущен — в Discord придёт DM.")
end

-- ── Сканирование врагов и союзников ─────────────────────────────────────────

local function ScanEnemies(session)
    session.enemies = {}
    for _, unit in ipairs(ARENA_UNITS) do
        if UnitExists(unit) then
            local info = {
                unit  = unit,
                class = select(2, UnitClass(unit)) or "UNKNOWN",
                race  = select(2, UnitRace(unit)) or "UNKNOWN",
            }
            table.insert(session.enemies, info)
        end
    end
end

-- Союзники: игрок ВСЕГДА первым (backend таргетирует советы под его класс)
local function ScanAllies(session)
    session.allies = {}
    for _, unit in ipairs(PLAYER_UNITS) do
        if UnitExists(unit) then
            table.insert(session.allies, {
                unit  = unit,
                class = select(2, UnitClass(unit)) or "UNKNOWN",
                race  = select(2, UnitRace(unit)) or "UNKNOWN",
            })
        end
    end
end

local function UnitsToParts(list)
    local parts = {}
    for _, e in ipairs(list) do
        -- Формат: CLASS/RACE (напр. ROGUE/HUMAN)
        table.insert(parts, (e.class or "UNKNOWN") .. "/" .. (e.race or "UNKNOWN"))
    end
    return table.concat(parts, ",")
end

-- Bracket: сперва через GetBattlefieldStatus (teamSize — надёжно),
-- fallback — по числу видимых arena-unit'ов (стелс скрывает врагов!)
local function DetectBracket(session)
    local maxq = (GetMaxBattlefieldID and GetMaxBattlefieldID()) or 3
    for i = 1, maxq do
        local status, _, _, _, _, teamSize = GetBattlefieldStatus(i)
        if status == "active" and teamSize and teamSize > 0 then
            return teamSize .. "v" .. teamSize
        end
    end
    local count = #(session.enemies or {})
    if count >= 3 then return "3v3" end
    return "2v2"  -- 0-2 видимых врага: часть может быть в стелсе
end

-- Эмит ARENA_START с дедупом: повторный вызов (враг вышел из стелса)
-- шлёт событие заново только если состав врагов реально изменился.
local function EmitArenaStart(session)
    local enemySig = UnitsToParts(session.enemies)
    if session.lastEnemySig == enemySig then return end
    session.lastEnemySig = enemySig
    AC.EmitToChat("ARENA_START", session.bracket, enemySig, UnitsToParts(session.allies))
    AC.RequestChatFlush()
end

-- ── Старт / финиш матча ───────────────────────────────────────────────────────

local function OnArenaStart()
    local session = {
        id         = AC.NewSessionID(),
        bracket    = "unknown",
        map        = GetRealZoneText() or "unknown",
        started_at = AC.Now(),
        ended_at   = nil,
        enemies    = {},
        allies     = {},
        events     = {},
    }

    ScanEnemies(session)
    ScanAllies(session)
    session.bracket = DetectBracket(session)
    AC.currentSession = session
    AC.Print("Арена началась (" .. session.bracket .. ") — трекинг активен.")

    -- Визуальный слой (Phase 4.18) поднимаем ПЕРВЫМ: он не ждёт ни моста, ни
    -- сети — килл-таргет виден в тот же кадр, что и ростер.
    if AC.Overlay then AC.Overlay:StartMatch() end

    -- Сообщаем bridge о старте, составе врагов и союзников
    EmitArenaStart(session)
end

local function OnArenaEnd()
    if AC.Overlay then AC.Overlay:EndMatch() end
    if not AC.currentSession then return end
    AC.currentSession.ended_at = AC.Now()
    AC.EmitToChat("ARENA_END", tostring(#AC.currentSession.events))
    AC.RequestChatFlush()
    table.insert(ArenaCoachDB.sessions, AC.currentSession)
    AC.TrimSessions()
    AC.Print("Арена завершена. Событий записано: " .. #AC.currentSession.events)
    AC.currentSession = nil
end

-- ── COMBAT_LOG_EVENT_UNFILTERED ──────────────────────────────────────────────
-- В TBC 2.4.3 параметры приходят как varargs:
--   timestamp, subevent, sourceGUID, sourceName, sourceFlags,
--   destGUID, destName, destFlags [, spellId, spellName, spellSchool, ...]

local function OnCombatLog(timestamp, subevent, sourceGUID, sourceName, sourceFlags,
                            destGUID, destName, destFlags, spellId, spellName, spellSchool, ...)
    if not AC.currentSession then return end

    -- Голос смотрит событие ПЕРВЫМ и до фильтров: ему нужен SPELL_CAST_START,
    -- единственный сигнал ДО факта (пока хилер кастует, кик ещё имеет смысл).
    if AC.Voice then
        AC.Voice:OnCombatLog(subevent, sourceGUID, sourceName, sourceFlags,
            destGUID, destName, destFlags, tonumber(spellId), spellName)
    end

    -- Нас интересуют только SPELL_CAST_SUCCESS и SPELL_AURA_APPLIED
    if subevent ~= "SPELL_CAST_SUCCESS" and subevent ~= "SPELL_AURA_APPLIED" then
        return
    end

    if not spellId then return end
    spellId = tonumber(spellId)
    if not spellId then return end

    -- Тринкеты — отслеживаем для обеих сторон
    if AC.TRINKET_IDS[spellId] then
        local isEnemy = IsArenaUnit(sourceGUID) ~= nil
        AppendEvent(
            AC.currentSession,
            "trinket_used",
            sourceName,
            destName,
            spellId,
            spellName,
            { trinket_type = AC.TRINKET_IDS[spellId], is_enemy = isEnemy }
        )
        if isEnemy then
            -- Оверлей трекает тринкеты сам: метка «БЕЗ ТРИНКЕТА» и выбор цели
            -- при дублях класса должны обновиться мгновенно, без круга через мост.
            if AC.Overlay then AC.Overlay:NoteTrinket(sourceGUID) end
            AC.Print("ТРИНКЕТ: " .. (sourceName or "?") .. " использовал " .. (spellName or "?"))
            -- Сообщаем bridge — это самый важный real-time сигнал
            AC.EmitToChat("TRINKET", sourceName or "", tostring(spellId),
                AC.TRINKET_IDS[spellId] or "pvp_trinket")
            AC.RequestChatFlush()
        end
        return
    end

    -- Ключевые спеллы врагов
    if AC.TRACKED_SPELLS[spellId] and IsArenaUnit(sourceGUID) then
        AppendEvent(
            AC.currentSession,
            "ability_used",
            sourceName,
            destName,
            spellId,
            spellName,
            { spell_key = AC.TRACKED_SPELLS[spellId] }
        )
        -- Сообщаем bridge о CD врага
        AC.EmitToChat("ABILITY", sourceName or "", tostring(spellId),
            AC.TRACKED_SPELLS[spellId])
        AC.RequestChatFlush()
    end
end

-- ── ARENA_OPPONENT_UPDATE ────────────────────────────────────────────────────

local function OnArenaOpponentUpdate()
    if not AC.currentSession then return end
    -- Обновляем данные врагов (класс может появиться не сразу: стелс,
    -- поздний зум). Если состав изменился — повторный ARENA_START, чтобы
    -- backend прислал уточнённый матчап-совет.
    ScanEnemies(AC.currentSession)
    if AC.Overlay then AC.Overlay:ScanRoster() end
    EmitArenaStart(AC.currentSession)
end

-- ── UNIT_AURA ────────────────────────────────────────────────────────────────
-- Отслеживаем появление/снятие ауры на arena-unit'ах.
-- Используем для детекта активных CC на врагах (cyclone, fear, poly и т.д.)
-- В TBC 2.4.3: UNIT_AURA передаёт только unitId ("arena1", "arena2", ...)

local function OnUnitAura(unitId)
    if not AC.currentSession then return end
    -- Проверяем только arena-units
    local isArena = false
    for _, u in ipairs(ARENA_UNITS) do
        if u == unitId then isArena = true; break end
    end
    if not isArena then return end

    -- Сканируем ауры unit'а в поисках отслеживаемых CC/дефенсивов
    local i = 1
    while true do
        -- UnitDebuff/UnitBuff: name, rank, icon, count, debuffType, duration, expirationTime, ...
        local name, _, _, _, _, _, _, _, _, spellId = UnitDebuff(unitId, i)
        if not name then break end
        if spellId and AC.TRACKED_SPELLS[spellId] then
            AppendEvent(
                AC.currentSession,
                "aura_applied",
                unitId,
                unitId,
                spellId,
                name,
                { spell_key = AC.TRACKED_SPELLS[spellId], aura_index = i }
            )
        end
        i = i + 1
    end
end

-- ── Основной фрейм событий ───────────────────────────────────────────────────
-- (ScheduleCall определён выше, в секции таймера перед bridge-каналом)

local frame = CreateFrame("Frame", "ArenaCoachTrackerFrame")

frame:RegisterEvent("ADDON_LOADED")
frame:RegisterEvent("PLAYER_LOGIN")
frame:RegisterEvent("PLAYER_ENTERING_WORLD")
-- ARENA_PREP_OPPONENT_SPECIALIZATIONS не существует в TBC 2.4.3 — пропускаем
frame:RegisterEvent("ARENA_OPPONENT_UPDATE")
frame:RegisterEvent("COMBAT_LOG_EVENT_UNFILTERED")
frame:RegisterEvent("UNIT_AURA")
-- START/END через zone change — TBC не имеет прямого ARENA_MATCH_START
frame:RegisterEvent("ZONE_CHANGED_NEW_AREA")
frame:RegisterEvent("UPDATE_BATTLEFIELD_STATUS")

local inArena = false

-- В TBC 2.4.3 CombatLogGetCurrentEventInfo() не существует.
-- Данные COMBAT_LOG_EVENT_UNFILTERED приходят как varargs в OnEvent.
-- Формат для SPELL_ событий:
--   timestamp(1), subevent(2), sourceGUID(3), sourceName(4), sourceFlags(5),
--   destGUID(6), destName(7), destFlags(8), spellId(9), spellName(10), spellSchool(11)

frame:SetScript("OnEvent", function(self, event, ...)
    if event == "ADDON_LOADED" then
        local addonName = ...
        if addonName == "ArenaCoach" then
            AC.InitDB()
            if AC.Overlay then AC.Overlay:RestorePosition() end
            AC.Print("v" .. AC.VERSION .. " загружен. /ac для помощи.")
        end

    elseif event == "PLAYER_LOGIN" then
        -- КРИТИЧНО для bridge: включаем запись чата в файл.
        -- Без этого whisper-to-self не попадёт в Logs/Chat-*.txt и
        -- bridge не увидит ни одного [AC#...] события.
        AC.EnsureChatLogging()
        -- Phase 4.2: realtime-канал bridge читает COMBAT-лог — включаем и его.
        AC.EnsureCombatLogging()

    elseif event == "PLAYER_ENTERING_WORLD" or event == "ZONE_CHANGED_NEW_AREA" then
        local _, instanceType = IsInInstance()
        if instanceType == "arena" and not inArena then
            inArena = true
            -- Задержка 1.5с чтобы arena units успели появиться в мире
            ScheduleCall(1.5, OnArenaStart)
        elseif instanceType ~= "arena" and inArena then
            inArena = false
            OnArenaEnd()
        end

    elseif event == "ARENA_OPPONENT_UPDATE" then
        OnArenaOpponentUpdate()

    elseif event == "UNIT_AURA" then
        local unitId = ...
        OnUnitAura(unitId)

    elseif event == "COMBAT_LOG_EVENT_UNFILTERED" then
        -- Передаём varargs напрямую — не используем CombatLogGetCurrentEventInfo()
        OnCombatLog(...)
    end
end)
