---
slug: rl-vs-ret-paladin-resto-shaman
schema_version: 1
expansion: tbc
composition: rogue+warlock
vs: ret-paladin+resto-shaman
bracket: 2v2
difficulty: moderate
kill_target:
  primary: shaman
  fallback: paladin
maps_notes: {}
sources:
- type: web
  url: "https://www.icy-veins.com/tbc-classic/2v2-arena-composition-rankings"
  title: "2v2 Arena Composition Rankings (Icy Veins) — Ret Paladin/Resto Shaman: «Can remove anything but curses; Incredible offensive potential with Windfury Totem, Bloodlust», weaknesses «Vulnerable to curses; Very limited crowd control; Easy to kite»"
  retrieved: '2026-07-24'
- type: web
  url: "https://www.wowhead.com/tbc/guide/warlock-dps-pvp-arena-guide-burning-crusade-classic-wow"
  title: "Warlock DPS Arena Guide (Wowhead) — Rogue/Warlock premier pairing: keep one feared/blinded/sapped, burst the other while stun-locked"
  retrieved: '2026-07-24'
last_reviewed: '2026-07-24'
reviewer: null
confidence: draft
tags: [community-sourced, needs-top-source, synthesized-execution, new-comp-rl]
---

<!-- АВТО-РЕНДЕР слоя slang (prototype). Источник правды: kb/drafts/rl-vs-ret-paladin-resto-shaman.md. Сгенерировано tools/render_slang.py — не редактировать вручную. -->

## опенер

_Провенанс: состав **RL (рога / лок 2v2, SL/SL)**. Sourced-каркас: Icy Veins по Ret/RSham — «Can remove anything but curses; Incredible offensive potential with Windfury Totem, Bloodlust», слабости «Vulnerable to curses; Very limited контроль; Easy to kite»; наша сторона (SL/SL лок/рога) — сильный урон + много interrupts/CC. Per-matchup исполнение синтезировано из механик TBC 2.4.3. Теги `synthesized-execution`/`needs-top-source` — нужна верификация топ-RL._

Матч в нашу пользу по CC: у них «very limited контроль» и они «easy to kite», а мы завалены контролем. Два их контр-механизма: **Tremor Totem** снимает наши фиры и **Purge** стрипает Fel Armor/Soul Link-слой. И их слабость — **curse** (шаман снимает «anything but curses», Curse of Tongues на нём держится намертво).

Килл-таргет — **шаман** (стоп хилам; на нём висит несносимый CoT):

- Старт: сап паладина, открываемся на шамана — рог чип → кидни, варлок Curse of Tongues на шамана (замедляет хил-касты) и бёрст в стан-окно.
- **Стомпай Tremor Totem** (рог/пет) перед фиром — иначе фир-цепь снимается пульсом. Нет возможности снести — фирь в паузах между пульсами (~3с).
- Реаплай Fel Armor/баффы после Purge-спама; ключевые под purge не держи.

## Alternative опенер

Если они открывают бёрст-окном Windfury Totem + Bloodlust по варлоку — уходи в лос за пилар под Soul Link, рог блайнд'ит паладина, варлок каналит Drain Life и ждёт спад Lust. Их бёрст конечен, кайт бесконечен — разрывай дистанцию и возвращай CoT на шамана.

## If enemy trinkets

- Шаман тринкетит кидни/фир и Grounding Totem съедает следующий одиночный фир/Spell Lock — сбрось Grounding Totem пустышкой (Curse/Corruption) и следом реальный фир.
- Паладин тринкетит Seduction/стан — переведи CC-цепь на шамана и добивай его, пока паладин без тринка и Bubble.

## Common mistakes

- Фирить в Tremor Totem не глядя — пульс снимает; сначала снеси тотем или лови паузы.
- Держать Fel Armor/Soul Link-баффы под Purge — реаплай после стрипа, не давай стрелять по голому варлоку.
- Тунеллить паладина в Bubble/BoP — потеря темпа; CoT-лок шамана и урон, форсируй его оом.
- Стоять в Windfury Totem+Bloodlust-окне — переживай его через лос/CC, не меняйся хилами.

## Key cooldowns to track

- enemy: шам — Tremor Totem, Grounding Totem, Purge, Bloodlust, Windfury Totem, тринка; пал — bubble (Divine Shield), Blessing of Freedom, подж, тринка.
- ours: рога — блайнд, ваниш, преп, Cloak of Shadows, кидни, Shiv; лок — фир, Death Coil, Howl of Terror, Seduction, Spell Lock, Curse of Tongues, Soul Link, тринка.
