-- core/ArenaTracker.lua — трекинг арена-матча: opponent spec/race, состав, map.
--
-- Phase 3 stub. Будет регистрироваться на:
--   ARENA_OPPONENT_UPDATE — список противников
--   PLAYER_ENTERING_WORLD — старт матча, определение map'а
--   UPDATE_BATTLEFIELD_SCORE — финальный счёт
--
-- TODO(Phase 3): полная реализация согласно docs/phase-0-design.md §6.1

local ArenaTracker = {}

function ArenaTracker:OnLoad()
    -- TODO: register events, init session state
end

ArenaCoach.registerModule("ArenaTracker", ArenaTracker)
