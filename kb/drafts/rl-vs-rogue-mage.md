---
slug: rl-vs-rogue-mage
schema_version: 1
expansion: tbc
composition: rogue+warlock
vs: rogue+mage
bracket: 2v2
difficulty: hard
kill_target:
  primary: mage
  fallback: rogue
maps_notes: {}
sources:
- type: web
  url: "https://www.icy-veins.com/tbc-classic/2v2-arena-composition-rankings"
  title: "2v2 Arena Composition Rankings (Icy Veins) — SL/SL Warlock/Rogue best-tier: strong damage + multiple interrupts/CC, weakness low healing / limited Devour Magic dispel"
  retrieved: '2026-07-23'
- type: web
  url: "https://www.wowhead.com/tbc/guide/warlock-dps-pvp-arena-guide-burning-crusade-classic-wow"
  title: "Warlock DPS Arena Guide (Wowhead) — Rogue/Warlock premier pairing: keep one feared/blinded/sapped, burst the other while stun-locked"
  retrieved: '2026-07-23'
last_reviewed: '2026-07-23'
reviewer: null
confidence: draft
tags: [community-sourced, needs-top-source, synthesized-execution, new-comp-rl]
---

## Opener

_Провенанс: новый состав **RL (Rogue / Warlock 2v2, SL/SL)** — фаза только заведена. Источники: Icy Veins (тирует SL/SL Warlock/Rogue как best-tier; kit — сильный урон + много interrupts/CC, слабости «Low healing; Limited dispel from Devour Magic») и Wowhead (Rogue/Warlock — «premier pairing», план дословно: «keep one opponent feared, blinded, or sapped and burst down the other whilst its stun locked»; sustain через Soul Link / Siphon Life / Master Healthstone). Per-matchup исполнение синтезировано из механик TBC 2.4.3 на этом sourced-каркасе. Теги `community-sourced`/`needs-top-source`/`synthesized-execution`/`new-comp-rl` — нужна верификация топ-RL перед approve. Есть выделенный WT-гайд «Rogue/Warlock 2v2» (тело за client-render) — можно добрать через Chrome для per-matchup апгрейда._

RM — топ-burst состав (Icy Veins: «best burst damage and opener»). У нас **нет хилера**, поэтому чистый shatter-глобал по одному нас убивает — играем от контроля и sustain'а, а не от размена хилов.

Килл-таргет — **маг**: он даёт shatter-burst и [[ability:sheep]] по нашему варлоку (наш sustain-мотор). Убрать мага = убрать их вин-кондишн.

- Старт: [[ability:sap]] вражеского рога ещё до размена — снимаем их опенер и combo points.
- Открываемся на мага: рог [[ability:premed]] → [[ability:cheap-shot]] → [[ability:kidney-shot]]; варлок вешает [[ability:curse-of-tongues]] (режет их касты/блинк-реакцию) и льёт урон в стан-окно.
- Варлок держит вражеского рога [[ability:fear]]/[[ability:death-coil]], чтобы тот не снял давление. **Важно:** Fear, Death Coil и [[ability:howl-of-terror]] делят [[ability:dr]] fear — чередуй фир варлока с рог-станом, не жги фиры подряд.

## Alternative opener

Если RM опенят первыми (обычно shatter на варлока или на рога): [[ability:soul-link]] + [[ability:fel-armor]] уже висят — держат нас в бою. Под burst варлок каналит [[ability:drain-life]] из-за pillar'а (LoS от мага), рог мгновенно снимает стан-лок с варлока через [[ability:blind]] на вражеского рога, затем [[ability:vanish]] → [[ability:sap]] для сброса DR и переоткрытия.

Маг будет [[ability:sheep]]'ить варлока постоянно — держи trinket на первый **ключевой** sheep (под их burst), а не трать на нупокаст.

## If enemy trinkets

- Маг тринкетит [[ability:kidney-shot]]/[[ability:blind]] и уходит в [[ability:ice-block]] под добив — **не жги** бёрст в открытый iceblock, вынуди его и продолжай после выхода.
- Рог тринкетит [[ability:kidney-shot]] — тогда переводим фир-цепь ([[ability:fear]]/[[ability:death-coil]]) на мага в его [[ability:icy-veins]]-окно и добиваем, пока он без блинк-эскейпа.

## Common mistakes

- Жечь фиры подряд по одной цели — делят [[ability:dr]] и быстро уходят в иммун; чередуй фир варлока с рог-станом ([[ability:cheap-shot]]/[[ability:kidney-shot]]).
- Тунеллить мага в [[ability:ice-block]] или [[ability:nova]]+blink — теряешь темп; свяжи вражеского рога и жди чистое окно.
- Бросить варлока под непрерывный [[ability:sheep]] — без sustain-мотора RL разваливается; расходуй trinket/[[ability:devour-magic]] по ключевым CC.
- Забыть превентивный [[ability:evasion]]/[[ability:cloak-of-shadows]] рога против их рог-давления и nova-DoT'ов.

## Key cooldowns to track

- enemy: mage — [[ability:ice-block]], blink, [[ability:nova]], [[ability:sheep]], [[ability:counterspell]], [[ability:icy-veins]], trinket; rogue — [[ability:cloak-of-shadows]], [[ability:vanish]], [[ability:blind]], [[ability:kidney-shot]], trinket.
- ours: rogue — [[ability:blind]], [[ability:vanish]], [[ability:preparation]], [[ability:cloak-of-shadows]], [[ability:evasion]], [[ability:kidney-shot]]; warlock — [[ability:fear]], [[ability:death-coil]], [[ability:howl-of-terror]], [[ability:seduction]], [[ability:spell-lock]], [[ability:curse-of-tongues]], [[ability:soul-link]], [[ability:drain-life]], trinket.
