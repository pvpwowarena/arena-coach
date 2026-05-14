-- ArenaCoach/Tracker.lua
-- Регистрирует события арены и пишет их в SavedVariables.
-- Отслеживает: трикеты, основные CC/defensive CDs, старт/конец матча.

local AC = ArenaCoach

-- ── Spell ID таблицы ─────────────────────────────────────────────────────────

-- PvP-трикеты (Every Man for Himself = 59752, стандартный = 42292 / 7744)
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

-- ── Сканирование врагов при старте ───────────────────────────────────────────

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

-- ── Старт / финиш матча ───────────────────────────────────────────────────────

local function OnArenaStart()
    local session = {
        id         = AC.NewSessionID(),
        bracket    = "unknown",
        map        = GetRealZoneText() or "unknown",
        started_at = AC.Now(),
        ended_at   = nil,
        enemies    = {},
        events     = {},
    }

    -- Определяем bracket по количеству arena-unit'ов
    local count = 0
    for _, unit in ipairs(ARENA_UNITS) do
        if UnitExists(unit) then count = count + 1 end
    end
    if count == 1 then session.bracket = "2v2"
    elseif count == 2 then session.bracket = "3v3"
    end

    ScanEnemies(session)
    AC.currentSession = session
    AC.Print("Арена началась (" .. session.bracket .. ") — трекинг активен.")
end

local function OnArenaEnd()
    if not AC.currentSession then return end
    AC.currentSession.ended_at = AC.Now()
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

    -- Нас интересуют только SPELL_CAST_SUCCESS и SPELL_AURA_APPLIED
    if subevent ~= "SPELL_CAST_SUCCESS" and subevent ~= "SPELL_AURA_APPLIED" then
        return
    end

    if not spellId then return end
    spellId = tonumber(spellId)
    if not spellId then return end

    -- Трикеты — отслеживаем для обеих сторон
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
            AC.Print("ТРИКЕТ: " .. (sourceName or "?") .. " использовал " .. (spellName or "?"))
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
    end
end

-- ── ARENA_OPPONENT_UPDATE ────────────────────────────────────────────────────

local function OnArenaOpponentUpdate()
    if not AC.currentSession then return end
    -- Обновляем данные врагов (spec/class может появиться не сразу)
    ScanEnemies(AC.currentSession)
end

-- ── Простой OnUpdate-таймер (замена C_Timer.After, которого нет в 2.4.3) ──────

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

-- ── Основной фрейм событий ───────────────────────────────────────────────────

local frame = CreateFrame("Frame", "ArenaCoachTrackerFrame")

frame:RegisterEvent("ADDON_LOADED")
frame:RegisterEvent("PLAYER_LOGIN")
frame:RegisterEvent("PLAYER_ENTERING_WORLD")
-- ARENA_PREP_OPPONENT_SPECIALIZATIONS не существует в TBC 2.4.3 — пропускаем
frame:RegisterEvent("ARENA_OPPONENT_UPDATE")
frame:RegisterEvent("COMBAT_LOG_EVENT_UNFILTERED")
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
            AC.Print("v" .. AC.VERSION .. " загружен. /ac для помощи.")
        end

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

    elseif event == "COMBAT_LOG_EVENT_UNFILTERED" then
        -- Передаём varargs напрямую — не используем CombatLogGetCurrentEventInfo()
        OnCombatLog(...)
    end
end)
