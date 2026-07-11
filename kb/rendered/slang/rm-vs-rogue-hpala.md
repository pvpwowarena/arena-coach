---
slug: rm-vs-rogue-hpala
schema_version: 1
expansion: tbc
composition: rogue+mage
vs: rogue+holy-paladin
bracket: 2v2
difficulty: hard
kill_target:
  primary: rogue
  fallback: paladin
maps_notes: {}
sources:
- type: web
  url: "https://www.wowhead.com/tbc/guide/holy-paladin-healer-pvp-arena-guide-burning-crusade-classic-wow"
  title: "TBC Classic Holy Paladin Healing Arena Guide (Wowhead, patch 2.5.5, upd. 2026-02-10) — «Paladin / Warrior or Rogue» назван самым распространённым 2v2-сетапом hpala (посвящённая секция: Cleanse, Blessing of Freedom на мили-партнёра, HoJ, Consecration против стелса, bubble/BoP + Forbearance); роль в арене: «the worst healers to bring» — hard-cast хилы (лок дается легко), нет мобильности («contained quite easily»), fake-casting как выживание"
  retrieved: '2026-07-02'
- type: web
  url: "https://www.wowhead.com/tbc/guide/holy-paladin-tbcc-pvp-guide-gearing-tips-tricks-and-2v2-warrior-paladin-matchups-15309"
  title: "Hesback (Gladiator S2, Firemaw-EU) — Holy Paladin TBCC PvP Guide (Wowhead) — поведение hpala против rogue-команд: «Stoneform is amazing against rogue teams» (сброс wound + вторая freedom), «Against non dispelling Rogue teams you can basically keep Blessing of Sacrifice 24/7 until Blind», «stay at max range vs rogue teams», экономия тринкета/BoP («BoP 2nd Kidney», «save trinket to BoP the 2nd Blind»)"
  retrieved: '2026-07-02'
last_reviewed: '2026-07-02'
reviewer: null
confidence: draft
tags: [community-sourced, needs-top-source, synthesized-execution]
---

<!-- АВТО-РЕНДЕР слоя slang (prototype). Источник правды: kb/drafts/rm-vs-rogue-hpala.md. Сгенерировано tools/render_slang.py — не редактировать вручную. -->

## опенер

_Провенанс: якорь пары — официальный hpala-arena-гайд Wowhead (patch 2.5.5): «пал / вар or рога» = каноничный 2v2-сетап hpala, с посвящённой секцией по киту (Cleanse/Freedom/HoJ/Consecration/bubble); там же оценка компа: hpala — «худший хилер для арены», hard-cast хилы, нет мобильности. Поведение паладина против рога-команд — Hesback (Gladiator). Ни один tier-лист (AOEAH/WT/Skill Capped/Mirlol) пару рога+hpala не тирует — комп ниже меты. Пошаговое исполнение синтезировано из механик TBC 2.4.3 — теги `community-sourced`/`needs-top-source`/`synthesized-execution`._

Вражеский состав — их рог даёт весь урон и контроль, hpala держит его хилом, Cleanse'ом и freedom/BoP (источник: секция Wowhead). Ключевая асимметрия: у RM нет манабёрна, а Cleanse снимает шип с паладина и яды с их рога — поэтому оом-план недоступен, играем **от бурст-окон по их рогу**. фокус — вражеский **рога**: hpala сам не убивает, а рог без хила от команды RM умирает в один правильный сетап.

Опенер: наш рог ищет их рога (care: их hpala может выбить нашего рога из стелса Consecration'ом — это прямой совет их гайда; держись вне 8-ярдовой зоны паладина). Маг открывает шип на паладина ТОЛЬКО как бейт (Cleanse снимет — но потратит его GCD/ману), реальный сетап: чип→кидни на их роге + нова-шаттер, кс на heal-школу паладина в килл-окно. Burst вкладываем, когда у паладина нет freedom/BoP/bubble — Hesback прямо описывает их экономию: BoP держат на 2-й кидни, тринкет — на 2-й блайнд. Значит, первый блайнд на паладина обычно проходит → используем его для чистого кила-окна по рогу.

## Alternative опенер

Если их рог открылся первым на маге (чип→кидни, сверху подж паладина): маг тринкетит kidney (не их блайнд), блок под ярость, наш рог немедленно перекрывает их рога кидни/Gouge и снимает давление. Дальше — назад к нашему сетапу: их hpala после раннего HoJ остаётся без стана на ~минуту.

## If enemy trinkets

Их пал по гайду Hesback **не** тринкетит первый сетап — держит тринкет под наш блайнд (BoP-очередь: 2-й kidney). Если паладин всё же тринкетнул рано — это окно: блайнд залипнет, маг свободно кастует в их рога. Их рог тринкетит кидни/шип; после его тринкета — полный шаттер-сетап. Dwarf-паладин: Stoneform = вторая freedom + сброс wound (Hesback) — не считай его законтроленным по снарам.

## Common mistakes

- Бурстить их рога, пока у паладина доступны freedom/BoP/bubble — вся тройка отменяет сетап (Wowhead: кит компа).
- Кидать шип в паладина как реальный CC (Cleanse снимает мгновенно) — это только бейт GCD.
- Открываться в радиусе Consecration — hpala выбивает из стелса (прямой совет их гайда).
- Играть лонг-гейм: без манабёрна RM не выигрывает истощение — против hard-cast хилера выигрывают лок-даун окна (кс, кидни на пала в момент каста).

## Key cooldowns to track

- enemy: рога — ваниш, Cloak of Shadows, блайнд, кидни, преп, Evasion, тринка; пал — bubble (Divine Shield), BoP (+Forbearance после), freedom, Cleanse, подж, Consecration, тринка, Stoneform (если dwarf).
- ours: кс, шип, нова, блайнд, кидни, ваниш, блок, тринка.
