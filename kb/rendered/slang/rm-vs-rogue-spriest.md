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

<!-- АВТО-РЕНДЕР слоя slang (prototype). Источник правды: kb/drafts/rm-vs-rogue-spriest.md. Сгенерировано tools/render_slang.py — не редактировать вручную. -->

## опенер

Sourced-каркас (Windz, Warcraft Tavern, «SPR vs маг/рога» + обзорная SPR-страница, секция Counters): **RM — один из главных контр-составов Spriest/рога** («your gonna lose often game against rm... this is the best double дд»). Вражеский shadow прист не имеет мобильности (нет блинк/sprint), не имеет жёсткого defensive CD уровня блок/cloak и проигрывает затяжной/мана-бой. Поэтому **фокус — вражеский shadow прист** (рог — fallback).

Исполнение опенера — *synthesized-execution* на стандартной RM-механике (Mirlol RM-гайд, уже в KB): маг и рог садятся на shadow прист. сап вражеского рога, затем премед → чип → Hemorrhage → кидни по прийсту; маг шатерит в окно kidney (нова → ice lance/frostbolt). Держи кс на shadow-школу прийста — один lockout закрывает и его Psychic Scream (AoE фир), и mind blast/SW:D в kill-окне (по источнику Psychic Scream и Silence — главные swing-абилки SP).

## Alternative опенер

Если их рог открыл первым на нашего мага: маг нова и при необходимости блок под их burst, рог разрывает сетап чип → кидни по их рогу либо помогает шип/блайнд. Пережив открытие — возвращаемся к плану «сап их рога / train shadow прист». (synthesized-execution)

## If enemy trinkets

У shadow прист почти нет аутов — на его тринка держи повторный кидни/шип и не давай свободных кастов. Его Psychic Scream (магия школы shadow) рвёт burst: маг может снять фир блок, рог — Cloak of Shadows. Вражеский рог тринкетит kidney → ваниш или блайнд и продолжаем давить прийста. Учти: SP в shadowform мягко танчит урон и лечится от своих DoT'ов (passive heal по источнику), поэтому добивать его нужно в чистое burst-окно, а не размазанным уроном.

## Common mistakes

- Бурстить прийста, не закрыв кс/kick его Psychic Scream — фир сбрасывает весь сетап.
- Гоняться за рогом вместо immobile-прийста (по источнику SP — фокус, escape у него нет).
- Размазывать урон: shadowform + self-heal от DoT'ов отлечивают медленный дамаг — нужен сфокусированный шатер.
- Забывать, что SP offensive-dispel'ит наши баффы и может снимать нова-root с союзника (purge-эффекта нет, но dispel magic есть).

## Key cooldowns to track

- enemy: shadow прист — Psychic Scream (фир др), Silence, Dispel Magic, тринка (нет блок/блинк, нет dispersion в TBC); рога — тринка, Cloak of Shadows, ваниш, блайнд, кидни, Evasion.
- ours: кс, шип, нова, кидни, блайнд, ваниш, блок, Cloak of Shadows, тринка.

---

> **Тиринг:** sourced-каркас (Windz/WT: RM контрит SPR; kill SP; SP immobile, без жёстких CD, lose mana war) + *synthesized-execution* для точной последовательности опенера (на RM-механике из Mirlol-гайда). Перед промоутом в `kb/matchups/` — желателен ревью топ-игрока по конкретным combo-таймингам.
