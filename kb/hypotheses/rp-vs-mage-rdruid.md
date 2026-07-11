---
slug: rp-vs-mage-rdruid
schema_version: 1
expansion: tbc
composition: rogue+priest
vs: mage+resto-druid
bracket: 2v2
difficulty: hard
kill_target:
  primary: mage
  fallback: druid
provenance: "AI-synthesized (Claude), UNVERIFIED — нет внешнего источника"
confidence: hypothesis
status: sourced-promoted
promoted_to: kb/drafts/rp-vs-mage-rdruid.md
promoted_at: '2026-06-28'
tags: [ai-synthesized, unverified, needs-source-or-review]
---

> ✅ **ЗАСОРСЕНО (2026-06-28).** Promoted to `kb/drafts/rp-vs-mage-rdruid.md`. Источник: in-depth DP/R-гайд Deadlycoward (Infernal Gladiator) на Warcraft Tavern, секция «DPR vs. Druid / Frost Mage» (5/10) — kill mage via mana-burn OOM, добив друида в human form после тринкета, прийст диспелит весь контроль кроме cyclone. Awaits owner approval via `python -m arena_ingest review approve --slug rp-vs-mage-rdruid`.

## Opener

Вражеский frost-маг + resto-друид: каст-дамаг + кайт-хилер. Без бурста мага у нас (как у RM) — давим роговым контролем и манабёрном. Kill target — вражеский маг (сквишовее; убрав его, играешь 2v1 на друида).

Опенер: рог [[ability:sap]] друида, открывает на вражеском маге через [[ability:garrote]] (silence рвёт каст) → [[ability:cheap-shot]]/[[ability:kidney-shot]], держит мага в [[ability:gouge]]/[[ability:kidney-shot]] (interrupt + lockout кастов). Прийст [[ability:mana-burn]] друида, dispel'ит regrowth/rejuv и [[ability:fear]] друида (tremor тут нет). Цель — не дать вражескому магу кастовать, а друиду — спокойно лить/innervate.

## Alternative opener

Если открыли на прийсте: вражеский маг CS-лочит школу хила прийста (fake-cast), sheep, друид [[ability:cyclone]]. [[ability:pain-suppression]] под burst, рог [[ability:blind]]/[[ability:kidney-shot]] разрывает сетап, [[ability:fear]] мага/друида в DR-окна. Затем назад на давление по магу.

## If enemy trinkets

Друид тринкетит [[ability:kidney-shot]]/[[ability:fear]] + NS-[[ability:cyclone]]; маг тринкетит [[ability:kidney-shot]]/[[ability:blind]]. Держи [[ability:blind]] на пост-тринкет друида, чтобы закрыть kill-окно на маге или дать прийсту докрутить манабёрн.

## Common mistakes

- Дать вражескому магу свободно кастовать — рог обязан рвать касты ([[ability:garrote]]/[[ability:gouge]]/[[ability:kidney-shot]]).
- Полагаться только на [[ability:fear]] по друиду — он barkskin/HoT'ит и кайтит; чередуй с физ-контролем по магу.
- Бурстить при свободном друиде ([[ability:cyclone]]/NS оборвут).
- Не следить за иннервейтом/питьём друида — затянет матч в свою пользу.

## Key cooldowns to track

- enemy: druid — [[ability:cyclone]], Nature's Swiftness, innervate, barkskin, trinket; mage — [[ability:ice-block]], blink, [[ability:counterspell]] (по прийсту), [[ability:sheep]], trinket.
- ours: [[ability:kidney-shot]], [[ability:blind]], [[ability:garrote]], [[ability:vanish]], [[ability:fear]]; priest — [[ability:mana-burn]], [[ability:pain-suppression]], dispel, trinket.
