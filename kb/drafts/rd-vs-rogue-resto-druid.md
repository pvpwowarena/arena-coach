---
slug: rd-vs-rogue-resto-druid
schema_version: 1
expansion: tbc
composition: rogue+resto-druid
vs: rogue+resto-druid
bracket: 2v2
difficulty: mirror
kill_target:
  primary: druid
  fallback: rogue
maps_notes: {}
sources:
- type: web
  url: "https://www.icy-veins.com/tbc-classic/restoration-druid-pvp-guide"
  title: "Restoration Druid PvP Guide (Icy Veins) — Druid+Rogue top comp; Cyclone «immune to damage and healing», Blind/stuns not sharing DRs; Nature's Grasp self-peel; mirror = opener + CC-chain race"
  retrieved: '2026-07-26'
- type: web
  url: "https://www.icy-veins.com/tbc-classic/2v2-arena-composition-rankings"
  title: "2v2 Arena Composition Rankings (Icy Veins) — Rogue/Resto Druid: «Double stealth ensures strong openers, and crowd control chains are powerful due to stuns, Cyclone, and Blind not sharing DRs»"
  retrieved: '2026-07-26'
last_reviewed: '2026-07-26'
reviewer: null
confidence: draft
tags: [community-sourced, needs-top-source, synthesized-execution, new-comp-rd, mirror]
---

## Opener

_Провенанс: новый состав **RD (Rogue / Resto Druid 2v2)** — зеркало. Источники — Icy Veins Resto Druid guide + 2v2 rankings (RD: «double stealth ensures strong openers; CC chains powerful — stuns, Cyclone, Blind not sharing DRs»). Исполнение синтезировано из механик TBC 2.4.3; теги `community-sourced`/`needs-top-source`/`synthesized-execution`/`new-comp-rd`/`mirror`. Нужна верификация топ-RD._

Зеркало: всё решает **опенер и первая CC-цепь**. Кто первым сложит stun→[[ability:cyclone]]→[[ability:blind]] (не шарят DR — источник) на вражеском друиде, тот и берёт темп. Обе стороны на double-stealth, так что бой стартует с размена стелсов.

Килл-таргет — **их друид** (снять хил); fallback — их рог, когда друид ушёл в NS/travel.

- [[ability:sap]] на их **рога**, не на друида (сапнёшь друида — их рог свободно опенит нашего). Ищем друг друга.
- Открываемся на их друида: [[ability:cheap-shot]] → [[ability:kidney-shot]], wound-poison; наш друид [[ability:cyclone]] их рога (лишаем его опенера на нашем друиде) и [[ability:entangling-roots]] на пил.
- Защита нашего друида: [[ability:natures-grasp]]/[[ability:entangling-roots]] на их рога, [[ability:barkskin]] под их [[ability:kidney-shot]], NS-[[ability:cyclone]] их рога; [[ability:faerie-fire]] на его restealth.

## Alternative opener

Их рог заопенил первым по нашему друиду: [[ability:barkskin]] + NS-инстант-хил, тринкет под их [[ability:kidney-shot]]; наш рог [[ability:blind]] их рога / [[ability:cloak-of-shadows]] под добив, [[ability:cyclone]] их друида чтобы прервать их kill-сетап. Симметрично — не паникуй свапами, верни контроль.

## If enemy trinkets

Всё симметрично: первым [[ability:kidney-shot]] выбей тринкет их друида, **второй** цепью (сохранённой) убивай. Наш тринкет держи под их NS-[[ability:cyclone]] или [[ability:kidney-shot]] по нашему друиду. Их рог тринкетит → [[ability:vanish]]-restealth — [[ability:faerie-fire]] + [[ability:evasion]] превентивно.

## Common mistakes

- [[ability:sap]] их друида вместо рога — освобождаешь их опенер по нашему хилеру.
- Слить контроль в одной [[ability:dr]] — вся сила зеркала в неперекрывающихся stun/[[ability:cyclone]]/[[ability:blind]].
- Тунеллить их рога — он под друид-хилом не падает; убивай друида.
- Профукать [[ability:faerie-fire]] — их рог restealth'ит и переоткрывает kill-сетап на нашем друиде.

## Key cooldowns to track

- enemy: rogue — [[ability:cheap-shot]], [[ability:kidney-shot]], [[ability:blind]], [[ability:vanish]], [[ability:cloak-of-shadows]], [[ability:preparation]], trinket; druid — [[ability:cyclone]], [[ability:natures-swiftness]], [[ability:barkskin]], [[ability:innervate]], [[ability:travel-form]], trinket.
- ours: rogue — [[ability:sap]], [[ability:cheap-shot]], [[ability:kidney-shot]], [[ability:blind]], [[ability:gouge]], [[ability:vanish]], [[ability:evasion]], [[ability:cloak-of-shadows]], [[ability:shadowstep]], [[ability:preparation]]; druid — [[ability:cyclone]], [[ability:natures-swiftness]], [[ability:barkskin]], [[ability:entangling-roots]], [[ability:natures-grasp]], [[ability:faerie-fire]], [[ability:innervate]], trinket.
