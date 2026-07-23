---
slug: rrd-vs-mage-warlock-priest
schema_version: 1
expansion: tbc
composition: rogue+rogue+resto-druid
vs: mage+warlock+priest
bracket: 3v3
difficulty: hard
kill_target:
  primary: mage
  fallback: warlock
maps_notes: {}
sources:
- type: web
  url: "https://www.ownedcore.com/forums/world-of-warcraft/world-of-warcraft-guides/111880-arena-double-rogue-guide.html"
  title: "Double Rogue Arena Guide (OwnedCore, TBC 2.x) — permanent interrupts on casters, stunlock Cheap->Kidney, Sap/Blind 20s DR chain CC"
  retrieved: '2026-07-23'
- type: web
  url: "https://www.skill-capped.com/wowarticles/tbc/tier-lists/tbc-3v3/"
  title: "TBC 3v3 Tier List (Skill Capped) — MLP = S-tier all-caster cleave (double-rogue/RRD not tiered)"
  retrieved: '2026-07-23'
- type: web
  url: "https://www.icy-veins.com/tbc-classic/3v3-arena-composition-rankings"
  title: "3v3 Arena Composition Rankings (Icy Veins) — Rogue/Resto Druid double stealth + CC chains"
  retrieved: '2026-07-23'
last_reviewed: '2026-07-23'
reviewer: null
confidence: draft
tags: [community-sourced, needs-top-source, synthesized-execution, off-meta-comp, new-comp-rrd]
---

## Opener

_Провенанс: новый состав **RRD (Rogue / Rogue / Resto Druid, 3v3)**, off-meta (не тирится в 3v3 tier-листах). Каркас: OwnedCore «Double Rogue Guide» (TBC 2.x — движок двойного рога, перманентные interrupt'ы по кастерам), Icy Veins (Rogue/Druid синергия), Skill Capped 3v3 (MLP = S). Координация друида синтезирована; теги `community-sourced`/`needs-top-source`/`synthesized-execution`/`off-meta-comp`/`new-comp-rrd`. Нужна верификация топ-игрока._

MLP — три кастера, ни одного меле. Для двойного рога это **играбельнее большинства S-составов**: постоянные interrupt'ы (gouge/kidney/kick) душат касты, у них нет своего меле-пила. Но у MLP гора CC ([[ability:sheep]], [[ability:fear]], Psychic Scream) — нельзя дать им свободно расставить контроль.

Килл-таргет — **маг** (сквиши, кладём под перманентный interrupt); варлок — вторичный (танковый SL).

- Стелс-сетап: [[ability:sap]] варлока (убрать fear-давление на старте), оба рога на мага: [[ability:cheap-shot]] → [[ability:kidney-shot]], между станами — kick/[[ability:gouge]] по кастам. Друид [[ability:cyclone]] приста, [[ability:entangling-roots]] варлока.
- Держи мага в перманентном lockout'е — один рог всегда «на прерывании» его каста, второй бёрстит.
- Друид критичен против их spread-фиров: [[ability:barkskin]] под burst, разбрасывай HoT ([[ability:rejuvenation]]/[[ability:lifebloom]]) на обоих рогов, [[ability:travel-form]]-кайт между пилларами от их CC.

## Alternative opener

Если они опенят fear-цепью + [[ability:sheep]] по рогам: [[ability:cloak-of-shadows]] снимает поли/фир с рога, второй рог [[ability:blind]] их варлока (обрыв fear-мотора). Друид [[ability:natures-swiftness]]-хил на застанленного/зафиренного. Затем возвращаемся на мага всей связкой.

## If enemy trinkets

Маг тринкетит стан → [[ability:ice-block]]/blink: не добивай в iceblock. Варлок тринкетит стан → healthstone/[[ability:fear]]: держи Sap/Blind (20с DR) вторым слоем. Прист тринкетит [[ability:cyclone]] → [[ability:pain-suppression]]: вынуди дефы, добей после.

## Common mistakes

- Дать магу свободно кастовать [[ability:sheep]]/burst — один рог ВСЕГДА на его прерывании (kick/[[ability:gouge]]/[[ability:kidney-shot]]).
- Слить оба [[ability:blind]] в одном окне — держи второй на трин­кет (20с DR).
- Бросить друида без [[ability:barkskin]]/пила под их fear+burst spread — он твой единственный sustain.
- Не разменять [[ability:cloak-of-shadows]] рога на ключевой [[ability:sheep]]/[[ability:fear]].

## Key cooldowns to track

- enemy: mage — [[ability:ice-block]], blink, [[ability:nova]], [[ability:sheep]], [[ability:counterspell]], [[ability:icy-veins]], trinket; warlock — [[ability:fear]], [[ability:death-coil]], [[ability:spell-lock]], [[ability:soul-link]], trinket; priest — Psychic Scream, [[ability:pain-suppression]], [[ability:mana-burn]], trinket.
- ours: rogues — [[ability:sap]], [[ability:blind]], [[ability:cheap-shot]], [[ability:kidney-shot]], [[ability:gouge]], [[ability:cloak-of-shadows]], [[ability:vanish]], [[ability:preparation]]; druid — [[ability:cyclone]], [[ability:entangling-roots]], [[ability:barkskin]], [[ability:natures-swiftness]], [[ability:rejuvenation]], [[ability:lifebloom]], [[ability:innervate]], trinket.
