-- ui/StatusFrame.lua — крошечный non-interactive фрейм со статусом.
--
-- Phase 3 stub. Показывает только: connected / idle / paused. Никакого interactive UI
-- во время боя (secure templates — отдельный риск, и нам это не нужно для advisory output).

local StatusFrame = {}

function StatusFrame:OnLoad()
    -- TODO(Phase 3): создать маленький фрейм 80x20px в верхнем правом углу,
    -- показывать состояние ArenaCoach (connected/idle/paused).
end

ArenaCoach.registerModule("StatusFrame", StatusFrame)
