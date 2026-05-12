-- core/EventBus.lua — внутренняя шина событий между модулями.
--
-- Phase 3 stub. Реальная реализация:
--   ArenaCoach.EventBus:Subscribe(eventName, handlerFn)
--   ArenaCoach.EventBus:Emit(eventName, payload)
--
-- Используется ArenaTracker, CombatLog, CooldownTracker для развязки логики.

local EventBus = {}
EventBus.handlers = {}

function EventBus:Subscribe(eventName, handler)
    if not self.handlers[eventName] then
        self.handlers[eventName] = {}
    end
    table.insert(self.handlers[eventName], handler)
end

function EventBus:Emit(eventName, payload)
    local hs = self.handlers[eventName]
    if not hs then return end
    for _, h in ipairs(hs) do
        local ok, err = pcall(h, payload)
        if not ok then
            DEFAULT_CHAT_FRAME:AddMessage("|cffff5555[AC]|r EventBus handler error in " .. tostring(eventName) .. ": " .. tostring(err))
        end
    end
end

ArenaCoach.EventBus = EventBus
