-- core/CooldownTracker.lua — отслеживание ключевых КД противника и наших.
--
-- Phase 3 stub. Списки КД на трекинг (см. docs/phase-0-design.md §3.4):
--   Enemy: trinket (42292/7744), intercept, spell-reflect, pvp-trinket-break,
--          rogue cooldowns (evasion, cloak, vanish, prep, blind),
--          paladin (hand of freedom, divine shield, bubble), druid (NS, barkskin),
--          mage (ice block), priest (PS, fear, AMS-?), etc.
--   Ours: симметрично для нашего класса.

local CooldownTracker = {}

function CooldownTracker:OnLoad()
    -- TODO(Phase 3): subscribe to CombatLog events; track CD timers
end

ArenaCoach.registerModule("CooldownTracker", CooldownTracker)
