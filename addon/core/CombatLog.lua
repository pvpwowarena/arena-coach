-- core/CombatLog.lua — обработка COMBAT_LOG_EVENT_UNFILTERED.
--
-- Phase 3 stub. Будет фильтровать релевантные события:
--   SPELL_CAST_SUCCESS, SPELL_AURA_APPLIED/REMOVED, UNIT_DIED
-- и эмитить через EventBus.

local CombatLog = {}

function CombatLog:OnLoad()
    -- TODO(Phase 3): RegisterEvent("COMBAT_LOG_EVENT_UNFILTERED")
end

ArenaCoach.registerModule("CombatLog", CombatLog)
