-- Заглушка клиентского API WoW 2.4.3 — чтобы гонять логику аддона в обычном
-- lua5.1 из pytest. Реализуем ровно то, что аддон трогает: фреймы-пустышки,
-- Unit*-функции поверх таблицы сценария и минимум глобалей.
--
-- Смысл: логика килл-таргета и тринкетов должна быть проверяема без клиента.

local scenario = { units = {}, party = {} }
_G.SCENARIO = scenario

-- ── фреймы ──────────────────────────────────────────────────────────────────

local function NewRegion()
    local r = {}
    local noop = function() return r end
    for _, m in ipairs({
        "SetWidth", "SetHeight", "SetPoint", "SetAllPoints", "SetTexture", "SetText",
        "SetJustifyH", "Show", "Hide", "SetTexCoord", "ClearAllPoints", "SetVertexColor",
    }) do
        r[m] = noop
    end
    r.IsShown = function() return true end
    return r
end

function _G.CreateFrame(_, name, _, _)
    local f = NewRegion()
    f.scripts = {}
    f.shown = false
    f.SetScript = function(self, key, fn) self.scripts[key] = fn; return self end
    f.GetScript = function(self, key) return self.scripts[key] end
    f.RegisterEvent = function() end
    f.UnregisterEvent = function() end
    f.RegisterForDrag = function() end
    f.SetMovable = function() end
    f.EnableMouse = function() end
    f.StartMoving = function() end
    f.StopMovingOrSizing = function() end
    f.GetPoint = function() return "RIGHT", nil, "RIGHT", -40, 60 end
    f.Show = function(self) self.shown = true end
    f.Hide = function(self) self.shown = false end
    f.IsShown = function(self) return self.shown end
    f.CreateTexture = function() return NewRegion() end
    f.CreateFontString = function()
        local fs = NewRegion()
        fs.text = ""
        fs.SetText = function(self, t) self.text = t end
        fs.GetText = function(self) return self.text end
        return fs
    end
    if name then _G[name] = f end
    return f
end

_G.UIParent = NewRegion()
_G.GameTooltip = { SetOwner = function() end, AddLine = function() end, Show = function() end,
                   Hide = function() end }
_G.DEFAULT_CHAT_FRAME = { AddMessage = function() end }
_G.SlashCmdList = {}

-- ── Unit API поверх сценария ────────────────────────────────────────────────

local function unitInfo(unit)
    return scenario.units[unit] or scenario.party[unit]
end

function _G.UnitExists(unit) return unitInfo(unit) ~= nil end
function _G.UnitClass(unit)
    local u = unitInfo(unit)
    if not u then return nil end
    return u.class, u.class
end
function _G.UnitRace(unit)
    local u = unitInfo(unit)
    local r = u and u.race or "Human"
    return r, r
end
function _G.UnitName(unit)
    local u = unitInfo(unit)
    return u and (u.name or unit) or nil
end
function _G.UnitGUID(unit)
    local u = unitInfo(unit)
    return u and (u.guid or ("GUID-" .. unit)) or nil
end
function _G.UnitHealth(unit)
    local u = unitInfo(unit)
    if u and u.dead then return 0 end
    return u and (u.hp or 100) or 0
end
function _G.UnitHealthMax(unit) return 100 end
-- Труп остаётся валидным юнитом: UnitExists = true, HP = 0. Именно на этом аддон
-- держал череп на убитом присте, поэтому в заглушке смерть моделируется явно.
function _G.UnitIsDeadOrGhost(unit)
    local u = unitInfo(unit)
    return (u and u.dead) and true or false
end
function _G.UnitDebuff() return nil end
function _G.UnitBuff() return nil end

-- ── прочие глобали, которые дергает аддон при загрузке ──────────────────────

function _G.GetTime() return 0 end
function _G.IsInInstance() return false, "none" end
function _G.GetRealZoneText() return "Nagrand Arena" end
function _G.GetBattlefieldStatus() return "none" end
function _G.GetMaxBattlefieldID() return 3 end
function _G.SendChatMessage() end
function _G.LoggingChat() return true end
function _G.LoggingCombat() return true end
function _G.strtrim(s) return (string.gsub(s or "", "^%s*(.-)%s*$", "%1")) end
function _G.date() return { year = 2026, month = 7, day = 30, hour = 12, min = 0, sec = 0 } end

-- Метка на цели: записываем вызовы, чтобы тест видел, что череп ставился.
scenario.marks = {}
function _G.SetRaidTarget(unit, index)
    table.insert(scenario.marks, { unit = unit, index = index })
end

-- Голосовые клипы: записываем, что аддон пытался проиграть.
scenario.clips = {}
function _G.PlaySoundFile(path, channel)
    local key = string.match(path, "([^\\]+)%.ogg$") or path
    table.insert(scenario.clips, key)
    return true
end
function _G.PlaySound(name)
    table.insert(scenario.clips, "builtin:" .. tostring(name))
end
