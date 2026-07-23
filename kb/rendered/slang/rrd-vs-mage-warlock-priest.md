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

<!-- АВТО-РЕНДЕР слоя slang (prototype). Источник правды: kb/drafts/rrd-vs-mage-warlock-priest.md. Сгенерировано tools/render_slang.py — не редактировать вручную. -->

## опенер

_Провенанс: новый состав **RRD (рога / рога / Resto друид, 3v3)**, off-meta (не тирится в 3v3 tier-листах). Каркас: OwnedCore «Double рога Guide» (TBC 2.x — движок двойного рога, перманентные interrupt'ы по кастерам), Icy Veins (рога/друид синергия), Skill Capped 3v3 (MLP = S). Координация друида синтезирована; теги `community-sourced`/`needs-top-source`/`synthesized-execution`/`off-meta-comp`/`new-comp-rrd`. Нужна верификация топ-игрока._

MLP — три кастера, ни одного меле. Для двойного рога это **играбельнее большинства S-составов**: постоянные interrupt'ы (gouge/kidney/kick) душат касты, у них нет своего меле-пила. Но у MLP гора CC (шип, фир, Psychic Scream) — нельзя дать им свободно расставить контроль.

Килл-таргет — **маг** (сквиши, кладём под перманентный interrupt); варлок — вторичный (танковый SL).

- Стелс-сетап: сап варлока (убрать фир-давление на старте), оба рога на мага: чип → кидни, между станами — kick/Gouge по кастам. Друид циклон приста, Entangling Roots варлока.
- Держи мага в перманентном lockout'е — один рог всегда «на прерывании» его каста, второй бёрстит.
- Друид критичен против их spread-фиров: Barkskin под burst, разбрасывай HoT (Rejuvenation/Lifebloom) на обоих рогов, Travel Form-кайт между пилларами от их CC.

## Alternative опенер

Если они опенят фир-цепью + шип по рогам: Cloak of Shadows снимает поли/фир с рога, второй рог блайнд их варлока (обрыв фир-мотора). Друид Nature's Swiftness-хил на застанленного/зафиренного. Затем возвращаемся на мага всей связкой.

## If enemy trinkets

Маг тринкетит стан → блок/блинк: не добивай в iceblock. Варлок тринкетит стан → healthstone/фир: держи сап/блайнд (20с др) вторым слоем. Прист тринкетит циклон → Pain Suppression: вынуди дефы, добей после.

## Common mistakes

- Дать магу свободно кастовать шип/burst — один рог ВСЕГДА на его прерывании (kick/Gouge/кидни).
- Слить оба блайнд в одном окне — держи второй на трин­кет (20с др).
- Бросить друида без Barkskin/пила под их фир+burst spread — он твой единственный sustain.
- Не разменять Cloak of Shadows рога на ключевой шип/фир.

## Key cooldowns to track

- enemy: маг — блок, блинк, нова, шип, кс, Icy Veins, тринка; лок — фир, Death Coil, Spell Lock, Soul Link, тринка; прист — Psychic Scream, Pain Suppression, Mana Burn, тринка.
- ours: rogues — сап, блайнд, чип, кидни, Gouge, Cloak of Shadows, ваниш, преп; друид — циклон, Entangling Roots, Barkskin, Nature's Swiftness, Rejuvenation, Lifebloom, Innervate, тринка.
