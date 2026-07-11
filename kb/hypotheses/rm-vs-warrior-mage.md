---
slug: rm-vs-warrior-mage
schema_version: 1
expansion: tbc
composition: rogue+mage
vs: warrior+mage
bracket: 2v2
difficulty: moderate
kill_target:
  primary: mage
  fallback: warrior
provenance: "AI-synthesized (Claude), UNVERIFIED — нет внешнего источника"
confidence: hypothesis
status: sourced-promoted
promoted_to: kb/drafts/rm-vs-warrior-mage.md
promoted_at: '2026-06-27'
tags: [ai-synthesized, unverified, needs-source-or-review]
---

> ✅ **ЗАСОРСЕНО (2026-06-27).** Promoted to `kb/drafts/rm-vs-warrior-mage.md`. Источники: AOEAH TBC 2v2 tier-list (Dec 2025) — warrior+mage D-tier anchor; Icy Veins 2v2 ranking (Jan 2026) — RM best-tier confirmation. Awaits owner approval via `python -m arena_ingest review approve --slug rm-vs-warrior-mage`.

## Opener

Вражеский состав — warrior + mage (мили + каст-бурст). Воин даёт давление и spell-lock через pummel/intercept, маг — sheep/nova/burst. Матчап решается mage-vs-mage 1v1 и тем, поймает ли наш рог их мага. Kill target — вражеский **mage** (сквишовее воина в plate; убрав его, легко добиваем воина 2v1).

Опенер: ищем их мага. [[ability:sap]] не на маге (он словит nova/blink), а контроль воина. Когда нашли мага — [[ability:premed]] → [[ability:cheap-shot]] → [[ability:hemo]] → [[ability:kidney-shot]] по магу, наш маг шатерит в окно ([[ability:nova]] → ice lance). Держи [[ability:counterspell]] на frost-школу их мага (блокирует их sheep/nova/burst). Превентивная [[ability:evasion]], когда воин в радиусе.

## Alternative opener

Если их воин+маг открыли на нашем маге (nova + charge): наш маг [[ability:ice-block]] под burst или [[ability:nova]] + blink, рог [[ability:cheap-shot]] → [[ability:kidney-shot]] их мага. Сбив их сетап, переходим в фокус мага.

## If enemy trinkets

Их маг тринкетит [[ability:kidney-shot]]/[[ability:sheep]] → [[ability:ice-block]] под наш добив, выжидай: после IB он всё ещё под давлением 2v1. Воин тринкетит [[ability:sheep]]/[[ability:nova]] → resheep или [[ability:blind]]. Опасайся spell-reflect (наши nova/sheep отлетают) и того, что их маг counterspell'ит нашего мага в kill-окне.

## Common mistakes

- Сесть на воина в plate вместо сквишового мага.
- Пропустить spell-reflect воина и засендить в него nova/sheep.
- Не закрыть [[ability:counterspell]] на frost-школу их мага — он спокойно sheep'ит и кайтит.
- Оставить нашего мага под одновременным charge воина и nova их мага.

## Key cooldowns to track

- enemy: warrior — charge/intercept, pummel, spell-reflect, hamstring, Mortal Strike, trinket; mage — [[ability:ice-block]], blink, [[ability:counterspell]], [[ability:sheep]], [[ability:nova]], [[ability:icy-veins]], trinket.
- ours: [[ability:counterspell]], [[ability:sheep]], [[ability:nova]], [[ability:kidney-shot]], [[ability:blind]], [[ability:vanish]], [[ability:evasion]], [[ability:ice-block]], trinket.
