---
slug: rp-vs-mage-hpala
schema_version: 1
expansion: tbc
composition: rogue+priest
vs: mage+holy-paladin
bracket: 2v2
difficulty: hard
kill_target:
  primary: mage
  fallback: paladin
provenance: "AI-synthesized (Claude), UNVERIFIED — нет внешнего источника"
confidence: hypothesis
status: sourced-promoted
promoted_to: kb/drafts/rp-vs-mage-hpala.md
promoted_at: '2026-07-07'
tags: [ai-synthesized, unverified, needs-source-or-review]
---

> ✅ **ЗАСОРСЕНО (2026-07-07).** Promoted to `kb/drafts/rp-vs-mage-hpala.md`. Якорь пары: Skill Capped (Season 2, Patch 2.5.5, upd. 2026-01-01) **называет пару тиром** на двух страницах — hpala-comps и fmage-comps: «C Tier: Holy Paladin + Frost Mage». Выполнено условие (а) из блока 🔎 ниже — пара оценена источником; class-handling якоря Deadlycoward (зафиксированы 06-30) вплетены только как обвязка с явной пометкой в sources. Awaits owner approval via `python -m arena_ingest review approve --slug rp-vs-mage-hpala`.
>
> ⚠ **AI-СИНТЕЗ, НЕ ПРОВЕРЕНО.** Из общих знаний по TBC 2.4.3, без гайда/стрима. Не отдавать игрокам как факт из базы. Нужен реальный источник или ревью топ-игрока перед переносом в kb/drafts/.
>
> 🔎 **Пере-проверено 2026-06-30 (браузер подключён, гайд перечитан напрямую через Chrome).** В гайде Deadlycoward (Warcraft Tavern, 20 матчапов) **нет отдельной секции mage+holy-paladin**. Есть только соседние: обработка frost-мага (DPriest/Mage 7/10, Druid/Mage 5/10 — «OOM the mage, never go aggressive, kite + Mana Burns») и holy-пала (Hpala/Warr 7/10, Rsham/Ret 7/10 — «kill pala after no mana»). Это class-handling, а не оценка самой пары. Промоут на склейке соседних секций = ровно тот conflation, который поймал SCAN-REPORT 2026-06-29 → **остаётся гипотезой** до (а) источника, оценивающего комбо mage+hpala, или (б) policy-решения владельца разрешить class-synthesis-промоут. Зафиксированные якоря — в `docs/SCAN-REPORT-2026-06-30.md`.

## Opener

Frost-маг + holy paladin: каст-дамаг под пала-хилом. У RP — [[ability:mana-burn]] (OOM паладина как alt-win) и силенс рога против кастов мага.

Kill target — вражеский маг. Опенер: рог [[ability:sap]] паладина, открывает на маге через [[ability:garrote]] (silence рвёт каст) → [[ability:cheap-shot]]/[[ability:kidney-shot]]/[[ability:gouge]], не давая блинкать-кайтить. Прийст [[ability:mana-burn]] паладина, dispel'ит freedom, [[ability:fear]] мага. Берегись вражеского [[ability:counterspell]] по прийсту (fake-cast) и [[ability:hammer-of-justice]].

## Alternative opener

Если открыли на прийсте: вражеский [[ability:counterspell]]+[[ability:sheep]], [[ability:hammer-of-justice]]. [[ability:pain-suppression]] под burst, рог [[ability:blind]]/[[ability:kidney-shot]] на маге снимает давление, [[ability:fear]] в DR-окна. Затем назад на мага + манабёрн паладина.

## If enemy trinkets

Paladin трикетит [[ability:fear]]/[[ability:hammer-of-justice]]; маг трикетит [[ability:kidney-shot]]/[[ability:blind]]. Держи [[ability:blind]] на пост-трикет паладина — докрутить манабёрн или закрыть kill-окно на маге.

## Common mistakes

- Дать вражескому магу свободно кастовать/блинкать — рог рвёт ([[ability:garrote]]/[[ability:gouge]]/[[ability:kidney-shot]]).
- Диспелить без разбора под [[ability:counterspell]]-угрозой; не fake-cast'ить.
- Бросить OOM-план паладина — без него матч затягивается.

## Key cooldowns to track

- enemy: mage — [[ability:ice-block]], blink, [[ability:counterspell]], [[ability:sheep]], trinket; paladin — bubble, freedom, cleanse, [[ability:hammer-of-justice]], trinket.
- ours: [[ability:kidney-shot]], [[ability:blind]], [[ability:garrote]], [[ability:vanish]], [[ability:fear]]; priest — [[ability:mana-burn]], [[ability:pain-suppression]], dispel, trinket.
