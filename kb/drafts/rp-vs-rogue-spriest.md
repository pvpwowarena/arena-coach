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

## Strategy

Sourced-каркас (Windz, Warcraft Tavern, «SPR vs Disc Priest/Rogue», difficulty 6/10 со стороны SPR): в этом матчапе Spriest/Rogue **CC'ит рога и убивает disc-прийста** — «without buffs the priest can almost be one shot». Значит для RP **главная угроза — burst по нашему диско-прийсту** (их kill target — наш healer), а их рог будет вешать [[ability:sap]]/[[ability:blind]] на нашего рога и снимать его с пилла, открывая SP свободные касты и dispel'ы. Обзорная SPR-страница (Counters) подтверждает, что «Dwarf Disc + Caster» — один из контр-сетапов SPR, т.е. dwarf-диско с хорошим позиционированием перетягивает матчап на свою сторону.

Наш план (*synthesized-execution* на disc/rogue-механике из Mirlol RP-гайда): диско держит дистанцию и LoS относительно их прийста, шилдит себя и рога, **снимает с себя их DoT'ы** (Vampiric Touch / SW:Pain / DP — магия, dispel'ятся), держит [[ability:pain-suppression]] под их обозначенное burst-окно. Рог пилит их **shadow priest** (immobile, без жёсткого defensive CD, проигрывает мана-бой), [[ability:sap]] их рога на сетапе, [[ability:kidney-shot]] + [[ability:blind]] рвут их связку. dwarf-прийст добавляет Stoneform (снимает bleed/poison) — большой плюс в этом матчапе.

## Opener

Их рог почти всегда открывает на нашем диско. Превентив: рог рядом с прийстом, готов [[ability:gouge]]/[[ability:kidney-shot]] вражеского рога с их открытия; диско [[ability:fear]] (Psychic Scream) на их рога/SP, чтобы сорвать сетап, и сразу шилд. Дальше — наш [[ability:sap]] их рога и开 на их shadow priest. (synthesized-execution)

## If enemy trinkets

Их SP тринкетит наш [[ability:kidney-shot]] → [[ability:blind]] и резап, либо mana-burn-давление (он лимитирован маной — источник). Их рог тринкетит [[ability:sap]]/[[ability:blind]] → готовь [[ability:vanish]]/повторный [[ability:gouge]]. Под их синхронный burst (Psychic Scream → silence нашего диско → kidney) спасает [[ability:pain-suppression]] + шилд; silence лечится только пережиданием, поэтому диско не должен стоять mid-map.

## Common mistakes

- Дать их рогу свободно снимать нашего рога с пилла [[ability:sap]]/[[ability:blind]] — тогда SP кастует без помех.
- Не dispel'ить DoT'ы SP с диско: passive-heal SP от своих DoT'ов + их тиканье по нашему прийсту = проигранный мана/HP-обмен.
- Тратить [[ability:fear]] не вовремя: держи его на их kill-окно или на спасение, а не на ровном месте.
- Игнорировать, что их SP — immobile и без жёстких CD: это наш kill target, а не вражеский рог.

## Key cooldowns to track

- enemy: shadow priest — Psychic Scream ([[ability:fear]] DR), Silence, Dispel Magic, trinket; rogue — trinket, [[ability:cloak-of-shadows]], [[ability:vanish]], [[ability:blind]], [[ability:kidney-shot]], [[ability:sap]].
- ours: [[ability:fear]] (Psychic Scream), [[ability:pain-suppression]], [[ability:mana-burn]], dispel, [[ability:blind]], [[ability:gouge]], [[ability:kidney-shot]], [[ability:vanish]], trinket.

---

> **Тиринг:** sourced-каркас (Windz/WT: SPR kill = disc priest, our healer под угрозой; SP immobile/mana-limited; dwarf disc контрит SPR) + *synthesized-execution* для нашей последовательности пилов/опенера (на disc/rogue-механике из Mirlol-гайда). Перед промоутом в `kb/matchups/` — ревью топ-игрока.
