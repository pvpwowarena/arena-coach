---
slug: rp-vs-rogue-spriest
schema_version: 1
expansion: tbc
composition: rogue+priest
vs: rogue+shadow-priest
bracket: 2v2
difficulty: moderate
kill_target:
  primary: priest
  fallback: rogue
maps_notes: {}
sources:
- type: web
  url: https://www.warcrafttavern.com/tbc/guides/rogue-shadow-priest-2v2/
  retrieved: '2026-06-23'
  title: Windz — Rogue/Shadow Priest 2v2 (раздел SPR vs Disc Priest/Rogue)
- type: web
  url: https://www.warcrafttavern.com/tbc/guides/rogue-shadow-priest-rogue-arena-strategies/
  retrieved: '2026-06-23'
  title: Shadow Priest/Rogue — TBC 2v2 Strategies (counters - Dwarf Disc + Caster)
- type: file
  path: WOW TBC ARENA - Rogue Priest.md
  author: Mirlol (transcribed)
  retrieved: '2026-05-12'
last_reviewed: '2026-06-23'
reviewer: null
confidence: draft
tags: [sourced, synthesized-execution, vs-double-dps]
---

<!-- АВТО-РЕНДЕР слоя slang (prototype). Источник правды: kb/drafts/rp-vs-rogue-spriest.md. Сгенерировано tools/render_slang.py — не редактировать вручную. -->

## Strategy

Sourced-каркас (Windz, Warcraft Tavern, «SPR vs Disc прист/рога», difficulty 6/10 со стороны SPR): в этом матчапе Spriest/рога **CC'ит рога и убивает disc-прийста** — «without buffs the прист can almost be one shot». Значит для RP **главная угроза — burst по нашему диско-прийсту** (их фокус — наш хил), а их рог будет вешать сап/блайнд на нашего рога и снимать его с пилла, открывая SP свободные касты и dispel'ы. Обзорная SPR-страница (Counters) подтверждает, что «Dwarf Disc + Caster» — один из контр-сетапов SPR, т.е. dwarf-диско с хорошим позиционированием перетягивает матчап на свою сторону.

Наш план (*synthesized-execution* на disc/рога-механике из Mirlol RP-гайда): диско держит дистанцию и лос относительно их прийста, шилдит себя и рога, **снимает с себя их DoT'ы** (Vampiric Touch / SW:Pain / DP — магия, dispel'ятся), держит Pain Suppression под их обозначенное burst-окно. Рог пилит их **shadow прист** (immobile, без жёсткого defensive CD, проигрывает мана-бой), сап их рога на сетапе, кидни + блайнд рвут их связку. dwarf-прийст добавляет Stoneform (снимает bleed/poison) — большой плюс в этом матчапе.

## опенер

Их рог почти всегда открывает на нашем диско. Превентив: рог рядом с прийстом, готов Gouge/кидни вражеского рога с их открытия; диско фир (Psychic Scream) на их рога/SP, чтобы сорвать сетап, и сразу шилд. Дальше — наш сап их рога и开 на их shadow прист. (synthesized-execution)

## If enemy trinkets

Их SP тринкетит наш кидни → блайнд и резап, либо mana-burn-давление (он лимитирован маной — источник). Их рог тринкетит сап/блайнд → готовь ваниш/повторный Gouge. Под их синхронный burst (Psychic Scream → silence нашего диско → kidney) спасает Pain Suppression + шилд; silence лечится только пережиданием, поэтому диско не должен стоять mid-map.

## Common mistakes

- Дать их рогу свободно снимать нашего рога с пилла сап/блайнд — тогда SP кастует без помех.
- Не dispel'ить DoT'ы SP с диско: passive-heal SP от своих DoT'ов + их тиканье по нашему прийсту = проигранный мана/HP-обмен.
- Тратить фир не вовремя: держи его на их kill-окно или на спасение, а не на ровном месте.
- Игнорировать, что их SP — immobile и без жёстких CD: это наш фокус, а не вражеский рог.

## Key cooldowns to track

- enemy: shadow прист — Psychic Scream (фир др), Silence, Dispel Magic, тринка; рога — тринка, Cloak of Shadows, ваниш, блайнд, кидни, сап.
- ours: фир (Psychic Scream), Pain Suppression, Mana Burn, dispel, блайнд, Gouge, кидни, ваниш, тринка.

---

> **Тиринг:** sourced-каркас (Windz/WT: SPR kill = disc прист, our хил под угрозой; SP immobile/mana-limited; dwarf disc контрит SPR) + *synthesized-execution* для нашей последовательности пилов/опенера (на disc/рога-механике из Mirlol-гайда). Перед промоутом в `kb/matchups/` — ревью топ-игрока.
