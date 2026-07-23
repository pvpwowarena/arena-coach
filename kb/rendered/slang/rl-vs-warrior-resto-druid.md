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

<!-- АВТО-РЕНДЕР слоя slang (prototype). Источник правды: kb/drafts/rl-vs-warrior-resto-druid.md. Сгенерировано tools/render_slang.py — не редактировать вручную. -->

## опенер

_Провенанс: новый состав **RL (рога / лок 2v2, SL/SL)**. Источники — Icy Veins (SL/SL лок/рога best-tier; вар/Resto друид — «Great durability with easy drink mechanics») и Wowhead (рога/лок: контроль одного + бёрст второго, outlast через Soul Link/Siphon Life). Per-matchup исполнение синтезировано из механик TBC 2.4.3 на sourced-каркасе; теги `community-sourced`/`needs-top-source`/`synthesized-execution`/`new-comp-rl`. Нужна верификация топ-RL (доступен выделенный WT-гайд «рога/лок 2v2» через Chrome)._

Warr/RDruid — durable-состав, живёт на мобильности и хиле друида (Icy Veins: «great durability with easy drink mechanics»). Это **длинный размен**: наш sustain (Soul Link / Siphon Life / Drain Life) против друид-хила. Побеждает тот, кто первым лишит соперника ресурса.

Килл-таргет — **друид**: пока он жив и с маной, воин перекрывается хилом. План — не дать друиду хилить и пить.

- сап друида до ворот, открываемся на него: рог чип → кидни, варлок вешает Curse of Tongues (дольше касты хила) и DoT'ы.
- CC-цепь по друиду **чередуя категории** др: рог-стан → варлок фир/Seduction (succubus) → Gouge/блайнд. Друид будет уходить в travel/лос и кайтить — рог держит Shadowstep для гэпа, варлок Death Coil на его escape.
- Воина рог обязан пил'ить с варлока: блайнд воина (снимает MS-давление), иначе Mortal Strike (−50% хил) не даст нашему drain/siphon отхиливать.

## Alternative опенер

Если открылись на воина (друид спрятался/зашёл за лос): не тунеллить — воин под друид-хилом бессмертен. Заставь друида показаться: варлок фирит/сидит на друиде Curse of Tongues, рог ищет и сап'ает. Свапайся на друида, как только он в зоне. Против их MS-окна варлок заранее держит Soul Link+healthstone.

## If enemy trinkets

Друид тринкетит кидни/фир и уходит в travel-form/Barkskin под добив — держи **второй** слой CC на его тринка: рог ваниш → сап → переоткрытие, либо блайнд сразу после его тринка'а. Воин тринкетит блайнд/фир — тогда фир варлока переводим на него в момент бёрста по друиду.

## Common mistakes

- Тунеллить воина — он перекрыт друид-хилом; выигрывает только давление на друида/его ману.
- Жечь весь CC по друиду в одной др-категории — чередуй рог-стан / лок-фир / incapacitate (Gouge/блайнд/Seduction).
- Не пил'ить воина с варлока — MS режет наш Drain Life/Siphon Life на 50%, sustain рушится.
- Идти в затяжную гонку без мана-давления: Curse of Tongues + постоянный CC на друида не дают ему пить (их «easy drink» — ломается только непрерывным контролем).

## Key cooldowns to track

- enemy: друид — циклон, Nature's Swiftness, Barkskin, тринка, innervate, travel-form; вар — Mortal Strike, Intercept, Spell Reflect, Death Wish, тринка.
- ours: рога — сап, блайнд, Gouge, кидни, ваниш, преп, Shadowstep; лок — фир, Death Coil, Seduction, Curse of Tongues, Soul Link, Siphon Life, Drain Life, тринка.
