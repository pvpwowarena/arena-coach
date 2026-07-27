---
slug: rd-vs-warrior-resto-druid
schema_version: 1
expansion: tbc
composition: rogue+resto-druid
vs: warrior+resto-druid
bracket: 2v2
difficulty: moderate
kill_target:
  primary: druid
  fallback: warrior
maps_notes: {}
sources:
- type: web
  url: "https://www.icy-veins.com/tbc-classic/restoration-druid-pvp-guide"
  title: "Restoration Druid PvP Guide (Icy Veins) — Druid+Rogue top comp; Cyclone lockout, Lifebloom mana-efficient dispel-protected heal, Abolish Poison counters enemy rogue poison; Nature's Grasp/Entangling Roots peel"
  retrieved: '2026-07-26'
- type: web
  url: "https://www.icy-veins.com/tbc-classic/2v2-arena-composition-rankings"
  title: "2v2 Arena Composition Rankings (Icy Veins) — Warrior/Resto Druid: «Great durability; Easy to drink for Druid»"
  retrieved: '2026-07-26'
last_reviewed: '2026-07-26'
reviewer: null
confidence: draft
tags: [community-sourced, needs-top-source, synthesized-execution, new-comp-rd]
---

<!-- АВТО-РЕНДЕР слоя slang (prototype). Источник правды: kb/drafts/rd-vs-warrior-resto-druid.md. Сгенерировано tools/render_slang.py — не редактировать вручную. -->

## опенер

_Провенанс: новый состав **RD (рога / Resto друид 2v2)**. Источники — Icy Veins Resto друид guide (друид+рога — top-состав; наш контроль циклон + Entangling Roots/Nature's Grasp пил) и Icy Veins 2v2 rankings (Warr/RDruid — «great durability; easy to drink for друид»). Исполнение синтезировано из механик TBC 2.4.3; теги `community-sourced`/`needs-top-source`/`synthesized-execution`/`new-comp-rd`. Нужна верификация топ-RD._

Warr/RDruid — durable-состав на мобильности и хиле друида (источник: «great durability, easy to drink»). Это **длинный размен хилеров**: у нас лучше kill-setup на их друида (рог-контроль + циклон без общего др), у них нет жёсткого свапа. Побеждаем kill-сетапом на друида + wound-давлением, не даём ему пить.

Килл-таргет — **их друид**: пока он с маной, воин перекрыт хилом.

- Рог сап воина; ищем друида в стелсе. Нашли — открываемся на друида: чип → Hemorrhage → Gouge → кидни, держим wound-poison (−50% хил их друиду) и crippling (Shiv) чтобы он не кайтил.
- В окно кидни наш друид циклон их друида (продлить лок) ИЛИ Entangling Roots воина — снять Faerie Fire-открытого воина с нашего хилера.
- Воина рог обязан пилить с нашего друида: блайнд воина под его Mortal Strike-окно (MS режет наш хил), затем снова фокус их друида.

## Alternative опенер

Их друид спрятался/кайтит за лос — не тунелль воина (он под хилом бессмертен). Заставь друида показаться: наш друид Faerie Fire на подозрение + Entangling Roots воина, рог ищет и сап/чип. Против MS-окна воина — Barkskin заранее, блайнд воина.

## If enemy trinkets

Их друид тринкетит кидни → NS-инстант-хил / Travel Form / Barkskin под добив — держи **второй** слой CC (блайнд/Gouge/циклон) под его тринкет, не добивай в открытый NS. Воин тринкетит кидни/Entangling Roots — тогда наш циклон переводим на воина в момент бёрста по их друиду.

## Common mistakes

- Тунеллить воина — он перекрыт друид-хилом; выигрывает только давление на их друида и его ману.
- Жечь весь CC в одной др — чередуй рог-стан / циклон / блайнд (не шарят др).
- Забыть wound-poison на их друиде — без −50% к хилу он пересиживает наш бёрст.
- Не пилить воина блайнд — Mortal Strike режет наш друид-хил, sustain рушится.

## Key cooldowns to track

- enemy: друид — циклон, Nature's Swiftness, Barkskin, Innervate, Travel Form, тринка; вар — Mortal Strike, Intercept, Hamstring, Spell Reflect, Death Wish, тринка.
- ours: рога — сап, блайнд, Gouge, кидни, Shiv, ваниш, преп, Shadowstep; друид — циклон, Nature's Swiftness, Barkskin, Entangling Roots, Nature's Grasp, Faerie Fire, Innervate, тринка.
