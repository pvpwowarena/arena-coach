---
slug: rmp-vs-rogue-warlock-druid
schema_version: 1
expansion: tbc
composition: rogue+mage+priest
vs: rogue+warlock+druid
bracket: 3v3
difficulty: very-hard
kill_target:
  primary: warlock
  fallback: rogue
maps_notes: {}
sources:
- type: web
  url: https://www.warcrafttavern.com/tbc/guides/3v3-arena-tier-list/
  title: Best 3v3 Arena Comps (Warcraft Tavern) — RLD описание (attrition, healer triage)
  retrieved: '2026-06-23'
- type: web
  url: https://www.skill-capped.com/wowarticles/tbc/tier-lists/tbc-3v3/
  title: TBC Classic 3v3 Tier List (Skill Capped, Anniversary 2.5.5) — RLD = A-tier
  retrieved: '2026-06-23'
last_reviewed: '2026-06-23'
reviewer: null
confidence: draft
tags: [community-sourced, needs-top-source, synthesized-execution, bracket-3v3-new]
---

## Strategy

_Провенанс: 3v3-драфт по принятому паттерну (как rmp-vs-WLD). Источники — Warcraft Tavern и Skill Capped (Anniversary 2.5.5): **RLD** = S/A-tier attrition-состав. RMP-сторона синтезирована из механик TBC 2.4.3. Теги `community-sourced`/`needs-top-source`/`synthesized-execution` — нужна верификация топ-RMP перед approve._

RLD (источник, WT): «skips the CC of a Frost Mage in favor of constant pressure and attrition of a Warlock — with enough time the healer enters triage, и одна CC-цепочка каскадит в win». То есть **resto druid** кайтит (travel/HoT) + [[ability:cyclone]] протектит kill-attempts, **affliction warlock** размазывает DoT'ы и фирит, **rogue** контролит. Их сила — время и spread-damage.

Наш план (синтез): **не давать игре затянуться** — нужен чистый CC-сетап и быстрый kill, пока druid связан. Kill target — **warlock** (источник DoT-аттриции и fear'а; druid почти некиллабелен из-за кайта/цикла). Сетап: [[ability:sap]] druid → маг [[ability:sheep]]/[[ability:counterspell]] на его heal/cyclone-каст → бурст warlock'а ([[ability:cheap-shot]] → [[ability:kidney-shot]] + shatter [[ability:nova]]→ice lance) в окно, когда druid под CC и не может оборвать добив [[ability:cyclone]]. Прийст dispel'ит DoT'ы, [[ability:pain-suppression]] под их fear+burst.

## Opener

Стелс-открытие: найти druid'а или warlock'а. [[ability:sap]] одного, [[ability:sheep]] второго, бурст warlock. Перед kill-окном **свяжи druid'а** ([[ability:sheep]]/[[ability:counterspell]] на его cast) — свободный druid циклонит наш добив. Осторожно с felhunter (Spell Lock/Devour снимает [[ability:sheep]]/[[ability:nova]]).

## If enemy trinkets

Druid трикетит [[ability:sheep]]/[[ability:kidney-shot]] и держит NS-[[ability:cyclone]] на kill-attempt; warlock трикетит [[ability:kidney-shot]] → fear/[[ability:death-coil]]. Не вкладывай бурст, пока свободный druid с трикетом+NS может оборвать kill [[ability:cyclone]] — сперва свяжи druid'а.

## Common mistakes

- Бурстить warlock при свободном druid'е — [[ability:cyclone]]/NS-heal оборвут (источник: druid-protect).
- Гнаться за druid'ом (кайтит travel/HoT) вместо фокуса warlock'а.
- Идти в attrition-размен — RLD выигрывает по времени (источник: healer triage win-con).
- Дать felhunter снять наш [[ability:sheep]] druid'а перед добивом.

## Key cooldowns to track

- enemy: druid — [[ability:cyclone]], Nature's Swiftness, innervate, barkskin, travel-form, trinket; warlock — fear, [[ability:death-coil]], felhunter Spell Lock/Devour, healthstone, trinket; rogue — [[ability:cheap-shot]], [[ability:kidney-shot]], [[ability:blind]], [[ability:vanish]], [[ability:cloak-of-shadows]], trinket.
- ours: [[ability:sap]], [[ability:sheep]], [[ability:counterspell]], [[ability:nova]], [[ability:kidney-shot]], [[ability:blind]], [[ability:vanish]], [[ability:ice-block]]; priest — Mass Dispel, [[ability:pain-suppression]], [[ability:mana-burn]], [[ability:fear]], trinket.
