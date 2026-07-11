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
  title: "Hesback (Gladiator S2, Firemaw-EU) — Holy Paladin TBCC PvP Guide (Wowhead) — поведение hpala против rogue-команд: «Stoneform is amazing against rogue teams» (сброс wound + вторая freedom), «Against non dispelling Rogue teams you can basically keep Blessing of Sacrifice 24/7 until Blind», «stay at max range vs rogue teams», экономия трикета/BoP («BoP 2nd Kidney», «save trinket to BoP the 2nd Blind»)"
  retrieved: '2026-07-02'
last_reviewed: '2026-07-02'
reviewer: null
confidence: draft
tags: [community-sourced, needs-top-source, synthesized-execution]
---

## Opener

_Провенанс: якорь пары — официальный hpala-arena-гайд Wowhead (patch 2.5.5): «Paladin / Warrior or Rogue» = каноничный 2v2-сетап hpala, с посвящённой секцией по киту (Cleanse/Freedom/HoJ/Consecration/bubble); там же оценка компа: hpala — «худший хилер для арены», hard-cast хилы, нет мобильности. Поведение паладина против rogue-команд — Hesback (Gladiator). Ни один tier-лист (AOEAH/WT/Skill Capped/Mirlol) пару rogue+hpala не тирует — комп ниже меты. Пошаговое исполнение синтезировано из механик TBC 2.4.3 — теги `community-sourced`/`needs-top-source`/`synthesized-execution`._

Вражеский состав — их рог даёт весь урон и контроль, hpala держит его хилом, Cleanse'ом и freedom/BoP (источник: секция Wowhead). Ключевая асимметрия: у RM нет манабёрна, а Cleanse снимает [[ability:sheep]] с паладина и яды с их рога — поэтому OOM-план недоступен, играем **от бурст-окон по их рогу**. Kill target — вражеский **rogue**: hpala сам не убивает, а рог без хила от команды RM умирает в один правильный сетап.

Опенер: наш рог ищет их рога (care: их hpala может выбить нашего рога из стелса Consecration'ом — это прямой совет их гайда; держись вне 8-ярдовой зоны паладина). Маг открывает [[ability:sheep]] на паладина ТОЛЬКО как бейт (Cleanse снимет — но потратит его GCD/ману), реальный сетап: [[ability:cheap-shot]]→[[ability:kidney-shot]] на их роге + [[ability:nova]]-shatter, [[ability:counterspell]] на heal-школу паладина в килл-окно. Burst вкладываем, когда у паладина нет freedom/BoP/bubble — Hesback прямо описывает их экономию: BoP держат на 2-й [[ability:kidney-shot]], трикет — на 2-й [[ability:blind]]. Значит, первый [[ability:blind]] на паладина обычно проходит → используем его для чистого кила-окна по рогу.

## Alternative opener

Если их рог открылся первым на маге ([[ability:cheap-shot]]→[[ability:kidney-shot]], сверху [[ability:hammer-of-justice]] паладина): маг трикетит kidney (не их blind), [[ability:ice-block]] под ярость, наш рог немедленно перекрывает их рога [[ability:kidney-shot]]/[[ability:gouge]] и снимает давление. Дальше — назад к нашему сетапу: их hpala после раннего HoJ остаётся без стана на ~минуту.

## If enemy trinkets

Их paladin по гайду Hesback **не** трикетит первый сетап — держит трикет под наш [[ability:blind]] (BoP-очередь: 2-й kidney). Если паладин всё же трикетнул рано — это окно: [[ability:blind]] залипнет, маг свободно кастует в их рога. Их рог трикетит [[ability:kidney-shot]]/[[ability:sheep]]; после его трикета — полный шаттер-сетап. Dwarf-паладин: Stoneform = вторая freedom + сброс wound (Hesback) — не считай его законтроленным по снарам.

## Common mistakes

- Бурстить их рога, пока у паладина доступны freedom/BoP/bubble — вся тройка отменяет сетап (Wowhead: кит компа).
- Кидать [[ability:sheep]] в паладина как реальный CC (Cleanse снимает мгновенно) — это только бейт GCD.
- Открываться в радиусе Consecration — hpala выбивает из стелса (прямой совет их гайда).
- Играть лонг-гейм: без манабёрна RM не выигрывает истощение — против hard-cast хилера выигрывают лок-даун окна ([[ability:counterspell]], [[ability:kidney-shot]] на пала в момент каста).

## Key cooldowns to track

- enemy: rogue — [[ability:vanish]], [[ability:cloak-of-shadows]], [[ability:blind]], [[ability:kidney-shot]], [[ability:preparation]], [[ability:evasion]], trinket; paladin — bubble (Divine Shield), BoP (+Forbearance после), freedom, Cleanse, [[ability:hammer-of-justice]], Consecration, trinket, Stoneform (если dwarf).
- ours: [[ability:counterspell]], [[ability:sheep]], [[ability:nova]], [[ability:blind]], [[ability:kidney-shot]], [[ability:vanish]], [[ability:ice-block]], trinket.
