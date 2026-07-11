---
slug: rm-vs-rogue-spriest
schema_version: 1
expansion: tbc
composition: rogue+mage
vs: rogue+shadow-priest
bracket: 2v2
difficulty: easy
kill_target:
  primary: priest
  fallback: rogue
maps_notes: {}
sources:
- type: web
  url: https://www.warcrafttavern.com/tbc/guides/rogue-shadow-priest-2v2/
  retrieved: '2026-06-23'
  title: Windz — Rogue/Shadow Priest 2v2 (раздел SPR vs Mage/Rogue)
- type: web
  url: https://www.warcrafttavern.com/tbc/guides/rogue-shadow-priest-rogue-arena-strategies/
  retrieved: '2026-06-23'
  title: Shadow Priest/Rogue — TBC 2v2 Strategies (counters - Rogue Mage)
- type: file
  path: WOW TBC ARENA - Rogue  Mage.md
  author: Mirlol (transcribed)
  retrieved: '2026-05-12'
last_reviewed: '2026-06-23'
reviewer: null
confidence: draft
tags: [sourced, synthesized-execution, vs-double-dps]
---

## Opener

Sourced-каркас (Windz, Warcraft Tavern, «SPR vs Mage/Rogue» + обзорная SPR-страница, секция Counters): **RM — один из главных контр-составов Spriest/Rogue** («your gonna lose often game against rm... this is the best double dps»). Вражеский shadow priest не имеет мобильности (нет blink/sprint), не имеет жёсткого defensive CD уровня ice block/cloak и проигрывает затяжной/мана-бой. Поэтому **kill target — вражеский shadow priest** (рог — fallback).

Исполнение опенера — *synthesized-execution* на стандартной RM-механике (Mirlol RM-гайд, уже в KB): маг и рог садятся на shadow priest. [[ability:sap]] вражеского рога, затем [[ability:premed]] → [[ability:cheap-shot]] → [[ability:hemo]] → [[ability:kidney-shot]] по прийсту; маг шатерит в окно kidney ([[ability:nova]] → ice lance/frostbolt). Держи [[ability:counterspell]] на shadow-школу прийста — один lockout закрывает и его Psychic Scream (AoE fear), и mind blast/SW:D в kill-окне (по источнику Psychic Scream и Silence — главные swing-абилки SP).

## Alternative opener

Если их рог открыл первым на нашего мага: маг [[ability:nova]] и при необходимости [[ability:ice-block]] под их burst, рог разрывает сетап [[ability:cheap-shot]] → [[ability:kidney-shot]] по их рогу либо помогает [[ability:sheep]]/[[ability:blind]]. Пережив открытие — возвращаемся к плану «[[ability:sap]] их рога / train shadow priest». (synthesized-execution)

## If enemy trinkets

У shadow priest почти нет аутов — на его trinket держи повторный [[ability:kidney-shot]]/[[ability:sheep]] и не давай свободных кастов. Его Psychic Scream (магия школы shadow) рвёт burst: маг может снять фир [[ability:ice-block]], рог — [[ability:cloak-of-shadows]]. Вражеский рог тринкетит kidney → [[ability:vanish]] или [[ability:blind]] и продолжаем давить прийста. Учти: SP в shadowform мягко танчит урон и лечится от своих DoT'ов (passive heal по источнику), поэтому добивать его нужно в чистое burst-окно, а не размазанным уроном.

## Common mistakes

- Бурстить прийста, не закрыв [[ability:counterspell]]/kick его Psychic Scream — фир сбрасывает весь сетап.
- Гоняться за рогом вместо immobile-прийста (по источнику SP — kill target, escape у него нет).
- Размазывать урон: shadowform + self-heal от DoT'ов отлечивают медленный дамаг — нужен сфокусированный шатер.
- Забывать, что SP offensive-dispel'ит наши баффы и может снимать [[ability:nova]]-root с союзника (purge-эффекта нет, но dispel magic есть).

## Key cooldowns to track

- enemy: shadow priest — Psychic Scream ([[ability:fear]] DR), Silence, Dispel Magic, trinket (нет ice block/blink, нет dispersion в TBC); rogue — trinket, [[ability:cloak-of-shadows]], [[ability:vanish]], [[ability:blind]], [[ability:kidney-shot]], [[ability:evasion]].
- ours: [[ability:counterspell]], [[ability:sheep]], [[ability:nova]], [[ability:kidney-shot]], [[ability:blind]], [[ability:vanish]], [[ability:ice-block]], [[ability:cloak-of-shadows]], trinket.

---

> **Тиринг:** sourced-каркас (Windz/WT: RM контрит SPR; kill SP; SP immobile, без жёстких CD, lose mana war) + *synthesized-execution* для точной последовательности опенера (на RM-механике из Mirlol-гайда). Перед промоутом в `kb/matchups/` — желателен ревью топ-игрока по конкретным combo-таймингам.
