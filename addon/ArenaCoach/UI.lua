-- ArenaCoach/UI.lua
-- Минимальный статус-бар: показывает connected/idle и количество событий в текущей сессии.
-- Никакого интерактива в бою — только информация.

local AC = ArenaCoach

-- ── Создаём фрейм ────────────────────────────────────────────────────────────

local UIFrame = CreateFrame("Frame", "ArenaCoachUIFrame", UIParent)
UIFrame:SetWidth(160)
UIFrame:SetHeight(20)
UIFrame:SetPoint("TOPRIGHT", UIParent, "TOPRIGHT", -220, -80)
UIFrame:SetMovable(true)
UIFrame:EnableMouse(true)
UIFrame:RegisterForDrag("LeftButton")
UIFrame:SetScript("OnDragStart", UIFrame.StartMoving)
UIFrame:SetScript("OnDragStop",  UIFrame.StopMovingOrSizing)

-- Фон
local bg = UIFrame:CreateTexture(nil, "BACKGROUND")
bg:SetAllPoints()
bg:SetTexture(0, 0, 0, 0.6)

-- Текстовая метка
local label = UIFrame:CreateFontString(nil, "OVERLAY", "GameFontNormalSmall")
label:SetPoint("LEFT", UIFrame, "LEFT", 4, 0)
label:SetPoint("RIGHT", UIFrame, "RIGHT", -4, 0)
label:SetJustifyH("LEFT")
label:SetText("|cff888888[AC]|r idle")

-- ── Обновление каждые 2 секунды ──────────────────────────────────────────────

local ticker = 0
UIFrame:SetScript("OnUpdate", function(self, elapsed)
    ticker = ticker + elapsed
    if ticker < 2 then return end
    ticker = 0

    if AC.currentSession then
        local evCount = #AC.currentSession.events
        label:SetText("|cff00ff00[AC]|r " .. AC.currentSession.bracket
            .. " |cffffcc00" .. evCount .. " ev|r")
    else
        label:SetText("|cff888888[AC]|r idle")
    end
end)

-- ── Tooltip ──────────────────────────────────────────────────────────────────

UIFrame:SetScript("OnEnter", function(self)
    GameTooltip:SetOwner(self, "ANCHOR_BOTTOMLEFT")
    GameTooltip:AddLine("ArenaCoach v" .. AC.VERSION)
    GameTooltip:AddLine(" ")
    if AC.currentSession then
        GameTooltip:AddLine("|cff00ff00Арена активна|r")
        GameTooltip:AddLine("Bracket: " .. AC.currentSession.bracket)
        GameTooltip:AddLine("Событий: " .. #AC.currentSession.events)
        GameTooltip:AddLine("Карта: " .. (AC.currentSession.map or "?"))
        if #AC.currentSession.enemies > 0 then
            GameTooltip:AddLine(" ")
            GameTooltip:AddLine("Враги:")
            for _, e in ipairs(AC.currentSession.enemies) do
                GameTooltip:AddLine("  " .. e.unit .. ": " .. e.class .. " (" .. e.race .. ")")
            end
        end
    else
        GameTooltip:AddLine("|cff888888Ожидание арены|r")
        GameTooltip:AddLine("Сессий в DB: " .. #ArenaCoachDB.sessions)
    end
    GameTooltip:AddLine(" ")
    GameTooltip:AddLine("|cffaaaaaa/ac status — подробности|r")
    GameTooltip:Show()
end)

UIFrame:SetScript("OnLeave", function()
    GameTooltip:Hide()
end)

-- ── Показать/скрыть через /ac ui ─────────────────────────────────────────────

function AC.ToggleUI()
    if UIFrame:IsShown() then
        UIFrame:Hide()
        AC.Print("UI скрыт.")
    else
        UIFrame:Show()
        AC.Print("UI показан.")
    end
end

-- Расширяем slash-команду (определена в Core.lua)
local _origSlash = SlashCmdList["ARENACOACH"]
SlashCmdList["ARENACOACH"] = function(msg)
    local cmd = strtrim(msg or ""):lower()
    if cmd == "ui" then
        AC.ToggleUI()
    elseif cmd == "coach pause" then
        AC.SetBridgeEnabled(false)
    elseif cmd == "coach resume" then
        AC.SetBridgeEnabled(true)
    else
        _origSlash(msg)
    end
end
