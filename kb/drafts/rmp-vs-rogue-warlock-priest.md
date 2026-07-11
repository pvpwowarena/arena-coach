---
slug: rmp-vs-rogue-warlock-priest
schema_version: 1
expansion: tbc
composition: rogue+mage+priest
vs: rogue+warlock+priest
bracket: 3v3
difficulty: very-hard
kill_target:
  primary: warlock
  fallback: rogue
maps_notes: {}
sources:
- type: web
  url: https://www.skill-capped.com/wowarticles/tbc/tier-lists/tbc-3v3/
  title: TBC Classic 3v3 Tier List (Skill Capped, Anniversary 2.5.5) — RLP = S-tier
  retrieved: '2026-06-23'
- type: web
  url: https://www.warcrafttavern.com/tbc/guides/3v3-arena-tier-list/
  title: Best 3v3 Arena Comps (Warcraft Tavern) — RLP/RLD, RMP описания
  retrieved: '2026-06-23'
last_reviewed: '2026-06-23'
reviewer: null
confidence: draft
tags: [community-sourced, needs-top-source, synthesized-execution, bracket-3v3-new]
---

## Strategy

_Провенанс: 3v3-драфт по принятому паттерну (как rmp-vs-WLD). Источники — tier-листы Skill Capped (Anniversary 2.5.5) и Warcraft Tavern: **RLP — S-tier**, peer RMP. RMP-сторона (kill-выбор, сетап, защита прийста) синтезирована из механик TBC 2.4.3. Теги `community-sourced`/`needs-top-source`/`synthesized-execution` — нужна верификация топ-RMP перед approve._

S-vs-S зеркало по духу: оба состава — control/attrition. RLP (источник): rogue-контроль + **affliction warlock** (постоянный DoT-spread, fear + [[ability:death-coil]], felhunter Spell Lock/Devour) + **disc priest** (dispel, mana burn, Psychic Scream, Mind Control, SW:D-бурст). Их win-con — аттриция и **мана-война** (mana burn), плюс одна CC-цепочка каскадит в kill.

Наш план (синтез): это игра в **чистый CC-сетап + быстрый kill-window**, а не в долгий размен (его мы проигрываем по мане/DoT). Kill target — **warlock** (убираем DoT-давление и второй fear-источник; сквишовее диско). Маг [[ability:sheep]] их прийста/рога вне kill-окна, [[ability:counterspell]] держит на heal/fear; рог [[ability:sap]] на сетапе и [[ability:cheap-shot]] → [[ability:kidney-shot]] по warlock в окно shatter ([[ability:nova]] → ice lance). Наш прийст играет от LoS, dispel'ит DoT'ы, держит [[ability:pain-suppression]].

## Opener

Стелс-открытие RMP: [[ability:sap]] одного (их рог или прийст), маг [[ability:sheep]] второго, бурст на warlock'е [[ability:premed]] → [[ability:cheap-shot]] → [[ability:kidney-shot]] + shatter. **Осторожно с felhunter** — Spell Lock прерывает наш ключевой каст, Devour Magic снимает [[ability:sheep]]/[[ability:nova]]; убери/отвлеки пета перед kill-окном.

## If enemy trinkets

Их warlock тринкетит [[ability:kidney-shot]] → death coil/fear-ловля; готовь [[ability:blind]] и второй сетап. Disc-прийст тринкетит и жмёт [[ability:pain-suppression]] — не вкладывай весь бурст в PS-окно. **Не blanket-dispel'ить** их прийста бездумно: снятие Unstable Affliction (warlock DoT) сайленсит снимающего — диспелим аккуратно.

## Common mistakes

- Идти в долгий размен — RLP выигрывает по мане/DoT (источник: mana-burn/attrition win-con).
- Бурстить под Spell Lock felhunter'а или дать Devour снять наш [[ability:sheep]].
- Снять UA с врага и поймать silence на нашем касте.
- Бросить прийста под их fear-цепочку (warlock fear + [[ability:death-coil]] + Psychic Scream) — он должен играть от LoS.

## Key cooldowns to track

- enemy: warlock — fear, [[ability:death-coil]], felhunter Spell Lock/Devour, UA-silence-on-dispel, healthstone, trinket; priest — Psychic Scream ([[ability:fear]]), Mass Dispel, [[ability:pain-suppression]], [[ability:mana-burn]], trinket; rogue — [[ability:cheap-shot]], [[ability:kidney-shot]], [[ability:blind]], [[ability:vanish]], [[ability:cloak-of-shadows]], trinket.
- ours: [[ability:sap]], [[ability:sheep]], [[ability:counterspell]], [[ability:nova]], [[ability:kidney-shot]], [[ability:blind]], [[ability:vanish]], [[ability:ice-block]]; priest — Mass Dispel, [[ability:pain-suppression]], [[ability:mana-burn]], [[ability:fear]], trinket.
