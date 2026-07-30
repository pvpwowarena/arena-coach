-- ArenaCoach/Overlay.lua
-- Визуальный слой: килл-таргет, тринкеты и номера арена-фреймов — ЛОКАЛЬНО.
--
-- Зачем отдельный слой (Phase 4.18). Измеренная цепочка «ворота → голос» —
-- combat-лог → мост → POST → бэкенд → поллинг /v1/hints → TTS → проговаривание —
-- даже в идеале даёт ~1.5-2с, а на живом тесте 30.07 дала 26с. Требование Влада —
-- успевать в окно ваншота, доли секунды. Ни одно звено с сетью в это окно не лезет.
--
-- Аддон в этот бюджет попадает по построению: `UnitClass("arena1")` отдаёт класс
-- врага В МОМЕНТ ВОРОТ (без кастов и без лога), KB-килл-таргет скомпилирован в
-- KillTargets.lua, тринкеты аддон видит своим CLEU. Сети в цепочке нет вообще.
--
-- Показываем ГЛАЗАМИ, а не голосом: череп на килл-таргете, метка «нет тринкета»,
-- номер арена-фрейма. Череп виден и напарнику, и на нейтплейте, и не тратит
-- бюджет речи (Phase 4.17). Голос остаётся тому, что терпит секунду: старт, окна
-- КД, постматч.
--
-- Ничего наружу не шлёт: решение принимается и отображается на месте.

local AC = ArenaCoach

AC.Overlay = AC.Overlay or {}
local O = AC.Overlay

local ARENA_UNITS = { "arena1", "arena2", "arena3" }
local PARTY_UNITS = { "player", "party1", "party2" }

-- Короткие имена классов для панели (то же, чем говорит команда).
local CLASS_SHORT = {
    WARRIOR = "ВАР",
    PALADIN = "ПАЛА",
    HUNTER  = "ХАНТ",
    ROGUE   = "РОГА",
    PRIEST  = "ЖРЕЦ",
    SHAMAN  = "ШАМ",
    MAGE    = "МАГ",
    WARLOCK = "ЛОК",
    DRUID   = "ДРУИД",
}

local CLASS_COLOR = {
    WARRIOR = "ffc79c6e", PALADIN = "fff58cba", HUNTER = "ffabd473", ROGUE = "fffff569",
    PRIEST  = "ffffffff", SHAMAN  = "ff0070de", MAGE   = "ff69ccf0", WARLOCK = "ff9482c9",
    DRUID   = "ffff7d0a",
}

-- Фолбэк-приоритет добива, когда матчапа нет в KB. Порт эвристики бэкенда
-- (backend/arena_coach/orchestrator/killpriority.py): клоти-дпс умирают быстрее
-- всех, хилеры — в самом низу. Меньше число — выше приоритет.
local CLASS_RANK = {
    WARLOCK = 0, MAGE = 1, PRIEST = 2, SHAMAN = 3, HUNTER = 4,
    DRUID = 5, ROGUE = 6, WARRIOR = 7, PALADIN = 8,
}
-- Класс, который в наших брекетах почти всегда хилер: двигаем вниз, но не убираем.
local LIKELY_HEALER = { PALADIN = true }
local HEALER_PENALTY = 100

-- PvP-тринкет: КД не подтверждён источником (см. память проекта, Phase 4.14),
-- поэтому обратный отсчёт НЕ показываем — только факт «потрачен / ещё есть».
local TRINKET_IDS = AC.TRINKET_IDS or {}

-- ── Состояние матча ─────────────────────────────────────────────────────────

O.enabled = true
O.markEnabled = true          -- ставить ли череп через raid-target
O.units = {}                  -- список { unit, class, name, trinketUsed }
O.targetUnit = nil            -- "arena1" | ...
O.targetSure = true           -- уверенность источника (KB / эвристика)
O.source = "—"                -- откуда взялась цель (для tooltip)
O.markedGUID = nil

-- ── Килл-таргет ─────────────────────────────────────────────────────────────

local function SortedClasses(list)
    local out = {}
    for _, c in ipairs(list) do
        if c and c ~= "" then table.insert(out, string.lower(c)) end
    end
    table.sort(out)
    return table.concat(out, "+")
end

local function OurClasses()
    local out = {}
    for _, unit in ipairs(PARTY_UNITS) do
        if UnitExists(unit) then
            table.insert(out, select(2, UnitClass(unit)) or "")
        end
    end
    return out
end

--- Ключ матчапа. Один и тот же для `KillTargets.lua` и `Openers.lua`: оба
--- скомпилированы из KB одним ключом, и собрать его аддон может сам из UnitClass
--- в момент ворот — без кастов, лога и сети.
local function MatchupKey(bracket, ourList, enemyList)
    return bracket .. "|" .. SortedClasses(ourList) .. "|" .. SortedClasses(enemyList)
end

-- KB-таблица: точный матчап (наш состав vs их) → класс цели.
local function LookupKB(key)
    local kb = AC.KB_KILL_TARGETS
    if not kb or not key then return nil end
    local hit = kb[key]
    if not hit then return nil end
    return hit.t, hit.sure, "KB"
end

-- Фолбэк: эвристика по классам (тот же порядок, что у бэкенда).
local function HeuristicTarget(enemyList)
    local best, bestRank
    for _, class in ipairs(enemyList) do
        local rank = CLASS_RANK[class]
        if rank then
            if LIKELY_HEALER[class] then rank = rank + HEALER_PENALTY end
            if not bestRank or rank < bestRank then
                best, bestRank = class, rank
            end
        end
    end
    return best
end

--- Жив ли враг. Труп остаётся валидным юнитом (`UnitExists` = true, HP = 0), и без
--- этой проверки он ВЫИГРЫВАЛ выбор цели: скор считается по HP, «меньше — лучше»,
--- а у мёртвого он нулевой. Живой промах 30.07: приста убили, а аддон продолжал
--- звать «Бей жреца!» и держал череп на трупе.
local function IsAlive(unit)
    if not unit or not UnitExists(unit) then return false end
    if UnitIsDeadOrGhost and UnitIsDeadOrGhost(unit) then return false end
    return UnitHealth(unit) > 0
end

-- Из класса цели выбираем КОНКРЕТНОГО врага. При дублях класса (две роги)
-- class-level решение неразрешимо — а аддон видит то, чего не видит сервер:
-- кто уже потратил тринкет и у кого меньше HP. Это и есть признак выбора.
local function PickUnit(targetClass)
    local best, bestScore
    for _, u in ipairs(O.units) do
        if u.class == targetClass and IsAlive(u.unit) then
            local hp = 1
            if UnitExists(u.unit) and UnitHealthMax(u.unit) > 0 then
                hp = UnitHealth(u.unit) / UnitHealthMax(u.unit)
            end
            -- Без тринкета — заметно приоритетнее; при равенстве берём слабее по HP.
            local score = hp - (u.trinketUsed and 0.5 or 0)
            if not bestScore or score < bestScore then
                best, bestScore = u, score
            end
        end
    end
    return best
end

--- Является ли GUID одним из врагов на арене (нужен голосу для фильтра «свой/чужой»).
function O:IsEnemyGUID(guid)
    if not guid then return false end
    for _, u in ipairs(self.units) do
        if UnitExists(u.unit) and UnitGUID(u.unit) == guid then return true end
    end
    return false
end

function O:Recompute()
    -- В расчёт идут только ЖИВЫЕ враги. Труп не только не может быть целью — он ещё
    -- и портит ключ матчапа: после смерти приста «rogue+priest» превращается в
    -- «rogue», и искать в KB надо уже другой сетап, а не прежний.
    local enemyList = {}
    for _, u in ipairs(self.units) do
        if u.class and u.class ~= "UNKNOWN" and IsAlive(u.unit) then
            table.insert(enemyList, u.class)
        end
    end
    if #enemyList == 0 then
        -- Различаем «ещё не видны» (стелс-опенер) и «уже мертвы»: на панели это
        -- разные состояния, и второе означает, что бой по сути выигран.
        local reason = "враги не видны"
        for _, u in ipairs(self.units) do
            if u.class and u.class ~= "UNKNOWN" then reason = "враги мертвы" end
        end
        self.targetUnit, self.source, self.targetSure = nil, reason, true
        self.markedGUID = nil
        self:Refresh()
        return
    end

    local bracket = (AC.currentSession and AC.currentSession.bracket) or "2v2"
    local key = MatchupKey(bracket, OurClasses(), enemyList)
    local class, sure, source = LookupKB(key)
    if not class then
        class, sure, source = HeuristicTarget(enemyList), false, "эвристика"
    end

    local pick = class and PickUnit(class) or nil
    self.targetUnit = pick and pick.unit or nil
    self.targetSure = sure and true or false
    self.source = source or "—"
    self:ApplyMark(pick)
    self:Refresh()

    -- Голос: сперва пробуем тактический колаут матчапа («Сап приста, бей мага!
    -- Чип, кидни»), и только если такого ключа нет — короткое «Бей мага!».
    -- Оба варианта знают цель уже на воротах, без единого каста и без сети.
    if pick and AC.Voice then AC.Voice:AnnounceOpener(key, pick.class) end

    -- «Тринкета нет» — отдельный сигнал: окно на добив открывается именно тут.
    if pick and pick.trinketUsed and AC.Voice then AC.Voice:Say("notrinket") end
end

-- ── Череп на цели ───────────────────────────────────────────────────────────
-- ⚠️ В 2.4.3 метку ставит лидер/ассист группы, и имя API отличается между
-- сборками. Поэтому вызов защищён pcall, а основной визуал — своя панель:
-- если метка не поставится, игрок всё равно всё видит.

local function SetMark(unit, index)
    local fn = SetRaidTarget or SetRaidTargetIcon
    if not fn then return false end
    local ok = pcall(fn, unit, index)
    return ok
end

function O:ApplyMark(pick)
    if not self.markEnabled or not pick then return end
    local guid = UnitGUID and UnitGUID(pick.unit)
    if guid and guid == self.markedGUID then return end   -- уже помечен
    if SetMark(pick.unit, 8) then                          -- 8 = череп
        self.markedGUID = guid
    end
end

-- ── Панель ──────────────────────────────────────────────────────────────────

local ROW_H = 18
local frame = CreateFrame("Frame", "ArenaCoachOverlayFrame", UIParent)
frame:SetWidth(190)
frame:SetHeight(ROW_H * 3 + 24)
frame:SetPoint("RIGHT", UIParent, "RIGHT", -40, 60)
frame:SetMovable(true)
frame:EnableMouse(true)
frame:RegisterForDrag("LeftButton")
frame:SetScript("OnDragStart", frame.StartMoving)
frame:SetScript("OnDragStop", function(self)
    self:StopMovingOrSizing()
    local point, _, relPoint, x, y = self:GetPoint()
    if ArenaCoachDB then
        ArenaCoachDB.overlay = { point = point, rel = relPoint, x = x, y = y }
    end
end)
frame:Hide()

local bg = frame:CreateTexture(nil, "BACKGROUND")
bg:SetAllPoints()
bg:SetTexture(0, 0, 0, 0.55)

local title = frame:CreateFontString(nil, "OVERLAY", "GameFontNormalSmall")
title:SetPoint("TOPLEFT", frame, "TOPLEFT", 6, -4)
title:SetText("|cff00ccffArenaCoach|r")

local rows = {}
for i = 1, 3 do
    local row = CreateFrame("Frame", nil, frame)
    row:SetWidth(178)
    row:SetHeight(ROW_H)
    row:SetPoint("TOPLEFT", frame, "TOPLEFT", 6, -(18 + (i - 1) * ROW_H))

    row.icon = row:CreateTexture(nil, "OVERLAY")
    row.icon:SetWidth(14)
    row.icon:SetHeight(14)
    row.icon:SetPoint("LEFT", row, "LEFT", 0, 0)
    row.icon:SetTexture("Interface\\TargetingFrame\\UI-RaidTargetingIcon_8")
    row.icon:Hide()

    row.text = row:CreateFontString(nil, "OVERLAY", "GameFontNormalSmall")
    row.text:SetPoint("LEFT", row, "LEFT", 18, 0)
    row.text:SetJustifyH("LEFT")
    row:Hide()
    rows[i] = row
end

function O:Refresh()
    if not self.enabled or #self.units == 0 then
        frame:Hide()
        return
    end
    frame:Show()
    for i = 1, 3 do
        local u, row = self.units[i], rows[i]
        if not u then
            row:Hide()
        else
            row:Show()
            local isTarget = (u.unit == self.targetUnit)
            if isTarget then row.icon:Show() else row.icon:Hide() end

            local num = string.sub(u.unit, 6)          -- "arena2" → "2"
            local color = CLASS_COLOR[u.class] or "ffcccccc"
            local short = CLASS_SHORT[u.class] or (u.class or "?")
            -- «АРЕНА N» — тот самый номер фрейма, которого не хватало при дублях.
            local line = string.format("|cffaaaaaaАРЕНА %s|r |c%s%s|r", num, color, short)
            if u.trinketUsed then
                line = line .. " |cffff4040БЕЗ ТРИНКЕТА|r"
            end
            if isTarget and not self.targetSure then
                line = line .. " |cffaaaaaa(?)|r"
            end
            row.text:SetText(line)
        end
    end
end

frame:SetScript("OnEnter", function(self)
    GameTooltip:SetOwner(self, "ANCHOR_LEFT")
    GameTooltip:AddLine("ArenaCoach — килл-таргет")
    GameTooltip:AddLine("Источник: " .. (O.source or "—"), 0.7, 0.7, 0.7)
    if not O.targetSure then
        GameTooltip:AddLine("Цель предположительная: матчапа нет в KB", 1, 0.8, 0.2)
    end
    GameTooltip:AddLine(" ")
    GameTooltip:AddLine("Череп — цель. БЕЗ ТРИНКЕТА — тринкет уже потрачен.", 0.7, 0.7, 0.7)
    GameTooltip:AddLine("/ac overlay — скрыть, /ac skull off — не ставить метку", 0.6, 0.6, 0.6)
    GameTooltip:Show()
end)
frame:SetScript("OnLeave", function() GameTooltip:Hide() end)

-- Позиция панели переживает /reload.
function O:RestorePosition()
    local p = ArenaCoachDB and ArenaCoachDB.overlay
    if p and p.point then
        frame:ClearAllPoints()
        frame:SetPoint(p.point, UIParent, p.rel or p.point, p.x or 0, p.y or 0)
    end
end

-- ── Вход из Tracker ─────────────────────────────────────────────────────────

-- Ворота / уточнение ростера: пересобираем список врагов из UnitClass.
-- Это МГНОВЕННО и не требует ни одного каста врага.
function O:ScanRoster()
    local prev = {}
    for _, u in ipairs(self.units) do prev[u.unit] = u.trinketUsed end

    self.units = {}
    for _, unit in ipairs(ARENA_UNITS) do
        if UnitExists(unit) then
            table.insert(self.units, {
                unit        = unit,
                class       = select(2, UnitClass(unit)) or "UNKNOWN",
                name        = UnitName(unit) or "?",
                trinketUsed = prev[unit] or false,
            })
        end
    end
    self:Recompute()
end

function O:StartMatch()
    self.units = {}
    self.targetUnit = nil
    self.markedGUID = nil
    if AC.Voice then AC.Voice:ResetMatch() end
    self:ScanRoster()
end

function O:EndMatch()
    self.units = {}
    self.targetUnit = nil
    self.markedGUID = nil
    frame:Hide()
end

-- Тринкет врага: аддон трекает сам, тем же CLEU, что и Tracker.
function O:NoteTrinket(sourceGUID)
    local changed = false
    for _, u in ipairs(self.units) do
        if UnitExists(u.unit) and UnitGUID(u.unit) == sourceGUID and not u.trinketUsed then
            u.trinketUsed = true
            changed = true
        end
    end
    if changed then self:Recompute() end
end

function O:IsTrinketSpell(spellId)
    return TRINKET_IDS[spellId] ~= nil
end

function O:Toggle()
    self.enabled = not self.enabled
    if self.enabled then self:Refresh() else frame:Hide() end
    AC.Print("Оверлей: " .. (self.enabled and "ВКЛ" or "ВЫКЛ"))
end

function O:SetMarkEnabled(val)
    self.markEnabled = val
    AC.Print("Череп на килл-таргете: " .. (val and "ВКЛ" or "ВЫКЛ"))
end

-- HP меняется постоянно — при дублях класса цель может переехать на более
-- слабого. Пересчитываем редко (2/с): решение должно быть стабильным, а не
-- дёргаться на каждый тик урона.
local elapsed = 0
frame:SetScript("OnUpdate", function(self, e)
    elapsed = elapsed + e
    if elapsed < 0.5 then return end
    elapsed = 0
    if O.enabled and #O.units > 0 then O:Recompute() end
end)
