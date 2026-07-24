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

## Opener

_Провенанс: состав **RL (Rogue / Warlock 2v2, SL/SL)**. Sourced-каркас: Icy Veins по Ret/RSham — «Can remove anything but curses; Incredible offensive potential with Windfury Totem, Bloodlust», слабости «Vulnerable to curses; Very limited crowd control; Easy to kite»; наша сторона (SL/SL Warlock/Rogue) — сильный урон + много interrupts/CC. Per-matchup исполнение синтезировано из механик TBC 2.4.3. Теги `synthesized-execution`/`needs-top-source` — нужна верификация топ-RL._

Матч в нашу пользу по CC: у них «very limited crowd control» и они «easy to kite», а мы завалены контролем. Два их контр-механизма: **[[ability:tremor-totem]]** снимает наши фиры и **[[ability:purge]]** стрипает [[ability:fel-armor]]/[[ability:soul-link]]-слой. И их слабость — **curse** (шаман снимает «anything but curses», [[ability:curse-of-tongues]] на нём держится намертво).

Килл-таргет — **шаман** (стоп хилам; на нём висит несносимый CoT):

- Старт: [[ability:sap]] паладина, открываемся на шамана — рог [[ability:cheap-shot]] → [[ability:kidney-shot]], варлок [[ability:curse-of-tongues]] на шамана (замедляет хил-касты) и бёрст в стан-окно.
- **Стомпай [[ability:tremor-totem]]** (рог/пет) перед фиром — иначе фир-цепь снимается пульсом. Нет возможности снести — фирь в паузах между пульсами (~3с).
- Реаплай [[ability:fel-armor]]/баффы после [[ability:purge]]-спама; ключевые под purge не держи.

## Alternative opener

Если они открывают бёрст-окном [[ability:windfury-totem]] + [[ability:bloodlust]] по варлоку — уходи в LoS за pillar под [[ability:soul-link]], рог [[ability:blind]]'ит паладина, варлок каналит [[ability:drain-life]] и ждёт спад Lust. Их бёрст конечен, кайт бесконечен — разрывай дистанцию и возвращай CoT на шамана.

## If enemy trinkets

- Шаман тринкетит [[ability:kidney-shot]]/[[ability:fear]] и [[ability:grounding-totem]] съедает следующий одиночный [[ability:fear]]/[[ability:spell-lock]] — сбрось [[ability:grounding-totem]] пустышкой (Curse/Corruption) и следом реальный [[ability:fear]].
- Паладин тринкетит [[ability:seduction]]/стан — переведи CC-цепь на шамана и добивай его, пока паладин без trinket и Bubble.

## Common mistakes

- Фирить в [[ability:tremor-totem]] не глядя — пульс снимает; сначала снеси тотем или лови паузы.
- Держать [[ability:fel-armor]]/[[ability:soul-link]]-баффы под [[ability:purge]] — реаплай после стрипа, не давай стрелять по голому варлоку.
- Тунеллить паладина в Bubble/BoP — потеря темпа; CoT-лок шамана и урон, форсируй его OOM.
- Стоять в [[ability:windfury-totem]]+[[ability:bloodlust]]-окне — переживай его через LoS/CC, не меняйся хилами.

## Key cooldowns to track

- enemy: shaman — [[ability:tremor-totem]], [[ability:grounding-totem]], [[ability:purge]], [[ability:bloodlust]], [[ability:windfury-totem]], trinket; paladin — bubble (Divine Shield), [[ability:blessing-of-freedom]], [[ability:hammer-of-justice]], trinket.
- ours: rogue — [[ability:blind]], [[ability:vanish]], [[ability:preparation]], [[ability:cloak-of-shadows]], [[ability:kidney-shot]], [[ability:shiv]]; warlock — [[ability:fear]], [[ability:death-coil]], [[ability:howl-of-terror]], [[ability:seduction]], [[ability:spell-lock]], [[ability:curse-of-tongues]], [[ability:soul-link]], trinket.
