---
slug: rp-vs-rogue-hpala
schema_version: 1
expansion: tbc
composition: rogue+priest
vs: rogue+holy-paladin
bracket: 2v2
difficulty: hard
kill_target:
  primary: rogue
  fallback: paladin
provenance: "AI-synthesized (Claude), UNVERIFIED — нет внешнего источника"
confidence: hypothesis
status: sourced-promoted
promoted_to: kb/drafts/rp-vs-rogue-hpala.md
promoted_at: '2026-07-02'
tags: [ai-synthesized, unverified, needs-source-or-review]
---

> ✅ **ЗАСОРСЕНО (2026-07-02).** Promoted to `kb/drafts/rp-vs-rogue-hpala.md`. Якорь пары: официальный Wowhead hpala-arena-гайд (patch 2.5.5, upd. 2026-02-10) — «Paladin / Warrior or Rogue» назван каноничным 2v2-сетапом hpala с посвящённой секцией + «the worst healers to bring». Анти-hpala план — Deadlycoward («Killing Pala with a few Mana Burns», якоря зафиксированы 06-30); поведение hpala vs rogue-команды — Hesback. Это снимает conflation-блок 06-29/06-30: пара теперь **названа источником** (Wowhead), class-handling якоря используются только как обвязка. kill_target в драфте изменён на paladin (по Deadlycoward). Awaits owner approval via `python -m arena_ingest review approve --slug rp-vs-rogue-hpala`.
>
> ⚠ **AI-СИНТЕЗ, НЕ ПРОВЕРЕНО.** Из общих знаний по TBC 2.4.3, без гайда/стрима. Не отдавать игрокам как факт из базы. Нужен реальный источник или ревью топ-игрока перед переносом в kb/drafts/.
>
> 🔎 **Пере-проверено 2026-06-30 (браузер подключён, гайд перечитан напрямую через Chrome).** В гайде Deadlycoward (Warcraft Tavern, 20 матчапов) **нет отдельной секции rogue+holy-paladin**. Есть только соседние: holy-пала (Hpala/Warr 7/10, Rsham/Ret 7/10 — «kill pala after no mana», dispel BoF) и контроль вражеского рога (Rogue/Rogue 7/10, Mirror 5/10 — «priest back to wall, stand away, blind the rogue»). Это class-handling, а не оценка самой пары. Промоут на склейке = conflation-риск (см. SCAN-REPORT 2026-06-29) → **остаётся гипотезой** до источника, оценивающего комбо rogue+hpala, или policy-решения владельца. Зафиксированные якоря — в `docs/SCAN-REPORT-2026-06-30.md`.

## Opener

Вражеский рог + holy paladin: их рог давит/контролит, пала хилит и BoP/freedom'ит его. У RP — [[ability:mana-burn]] (OOM паладина) и зеркальный рог. Kill target — вражеский рог; пала почти неубиваем, но манабёрн делает OOM-план реальным.

Опенер: наш рог [[ability:sap]] паладина (или ищет вражеского рога), садится на вражеского рога — [[ability:cheap-shot]]→[[ability:kidney-shot]], держит crippling+wound (но **cleanse снимает яды** — ре-шив). Прийст [[ability:mana-burn]] паладина + [[ability:fear]] вражеского рога когда тот вне стелса, dispel'ит freedom. Не дай засапать прийста на старте.

## Alternative opener

Если открыли на прийсте: вражеский [[ability:cheap-shot]]→[[ability:kidney-shot]], [[ability:hammer-of-justice]]. [[ability:pain-suppression]], трикет [[ability:kidney-shot]] (не [[ability:blind]]), наш рог [[ability:blind]]/[[ability:kidney-shot]] вражеского рога, [[ability:fear]] на его [[ability:vanish]].

## If enemy trinkets

Paladin трикетит [[ability:fear]]/[[ability:hammer-of-justice]]; вражеский рог трикетит [[ability:kidney-shot]]/[[ability:blind]]. Держи [[ability:blind]] на пала или на пост-[[ability:cloak-of-shadows]] вражеского рога; докручивай манабёрн.

## Common mistakes

- Забыть про cleanse: пала снимет crippling/wound — нужен ре-шив.
- Полагаться на [[ability:fear]] вражеского рога, когда он в [[ability:cloak-of-shadows]]/[[ability:vanish]].
- Тунелить пала без OOM-плана; дать вражескому рогу чистый опенер на прийста.

## Key cooldowns to track

- enemy: rogue — [[ability:vanish]], [[ability:cloak-of-shadows]], [[ability:blind]], [[ability:kidney-shot]], prep, evasion, trinket; paladin — bubble, freedom, cleanse, BoP, [[ability:hammer-of-justice]], trinket.
- ours: [[ability:kidney-shot]], [[ability:blind]], [[ability:vanish]], [[ability:fear]]; priest — [[ability:mana-burn]], [[ability:pain-suppression]], dispel, trinket.
