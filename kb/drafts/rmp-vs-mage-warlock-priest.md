---
slug: rmp-vs-mage-warlock-priest
schema_version: 1
expansion: tbc
composition: rogue+mage+priest
vs: mage+warlock+priest
bracket: 3v3
difficulty: moderate
kill_target:
  primary: mage
  fallback: warlock
maps_notes: {}
sources:
- type: web
  url: https://www.warcrafttavern.com/tbc/guides/3v3-arena-tier-list/
  title: Best 3v3 Arena Comps (Warcraft Tavern) — MLP all-in casters, слаб vs melee/interrupt
  retrieved: '2026-06-23'
- type: web
  url: https://www.skill-capped.com/wowarticles/tbc/tier-lists/tbc-3v3/
  title: TBC Classic 3v3 Tier List (Skill Capped, Anniversary 2.5.5) — MLP = S-tier
  retrieved: '2026-06-23'
last_reviewed: '2026-06-23'
reviewer: null
confidence: draft
tags: [community-sourced, needs-top-source, synthesized-execution, bracket-3v3-new]
---

## Strategy

_Провенанс: 3v3-драфт по принятому паттерну (как rmp-vs-WLD). Источники — WT/Skill Capped 3v3 tier-lists (Anniversary 2.5.5): **MLP = S-tier**, но «all-in casters, struggles against heavy melee pressure or interrupt-heavy teams». RMP-сторона синтезирована из механик TBC 2.4.3. Теги — нужна верификация топ-RMP перед approve._

Ключ из источника: MLP — тройной каст без рога, и его **документированная слабость — мили-давление и interrupt-heavy команды**. RMP — ровно это (рог-мили + [[ability:counterspell]] мага + kick). Поэтому матчап играем агрессивно: рог приклеивается к их **магу** (kill target — сквишовее, и без рога у MLP меньше пилов), маг держит [[ability:counterspell]] на их каст-школы, прийст dispel'ит и помогает CC.

Сетап: [[ability:sap]] их прийста/варлока → [[ability:sheep]] второго каста → бурст мага [[ability:premed]] → [[ability:cheap-shot]] → [[ability:kidney-shot]] + shatter ([[ability:nova]] → ice lance). Их felhunter (Spell Lock/Devour) и наш CS — interrupt-война; не давай их прийсту свободно dispel'ить наш [[ability:sheep]].

## Opener

Стелс-открытие на их мага. Рог не даёт магу свободно кастовать ([[ability:cheap-shot]]/[[ability:kidney-shot]]/[[ability:gouge]]), наш маг блэнкетит [[ability:counterspell]] их прийста/варлока. Прийст готов [[ability:fear]] на их варлока, чтобы оборвать fear-обмен.

## If enemy trinkets

Их маг тринкетит [[ability:kidney-shot]] → [[ability:ice-block]] под добив, выжидай (у MLP нет рога, чтобы peel'ить — давление держится). Варлок тринкетит → fear/[[ability:death-coil]]; прийст [[ability:pain-suppression]] под их burst. Не blanket-dispel в UA (silence).

## Common mistakes

- Уйти в каст-размен на их условиях вместо мили-давления (источник: MLP силён против пассивных, слаб против interrupt/melee).
- Дать их магу свободные касты — рог обязан сидеть на нём.
- Бурстить мага под Spell Lock felhunter'а.
- Снять UA и поймать silence.

## Key cooldowns to track

- enemy: mage — [[ability:ice-block]], blink, [[ability:counterspell]], [[ability:sheep]], [[ability:nova]], trinket; warlock — fear, [[ability:death-coil]], felhunter Spell Lock/Devour, healthstone, trinket; priest — Psychic Scream ([[ability:fear]]), Mass Dispel, [[ability:pain-suppression]], trinket.
- ours: [[ability:sap]], [[ability:sheep]], [[ability:counterspell]], [[ability:nova]], [[ability:kidney-shot]], [[ability:blind]], [[ability:vanish]], [[ability:ice-block]]; priest — Mass Dispel, [[ability:pain-suppression]], [[ability:fear]], trinket.
