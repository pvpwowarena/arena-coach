---
slug: rl-vs-warrior-resto-druid
schema_version: 1
expansion: tbc
composition: rogue+warlock
vs: warrior+resto-druid
bracket: 2v2
difficulty: hard
kill_target:
  primary: druid
  fallback: warrior
maps_notes: {}
sources:
- type: web
  url: "https://www.icy-veins.com/tbc-classic/2v2-arena-composition-rankings"
  title: "2v2 Arena Composition Rankings (Icy Veins) — SL/SL Warlock/Rogue best-tier; Arms Warrior/Resto Druid durable comp with easy drink mechanics"
  retrieved: '2026-07-23'
- type: web
  url: "https://www.wowhead.com/tbc/guide/warlock-dps-pvp-arena-guide-burning-crusade-classic-wow"
  title: "Warlock DPS Arena Guide (Wowhead) — Rogue/Warlock plan: control one, burst the other, outlast via Soul Link / Siphon Life"
  retrieved: '2026-07-23'
last_reviewed: '2026-07-23'
reviewer: null
confidence: draft
tags: [community-sourced, needs-top-source, synthesized-execution, new-comp-rl]
---

## Opener

_Провенанс: новый состав **RL (Rogue / Warlock 2v2, SL/SL)**. Источники — Icy Veins (SL/SL Warlock/Rogue best-tier; Warrior/Resto Druid — «Great durability with easy drink mechanics») и Wowhead (Rogue/Warlock: контроль одного + бёрст второго, outlast через Soul Link/Siphon Life). Per-matchup исполнение синтезировано из механик TBC 2.4.3 на sourced-каркасе; теги `community-sourced`/`needs-top-source`/`synthesized-execution`/`new-comp-rl`. Нужна верификация топ-RL (доступен выделенный WT-гайд «Rogue/Warlock 2v2» через Chrome)._

Warr/RDruid — durable-состав, живёт на мобильности и хиле друида (Icy Veins: «great durability with easy drink mechanics»). Это **длинный размен**: наш sustain (Soul Link / [[ability:siphon-life]] / [[ability:drain-life]]) против друид-хила. Побеждает тот, кто первым лишит соперника ресурса.

Килл-таргет — **друид**: пока он жив и с маной, воин перекрывается хилом. План — не дать друиду хилить и пить.

- [[ability:sap]] друида до ворот, открываемся на него: рог [[ability:cheap-shot]] → [[ability:kidney-shot]], варлок вешает [[ability:curse-of-tongues]] (дольше касты хила) и DoT'ы.
- CC-цепь по друиду **чередуя категории** [[ability:dr]]: рог-стан → варлок [[ability:fear]]/[[ability:seduction]] (succubus) → [[ability:gouge]]/[[ability:blind]]. Друид будет уходить в travel/LoS и кайтить — рог держит [[ability:shadowstep]] для гэпа, варлок [[ability:death-coil]] на его escape.
- Воина рог обязан peel'ить с варлока: [[ability:blind]] воина (снимает MS-давление), иначе Mortal Strike (−50% хил) не даст нашему drain/siphon отхиливать.

## Alternative opener

Если открылись на воина (друид спрятался/зашёл за LoS): не тунеллить — воин под друид-хилом бессмертен. Заставь друида показаться: варлок фирит/сидит на друиде [[ability:curse-of-tongues]], рог ищет и sap'ает. Свапайся на друида, как только он в зоне. Против их MS-окна варлок заранее держит [[ability:soul-link]]+healthstone.

## If enemy trinkets

Друид тринкетит [[ability:kidney-shot]]/[[ability:fear]] и уходит в travel-form/Barkskin под добив — держи **второй** слой CC на его trinket: рог [[ability:vanish]] → [[ability:sap]] → переоткрытие, либо [[ability:blind]] сразу после его trinket'а. Воин тринкетит [[ability:blind]]/[[ability:fear]] — тогда фир варлока переводим на него в момент бёрста по друиду.

## Common mistakes

- Тунеллить воина — он перекрыт друид-хилом; выигрывает только давление на друида/его ману.
- Жечь весь CC по друиду в одной [[ability:dr]]-категории — чередуй рог-стан / warlock-fear / incapacitate ([[ability:gouge]]/[[ability:blind]]/[[ability:seduction]]).
- Не peel'ить воина с варлока — MS режет наш [[ability:drain-life]]/[[ability:siphon-life]] на 50%, sustain рушится.
- Идти в затяжную гонку без мана-давления: [[ability:curse-of-tongues]] + постоянный CC на друида не дают ему пить (их «easy drink» — ломается только непрерывным контролем).

## Key cooldowns to track

- enemy: druid — [[ability:cyclone]], Nature's Swiftness, Barkskin, trinket, innervate, travel-form; warrior — Mortal Strike, Intercept, Spell Reflect, Death Wish, trinket.
- ours: rogue — [[ability:sap]], [[ability:blind]], [[ability:gouge]], [[ability:kidney-shot]], [[ability:vanish]], [[ability:preparation]], [[ability:shadowstep]]; warlock — [[ability:fear]], [[ability:death-coil]], [[ability:seduction]], [[ability:curse-of-tongues]], [[ability:soul-link]], [[ability:siphon-life]], [[ability:drain-life]], trinket.
