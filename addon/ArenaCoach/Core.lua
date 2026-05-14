-- ArenaCoach/Core.lua
-- Namespace, constants, SavedVariables schema, utility functions.
-- Никакой логики событий здесь — только фундамент.

ArenaCoach = ArenaCoach or {}
local AC = ArenaCoach

-- ── Версия ──────────────────────────────────────────────────────────────────
AC.VERSION = "0.1.0"

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
    else
        AC.Print("Команды: /ac status | /ac sessions | /ac reset")
    end
end

function AC.PrintStatus()
    AC.Print("ArenaCoach v" .. AC.VERSION)
    AC.Print("Сессий в DB: " .. #ArenaCoachDB.sessions)
    if AC.currentSession then
        AC.Print("Активная сессия: " .. AC.currentSession.id)
        AC.Print("Событий: " .. #AC.currentSession.events)
    else
        AC.Print("Активной сессии нет.")
    end
end
