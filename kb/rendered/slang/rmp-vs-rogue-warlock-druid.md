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

<!-- АВТО-РЕНДЕР слоя slang (prototype). Источник правды: kb/drafts/rmp-vs-rogue-warlock-druid.md. Сгенерировано tools/render_slang.py — не редактировать вручную. -->

## Strategy

_Провенанс: 3v3-драфт по принятому паттерну (как rmp-vs-WLD). Источники — Warcraft Tavern и Skill Capped (Anniversary 2.5.5): **RLD** = S/A-tier attrition-состав. RMP-сторона синтезирована из механик TBC 2.4.3. Теги `community-sourced`/`needs-top-source`/`synthesized-execution` — нужна верификация топ-RMP перед approve._

RLD (источник, WT): «skips the CC of a Frost маг in favor of constant pressure and attrition of a лок — with enough time the хил enters triage, и одна CC-цепочка каскадит в win». То есть **resto друид** кайтит (travel/HoT) + циклон протектит kill-attempts, **affliction лок** размазывает DoT'ы и фирит, **рога** контролит. Их сила — время и spread-damage.

Наш план (синтез): **не давать игре затянуться** — нужен чистый CC-сетап и быстрый kill, пока друид связан. фокус — **лок** (источник DoT-аттриции и фир'а; друид почти некиллабелен из-за кайта/цикла). Сетап: сап друид → маг шип/кс на его heal/циклон-каст → бурст лок'а (чип → кидни + шаттер нова→ice lance) в окно, когда друид под CC и не может оборвать добив циклон. Прийст dispel'ит DoT'ы, Pain Suppression под их фир+burst.

## опенер

Стелс-открытие: найти друид'а или лок'а. сап одного, шип второго, бурст лок. Перед kill-окном **свяжи друид'а** (шип/кс на его cast) — свободный друид циклонит наш добив. Осторожно с felhunter (Spell Lock/Devour снимает шип/нова).

## If enemy trinkets

друид тринкетит шип/кидни и держит NS-циклон на kill-attempt; лок тринкетит кидни → фир/Death Coil. Не вкладывай бурст, пока свободный друид с тринкетом+NS может оборвать kill циклон — сперва свяжи друид'а.

## Common mistakes

- Бурстить лок при свободном друид'е — циклон/NS-heal оборвут (источник: друид-protect).
- Гнаться за друид'ом (кайтит travel/HoT) вместо фокуса лок'а.
- Идти в attrition-размен — RLD выигрывает по времени (источник: хил triage win-con).
- Дать felhunter снять наш шип друид'а перед добивом.

## Key cooldowns to track

- enemy: друид — циклон, Nature's Swiftness, innervate, barkskin, travel-form, тринка; лок — фир, Death Coil, felhunter Spell Lock/Devour, healthstone, тринка; рога — чип, кидни, блайнд, ваниш, Cloak of Shadows, тринка.
- ours: сап, шип, кс, нова, кидни, блайнд, ваниш, блок; прист — Mass Dispel, Pain Suppression, Mana Burn, фир, тринка.
