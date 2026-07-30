-- ArenaCoach/Core.lua
-- Namespace, constants, SavedVariables schema, utility functions.
-- Никакой логики событий здесь — только фундамент.

ArenaCoach = ArenaCoach or {}
local AC = ArenaCoach

-- ── Версия ──────────────────────────────────────────────────────────────────
AC.VERSION = "0.4.0"

-- ── SavedVariables schema ────────────────────────────────────────────────────
-- ArenaCoachDB инициализируется один раз при первом логине.
-- Структура:
--   ArenaCoachDB.sessions  = list<Session>
--   Session = {
--     id         = string,   -- "<date>-<time>"
--     bracket    = string,   -- "2v2" | "3v3"
--     map        = string,   -- локализованное название карты
--     started_at = number,   -- GetTime() при старте
--     ended_at   = number,   -- GetTime() при конце
--     enemies    = list<EnemyInfo>,
--     events     = list<Event>,
--   }
--   EnemyInfo = { unit="arena1"|"arena2"|"arena3", class, race, spec_guess }
--   Event = { ts, event, source, target, ability_id, ability_name, payload }

function AC.InitDB()
    if not ArenaCoachDB then
        ArenaCoachDB = { sessions = {} }
    end
    if not ArenaCoachDB.sessions then
        ArenaCoachDB.sessions = {}
    end
end

-- ── Утилиты ──────────────────────────────────────────────────────────────────

-- Текущее время в секундах с точностью до 0.001
function AC.Now()
    return GetTime()
end

-- Генератор простого строкового ID на основе даты/времени
function AC.NewSessionID()
    local d = date("*t")
    return string.format("%04d%02d%02d-%02d%02d%02d",
        d.year, d.month, d.day, d.hour, d.min, d.sec)
end

-- Обрезать список до MAX записей (защита от переполнения SV)
local MAX_SESSIONS = 50
function AC.TrimSessions()
    local s = ArenaCoachDB.sessions
    while #s > MAX_SESSIONS do
        table.remove(s, 1)
    end
end

-- Безопасный print в DEFAULT_CHAT_FRAME
function AC.Print(msg)
    DEFAULT_CHAT_FRAME:AddMessage("|cff00ccff[ArenaCoach]|r " .. tostring(msg))
end

-- ── Slash-команда ─────────────────────────────────────────────────────────────
SLASH_ARENACOACH1 = "/ac"
SLASH_ARENACOACH2 = "/arenacoach"
SlashCmdList["ARENACOACH"] = function(msg)
    local cmd = strtrim(msg or ""):lower()
    if cmd == "status" or cmd == "" then
        AC.PrintStatus()
    elseif cmd == "reset" then
        ArenaCoachDB.sessions = {}
        AC.Print("SavedVariables очищены.")
    elseif cmd == "sessions" then
        AC.Print("Сессий в DB: " .. #ArenaCoachDB.sessions)
    elseif cmd == "test" then
        if AC.RunBridgeTest then
            AC.RunBridgeTest()
        else
            AC.Print("Tracker ещё не загружен.")
        end
    elseif cmd == "log" then
        if LoggingChat and LoggingChat() then
            AC.Print("Запись чата: ВКЛ (Logs/WoWChatLog.txt или Chat-*.txt пишется).")
        else
            if AC.EnsureChatLogging then AC.EnsureChatLogging() end
            AC.Print("Запись чата: была ВЫКЛ — включил сейчас.")
        end
        if LoggingCombat and LoggingCombat() then
            AC.Print("Запись боя: ВКЛ (Logs/WoWCombatLog-*.txt пишется — канал bridge).")
        else
            if AC.EnsureCombatLogging then AC.EnsureCombatLogging() end
            AC.Print("Запись боя: была ВЫКЛ — включил сейчас (канал bridge, Phase 4.2).")
        end
    elseif cmd == "flushtest" then
        if AC.FlushCombatLog then AC.FlushCombatLog() end
    elseif cmd:match("^flush") then
        local arg = cmd:match("^flush%s+(%S+)")
        if arg == "on" and AC.SetFlushEnabled then
            AC.SetFlushEnabled(true)
        elseif arg == "off" and AC.SetFlushEnabled then
            AC.SetFlushEnabled(false)
        else
            local state = (AC.IsFlushEnabled and AC.IsFlushEnabled()) and "ВКЛ" or "ВЫКЛ"
            AC.Print("Форс-флаш чат-лога: " .. state .. ". Переключить: /ac flush on|off")
        end
    else
        AC.Print("Команды: /ac status | /ac ui | /ac overlay | /ac skull on|off")
        AC.Print("          /ac sound on|off|test — голос аддона")
        AC.Print("          /ac test | /ac log | /ac flush | /ac flushtest | /ac sessions | /ac reset")
    end
end

function AC.PrintStatus()
    AC.Print("ArenaCoach v" .. AC.VERSION)
    AC.Print("Матчапов в килл-таргет-таблице: " .. tostring(AC.KB_KILL_TARGETS_COUNT or 0))
    AC.Print("Сессий в DB: " .. #ArenaCoachDB.sessions)
    if AC.currentSession then
        AC.Print("Активная сессия: " .. AC.currentSession.id)
        AC.Print("Событий: " .. #AC.currentSession.events)
    else
        AC.Print("Активной сессии нет.")
    end
end
