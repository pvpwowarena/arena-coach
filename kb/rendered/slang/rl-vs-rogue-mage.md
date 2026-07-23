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

<!-- АВТО-РЕНДЕР слоя slang (prototype). Источник правды: kb/drafts/rl-vs-rogue-mage.md. Сгенерировано tools/render_slang.py — не редактировать вручную. -->

## опенер

_Провенанс: новый состав **RL (рога / лок 2v2, SL/SL)** — фаза только заведена. Источники: Icy Veins (тирует SL/SL лок/рога как best-tier; kit — сильный урон + много interrupts/CC, слабости «Low healing; Limited dispel from Devour Magic») и Wowhead (рога/лок — «premier pairing», план дословно: «keep one opponent feared, blinded, or sapped and burst down the other whilst its stun locked»; sustain через Soul Link / Siphon Life / Master Healthstone). Per-matchup исполнение синтезировано из механик TBC 2.4.3 на этом sourced-каркасе. Теги `community-sourced`/`needs-top-source`/`synthesized-execution`/`new-comp-rl` — нужна верификация топ-RL перед approve. Есть выделенный WT-гайд «рога/лок 2v2» (тело за client-render) — можно добрать через Chrome для per-matchup апгрейда._

RM — топ-burst состав (Icy Veins: «best burst damage and опенер»). У нас **нет хилера**, поэтому чистый шаттер-глобал по одному нас убивает — играем от контроля и sustain'а, а не от размена хилов.

Килл-таргет — **маг**: он даёт шаттер-burst и шип по нашему варлоку (наш sustain-мотор). Убрать мага = убрать их вин-кондишн.

- Старт: сап вражеского рога ещё до размена — снимаем их опенер и очки.
- Открываемся на мага: рог премед → чип → кидни; варлок вешает Curse of Tongues (режет их касты/блинк-реакцию) и льёт урон в стан-окно.
- Варлок держит вражеского рога фир/Death Coil, чтобы тот не снял давление. **Важно:** фир, Death Coil и Howl of Terror делят др фир — чередуй фир варлока с рог-станом, не жги фиры подряд.

## Alternative опенер

Если RM опенят первыми (обычно шаттер на варлока или на рога): Soul Link + Fel Armor уже висят — держат нас в бою. Под burst варлок каналит Drain Life из-за пилар'а (лос от мага), рог мгновенно снимает стан-лок с варлока через блайнд на вражеского рога, затем ваниш → сап для сброса др и переоткрытия.

Маг будет шип'ить варлока постоянно — держи тринка на первый **ключевой** sheep (под их burst), а не трать на нупокаст.

## If enemy trinkets

- Маг тринкетит кидни/блайнд и уходит в блок под добив — **не жги** бёрст в открытый iceblock, вынуди его и продолжай после выхода.
- Рог тринкетит кидни — тогда переводим фир-цепь (фир/Death Coil) на мага в его Icy Veins-окно и добиваем, пока он без блинк-эскейпа.

## Common mistakes

- Жечь фиры подряд по одной цели — делят др и быстро уходят в иммун; чередуй фир варлока с рог-станом (чип/кидни).
- Тунеллить мага в блок или нова+блинк — теряешь темп; свяжи вражеского рога и жди чистое окно.
- Бросить варлока под непрерывный шип — без sustain-мотора RL разваливается; расходуй тринка/Devour Magic по ключевым CC.
- Забыть превентивный Evasion/Cloak of Shadows рога против их рог-давления и nova-DoT'ов.

## Key cooldowns to track

- enemy: маг — блок, блинк, нова, шип, кс, Icy Veins, тринка; рога — Cloak of Shadows, ваниш, блайнд, кидни, тринка.
- ours: рога — блайнд, ваниш, преп, Cloak of Shadows, Evasion, кидни; лок — фир, Death Coil, Howl of Terror, Seduction, Spell Lock, Curse of Tongues, Soul Link, Drain Life, тринка.
