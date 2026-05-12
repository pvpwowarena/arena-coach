-- core/Serializer.lua — сериализация событий в (a) ArenaCoachDB (b) chat-frame mirror.
--
-- Phase 3 stub. См. ADR-0003 (docs/decisions/0003-chatframe-realtime-channel.md).
--
-- Канонический формат строки чат-фрейма: `[AC|<base64-encoded compact-JSON>]`
-- Bridge tail'ит Logs/Chat-*.txt и парсит эти строки.

local Serializer = {}

-- Минимальная base64-кодировка (без зависимостей).
-- TODO(Phase 3): использовать ту же таблицу, что и bridge'овский декодер.
local b64chars = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/"

function Serializer.b64encode(data)
    local result = ""
    local i = 1
    while i <= #data do
        local b1 = data:byte(i) or 0
        local b2 = data:byte(i + 1) or 0
        local b3 = data:byte(i + 2) or 0
        local triple = b1 * 65536 + b2 * 256 + b3
        local c1 = math.floor(triple / 262144) % 64
        local c2 = math.floor(triple / 4096) % 64
        local c3 = math.floor(triple / 64) % 64
        local c4 = triple % 64
        result = result .. b64chars:sub(c1 + 1, c1 + 1) .. b64chars:sub(c2 + 1, c2 + 1)
        if i + 1 <= #data then
            result = result .. b64chars:sub(c3 + 1, c3 + 1)
        else
            result = result .. "="
        end
        if i + 2 <= #data then
            result = result .. b64chars:sub(c4 + 1, c4 + 1)
        else
            result = result .. "="
        end
        i = i + 3
    end
    return result
end

-- TODO(Phase 3):
-- function Serializer.toMirrorLine(eventTable) ... end
-- function Serializer.appendToSV(eventTable) ... end

ArenaCoach.Serializer = Serializer
