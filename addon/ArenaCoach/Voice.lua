-- ArenaCoach/Voice.lua
-- Голос БЕЗ сети: аддон сам решает и сам проигрывает клип (Phase 4.19).
--
-- Почему это отдельный слой, а не «ещё один канал». Замер 30.07 доказал цифрами:
-- клиент сбрасывает combat-лог на диск блоками ~48КБ (измерено: 51437 / 47118 /
-- 45117 байт между приходами), поэтому события доезжают до моста пачками с
-- опозданием 13-28с. Худший POST при этом — 0.64с. То есть узкое место не сеть и
-- не бэкенд: данных просто нет на диске. Любой голос через мост опаздывает
-- структурно, и починить это в мосту невозможно.
--
-- Аддон видит те же события напрямую из COMBAT_LOG_EVENT_UNFILTERED — в тот же
-- кадр, без файла, без сети. Не хватало только звука: TTS в клиенте нет. Значит
-- фразы нарезаны заранее (tools/gen_addon_voice.py, espeak-ng → ogg) и лежат в
-- sfx/ рядом с аддоном.
--
-- Что озвучиваем — только то, что аддон знает ТОЧНО и что требует решения СЕЙЧАС:
--   • хилер начал каст  → «Кик хил!»  (единственный сигнал ДО факта)
--   • пошёл каст контроля → «Сбей каст!»
--   • враг нажал тринкет → «Тринкет!»
--   • ваниш / иммун      → «Ваниш!» / «Иммун!»
--   • ворота             → «Бей <класс>!» по килл-таргету оверлея
-- Всё остальное (разбор, постматч, статистика) остаётся за мостом: оно терпит.

local AC = ArenaCoach

AC.Voice = AC.Voice or {}
local V = AC.Voice

V.enabled = true

local SFX = "Interface\\AddOns\\ArenaCoach\\sfx\\"

-- Анти-спам: свой интервал на каждый ключ. Заевшая пластинка хуже молчания
-- (урок Phase 4.10), а бюджет речи общий — клип занимает канал целиком.
local COOLDOWN = {
    kick      = 3.0,
    cc        = 3.0,
    trinket   = 5.0,
    vanish    = 5.0,
    immune    = 5.0,
    notrinket = 15.0,
    target    = 30.0,   -- общий ключ для всех target_* : один анонс на матч
    opener    = 60.0,   -- тактический колаут: строго один раз за матч
}
local DEFAULT_CD = 3.0

local lastPlayed = {}

-- ── Таблицы триггеров (по ИМЕНИ спелла) ─────────────────────────────────────
-- Имена, а не id: у хилов по 8-12 рангов, и добивать таблицу id — гонка без конца
-- (ровно на этом мост потерял мага с Arcane Intellect ранга 1459). Ограничение —
-- английский клиент; на локализованном триггеры просто не сработают, молча.

local HEAL_CASTS = {
    ["Flash Heal"] = true, ["Greater Heal"] = true, ["Heal"] = true,
    ["Prayer of Healing"] = true, ["Binding Heal"] = true,
    ["Holy Light"] = true, ["Flash of Light"] = true,
    ["Healing Wave"] = true, ["Lesser Healing Wave"] = true, ["Chain Heal"] = true,
    ["Healing Touch"] = true, ["Regrowth"] = true, ["Tranquility"] = true,
}

local CC_CASTS = {
    ["Polymorph"] = true, ["Fear"] = true, ["Cyclone"] = true,
    ["Hibernate"] = true, ["Banish"] = true, ["Seduction"] = true,
    ["Repentance"] = true, ["Howl of Terror"] = true,
}

local IMMUNE_SPELLS = {
    ["Ice Block"] = true, ["Divine Shield"] = true, ["Cloak of Shadows"] = true,
    ["Divine Protection"] = true,
}

local VANISH_SPELLS = { ["Vanish"] = true }

-- Класс килл-таргета → клип «Бей ...».
local TARGET_CLIP = {
    PRIEST = "target_priest", MAGE = "target_mage", WARLOCK = "target_warlock",
    DRUID  = "target_druid",  SHAMAN = "target_shaman", HUNTER = "target_hunter",
    ROGUE  = "target_rogue",  WARRIOR = "target_warrior", PALADIN = "target_paladin",
}

-- ── Проигрывание ────────────────────────────────────────────────────────────

local function Now()
    return GetTime()
end

-- Клип может отсутствовать (старая раздача аддона) или API — отличаться между
-- сборками клиента. Поэтому pcall + фолбэк на встроенный звук: игрок в любом
-- случае получает сигнал, а панель показывает подробности.
local function PlayClip(key)
    local ok = false
    if PlaySoundFile then
        ok = pcall(PlaySoundFile, SFX .. key .. ".ogg", "Master")
        if not ok then
            ok = pcall(PlaySoundFile, SFX .. key .. ".ogg")
        end
    end
    if not ok and PlaySound then
        pcall(PlaySound, "RaidWarning")
    end
    return ok
end

--- Проиграть клип с учётом анти-спама. `cdKey` — общий ключ интервала.
function V:Say(key, cdKey)
    if not self.enabled then return false end
    cdKey = cdKey or key
    local cd = COOLDOWN[cdKey] or DEFAULT_CD
    local t = Now()
    if lastPlayed[cdKey] and (t - lastPlayed[cdKey]) < cd then
        return false
    end
    lastPlayed[cdKey] = t
    PlayClip(key)
    return true
end

function V:ResetMatch()
    lastPlayed = {}
    self.openerPlayed = false
end

--- Анонс килл-таргета на воротах — самая ценная фраза и самая ранняя.
--- Оверлей уже знает цель из UnitClass в момент открытия ворот.
function V:AnnounceTarget(class)
    local clip = class and TARGET_CLIP[class]
    if not clip then return false end
    return self:Say(clip, "target")
end

--- Тактический колаут матчапа на воротах (Phase 4.20).
---
--- Почему это отдельный вход, а не «ещё один target_*»: клип содержит ЦЕЛЬ И ПЛАН
--- («Сап приста, бей мага! Чип, кидни»), то есть вытесняет одиночное «Бей мага!».
--- Читать то же самое в DM во время боя невозможно, а состав врага до ворот в 2.4.3
--- не узнать (arena1 в prep-фазе пуст) — значит колаут обязан звучать ровно на
--- воротах, и на него есть 8-10 секунд, пока команды сходятся.
---
--- Состав может дорисоваться позже (враг вышел из стелса). Поэтому разрешаем ОДНО
--- уточнение: если сначала прозвучало короткое «Бей X!», а потом ключ матчапа
--- совпал — колаут всё равно играем, он несёт больше. Обратно (колаут → короткое)
--- не откатываемся никогда.
function V:AnnounceOpener(key, class)
    local op = key and AC.KB_OPENERS and AC.KB_OPENERS[key]
    if not op or not op.c then
        return self:AnnounceTarget(class)
    end
    if self.openerPlayed then return false end
    if not self.enabled then return false end
    self.openerPlayed = true
    -- Цель уже произнесена внутри колаута — гасим анти-спам target'а, чтобы
    -- «Бей мага!» не прозвучало вторым эхом.
    lastPlayed["target"] = Now()
    if op.t and AC.Print then
        -- Текстом — для того, кто играет без звука, и чтобы фразу можно было
        -- перечитать: колаут звучит один раз и переспросить его нельзя.
        AC.Print("|cff40ff40Тактика:|r " .. op.t)
    end
    return self:Say(op.c, "opener")
end

-- ── Вход из CLEU (зовётся из Tracker до всех фильтров) ──────────────────────

function V:OnCombatLog(subevent, srcGUID, srcName, srcFlags, dstGUID, dstName, dstFlags,
                       spellId, spellName)
    if not self.enabled or not AC.currentSession then return end
    if not spellName then return end
    -- Реагируем только на ВРАГОВ: свои касты игрок и так видит.
    if not (AC.Overlay and AC.Overlay:IsEnemyGUID(srcGUID)) then return end

    if subevent == "SPELL_CAST_START" then
        -- Единственный сигнал ДО факта: пока идёт каст, решение ещё можно принять.
        if HEAL_CASTS[spellName] then
            self:Say("kick")
        elseif CC_CASTS[spellName] then
            self:Say("cc")
        end
        return
    end

    if subevent ~= "SPELL_CAST_SUCCESS" and subevent ~= "SPELL_AURA_APPLIED" then
        return
    end

    if AC.TRINKET_IDS and spellId and AC.TRINKET_IDS[spellId] then
        self:Say("trinket")
    elseif VANISH_SPELLS[spellName] then
        self:Say("vanish")
    elseif IMMUNE_SPELLS[spellName] then
        self:Say("immune")
    end
end

function V:Toggle(val)
    self.enabled = val
    AC.Print("Голос аддона: " .. (val and "ВКЛ" or "ВЫКЛ"))
end

--- Проверка клипов без арены: `/ac sound test`.
function V:Test()
    AC.Print("Проверка звука: должно прозвучать «Кик хил!»")
    lastPlayed = {}
    self.openerPlayed = false
    if not PlayClip("kick") then
        AC.Print("|cffff4040Клип не проигрался|r — проверь папку "
            .. "Interface/AddOns/ArenaCoach/sfx/ (должны лежать .ogg).")
    end
    local n = 0
    if AC.KB_OPENERS then
        for _ in pairs(AC.KB_OPENERS) do n = n + 1 end
    end
    AC.Print("Тактических колаутов загружено: " .. n)
end
