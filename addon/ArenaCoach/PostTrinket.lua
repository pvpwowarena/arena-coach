-- ArenaCoach/PostTrinket.lua
-- СГЕНЕРИРОВАНО tools/gen_addon_posttrinket.py — не редактировать руками.
-- Источник: kb/drafts + kb/matchups, секции «If enemy trinkets».
--
-- Ключ: "<ключ матчапа как в KillTargets.lua>|<КЛАСС тринкетнувшего>".
-- Значение: { c = "клип без .ogg", t = "текст (панель и чат)" }.
-- Нет ключа → молчание: «Нет в KB → нет совета».

local AC = ArenaCoach

AC.KB_POST_TRINKET = {
    ["2v2|mage+rogue|druid+rogue|ROGUE"] = { c = "pt_blind", t = "Блайнд его!" },
    ["2v2|mage+rogue|druid+warlock|DRUID"] = { c = "pt_blind_vanish", t = "Блайнд, ваниш!" },
    ["2v2|mage+rogue|druid+warrior|DRUID"] = { c = "pt_blind_vanish", t = "Блайнд, ваниш!" },
    ["2v2|mage+rogue|hunter+priest|HUNTER"] = { c = "pt_wait_dr", t = "Пережди, рестан!" },
    ["2v2|mage+rogue|mage+priest|MAGE"] = { c = "pt_blind_mage", t = "Блайнд мага!" },
    ["2v2|mage+rogue|mage+rogue|ROGUE"] = { c = "pt_trade_stun", t = "Тринкеть его стан!" },
    ["2v2|mage+rogue|paladin+shaman|SHAMAN"] = { c = "pt_vanish_garrote", t = "Ваниш, гарота!" },
    ["2v2|mage+rogue|paladin+warrior|PALADIN"] = { c = "pt_full_kidney", t = "Полный кидни!" },
    ["2v2|mage+rogue|priest+rogue|ROGUE"] = { c = "pt_vanish_reopen", t = "Ваниш, реоткрытие!" },
    ["2v2|mage+rogue|priest+warlock|PRIEST"] = { c = "pt_blind_priest", t = "Блайнд приста!" },
    ["2v2|mage+rogue|priest+warrior|PRIEST"] = { c = "pt_full_kidney", t = "Полный кидни!" },
    ["2v2|mage+rogue|priest+warrior|WARRIOR"] = { c = "pt_blind_war", t = "Блайнд вара!" },
    ["2v2|mage+rogue|rogue+warlock|WARLOCK"] = { c = "pt_cloak_coil", t = "Клоак — коил!" },
}

AC.KB_POST_TRINKET_COUNT = 13
