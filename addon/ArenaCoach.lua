-- ArenaCoach.lua — bootstrap.
--
-- Phase 3 skeleton: регистрация namespace + delegate на модули core/.
-- Реальная логика арена-tracker'а и chat-frame mirror'а — Phase 3 (см. ADR-0003).
--
-- WoW Lua 2.4.3 (Burning Crusade Classic Anniversary), без сторонних библиотек.

local ADDON_NAME = ...
ArenaCoach = ArenaCoach or {}
ArenaCoach.version = "0.1.0-skeleton"
ArenaCoach.db = nil  -- ArenaCoachDB, инициализируется на ADDON_LOADED

-- Хелперы для модулей
ArenaCoach.modules = {}

function ArenaCoach.registerModule(name, mod)
    ArenaCoach.modules[name] = mod
    if mod.OnLoad then mod:OnLoad() end
end

-- Основной фрейм для регистрации событий
local frame = CreateFrame("Frame", "ArenaCoachFrame", UIParent)
frame:RegisterEvent("ADDON_LOADED")
frame:RegisterEvent("PLAYER_LOGIN")

frame:SetScript("OnEvent", function(self, event, ...)
    if event == "ADDON_LOADED" then
        local name = ...
        if name == ADDON_NAME then
            -- TODO(Phase 3): инициализировать ArenaCoachDB схему { schema=1, sessions={...} }
            ArenaCoachDB = ArenaCoachDB or { schema = 1, sessions = {} }
            ArenaCoach.db = ArenaCoachDB
        end
    elseif event == "PLAYER_LOGIN" then
        -- TODO(Phase 3): запустить трекеры
        DEFAULT_CHAT_FRAME:AddMessage("|cff7f7fffArena Coach|r v" .. ArenaCoach.version .. " loaded (skeleton)")
    end
end)
